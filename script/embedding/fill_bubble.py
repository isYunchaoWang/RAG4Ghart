import glob, os, torch
import pandas as pd
from tqdm import tqdm
from transformers import LlavaNextForConditionalGeneration

def get_data(base_url: str, model: LlavaNextForConditionalGeneration) -> list[dict]:
    data = []
    chart_type = "fill_bubble"
    csv_paths = glob.glob(f"{base_url}/Dataset-ZXQ/sample100/{chart_type}/csv/*.csv")

    for csv_path in tqdm(csv_paths, desc=f"Processing {chart_type}", unit="file"):
        datum_id = int(os.path.splitext(os.path.basename(csv_path))[0])
        theme, title, data_num = pd.read_csv(csv_path, nrows=1, encoding="gbk").columns
        with open(f"{base_url}/Dataset-ZXQ/sample100/{chart_type}/txt/{datum_id}.txt", "r", encoding="gbk") as f:
            text = f.read()
        df = pd.read_csv(csv_path, skiprows=1, encoding="gbk")
        datum = {
            "image_url": f"{base_url}/Dataset-ZXQ/sample100/{chart_type}/png/{datum_id}.png",
            "type": chart_type,
            "theme": theme,
            "title": title,
            "text": text,
            "metadata": {
                "data_num": data_num
            },
            "data": df.to_json(orient="records")
        }

        with torch.no_grad():
            text_inputs = model.data_process(
                text=text,
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

    return data
