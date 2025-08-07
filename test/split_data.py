import os
import shutil
import random
import argparse
from pathlib import Path

def split_dataset(seed=42):
    # 路径设置
    base_dir = Path("/home/dukaixing/RAG4Ghart/Dataset-ZXQ")
    source_dir = base_dir / "sample100"
    train_dir = base_dir / "train80"
    test_dir = base_dir / "test20"

    # 设置随机种子，确保可复现划分结果
    random.seed(seed)

    # 文件夹名 -> 文件扩展名映射（特别处理 QA 是 .json）
    ext_map = {
        "csv": "csv",
        "png": "png",
        "QA": "json",
        "svg": "svg",
        "txt": "txt"
    }

    # 创建目标根目录
    for target_dir in [train_dir, test_dir]:
        target_dir.mkdir(exist_ok=True)

    # 遍历每种图表类型：bar、box 等
    for chart_type in source_dir.iterdir():
        if chart_type.is_dir():
            print(f"🔍 正在处理图表类型：{chart_type.name}")

            # 从 png 文件夹中获取所有数据编号（以文件名为准）
            png_folder = chart_type / "png"
            data_ids = [file.stem for file in png_folder.glob("*.png")]
            data_ids = sorted(data_ids)
            random.shuffle(data_ids)

            # 按 8:2 划分
            split_idx = int(0.8 * len(data_ids))
            train_ids = set(data_ids[:split_idx])
            test_ids = set(data_ids[split_idx:])

            for split_name, id_set, target_root in [
                ("train", train_ids, train_dir),
                ("test", test_ids, test_dir)
            ]:
                chart_target_dir = target_root / chart_type.name

                # 创建子文件夹结构（csv/png/QA/svg/txt）
                for subfolder in ext_map:
                    (chart_target_dir / subfolder).mkdir(parents=True, exist_ok=True)

                # 复制对应的数据文件
                for subfolder, ext in ext_map.items():
                    src_subfolder = chart_type / subfolder
                    tgt_subfolder = chart_target_dir / subfolder

                    for data_id in id_set:
                        src_file = src_subfolder / f"{data_id}.{ext}"
                        if src_file.exists():
                            shutil.copy(src_file, tgt_subfolder / src_file.name)

    print(f"\n✅ 数据划分完成（seed={seed}），train80 和 test20 已生成并保持目录结构一致。")

# 支持命令行参数传入随机种子
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将 sample100 数据集按 8:2 划分为 train80/test20")
    parser.add_argument("--seed", type=int, default=42, help="随机种子（默认 42）")
    args = parser.parse_args()
    split_dataset(seed=args.seed)
