
from pymilvus import MilvusClient, DataType

client = MilvusClient(uri="http://localhost:19530")

def create_db():
    schema = client.create_schema(auto_id=False)

    schema.add_field(
        field_name="id",
        datatype=DataType.INT64,
        is_primary=True,
        auto_id=False,
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
        field_name="data",
        datatype=DataType.VARCHAR,
        max_length=4096,
    )

    schema.add_field(
        field_name="metadata",
        datatype=DataType.JSON,
        nullable=False
    )

    schema.add_field(
        field_name="text_dense",
        datatype=DataType.FLOAT_VECTOR,
        dim=4096
    )

    schema.add_field(
        field_name="img_dense",
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
        field_name="img_dense",
        index_name="img_dense_index",
        index_type="AUTOINDEX",
        metric_type="IP"
    )

    if client.has_collection(collection_name="test"):
        client.drop_collection(collection_name="test")
    client.create_collection(
        collection_name="test",
        dimension=4096,  # The vectors we will use in this demo has 768 dimensions
        schema=schema,
        index_params=index_params
    )


from modelscope import AutoModel

MODEL_NAME = "/home/public/dkx/model/BAAI/BGE-VL-v1.5-zs"

model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True)
model.eval()
model.cuda()

import glob, os, torch
import pandas as pd
from tqdm import tqdm
from copy import deepcopy

data = []

def embed_bar():
    csv_paths = glob.glob("../Dataset-ZXQ/sample100/bar/csv/*.csv")
    for csv_path in tqdm(csv_paths, desc="Processing bar", unit="file"):
        datum_id = int(os.path.splitext(os.path.basename(csv_path))[0])
        theme, title, unit, distribution, display = pd.read_csv(csv_path, nrows=1).columns
        df = pd.read_csv(csv_path, skiprows=1)
        datum = {
            "id": datum_id,
            "image_url": glob.glob(f"../Dataset-ZXQ/sample100/bar/png/{datum_id}.png")[0],
            # /home/dukaixing/RAG4Ghart/Dataset-ZXQ/sample100/bar/png/21.png
            "type": "bar",
            "theme": theme,
            "title": title,
            "metadata": {
                "distribution": distribution,
                "display": display,
                "header": df.columns.values.tolist(),
                "unit": unit
            },
            "data": df.to_json(orient="records")
        }
        with torch.no_grad():
            model.set_processor(MODEL_NAME)
            input_datum = deepcopy(datum)
            input_datum.pop("id")
            input_datum.pop("image_url")
            text_inputs = model.data_process(
                text=str(input_datum),
                q_or_c="c"
            )
            text_embs = model(**text_inputs, output_hidden_states=True)[:, -1, :]
            img_inputs = model.data_process(
                images=[datum["image_url"]],
                q_or_c="c"
            )
            img_embs = model(**img_inputs, output_hidden_states=True)[:, -1, :]
        datum["text_dense"] = text_embs.cpu().detach().numpy().tolist()[0]
        datum["img_dense"] = img_embs.cpu().detach().numpy().tolist()[0]
        data.append(datum)

def main():
    # csv_path = "../Dataset-ZXQ/sample100/bar/csv/21.csv"
    client.insert(collection_name="test", data=data)

if __name__ == "__main__":
    create_db()
    embed_bar()
    main()