import re
import os
import csv
from collections import defaultdict

# 根目录
root_dir = "../Dataset-ZXQ/sample100"

# 倒排索引结构：词语 -> 出现的图表类型集合
inverted_index = defaultdict(set)

# 正则表达式匹配词（可根据实际需要调整）
def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

# 遍历图表类型目录
for chart_type in os.listdir(root_dir):
    chart_csv_dir = os.path.join(root_dir, chart_type, "csv")
    if not os.path.isdir(chart_csv_dir):
        continue

    for filename in os.listdir(chart_csv_dir):
        if not filename.endswith(".csv"):
            continue

        file_path = os.path.join(chart_csv_dir, filename)

        # 提取前两行文本
        lines = []
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for _ in range(2):
                    row = next(reader, None)
                    if row:
                        lines.append(','.join(row))
        except Exception as e:
            print(f"读取失败: {file_path}, 错误: {e}")
            continue

        # 对文本内容分词，并构建索引
        content = '\n'.join(lines)
        words = tokenize(content)
        for word in words:
            inverted_index[word].add(chart_type)

# 将 set 转为 list，以便后续存 JSON
final_index = {word: sorted(list(types)) for word, types in inverted_index.items()}

# 输出到文件
import json
with open("word2chart_index.json", "w", encoding="utf-8") as f:
    json.dump(final_index, f, ensure_ascii=False, indent=2)