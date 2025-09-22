import os
import glob
import torch
from tqdm import tqdm
from pymilvus import MilvusClient

client = MilvusClient(
    uri="http://localhost:19530"
)


def BGE_VL_v1_5_zs_eval_mrr(
        model_name="/home/public/dkx/model/BAAI/BGE-VL-v1.5-zs",
        query_glob="/home/public/dataset-MegaCQA/test/*/txt/*.txt",
        collection_name="ChartGen",
        k_values=None,
        task_instruction="Recommend the most suitable chart with corresponding description for visualizing the information given by the provided text: ",
        anns_field="hybrid_dense",
        target_chart_types=None,
        samples_per_type=None,  # 新增：每种图表类型的样本数量，None表示使用所有样本
        random_seed=42  # 新增：随机种子，用于确保结果可复现
):
    """
    批量评估 MRR：
    - 相关性判定：命中文档的 hit['type'] == 该 query 的 chart_type（由路径 test/<chart_type>/txt/*.txt 推断）
    - MRR: 对每个查询取第一个相关命中的倒数排名，最后取平均
    - 同时输出多个k值的 Hit@1, Hit@3, Hit@5, Hit@10

    参数:
        target_chart_types: 指定要测试的图表类型列表，如 ["bar", "bubble", "chord"] 等
                           如果为None，则测试所有找到的图表类型
        samples_per_type: 每种图表类型的样本数量，如果为None则使用所有样本
                         可以是整数（所有类型使用相同数量）或字典（为每种类型指定不同数量）
        random_seed: 随机种子，用于样本采样的可复现性

    依赖：
        - 已经有全局变量 `client` 且连接到向量库，能调用 .load_collection 和 .search
        - modelscope 已安装
    """

    if k_values is None:
        k_values = [1, 3, 5, 10]

    def get_field(hit, name):
        try:
            if isinstance(hit, dict):
                return hit.get(name)
            if hasattr(hit, "get"):
                try:
                    v = hit.get(name, None)
                    if v is not None:
                        return v
                except Exception:
                    pass
            if hasattr(hit, "entity") and hasattr(hit.entity, "get"):
                try:
                    v = hit.entity.get(name, None)
                    if v is not None:
                        return v
                except Exception:
                    pass
            if hasattr(hit, name):
                return getattr(hit, name)
        except Exception:
            pass
        return None

    import re
    import random
    from collections import defaultdict

    # 设置随机种子以确保结果可复现
    if random_seed is not None:
        random.seed(random_seed)

    def normalize_chart_type(raw: str) -> str:
        s = raw.strip().lower().replace("-", "_")
        if re.fullmatch(r"treemap(?:_d3)?", s):
            return "treemap"
        return s

    from modelscope import AutoModel
    # 1) 模型
    model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
    model.eval()
    model.cuda()
    model.set_processor(model_name)

    # 2) 收集查询与目标类型（并做类型归一）
    txt_paths = glob.glob(query_glob)

    # 按图表类型分组收集查询
    queries_by_type = defaultdict(list)

    # 如果指定了target_chart_types，将其转换为归一化的集合
    if target_chart_types is not None:
        target_set = {normalize_chart_type(t) for t in target_chart_types}
    else:
        target_set = None

    # 首先按类型收集所有查询
    for txt_path in txt_paths:
        parts = os.path.normpath(txt_path).split(os.sep)
        raw_type = parts[-3]  # .../test/<chart_type>/txt/xxx.txt
        chart_type = normalize_chart_type(raw_type)

        # 如果指定了目标类型，只处理目标类型的文件
        if target_set is not None and chart_type not in target_set:
            continue

        # 读文本（尝试utf-8编码，如果失败则用gbk）
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
        except UnicodeDecodeError:
            with open(txt_path, "r", encoding="gbk") as f:
                text = f.read().strip()

        if not text:
            continue

        queries_by_type[chart_type].append((text, chart_type, txt_path))

    # 对每种类型进行采样
    queries = []

    if samples_per_type is not None:
        for chart_type, type_queries in queries_by_type.items():
            # 确定该类型要采样的数量
            if isinstance(samples_per_type, dict):
                n_samples = samples_per_type.get(chart_type, len(type_queries))
            else:
                n_samples = samples_per_type

            # 进行采样
            if n_samples >= len(type_queries):
                # 如果要求的样本数不少于现有样本数，使用全部样本
                sampled_queries = type_queries
            else:
                # 随机采样
                sampled_queries = random.sample(type_queries, n_samples)

            queries.extend(sampled_queries)
            print(f"图表类型 '{chart_type}': 总共 {len(type_queries)} 个样本，采样 {len(sampled_queries)} 个")
    else:
        # 如果没有指定采样数量，使用所有查询
        for chart_type, type_queries in queries_by_type.items():
            queries.extend(type_queries)
            print(f"图表类型 '{chart_type}': 使用全部 {len(type_queries)} 个样本")

    if not queries:
        raise RuntimeError("没有在指定路径找到任何查询文本。检查 query_glob 是否正确。")

    print(f"\n总共将评估 {len(queries)} 个查询")

    # 3) 向量库
    client.load_collection(collection_name)

    # 4) 统计容器 - 修改：为每个k值分别统计
    per_type_rrs = defaultdict(list)
    per_type_total = defaultdict(int)

    # 为每个k值创建Hit@k统计
    per_type_hitk = {}
    overall_hitk = {}
    for k in k_values:
        per_type_hitk[k] = defaultdict(int)
        overall_hitk[k] = 0

    overall_rrs = []

    # 5) 检索并累计 - 修改：使用最大k值作为检索限制
    max_k = max(k_values)
    with torch.no_grad():
        for text, target_type, path in tqdm(queries, desc="Evaluating MRR by type"):
            q = model.data_process(text=text, q_or_c="q", task_instruction=task_instruction)
            emb = model(**q, output_hidden_states=True)[:, -1, :]
            emb = torch.nn.functional.normalize(emb, dim=-1)
            emb_list = emb.detach().cpu().tolist()

            results = client.search(
                collection_name=collection_name,
                anns_field=anns_field,
                data=emb_list,
                limit=max_k,
                search_params={"metric_type": "IP"},
                output_fields=["type", "image_url"],
            )
            hits = results[0]

            rank = None
            for idx, hit in enumerate(hits, start=1):
                hit_type_raw = get_field(hit, "type")
                hit_type = normalize_chart_type(str(hit_type_raw)) if hit_type_raw is not None else None
                if hit_type == target_type:
                    rank = idx
                    break

            per_type_total[target_type] += 1
            if rank is None:
                per_type_rrs[target_type].append(0.0)
                overall_rrs.append(0.0)
            else:
                rr = 1.0 / rank
                per_type_rrs[target_type].append(rr)
                overall_rrs.append(rr)

                # 修改：为每个k值分别统计Hit@k
                for k in k_values:
                    if rank <= k:
                        per_type_hitk[k][target_type] += 1
                        overall_hitk[k] += 1

    # 6) 计算各类型与整体指标 - 修改：包含所有k值
    per_type_metrics = {}
    for t in sorted(per_type_total.keys()):
        Q_t = per_type_total[t]
        mrr_t = (sum(per_type_rrs[t]) / Q_t) if Q_t > 0 else 0.0

        metrics = {
            "queries": Q_t,
            "MRR": round(mrr_t, 6),
        }

        # 为每个k值添加Hit@k指标
        for k in k_values:
            hitk_rate_t = per_type_hitk[k][t] / Q_t if Q_t > 0 else 0.0
            metrics[f"Hit@{k}"] = round(hitk_rate_t, 6)

        per_type_metrics[t] = metrics

    Q_all = len(overall_rrs)
    overall_metrics = {
        "queries": Q_all,
        "MRR": round(sum(overall_rrs) / Q_all, 6) if Q_all > 0 else 0.0,
    }

    # 为整体添加所有k值的Hit@k指标
    for k in k_values:
        hitk_rate = overall_hitk[k] / Q_all if Q_all > 0 else 0.0
        overall_metrics[f"Hit@{k}"] = round(hitk_rate, 6)

    # 7) 输出 - 修改：显示所有k值的结果
    print("\n===== Per-Type Metrics =====")
    # 创建表头
    header = f"{'Type':<15} {'Queries':<8} {'MRR':<8}"
    for k in k_values:
        header += f" {'Hit@' + str(k):<8}"
    print(header)
    print("-" * len(header))

    # 输出每个类型的指标
    for t, m in per_type_metrics.items():
        row = f"{t:<15} {m['queries']:<8} {m['MRR']:<8.6f}"
        for k in k_values:
            row += f" {m[f'Hit@{k}']:<8.6f}"
        print(row)

    print("\n===== Overall Metrics =====")
    overall_row = f"{'Overall':<15} {overall_metrics['queries']:<8} {overall_metrics['MRR']:<8.6f}"
    for k in k_values:
        overall_row += f" {overall_metrics[f'Hit@{k}']:<8.6f}"
    print(overall_row)

    return {"per_type": per_type_metrics, "overall": overall_metrics}


