from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import os
from modelscope import AutoModel
import torch
from pymilvus import MilvusClient


# Model path and initialization
MODEL_PATH = "/home/public/dkx/model/BAAI/BGE-VL-v1.5-zs"
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True)
model.eval()
model.cuda()
model.set_processor(MODEL_PATH)

# Milvus client
milvus_client = MilvusClient(uri="http://localhost:19530")

# FastAPI initialization
app = FastAPI()

# Allow CORS from specific origins
origins = [
    "http://localhost:5173",  # Allow this origin
    "http://127.0.0.1:5173"  # Allow this origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Set allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all request headers
)

# 静态文件服务 - 用于提供图片文件
# 假设图片存储在 /home/public/dataset-MegaCQA/train/ 目录下
app.mount("/static", StaticFiles(directory="/home/public/dataset-MegaCQA/train"), name="static")

@app.post("/")
async def dense_retrieve(query: str = Body(..., embed=True)):
    # Process query with model
    q = model.data_process(
        text=query,
        q_or_c="q",
        task_instruction="Recommend the most suitable chart with corresponding description for visualizing the information given by the provided text: "
    )

    # Get embeddings from the model
    emb = model(**q, output_hidden_states=True)[:, -1, :]
    emb = torch.nn.functional.normalize(emb, dim=-1)
    emb_list = emb.detach().cpu().tolist()

    # Search in Milvus
    results = milvus_client.search(
        collection_name="BGE_VL_v1_5_zs",
        anns_field="hybrid_dense",
        data=emb_list,
        limit=5,
        search_params={"metric_type": "IP"},
        output_fields=["type", "image_url"],
    )

    # Process search results
    # hits = results[0]

    with open("/home/public/dataset-MegaCQA/train/bar/svg/2.svg", "r") as f:
        bar_svg = f.read()

    with open("/home/public/dataset-MegaCQA/train/bubble/svg/2.svg", "r") as f:
        bubble_svg = f.read()

    with open("/home/public/dataset-MegaCQA/train/chord/svg/3.svg", "r") as f:
        chord_svg = f.read()

    with open("/home/public/dataset-MegaCQA/train/funnel/svg/2.svg", "r") as f:
        funnel_svg = f.read()

    with open("/home/public/dataset-MegaCQA/train/pie/svg/2.svg", "r") as f:
        pie_svg = f.read()

    response_list = [
        {"chartType": "bar", "score": 0.9, "svg": bar_svg},
        {"chartType": "bubble", "score": 0.8, "svg": bubble_svg},
        {"chartType": "chord", "score": 0.7, "svg": chord_svg},
        {"chartType": "funnel", "score": 0.6, "svg": funnel_svg},
        {"chartType": "pie", "score": 0.5, "svg": pie_svg},
    ]

    # for hit in hits:
    #     svg_url = hit["image_url"].replace("/png/", "/svg/").replace(".png", ".svg")
    #     with open(svg_url, "r") as f:
    #         svg = f.read()
    #     response_list.append(
    #         {"chartType": hit["type"], "score": hit["distance"], "svg": svg}
    #     )

    # return list(reversed(response_list))
    return response_list

@app.get("/image/{chart_type}/{filename}")
async def get_image(chart_type: str, filename: str):
    """
    根据图表类型和文件名返回PNG图片
    例如: /image/bar/1.png
    """
    # 构建图片文件路径
    image_path = f"/home/public/dataset-MegaCQA/train/{chart_type}/png/{filename}"
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="图片文件不存在")
    
    # 检查文件扩展名是否为PNG
    if not filename.lower().endswith('.png'):
        raise HTTPException(status_code=400, detail="只支持PNG格式的图片")
    
    # 返回图片文件
    return FileResponse(
        path=image_path,
        media_type="image/png",
        filename=filename
    )
