import re
import os
import csv
import nltk
from collections import defaultdict
from Tokenizer import tokenize
# 根目录
root_dir = "../Dataset-ZXQ/sample100"

# 倒排索引结构：词语 -> {图表类型 -> 频率}
inverted_index = defaultdict(lambda: defaultdict(int))


# 遍历图表类型目录 csv
# for chart_type in os.listdir(root_dir):
#     chart_csv_dir = os.path.join(root_dir, chart_type, "csv")
#     if not os.path.isdir(chart_csv_dir):
#         continue
#
#     for filename in os.listdir(chart_csv_dir):
#         if not filename.endswith(".csv"):
#             continue
#
#         file_path = os.path.join(chart_csv_dir, filename)
#
#         # 提取前两行文本
#         lines = []
#         try:
#             with open(file_path, newline='', encoding='utf-8') as csvfile:
#                 reader = csv.reader(csvfile)
#                 for _ in range(2):
#                     row = next(reader, None)
#                     if row:
#                         lines.append(','.join(row))
#         except Exception as e:
#             print(f"读取失败: {file_path}, 错误: {e}")
#             continue
#
#         # 对文本内容分词，并构建索引
#         content = '\n'.join(lines)
#         words = tokenize(content)
#         for word in words:
#             inverted_index[word][chart_type] += 1


# 遍历图表类型目录 txt
for chart_type in os.listdir(root_dir):
    chart_txt_dir = os.path.join(root_dir, chart_type, "txt")  # 读取txt文件目录
    if not os.path.isdir(chart_txt_dir):
        continue

    for filename in os.listdir(chart_txt_dir):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(chart_txt_dir, filename)

        # 读取txt文件内容
        try:
            with open(file_path, 'r', encoding='GBK') as txtfile:
                lines = txtfile.readlines()
        except Exception as e:
            print(f"读取失败: {file_path}, 错误: {e}")
            continue

        # 对文本内容分词，并构建索引
        content = '\n'.join(lines)
        words = tokenize(content)
        for word in words:
            inverted_index[word][chart_type] += 1

# 将倒排索引转为常规格式，并对图表类型进行排序
final_index = {word: {chart_type: freq for chart_type, freq in sorted(types.items())}
               for word, types in inverted_index.items()}

# 输出到文件
import json

with open("txt_index.json", "w", encoding="utf-8") as f:
    json.dump(final_index, f, ensure_ascii=False, indent=2)