def so400m_long_ctx309_eval_mrr(
    model_name="/home/public/dkx/model/fancyfeast/so400m-long-ctx309",
    query_glob="/home/dkx/RAG4Ghart/Dataset-ZXQ/test20/*/txt/*.txt",
    collection_name="so400m_long_ctx309",
    k=5,
    anns_field="image_dense"
):
    """Require transformers >= 4.51.0"""
    from transformers import SiglipModel, SiglipProcessor
    model = SiglipModel.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto",
                                        attn_implementation="sdpa")
    processor = SiglipProcessor.from_pretrained(model_name)

    from PIL import Image
    # 2) 收集所有查询（文本 + 目标 chart_type）
    txt_paths = glob.glob(query_glob)
    # 把 txt 文件路径转换为对应的 png 文件路径
    png_paths = [txt_path.replace("/txt/", "/png/").replace(".txt", ".png") for txt_path in txt_paths]
    queries = []
    for txt_path, png_path in tqdm(zip(txt_paths, png_paths), desc="Loading queries"):
        # 目录结构：.../test20/<chart_type>/txt/<id>.txt
        parts = os.path.normpath(txt_path).split(os.sep)
        # 取倒数第三个作为 chart_type（.../<chart_type>/txt/file.txt）
        # e.g., [..., 'test20', '<chart_type>', 'txt', 'xxx.txt']
        chart_type = parts[-3]
        with open(txt_path, "r", encoding="gbk") as f:
            text = f.read().strip()
        if not text:
            continue
        image = Image.open(png_path).convert("RGB")
        queries.append((text, chart_type, image))

    if not queries:
        raise RuntimeError("没有在指定路径找到任何查询文本。检查 query_glob 是否正确。")

    # 3) 准备向量库
    client.load_collection(collection_name)

    reciprocal_ranks = []
    hit1 = 0
    hitk = 0

    # 4) 逐条生成向量并检索
    for text, target_type, image in tqdm(queries, desc="Evaluating MRR"):
        with torch.no_grad():
            query_inputs = processor(text=[text], images=image, padding="max_length", max_length=309, return_tensors="pt"
                             ).to("cuda")
            outputs = model(**query_inputs)
        query_embs = outputs.text_embeds
        results = client.search(
            collection_name=collection_name,
            anns_field=anns_field,
            data=query_embs.detach().cpu().tolist(),
            limit=k,
            search_params={"metric_type": "IP"},
            output_fields=["type", "image_url"],  # specifies fields to be returned
        )

        hits = results[0]

        # c) 寻找第一个相关命中的排名
        rank = None
        for idx, hit in enumerate(hits, start=1):
            # 命中判定规则：type 相同
            # SDK 可能返回 dict 或对象；这里做两手准备
            if hit.get("type") == target_type:
                rank = idx
                break

        # d) 统计
        if rank is None:
            reciprocal_ranks.append(0.0)
        else:
            reciprocal_ranks.append(1.0 / rank)
            if rank == 1:
                hit1 += 1
            if rank <= k:
                hitk += 1

    # 5) 汇总指标
    Q = len(reciprocal_ranks)
    mrr = sum(reciprocal_ranks) / Q
    hit1_rate = hit1 / Q
    hitk_rate = hitk / Q

    print(f"Queries: {Q}")
    print(f"MRR@{k}: {mrr:.6f}")
    print(f"Hit@1:   {hit1_rate:.6f}")
    print(f"Hit@{k}:  {hitk_rate:.6f}")

    return {
        "queries": Q,
        "mrr": mrr,
        "hit1": hit1_rate,
        f"hit@{k}": hitk_rate,
    }


