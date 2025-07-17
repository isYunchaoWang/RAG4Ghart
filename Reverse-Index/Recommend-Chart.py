import json
import nltk
from collections import defaultdict, Counter

# 加载已有倒排索引（词 → 图表类型列表）
with open("word2chart_index.json", "r", encoding="utf-8") as f:
    inverted_index = json.load(f)


def tokenize(text):
    return nltk.word_tokenize(text.lower())


# 推荐函数：输入一段描述，返回匹配度最高的 top_k 个图表类型
def recommend_and_show_word_to_charttype(description, top_k=3):
    tokens = tokenize(description)

    word_to_charttype_map = {}  # 存储每个词对应的图表类型
    chart_counter = Counter()  # 存储每个图表类型的匹配词频

    # 遍历输入文本中的每个词，统计匹配的图表类型
    for word in tokens:
        if word in inverted_index:
            word_to_charttype_map[word] = inverted_index[word]  # 映射词到图表类型
            chart_types = inverted_index[word]
            for chart_type in chart_types:
                chart_counter[chart_type] += 1

    # 返回得分最高的 top_k 个图表类型
    top_k_recommendations = chart_counter.most_common(top_k)

    return word_to_charttype_map, top_k_recommendations


# 示例调用
query = "According to the trend, give me the Education and Academics grades"
word_chart_map, top_k_recommendations = recommend_and_show_word_to_charttype(query, top_k=3)

# 输出结果
print(f"输入文本：{query}")
print("词语对应的图表类型如下：")
for word, chart_types in word_chart_map.items():
    print(f"  {word} → {chart_types}")

print(f"\n推荐的 top {len(top_k_recommendations)} 个图表类型：")
for chart_type, score in top_k_recommendations:
    print(f"  {chart_type}（匹配词数: {score}）")
