from tqdm import tqdm


def load_data(base_url: str = "/home/public/dataset-MegaCQA") -> list[dict]:
    import glob, os
    import pandas as pd

    data = []
    chart_types = ("bar", "box", "bubble", "funnel", "line", "pie", "radar","scatter", "stacked_area",
                    "stacked_bar", "treemap")
    for chart_type in chart_types:
        csv_paths = glob.glob(f"{base_url}/train/{chart_type}/csv/*.csv")
        for csv_path in tqdm(csv_paths, desc=f"Processing {chart_type}", unit="file"):
            datum_id = int(os.path.splitext(os.path.basename(csv_path))[0])

            with open(f"{base_url}/train/{chart_type}/txt/{datum_id}.txt", "r", encoding="gbk") as f:
                text = f.read()

            datum = {
                "image_url": f"{base_url}/train/{chart_type}/png/{datum_id}.png",
                "type": chart_type,
                "theme": str(),
                "title": str(),
                "text": text,
                "metadata": dict(),
                "data": str(),
                "text_dense": list()
            }
            df = pd.DataFrame()
            if chart_type in {"bar", "box", "stacked_bar"}:
                theme, title, unit, display = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "display": display,
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type == "bubble":
                theme, title = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "header": df.columns.values.tolist(),
                }
            elif chart_type in {"chord", "pie", "sunburst", "treemap", "violin"}:
                theme, title, unit = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type == "fill_bubble":
                theme, title, data_num = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {"data_num": data_num}
            elif chart_type == "funnel":
                theme, title, unit, distribution = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "distribution": distribution,
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type == "heatmap":
                theme, title, matrix_dim, distribution = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, names=["X", "Y", "Value"], encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "x_labels": df['X'].drop_duplicates().tolist(),  # 获取 X 轴标签（唯一的第一列值，顺序保留）
                    "y_labels": df['Y'].drop_duplicates().tolist(),  # 获取 Y 轴标签（唯一的第二列值，顺序保留）
                    "distribution": distribution
                }
            elif chart_type in {"line", "ridgeline", "stacked_area", "stream"}:
                theme, title, unit = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                # 读取csv（需要跳过第一行，然后手动读取第二行作为list）
                with open(csv_path, 'r', encoding='gbk') as f:
                    lines = f.readlines()
                # 第二行是trend,stable_rising,volatile_falling,...
                trend = lines[1].strip().split(',')[0:] if chart_type == "ridgeline" else lines[1].strip().split(',')[1:] # 按逗号分割
                df = pd.read_csv(csv_path, skiprows=2, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "trend": trend,
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type in {"nodelink", "parallel"}:
                theme, title = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {"header": df.columns.values.tolist()}
            elif chart_type == "radar":
                theme, unit = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["metadata"] = {
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type == "sankey":
                theme, title, unit, *labels = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "labels": labels,
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type == "scatter":
                theme, title, display = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "display": display,
                    "header": df.columns.values.tolist()
                }
            datum["data"] = df.to_json(orient="records")
            data.append(datum)
    return data

def load_ChartGen(base_url: str = "/home/public/ChartGen-200K/converted") -> list[dict]:
    import glob, os

    data = []
    # chart_types = ("bubble", "line", "pie", "radar", "stacked_area", "treemap")
    chart_types = ("bar", "box", "funnel", "scatter", "stacked_bar")
    for chart_type in chart_types:
        csv_paths = glob.glob(f"{base_url}/train/{chart_type}/csv/*.csv")
        for csv_path in tqdm(csv_paths, desc=f"Processing {chart_type}", unit="file"):
            datum_id = os.path.splitext(os.path.basename(csv_path))[0]

            with open(f"{base_url}/train/{chart_type}/txt/{datum_id}.txt", "r", encoding="utf-8") as f:
                text = f.read()

            datum = {
                "image_url": f"{base_url}/train/{chart_type}/png/{datum_id}.png",
                "type": chart_type,
                "theme": str(),
                "title": str(),
                "text": text,
                "metadata": dict(),
                "data": str(),
                "text_dense": list()
            }
            # try:
            #     df = pd.read_csv(csv_path, encoding="utf-8")
            # except pd.errors.ParserError:
            #     print(csv_path)
            # datum["metadata"] = {
            #     "header": df.columns.values.tolist()
            # }
            # datum["data"] = df.to_json(orient="records")
            data.append(datum)
    return data

from modelscope import AutoModel
import torch


def embed_data_BGE_VL_v1_5_zs(data: list[dict]) -> list[dict]:
    """Requires transformers<4.47.0"""
    MODEL_NAME = "/home/public/dkx/model/BAAI/BGE-VL-v1.5-zs"
    model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model.eval()
    model.cuda()
    model.set_processor(MODEL_NAME)

    for datum in tqdm(data, desc="embedding"):
        with torch.no_grad():
            text_inputs = model.data_process(
                text=datum["text"],
                q_or_c="c"
            )
            text_embs = model(**text_inputs, output_hidden_states=True)[:, -1, :]
            # img_inputs = model.data_process(
            #     images=[datum["image_url"]],
            #     q_or_c="c"
            # )
            # img_embs = model(**img_inputs, output_hidden_states=True)[:, -1, :]
            hybrid_inputs = model.data_process(
                text=datum["text"],
                images=datum["image_url"],
                q_or_c="c"
            )
            hybrid_embs = model(**hybrid_inputs, output_hidden_states=True)[:, -1, :]

            text_embs = torch.nn.functional.normalize(text_embs, dim=-1)
            # img_embs = torch.nn.functional.normalize(img_embs, dim=-1)
            hybrid_embs = torch.nn.functional.normalize(hybrid_embs, dim=-1)

        datum["text_dense"] = text_embs.detach().cpu().tolist()[0]
        # datum["image_dense"] = img_embs.detach().cpu().tolist()[0]
        datum["hybrid_dense"] = hybrid_embs.detach().cpu().tolist()[0]
    return data


def embed_data_so400m_long_ctx309(data: list[dict], batch_size: int = 4096) -> list[dict]:
    """批量嵌入，避免一次性塞满显存。Requires transformers>=4.51.0"""
    from PIL import Image
    from transformers import SiglipProcessor, SiglipModel
    from tqdm import tqdm

    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = SiglipModel.from_pretrained(
        "/home/public/dkx/model/fancyfeast/so400m-long-ctx309",
        torch_dtype=torch.float16,  # 嵌入时也可以用 fp16 减显存
        device_map="auto",
        attn_implementation="sdpa"
    )
    model.eval()

    processor = SiglipProcessor.from_pretrained("/home/public/dkx/model/fancyfeast/so400m-long-ctx309")

    # 遍历批次
    for start in tqdm(range(0, len(data), batch_size), desc="embedding batches"):
        end = min(start + batch_size, len(data))
        batch = data[start:end]

        texts = [item["text"] for item in batch]
        images = [Image.open(item["image_url"]).convert("RGB") for item in batch]

        with torch.no_grad():
            inputs = processor(
                text=texts,
                images=images,
                padding="max_length",
                max_length=309,
                return_tensors="pt"
            ).to(device)

            outputs = model(**inputs)

            # 写回到原 data 里的对应项
            for idx, item in enumerate(batch):
                item["text_dense"] = outputs.text_embeds[idx].detach().cpu().tolist()
                item["image_dense"] = outputs.image_embeds[idx].detach().cpu().tolist()

    return data


def embed_data_Qwen3_Embedding_8B(data: list[dict]) -> list[dict]:
    def last_token_pool(last_hidden_states: torch.Tensor,
                        attention_mask: torch.Tensor) -> torch.Tensor:
        left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
        if left_padding:
            return last_hidden_states[:, -1]
        else:
            sequence_lengths = attention_mask.sum(dim=1) - 1
            batch_size = last_hidden_states.shape[0]
            return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]

    from modelscope import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained('/home/public/dkx/model/Qwen/Qwen3-Embedding-8B', padding_side='left')
    from transformers import Qwen3Model
    model = Qwen3Model.from_pretrained('/home/public/dkx/model/Qwen/Qwen3-Embedding-8B')
    model.eval()
    model.cuda()

    import torch.nn.functional as F
    with torch.no_grad():
        for datum in tqdm(data, desc="embedding"):
            batch_dict = tokenizer(
                [datum.get("text")],
                padding=True,
                truncation=True,
                max_length=8192,
                return_tensors="pt",
            )
            batch_dict.to(model.device)
            outputs = model(**batch_dict)
            embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])

            embeddings = F.normalize(embeddings, p=2, dim=1)

            datum["text_dense"] = embeddings.detach().cpu().tolist()[0]

    return data


