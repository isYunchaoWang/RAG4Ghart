import json
import nltk
from collections import defaultdict, Counter
from Tokenizer import tokenize

# 加载已有倒排索引（词 → 图表类型列表）
with open("txt_index.json", "r", encoding="utf-8") as f:
    inverted_index = json.load(f)


# 推荐函数：输入一段描述，返回匹配度最高的 top_k 个图表类型
def recommend_and_show_word_to_charttype(description, top_k=3):
    tokens = tokenize(description)

    word_to_charttype_map = {}  # 存储每个词对应的图表类型
    chart_counter = Counter()  # 存储每个图表类型的匹配词频

    # 计算文本中每个词的频率
    word_frequency = Counter(tokens)

    # 遍历输入文本中的每个词，统计匹配的图表类型
    for word in word_frequency:
        if word in inverted_index:
            word_to_charttype_map[word] = inverted_index[word]  # 映射词到图表类型
            chart_types = inverted_index[word]

            # 将该词的频率与倒排索引中的频率结合
            for chart_type in chart_types:
                # 使用词频 * 倒排索引中的频率作为权重
                chart_counter[chart_type] += word_frequency[word] * chart_types[chart_type]

    # 返回得分最高的 top_k 个图表类型
    top_k_recommendations = chart_counter.most_common(top_k)

    return word_to_charttype_map, top_k_recommendations


# 示例调用
query = "The chart illustrates the production of different crops in an area, measured in metric tons. Among the crops, rapeseed has the highest production at 20,000 metric tons, indicating its dominance in the dataset. The lowest production is apple, with 2,488 metric tons. The total production across all crops amounts to 32,755 metric tons, with an average production of approximately 8,189 metric tons per crop. The data does not indicate a consistent trend such as an increase or decrease since each crop's production level stands alone. No specific turning points or growth rates can be discerned from this static dataset; however, the significant observation is the substantial disparity in production levels, notably with rapeseed leading substantially."
word_chart_map, top_k_recommendations = recommend_and_show_word_to_charttype(query, top_k=3)

# 输出结果
print(f"输入文本：{query}")
print("词语对应的图表类型如下：")
for word, chart_types in word_chart_map.items():
    print(f"  {word} → {chart_types}")

print(f"\n推荐的 top {len(top_k_recommendations)} 个图表类型：")
for chart_type, score in top_k_recommendations:
    print(f"  {chart_type}（匹配词数: {score}）")
