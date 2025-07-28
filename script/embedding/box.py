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
chart_type = "box"

csv_paths = glob.glob(f"../Dataset-ZXQ/sample100/{chart_type}/csv/*.csv")
for csv_path in tqdm(csv_paths, desc=f"Processing {chart_type}", unit="file"):
    datum_id = int(os.path.splitext(os.path.basename(csv_path))[0])
    theme, title, unit, distribution, display = pd.read_csv(csv_path, nrows=1).columns
    df = pd.read_csv(csv_path, skiprows=1)
    datum = {
        "id": datum_id,
        "image_url": glob.glob(f"../Dataset-ZXQ/sample100/{chart_type}/png/{datum_id}.png")[0],
        "type": chart_type,
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
    input_datum = deepcopy(datum)
    input_datum.pop("id")
    input_datum.pop("image_url")

    with torch.no_grad():
        model.set_processor(MODEL_NAME)
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
    datum["image_dense"] = img_embs.cpu().detach().numpy().tolist()[0]
    data.append(datum)


from pymilvus import MilvusClient

client = MilvusClient(uri="http://localhost:19530")
client.insert(collection_name="test", data=data)