from pymilvus import MilvusClient, DataType, CollectionSchema

client = MilvusClient(uri="http://localhost:19530")


def insert_data_BGE_VL_v1_5_zs(schema: CollectionSchema, data: list[dict], collection_name: str = "ChartGen"):
    # schema.add_field(
    #     field_name="text_dense",
    #     datatype=DataType.FLOAT_VECTOR,
    #     dim=4096
    # )
    #
    # schema.add_field(
    #     field_name="hybrid_dense",
    #     datatype=DataType.FLOAT_VECTOR,
    #     dim=4096
    # )
    #
    # index_params = client.prepare_index_params()
    #
    # # 3.4. Add indexes
    # index_params.add_index(
    #     field_name="text_dense",
    #     index_name="text_dense_index",
    #     index_type="AUTOINDEX",
    #     metric_type="IP"
    # )
    #
    #
    # index_params.add_index(
    #     field_name="hybrid_dense",
    #     index_name="hybrid_dense_index",
    #     index_type="AUTOINDEX",
    #     metric_type="IP"
    # )
    #
    # if client.has_collection(collection_name=collection_name):
    #     client.drop_collection(collection_name=collection_name)
    # client.create_collection(
    #     collection_name=collection_name,
    #     schema=schema,
    #     index_params=index_params
    # )

    batch_size = 500
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        client.insert(collection_name=collection_name, data=batch)


