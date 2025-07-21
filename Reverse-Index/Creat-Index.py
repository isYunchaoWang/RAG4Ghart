import re
import os
import csv
import nltk
from collections import defaultdict

# 根目录
root_dir = "../Dataset-ZXQ/sample100"

# 倒排索引结构：词语 -> {图表类型 -> 频率}
inverted_index = defaultdict(lambda: defaultdict(int))

# nltk.download('punkt')
# 正则表达式匹配词（可根据实际需要调整）
def tokenize(text):
    return nltk.word_tokenize(text.lower())

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
            inverted_index[word][chart_type] += 1

# 将倒排索引转为常规格式，并对图表类型进行排序
final_index = {word: {chart_type: freq for chart_type, freq in sorted(types.items())}
               for word, types in inverted_index.items()}

# 输出到文件
import json

with open("word2chart_index.json", "w", encoding="utf-8") as f:
    json.dump(final_index, f, ensure_ascii=False, indent=2)
