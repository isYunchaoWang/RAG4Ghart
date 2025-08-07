from modelscope.hub.snapshot_download import snapshot_download

model_dir = snapshot_download(model_id='vidore/colpali-v1.3-merged',
                              cache_dir="/home/public/dkx/model")