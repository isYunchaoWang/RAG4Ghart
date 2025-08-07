from tqdm import tqdm


def load_data(base_url: str = "/home/dukaixing/RAG4Ghart") -> list:
    import glob, os
    import pandas as pd

    data = []
    chart_types = ("bar", "box", "bubble", "chord", "fill_bubble", "funnel", "heatmap", "line", "node_link", "parallel",
                   "pie", "radar", "ridgeline", "sankey", "scatter", "stacked_area", "stacked_bar", "stream",
                   "sunburst",
                   "treemap", "treemap_D3", "violin")
    for chart_type in chart_types:
        csv_paths = glob.glob(f"{base_url}/Dataset-ZXQ/sample100/{chart_type}/csv/*.csv")
        for csv_path in tqdm(csv_paths, desc=f"Processing {chart_type}", unit="file"):
            datum_id = int(os.path.splitext(os.path.basename(csv_path))[0])
            with open(f"{base_url}/Dataset-ZXQ/sample100/{chart_type}/txt/{datum_id}.txt", "r", encoding="gbk") as f:
                text = f.read()
            datum = {
                "image_url": f"{base_url}/Dataset-ZXQ/sample100/{chart_type}/png/{datum_id}.png",
                "type": chart_type,
                "theme": str(),
                "title": str(),
                "text": text,
                "metadata": dict(),
                "data": str(),
                "text_dense": list(),
                "image_dense": list()
            }
            df = pd.DataFrame()
            if chart_type == "bar" or chart_type == "box":
                theme, title, unit, distribution, display = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "distribution": distribution,
                    "display": display,
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type == "bubble":
                theme, title, distribution = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "distribution": distribution,
                    "header": df.columns.values.tolist(),
                }
            elif chart_type in {"chord", "funnel", "violin"}:
                theme, title, unit, distribution = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "distribution": distribution,
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type == "fill_bubble":
                theme, title, data_num = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {"data_num": data_num}
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
                trend = lines[1].strip().split(',')[1:]  # 按逗号分割
                df = pd.read_csv(csv_path, skiprows=2, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "trend": trend,
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type == "node_link":
                theme, title = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {"header": df.columns.values.tolist()}
            elif chart_type == "parallel":
                theme, title = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                # 读取csv（需要跳过第一行，然后手动读取第二行作为list）
                with open(csv_path, 'r', encoding="utf-8") as f:
                    lines = f.readlines()
                # 第二行是Pattern,Clustering,Weak Correlation,Weak Correlation,Clustering
                pattern = lines[1].strip().split(',')[1:]  # 按逗号分割
                df = pd.read_csv(csv_path, skiprows=2, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "pattern": pattern,
                    "header": df.columns.values.tolist()
                }
            elif chart_type in {"pie", "sunburst", "treemap", "treemap_D3"}:
                if chart_type == "treemap_D3": datum["type"] = "treemap"
                theme, title, unit = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type == "radar":
                theme, unit = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["metadata"] = {
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type == "sankey":
                theme, title, unit, distribution, *labels = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "distribution": distribution,
                    "labels": labels,
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            elif chart_type == "scatter":
                theme, title, *display = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "display": display,
                    "header": df.columns.values.tolist()
                }
            elif chart_type == "stacked_bar":
                theme, title, unit, display = pd.read_csv(csv_path, nrows=1, encoding="utf-8").columns
                df = pd.read_csv(csv_path, skiprows=1, encoding="utf-8")
                datum["theme"] = theme
                datum["title"] = title
                datum["metadata"] = {
                    "display": display,
                    "header": df.columns.values.tolist(),
                    "unit": unit
                }
            datum["data"] = df.to_json(orient="records")
            data.append(datum)

        # with torch.no_grad():
        #     text_inputs = model.data_process(
        #         text=text,
        #         q_or_c="c"
        #     )
        #     text_embs = model(**text_inputs, output_hidden_states=True)[:, -1, :]
        #     img_inputs = model.data_process(
        #          images=[datum["image_url"]],
        #         q_or_c="c"
        #     )
        #     img_embs = model(**img_inputs, output_hidden_states=True)[:, -1, :]
        #
        #     text_embs = torch.nn.functional.normalize(text_embs, dim=-1)
        #     img_embs = torch.nn.functional.normalize(img_embs, dim=-1)
        #
        # datum["text_dense"] = text_embs.cpu().detach().numpy().tolist()[0]
        # datum["image_dense"] = img_embs.cpu().detach().numpy().tolist()[0]
    return data


from modelscope import AutoModel
import torch


def embed_data_BGE_VL_v1_5_zs(data: list) -> list:
    """Requires transformers<4.47.0"""
    MODEL_NAME = "/home/public/dkx/model/BAAI/BGE-VL-v1.5-zs"
    model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model.eval()
    model.cuda()
    model.set_processor(MODEL_NAME)

    for i in range(len(data)):
        with torch.no_grad():
            text_inputs = model.data_process(
                text=data[i]["text"],
                q_or_c="c"
            )
            text_embs = model(**text_inputs, output_hidden_states=True)[:, -1, :]
            img_inputs = model.data_process(
                images=[data[i]["image_url"]],
                q_or_c="c"
            )
            img_embs = model(**img_inputs, output_hidden_states=True)[:, -1, :]

            text_embs = torch.nn.functional.normalize(text_embs, dim=-1)
            img_embs = torch.nn.functional.normalize(img_embs, dim=-1)

        data[i]["text_dense"] = text_embs.detach().cpu().tolist()
        data[i]["image_dense"] = img_embs.detach().cpu().tolist()
    return data


def embed_data_so400m_long(data: list) -> list:
    """Requires transformers>=4.51.0"""
    from PIL import Image
    from modelscope import AutoProcessor
    model = AutoModel.from_pretrained("/home/public/dkx/model/fancyfeast/so400m-long", torch_dtype=torch.float32, device_map="auto", attn_implementation="sdpa")

    processor = AutoProcessor.from_pretrained("/home/public/dkx/model/fancyfeast/so400m-long")

    texts = [datum["text"] for datum in data]
    print("loading images...")
    images = [Image.open(datum["image_url"]).convert("RGB") for datum in data]
    print("processing...")
    inputs = processor(text=texts, images=images, padding="max_length", max_length=256, return_tensors="pt").to("cuda")

    print("embedding...")
    with torch.no_grad():
        outputs = model(**inputs)

    for i in range(len(data)):
        data[i]["text_dense"] = outputs.text_embeds[i].detach().cpu().tolist()
        data[i]["image_dense"] = outputs.image_embeds[i].detach().cpu().tolist()

    return data


from pymilvus import MilvusClient, DataType, CollectionSchema

client = MilvusClient(uri="http://localhost:19530")


def insert_data_BGE_VL_v1_5_zs(schema: CollectionSchema, data: list):
    schema.add_field(
        field_name="text_dense",
        datatype=DataType.FLOAT_VECTOR,
        dim=4096
    )

    schema.add_field(
        field_name="image_dense",
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

    index_params.add_index(
        field_name="image_dense",
        index_name="image_dense_index",
        index_type="AUTOINDEX",
        metric_type="IP"
    )

    if client.has_collection(collection_name="BGE_VL_v1_5_zs"):
        client.drop_collection(collection_name="BGE_VL_v1_5_zs")
    client.create_collection(
        collection_name="BGE_VL_v1_5_zs",
        schema=schema,
        index_params=index_params
    )

    batch_size = 500
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        client.insert(collection_name="BGE_VL_v1_5_zs", data=batch)


def insert_data_so400m_long(schema: CollectionSchema, data: list):
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

    if client.has_collection(collection_name="so400m_long"):
        client.drop_collection(collection_name="so400m_long")
    client.create_collection(
        collection_name="so400m_long",
        schema=schema,
        index_params=index_params
    )

    batch_size = 500
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        client.insert(collection_name="so400m_long", data=batch)


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

    data = load_data()

    # data = embed_data_BGE_VL_v1_5_zs(data)
    data = embed_data_so400m_long(data)
    insert_data_so400m_long(schema, data)