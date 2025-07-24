from modelscope.hub.snapshot_download import snapshot_download

model_dir = snapshot_download(model_id='BAAI/BGE-VL-v1.5-zs',
                              cache_dir="/home/public/dkx/model")