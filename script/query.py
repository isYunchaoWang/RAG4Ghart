# MODEL_NAME = "/home/public/dkx/model/BAAI/BGE-VL-v1.5-zs"
#
# from modelscope import AutoModel
# model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True)
# model.eval()
# model.cuda()

import glob, os
txt_paths = glob.glob("/home/dukaixing/RAG4Ghart/Dataset-ZXQ/sample100/*/txt")
print(len(txt_paths))

# import torch
# with torch.no_grad():
#     model.set_processor(MODEL_NAME)
#     query_input = model.data_process(
#         text="",
#         q_or_c="q",
#         task_instruction="Recommend the most suitable chart with corresponding description for visualizing the information given by the provided text: "
#     )
#
#     query_emb = model(**query_input, output_hidden_states=True)[:, -1, :]
#
#     query_emb = torch.nn.functional.normalize(query_emb, dim=-1)
#
# from pymilvus import MilvusClient
#
# client = MilvusClient(
#     uri="http://localhost:19530"
# )
#
# client.load_collection("test")
#
# text_search_results = client.search(
#     collection_name="test",
#     anns_field="text_dense",
#     data=query_emb.cpu().detach().tolist(),
#     limit=10,
#     search_params={"metric_type": "IP"},
#     output_fields=["type", "image_url"],  # specifies fields to be returned
# )