def Qwen3_Embedding_8B_eval_mrr(
        model_name="/home/public/dkx/model/Qwen/Qwen3-Embedding-8B",
        query_glob="/home/dkx/RAG4Ghart/Dataset-ZXQ/test20/*/txt/*.txt",
        collection_name="Qwen3_Embedding_8B",
        k=5,
        anns_field="text_dense"
):
    from modelscope import AutoTokenizer
    from transformers import Qwen3Model

    # 1) 准备模型（只 set_processor 一次，eval + cuda）
    def last_token_pool(last_hidden_states: torch.Tensor,
                        attention_mask: torch.Tensor) -> torch.Tensor:
        left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
        if left_padding:
            return last_hidden_states[:, -1]
        else:
            sequence_lengths = attention_mask.sum(dim=1) - 1
            batch_size = last_hidden_states.shape[0]
            return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]


    def get_detailed_instruct(task_description: str, query: str) -> str:
        return f'Instruct: {task_description}\nQuery:{query}'


    # Each query must come with a one-sentence instruction that describes the task
    task = 'Given a piece of text, recommend the most suitable type of chart to visualize it.'

    tokenizer = AutoTokenizer.from_pretrained('/home/public/dkx/model/Qwen/Qwen3-Embedding-8B', padding_side='left')
    model = Qwen3Model.from_pretrained('/home/public/dkx/model/Qwen/Qwen3-Embedding-8B')

    # 2) 收集所有查询（文本 + 目标 chart_type）
    txt_paths = glob.glob(query_glob)
    queries = []
    for txt_path in txt_paths:
        # 目录结构：.../test20/<chart_type>/txt/<id>.txt
        parts = os.path.normpath(txt_path).split(os.sep)
        # 取倒数第三个作为 chart_type（.../<chart_type>/txt/file.txt）
        # e.g., [..., 'test20', '<chart_type>', 'txt', 'xxx.txt']
        chart_type = parts[-3]
        with open(txt_path, "r", encoding="gbk") as f:
            text = f.read().strip()
        if not text:
            continue
        queries.append((text, chart_type, txt_path))

    if not queries:
        raise RuntimeError("没有在指定路径找到任何查询文本。检查 query_glob 是否正确。")

    # 3) 准备向量库
    client.load_collection(collection_name)

    reciprocal_ranks = []
    hit1 = 0
    hitk = 0

    import torch.nn.functional as F
    # 4) 逐条生成向量并检索
    with torch.no_grad():
        for text, target_type, path in tqdm(queries, desc="Evaluating MRR"):
            # a) 处理输入 -> embedding
            batch_dict = tokenizer(
                [get_detailed_instruct(task, text)],
                padding=True,
                truncation=True,
                max_length=8192,
                return_tensors="pt",
            )
            batch_dict.to(model.device)
            outputs = model(**batch_dict)
            embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
            # normalize embeddings
            emb = F.normalize(embeddings, p=2, dim=1)
            emb_list = emb.detach().cpu().tolist()

            # b) 检索（相似度内积）
            results = client.search(
                collection_name=collection_name,
                anns_field=anns_field,
                data=emb_list,
                limit=k,
                search_params={"metric_type": "IP"},
                output_fields=["type", "image_url"],
            )

            hits = results[0]

            # c) 寻找第一个相关命中的排名
            rank = None
            for idx, hit in enumerate(hits, start=1):
                # 命中判定规则：type 相同
                # SDK 可能返回 dict 或对象；这里做两手准备
                if hit.get("type") == target_type:
                    rank = idx
                    break

            # d) 统计
            if rank is None:
                reciprocal_ranks.append(0.0)
            else:
                reciprocal_ranks.append(1.0 / rank)
                if rank == 1:
                    hit1 += 1
                if rank <= k:
                    hitk += 1

    # 5) 汇总指标
    Q = len(reciprocal_ranks)
    mrr = sum(reciprocal_ranks) / Q
    hit1_rate = hit1 / Q
    hitk_rate = hitk / Q

    print(f"Queries: {Q}")
    print(f"MRR@{k}: {mrr:.6f}")
    print(f"Hit@1:   {hit1_rate:.6f}")
    print(f"Hit@{k}:  {hitk_rate:.6f}")

    return {
        "queries": Q,
        "mrr": mrr,
        "hit1": hit1_rate,
        f"hit@{k}": hitk_rate,
    }

