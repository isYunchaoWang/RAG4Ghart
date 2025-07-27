# from pathlib import Path
#
# # 你的文件路径列表（可以从 txt 文件中读取或手动列出）
# file_list = [r"../Dataset-ZXQ/sample100\bubble\png\4448.txt",
#              r"../Dataset-ZXQ/sample100\bubble\png\4666.txt",
#              r"../Dataset-ZXQ/sample100\bubble\txt\4448.txt",
#              r"../Dataset-ZXQ/sample100\bubble\txt\4666.txt",
#              r"../Dataset-ZXQ/sample100\chord\png\1315.txt",
#              r"../Dataset-ZXQ/sample100\chord\png\2719.txt",
#              r"../Dataset-ZXQ/sample100\chord\png\3912.txt",
#              r"../Dataset-ZXQ/sample100\chord\png\6454.txt",
#              r"../Dataset-ZXQ/sample100\chord\png\806.txt",
#              r"../Dataset-ZXQ/sample100\chord\png\8412.txt",
#              r"../Dataset-ZXQ/sample100\chord\png\8826.txt",
#              r"../Dataset-ZXQ/sample100\chord\txt\1315.txt",
#              r"../Dataset-ZXQ/sample100\chord\txt\2719.txt",
#              r"../Dataset-ZXQ/sample100\chord\txt\3912.txt",
#              r"../Dataset-ZXQ/sample100\chord\txt\6454.txt",
#              r"../Dataset-ZXQ/sample100\chord\txt\806.txt",
#              r"../Dataset-ZXQ/sample100\chord\txt\8412.txt",
#              r"../Dataset-ZXQ/sample100\chord\txt\8826.txt",
#              r"../Dataset-ZXQ/sample100\radar\png\15009.txt",
#              r"../Dataset-ZXQ/sample100\radar\png\60.txt",
#              r"../Dataset-ZXQ/sample100\radar\txt\15009.txt",
#              r"../Dataset-ZXQ/sample100\radar\txt\60.txt",
#              r"../Dataset-ZXQ/sample100\sankey\png\1791.txt",
#              r"../Dataset-ZXQ/sample100\sankey\png\544.txt",
#              r"../Dataset-ZXQ/sample100\sankey\txt\1791.txt",
#              r"../Dataset-ZXQ/sample100\sankey\txt\544.txt",
#              r"../Dataset-ZXQ/sample100\scatter\png\5619.txt",
#              r"../Dataset-ZXQ/sample100\scatter\png\7734.txt",
#              r"../Dataset-ZXQ/sample100\scatter\png\9588.txt",
#              r"../Dataset-ZXQ/sample100\scatter\txt\5619.txt",
#              r"../Dataset-ZXQ/sample100\scatter\txt\7734.txt",
#              r"../Dataset-ZXQ/sample100\scatter\txt\9588.txt",
#              r"../Dataset-ZXQ/sample100\violin\png\9011.txt",
#              r"../Dataset-ZXQ/sample100\violin\txt\9011.txt"
# ]
#
# for txt_path in file_list:
#     txt_path = Path(txt_path)
#     filename_stem = txt_path.stem  # 比如 "4448"
#     chart_root = txt_path.parents[1]  # 比如 ../Dataset-ZXQ/sample100/bubble
#
#     # 递归查找 bubble/ 下所有名为 4448.xxx 的文件
#     for file in chart_root.rglob(f"{filename_stem}.*"):
#         try:
#             file.unlink()
#             print(f"已删除: {file}")
#         except Exception as e:
#             print(f"删除失败: {file}，错误：{e}")



import os

base_dir = "../Dataset-ZXQ/sample100"

for root, dirs, files in os.walk(base_dir):
    if os.path.basename(root) == "png":
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"已删除：{file_path}")
                except Exception as e:
                    print(f"删除失败：{file_path}，错误：{e}")