def insert_data_so400m_long_ctx309(schema: CollectionSchema, data: list[dict]):
    print("inserting...")
    schema.add_field(
        field_name="text_dense",
        datatype=DataType.FLOAT_VECTOR,
        dim=1152
    )

    schema.add_field(
        field_name="image_dense",
        datatype=DataType.FLOAT_VECTOR,
        dim=1152
    )

    index_params = client.prepare_index_params()

    # 3.4. Add indexes
    index_params.add_index(
        field_name="text_dense",
        index_name="text_dense_index",
        index_type="AUTOINDEX",
        metric_type="IP"
    )

    index_params.add_index(
        field_name="image_dense",
        index_name="image_dense_index",
        index_type="AUTOINDEX",
        metric_type="IP"
    )

    if client.has_collection(collection_name="so400m_long_ctx309"):
        client.drop_collection(collection_name="so400m_long_ctx309")
    client.create_collection(
        collection_name="so400m_long_ctx309",
        schema=schema,
        index_params=index_params
    )

    batch_size = 500
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        client.insert(collection_name="so400m_long_ctx309", data=batch)


def insert_data_Qwen3_Embedding_8B(schema: CollectionSchema, data: list[dict]):
    schema.add_field(
        field_name="text_dense",
        datatype=DataType.FLOAT_VECTOR,
        dim=4096
    )

    index_params = client.prepare_index_params()

    # 3.4. Add indexes
    index_params.add_index(
        field_name="text_dense",
        index_name="text_dense_index",
        index_type="AUTOINDEX",
        metric_type="IP"
    )

    if client.has_collection(collection_name="Qwen3_Embedding_8B"):
        client.drop_collection(collection_name="Qwen3_Embedding_8B")
    client.create_collection(
        collection_name="Qwen3_Embedding_8B",
        schema=schema,
        index_params=index_params
    )

    batch_size = 500
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        client.insert(collection_name="Qwen3_Embedding_8B", data=batch)


if __name__ == "__main__":
    schema = client.create_schema(auto_id=True)
    schema.add_field(
        field_name="id",
        datatype=DataType.INT64,
        is_primary=True,
        auto_id=True,
    )

    schema.add_field(
        field_name="image_url",
        datatype=DataType.VARCHAR,
        max_length=128
    )

    schema.add_field(
        field_name="type",
        datatype=DataType.VARCHAR,
        max_length=32
    )

    schema.add_field(
        field_name="theme",
        datatype=DataType.VARCHAR,
        max_length=128
    )

    schema.add_field(
        field_name="title",
        datatype=DataType.VARCHAR,
        max_length=128
    )

    schema.add_field(
        field_name="text",
        datatype=DataType.VARCHAR,
        max_length=4096
    )

    schema.add_field(
        field_name="metadata",
        datatype=DataType.JSON,
        nullable=False
    )

    schema.add_field(
        field_name="data",
        datatype=DataType.VARCHAR,
        max_length=32768,
    )

    # data = load_data()
    data = load_ChartGen()

    data = embed_data_BGE_VL_v1_5_zs(data)
    insert_data_BGE_VL_v1_5_zs(schema, data)

    # data = embed_data_so400m_long_ctx309(data)
    # insert_data_so400m_long_ctx309(schema, data)

    # data = embed_data_Qwen3_Embedding_8B(data)
    # insert_data_Qwen3_Embedding_8B(schema, data)