# ===== 运行 =====
if __name__ == "__main__":
    # 只测试指定的9种图表类型
    target_types = ["bar", "box", "bubble", "funnel", "line", "pie", "radar","scatter",
                    "stacked_bar", "treemap"]

    results = BGE_VL_v1_5_zs_eval_mrr(
        k_values=[1, 5],
        target_chart_types=target_types,
        samples_per_type=200
    )

"""
Type            Queries  MRR      Hit@1    Hit@3    Hit@5    Hit@10  
---------------------------------------------------------------------
bar             2999     1.000000 1.000000 1.000000 1.000000 1.000000
bubble          1997     0.996161 0.992489 1.000000 1.000000 1.000000
chord           1950     0.995954 0.995897 0.995897 0.995897 0.996410
funnel          2999     1.000000 1.000000 1.000000 1.000000 1.000000
line            1999     1.000000 1.000000 1.000000 1.000000 1.000000
nodelink        2000     1.000000 1.000000 1.000000 1.000000 1.000000
pie             2000     1.000000 1.000000 1.000000 1.000000 1.000000
scatter         2000     0.998833 0.998000 1.000000 1.000000 1.000000
treemap         3000     1.000000 1.000000 1.000000 1.000000 1.000000

===== Overall Metrics =====
Overall         20944    0.999146 0.998711 0.999618 0.999618 0.999666


===== Per-Type Metrics =====
Type            Queries  MRR      Hit@1    Hit@3    Hit@5    Hit@10  
---------------------------------------------------------------------
bar             2999     1.000000 1.000000 1.000000 1.000000 1.000000
box             18       0.000000 0.000000 0.000000 0.000000 0.000000
bubble          1997     0.996161 0.992489 1.000000 1.000000 1.000000
funnel          2999     1.000000 1.000000 1.000000 1.000000 1.000000
line            1999     1.000000 1.000000 1.000000 1.000000 1.000000
pie             2000     1.000000 1.000000 1.000000 1.000000 1.000000
radar           23       0.000000 0.000000 0.000000 0.000000 0.000000
scatter         2000     0.998833 0.998000 1.000000 1.000000 1.000000
stacked_area    18       0.000000 0.000000 0.000000 0.000000 0.000000
stacked_bar     18       0.000000 0.000000 0.000000 0.000000 0.000000
treemap         3000     1.000000 1.000000 1.000000 1.000000 1.000000

===== Overall Metrics =====
Overall         17071    0.994904 0.994376 0.995489 0.995489 0.995489
"""