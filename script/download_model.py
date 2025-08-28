import argparse
from modelscope.hub.snapshot_download import snapshot_download

# 1. 创建命令行参数解析器
parser = argparse.ArgumentParser(description="Download model from ModelScope")
parser.add_argument('--model_id', type=str, required=True, help='Model ID from ModelScope')
parser.add_argument('--cache_dir', type=str, default='/home/public/dkx/model', help='Cache directory to store model')

# 2. 解析参数
args = parser.parse_args()

# 3. 使用传入的参数
model_dir = snapshot_download(
    model_id=args.model_id,
    cache_dir=args.cache_dir
)

print(f"Model downloaded to: {model_dir}")
