import torch, glob, os
from modelscope import AutoModel

MODEL_NAME= "/home/public/dkx/model/BAAI/BGE-VL-v1.5-zs"

model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True)
model.eval()
model.cuda()

with torch.no_grad():
    model.set_processor(MODEL_NAME)

    # query_inputs = model.data_process(
    #     text="Among the 358 listed environmental protection companies and New Third Board environmental protection companies included in this year's statistics, there are 141 large enterprises, 198 medium-sized enterprises, 17 small enterprises, and 2 micro-enterprises. It can be seen that listed environmental protection companies and New Third Board environmental protection companies are mainly large and medium-sized enterprises, accounting for 94.7%.",
    #     q_or_c="q",
    #     task_instruction="Recommend the most suitable chart with corresponding description for visualizing the information given by the provided text: "
    # )

    candidate_inputs = model.data_process(
        text=["""{"id":10093,"image_url":"/home/dkx/RAG4Ghart/bar/10093.png","type":"bar","theme":"Science and Engineering","title":"Data on R&D investment across cities","distribution":"random","display":"horizontal","header":"City,million USD(million USD)","data":[{"Crop category":"Rapeseed","metric tons":20000},{"Crop category":"Wheat","metric tons":2694},{"Crop category":"Apple","metric tons":2488},{"Crop category":"Sugarcane","metric tons":7573}]}"""],
        images=["/home/dukaixing/RAG4Ghart/Dataset-ZXQ/sample100/bar/png/21.png"],
        q_or_c="c",
    )

    # query_embs = model(**query_inputs, output_hidden_states=True)[:, -1, :]
    candi_embs = model(**candidate_inputs, output_hidden_states=True)[:, -1, :]

    # query_embs = torch.nn.functional.normalize(query_embs, dim=-1)
    candi_embs = torch.nn.functional.normalize(candi_embs, dim=-1)

    # scores = torch.matmul(query_embs, candi_embs.T)

    print(candi_embs.cpu().detach().tolist()[0])