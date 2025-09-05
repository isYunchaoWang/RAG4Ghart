from fastapi import FastAPI, Body
from starlette.middleware.cors import CORSMiddleware
# from modelscope import AutoModel
# import torch
# from pymilvus import MilvusClient
#
#
# # Model path and initialization
# model_name = "/home/public/dkx/model/BAAI/BGE-VL-v1.5-zs"
# model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
# model.eval()
# model.cuda()
# model.set_processor(model_name)
#
# # Milvus client
# client = MilvusClient(uri="http://localhost:19530")

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

@app.post("/")
def dense_retrieve(query: str = Body(..., embed=True)):
    # # Process query with model
    # q = model.data_process(
    #     text=query,
    #     q_or_c="q",
    #     task_instruction="Recommend the most suitable chart with corresponding description for visualizing the information given by the provided text: "
    # )
    #
    # # Get embeddings from the model
    # emb = model(**q, output_hidden_states=True)[:, -1, :]
    # emb = torch.nn.functional.normalize(emb, dim=-1)
    # emb_list = emb.detach().cpu().tolist()
    #
    # # Search in Milvus
    # results = client.search(
    #     collection_name="BGE_VL_v1_5_zs",
    #     anns_field="hybrid_dense",
    #     data=emb_list,
    #     limit=5,
    #     search_params={"metric_type": "IP"},
    #     output_fields=["type", "image_url"],
    # )

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
