from modelscope import AutoModel

MODEL_NAME = "/home/public/dkx/model/BAAI/BGE-VL-v1.5-zs"
model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True)
model.eval()
model.cuda()
model.set_processor(MODEL_NAME)

base_url = "/home/dukaixing/RAG4Ghart"

from embedding import (bar, box, bubble, chord, fill_bubble, funnel, heatmap, line, node_link, parallel, pie, radar,
                       ridgeline, sankey, scatter, stacked_area, stacked_bar, stream, sunburst, treemap, violin)

data = bar.get_data(base_url=base_url, model=model)
data.extend(box.get_data(base_url=base_url, model=model))
data.extend(bubble.get_data(base_url=base_url, model=model))
data.extend(chord.get_data(base_url=base_url, model=model))
data.extend(fill_bubble.get_data(base_url=base_url, model=model))
data.extend(funnel.get_data(base_url=base_url, model=model))
data.extend(heatmap.get_data(base_url=base_url, model=model))
data.extend(line.get_data(base_url=base_url, model=model))
data.extend(node_link.get_data(base_url=base_url, model=model))
data.extend(parallel.get_data(base_url=base_url, model=model))
data.extend(pie.get_data(base_url=base_url, model=model))
data.extend(radar.get_data(base_url=base_url, model=model))
data.extend(ridgeline.get_data(base_url=base_url, model=model))
data.extend(sankey.get_data(base_url=base_url, model=model))
data.extend(scatter.get_data(base_url=base_url, model=model))
data.extend(stacked_area.get_data(base_url=base_url, model=model))
data.extend(stacked_bar.get_data(base_url=base_url, model=model))
data.extend(stream.get_data(base_url=base_url, model=model))
data.extend(sunburst.get_data(base_url=base_url, model=model))
data.extend(treemap.get_data(base_url=base_url, model=model))
data.extend(violin.get_data(base_url=base_url, model=model))

from pymilvus import MilvusClient

client = MilvusClient(uri="http://localhost:19530")
client.insert(collection_name="test", data=data)
