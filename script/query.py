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
    query_glob="/home/dkx/RAG4Ghart/Dataset-ZXQ/test20/*/txt/*.txt",
    collection_name="BGE_VL_v1_5_zs",
    k=5,
    task_instruction="Recommend the most suitable chart with corresponding description for visualizing the information given by the provided text: ",
    anns_field="hybrid_dense"
):
    """
    批量评估 MRR：
    - 相关性判定：命中文档的 hit['type'] == 该 query 的 chart_type（由路径 test20/<chart_type>/txt/*.txt 推断）
    - MRR: 对每个查询取第一个相关命中的倒数排名，最后取平均
    - 同时输出 Hit@1 和 Hit@K（K=limit）
    依赖：
        - 已经有全局变量 `client` 且连接到向量库，能调用 .load_collection 和 .search
        - modelscope 已安装
    """

    # ---- 命中字段安全获取（兼容 dict / 对象 / entity）----
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
    # ---- 图表类型归一化：treemap_D3 -> treemap（大小写无关）----
    def normalize_chart_type(raw: str) -> str:
        s = raw.strip().lower().replace("-", "_")
        # treemap、treemap_d3、treemap__d3 等都统一到 treemap
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
    queries = []
    for txt_path in txt_paths:
        parts = os.path.normpath(txt_path).split(os.sep)
        raw_type = parts[-3]  # .../test20/<chart_type>/txt/xxx.txt
        chart_type = normalize_chart_type(raw_type)
        # 读文本（保持你原来的 gbk；如有文件异常可改为 errors="ignore" 或 utf-8）
        with open(txt_path, "r", encoding="gbk") as f:
            text = f.read().strip()
        if not text:
            continue
        queries.append((text, chart_type, txt_path))

    if not queries:
        raise RuntimeError("没有在指定路径找到任何查询文本。检查 query_glob 是否正确。")

    # 3) 向量库
    client.load_collection(collection_name)

    from collections import defaultdict
    # 4) 统计容器
    per_type_rrs = defaultdict(list)
    per_type_hit1 = defaultdict(int)
    per_type_hitk = defaultdict(int)
    per_type_total = defaultdict(int)

    overall_rrs, overall_hit1, overall_hitk = [], 0, 0

    # 5) 检索并累计
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
                limit=k,
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
                if rank == 1:
                    per_type_hit1[target_type] += 1
                    overall_hit1 += 1
                if rank <= k:
                    per_type_hitk[target_type] += 1
                    overall_hitk += 1

    # 6) 计算各类型与整体
    per_type_metrics = {}
    for t in sorted(per_type_total.keys()):
        Q_t = per_type_total[t]
        mrr_t = (sum(per_type_rrs[t]) / Q_t) if Q_t > 0 else 0.0
        hit1_rate_t = per_type_hit1[t] / Q_t if Q_t > 0 else 0.0
        hitk_rate_t = per_type_hitk[t] / Q_t if Q_t > 0 else 0.0
        per_type_metrics[t] = {
            "queries": Q_t,
            f"MRR@{k}": round(mrr_t, 6),
            "Hit@1": round(hit1_rate_t, 6),
            f"Hit@{k}": round(hitk_rate_t, 6),
        }

    Q_all = len(overall_rrs)
    overall_metrics = {
        "queries": Q_all,
        f"MRR@{k}": round(sum(overall_rrs) / Q_all, 6) if Q_all > 0 else 0.0,
        "Hit@1": round(overall_hit1 / Q_all, 6) if Q_all > 0 else 0.0,
        f"Hit@{k}": round(overall_hitk / Q_all, 6) if Q_all > 0 else 0.0,
    }

    # 7) 输出
    print("===== Per-Type Metrics =====")
    for t, m in per_type_metrics.items():
        print(f"[{t}] queries={m['queries']}  MRR@{k}={m[f'MRR@{k}']:.6f}  "
              f"Hit@1={m['Hit@1']:.6f}  Hit@{k}={m[f'Hit@{k}']:.6f}")
    print("===== Overall =====")
    print(f"queries={overall_metrics['queries']}  MRR@{k}={overall_metrics[f'MRR@{k}']:.6f}  "
          f"Hit@1={overall_metrics['Hit@1']:.6f}  Hit@{k}={overall_metrics[f'Hit@{k}']:.6f}")

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
    stats = BGE_VL_v1_5_zs_eval_mrr(k=5)
    # stats = so400m_long_ctx309_eval_mrr(k=5)
    # stats = Qwen3_Embedding_8B_eval_mrr(k=5)
    print(stats)