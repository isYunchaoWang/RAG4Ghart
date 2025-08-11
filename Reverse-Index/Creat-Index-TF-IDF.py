import re
import os
import csv
import nltk
from collections import defaultdict
from Tokenizer import tokenize
import json
from sklearn.feature_extraction.text import TfidfVectorizer

# 根目录
root_dir = "../Dataset-ZXQ/train80/"

# 读取所有文档的内容
documents = []
file_paths = []

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

        # 对文本内容分词，并构建文档列表
        content = '\n'.join(lines)
        documents.append(content)
        file_paths.append(file_path)


# 处理文本：分词 + 词形还原
def preprocess_text(text):
    return ' '.join(tokenize(text))


processed_documents = [preprocess_text(doc) for doc in documents]

# 使用TfidfVectorizer来计算TF-IDF矩阵
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(processed_documents)

# 词汇表中的所有词
vocab = vectorizer.get_feature_names_out()

# 创建倒排索引
inverted_index = defaultdict(lambda: defaultdict(float))

# 对每个文档中的每个词计算TF-IDF值，并填充倒排索引
for idx, doc in enumerate(processed_documents):
    for word_idx, word in enumerate(vocab):
        tfidf_score = X[idx, word_idx]
        if tfidf_score > 0:  # 只考虑非零的TF-IDF值
            inverted_index[word][file_paths[idx]] = tfidf_score

# 将倒排索引写入JSON文件
with open("tfidf_lemma.json", "w", encoding="utf-8") as f:
    json.dump(inverted_index, f, ensure_ascii=False, indent=2)
