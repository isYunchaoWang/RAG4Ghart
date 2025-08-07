import json
import os
from collections import Counter
from Tokenizer import tokenize

# 加载已有倒排索引（词 → 图表类型列表）
with open("train80_index.json", "r", encoding="utf-8") as f:
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


def get_charts_name(file_path):
    # 标准化文件路径
    file_path = os.path.normpath(file_path)

    path_parts = file_path.split(os.sep)
    if len(path_parts) > 2:
        return path_parts[3]
    return None


# 遍历指定目录下的所有txt文件，并处理它们
def process_directory(directory_path):
    file_results = {}

    # 遍历目录中的所有文件
    for root, dirs, files in os.walk(directory_path):
        charts_count = 0
        one_chart_match = 0
        top_k = 0
        for file in files:
            # 只处理txt文件
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                charts_count += 1
                # 标准化文件路径
                file_path = os.path.normpath(file_path)

                # 读取txt文件内容
                with open(file_path, "r", encoding="GBK") as f:
                    content = f.read()

                # 生成推荐结果
                word_chart_map, top_k_recommendations = recommend_and_show_word_to_charttype(content, top_k=10)
                top_k = len(top_k_recommendations)
                target_folder = get_charts_name(file_path)

                if target_folder:
                    # 统计目标文件夹名在 top_k 中出现的次数
                    folder_count = sum(1 for chart_file, _ in top_k_recommendations if target_folder in chart_file)

                    # 将文件路径和推荐结果保存到字典中
                    file_results[file_path] = {
                        "word_chart_map": word_chart_map,
                        "top_k_recommendations": top_k_recommendations,
                        "folder_count": folder_count  # 记录目标文件夹名出现次数
                    }
                    one_chart_match += folder_count
        if charts_count > 0:
            percent = (one_chart_match / (charts_count * top_k)) * 100
            print(f"{get_charts_name(root)}: {percent:.2f}%")

    return file_results


# 示例调用
directory_path = "../Dataset-ZXQ/test20/"
results = process_directory(directory_path)

# 输出结果
for file_path, result in results.items():
    print(f"文件路径: {file_path}")
    print(f"推荐的 top {len(result['top_k_recommendations'])} 个图表类型：")
    for chart_type, score in result['top_k_recommendations']:
        print(f"  {chart_type}（匹配词数: {score}）")

# 输出目标文件夹名在推荐结果中出现的次数
    print(f"  '{get_charts_name(file_path)}' 文件夹名出现的次数: {result['folder_count']}")
    print()
