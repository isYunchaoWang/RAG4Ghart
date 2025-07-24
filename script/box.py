import glob, os, torch
import pandas as pd
from modelscope import AutoModel
from pymilvus import MilvusClient, DataType
from tqdm import tqdm

MODEL_NAME = "/home/public/dkx/model/BAAI/BGE-VL-v1.5-zs"

model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True)
model.eval()
model.cuda()

client = MilvusClient(uri="http://localhost:19530")
schema = client.create_schema()
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
    field_name="distribution",
    datatype=DataType.VARCHAR,
    max_length=32
)

schema.add_field(
    field_name="display",
    datatype=DataType.VARCHAR,
    max_length=16
)

schema.add_field(
    field_name="header",
    datatype=DataType.ARRAY,
    element_type=DataType.VARCHAR,
    max_capacity=5,
    max_length=128,
)

schema.add_field(
    field_name="unit",
    datatype=DataType.VARCHAR,
    max_length=64
)

schema.add_field(
    field_name="data",
    datatype=DataType.VARCHAR,
    max_length=4096,
)

schema.add_field(
    field_name="vector",
    datatype=DataType.FLOAT_VECTOR,
    dim=4096
)

if client.has_collection(collection_name="bar"):
    client.drop_collection(collection_name="bar")
client.create_collection(
    collection_name="bar",
    dimension=4096,  # The vectors we will use in this demo has 768 dimensions
    schema=schema
)

def main():
    data = []
    # csv_path = "../Dataset-ZXQ/sample100/bar/csv/21.csv"
    csv_paths = glob.glob("../Dataset-ZXQ/sample100/bar/csv/*.csv")

    for csv_path in tqdm(csv_paths, desc="Processing CSVs", unit="file"):
        datum_id = int(os.path.splitext(os.path.basename(csv_path))[0])
        theme, title, unit, distribution, display = pd.read_csv(csv_path, nrows=1).columns
        df = pd.read_csv(csv_path, skiprows=1)
        datum = {
            "id": datum_id,
            "image_url": glob.glob(f"../Dataset-ZXQ/sample100/bar/png/{datum_id}.png")[0], # /home/dukaixing/RAG4Ghart/Dataset-ZXQ/sample100/bar/png/21.png
            "type": "bar",
            "theme": theme,
            "title": title,
            "distribution": distribution,
            "display": display,
            "header": df.columns.values.tolist(),
            "unit": unit,
            "data": df.to_json(orient="records"),
            "vector": []
        }
        with torch.no_grad():
            model.set_processor(MODEL_NAME)
            candidate_inputs = model.data_process(
                text=str(datum),
                images=[datum["image_url"]],
                q_or_c="c",
            )
            candi_embs = model(**candidate_inputs, output_hidden_states=True)[:, -1, :]
        datum["vector"] = candi_embs.cpu().detach().numpy().tolist()[0]
        data.append(datum)

    client.insert(collection_name="bar", data=data)

if __name__ == "__main__":
    main()