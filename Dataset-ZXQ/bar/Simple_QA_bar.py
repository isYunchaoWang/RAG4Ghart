import pandas as pd
import os
import json
import random
import requests
import re
# todo:根据你的csv里首行有的信息进行修改
# 读取文件的第一行，依次返回大标题、子标题、单位、模式
def read_metadata(filepath):
    # header=None 表示不把任何行当成列名，nrows=1 只读第一行
    meta = pd.read_csv(filepath, header=None, nrows=1).iloc[0].tolist()
    meta = [element.strip() for element in meta]
    keys = ['title', 'subtitle', 'unit', 'mode']
    return dict(zip(keys, meta))

def write_qa_to_json(csv_path: str, qa_type: str, qa_item: dict):

    # 找到 "csv" 在路径中的位置
    idx = csv_path.find('csv')
    # 截取 "/bar_chart/bar_chart_1.csv"
    rel = csv_path[idx + len('csv'):]
    # 取出子目录部分 "bar_chart"
    subdir = os.path.dirname(rel).lstrip(os.sep)

    # 前缀 "../"
    prefix = csv_path[:idx]
    # 构造 JSON 存放目录 "../QA/bar_chart"
    json_dir = "./QA/bar_chart/"
    os.makedirs(json_dir, exist_ok=True)

    # 构造 JSON 文件完整路径
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    json_path = os.path.join(json_dir, base_name + '.json')

    # 加载或初始化
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # 初始化各类空列表
        data = {key: [] for key in ["CTR", "VEC", "SPR", "VPR", "VE", "EVJ", "SC", "NF", "NC", "MSR", "VA"]}
    # 追加 QA
    data.setdefault(qa_type, []).append(qa_item)

    # 写回
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
def write_all_qa_to_json(csv_path: str, qa_dict: dict):
    # 找到 "csv" 在路径中的位置
    idx = csv_path.find('csv')
    rel = csv_path[idx + len('csv'):]
    subdir = os.path.dirname(rel).lstrip(os.sep)

    prefix = csv_path[:idx]
    json_dir = "./QA/bar_chart/"
    os.makedirs(json_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    json_path = os.path.join(json_dir, base_name + '.json')

    # 加载已有数据
    # if os.path.exists(json_path):
    #     with open(json_path, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    # else:
    data = {key: [] for key in ["CTR", "VEC", "SRP", "VPR", "VE", "EVJ", "SC", "NF", "NC", "MSR", "VA"]}

    # 合并每一类 QA
    for k, v in qa_dict.items():
        data.setdefault(k, []).extend(v)

    # 写入
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
def read_python_file(file_path):
    """
    以文本方式读取任意文件（包括 SVG）。
    返回文件内容的字符串形式。
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
def extract_text(content):
    """
    提取LLM返回的纯文本内容，去除Markdown代码块、换行、多余空格。
    """
    # 去除 Markdown 代码块（如 ```text\n...\n```）
    content = re.sub(r'```.*?\n(.*?)```', r'\1', content, flags=re.DOTALL)
    # 移除所有前后空格
    content = content.strip()
    # 替换中间多余空白为一个空格
    content = re.sub(r'\s+', ' ', content)
    return content
def call_llm_api(prompt, api_key):
    """
    调用 LLM API 并返回结果字符串。
    """
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "max_tokens": 512,
        "enable_thinking": False,
        "thinking_budget": 4096,
        "min_p": 0.05,
        "stop": None,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
        "tools": [
            {
                "type": "function",
                "function": {
                    "description": "<string>",
                    "name": "<string>",
                    "parameters": {},
                    "strict": False
                }
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    return data['choices'][0]['message']['content']

def main():
    # todo 修改路径和任务类型
    csv_folder = './csv/bar_chart/'
    svg_folder = './svg/bar_chart/'
    # 遍历文件夹下所有文件（全部都是 .csv）
    # for fname in os.listdir(csv_folder):
    for fname in ['bar_Agriculture_and_Food_Production_3.csv','bar_Agriculture_and_Food_Production_4.csv']:
        # 构造完整路径
        csv_path = os.path.join(csv_folder, fname)
        base_name = os.path.splitext(os.path.basename(csv_path))[0]

        # 读取首行信息
        meta = read_metadata(csv_path)

        qa_dict = {key: [] for key in ["CTR", "VEC", "SRP", "VPR", "VE", "EVJ", "SC", "NF", "NC", "MSR", "VA"]}

        df = pd.read_csv(csv_path, skiprows=1, header=0)
        column_names = df.columns.tolist()
        category_name = df.iloc[:, 0].to_list()
        bar_count = df.iloc[:, 0].count()
        

    #CTR
        CTR_question = {'Q': "What type of chart is this?", 'A': "This chart is a {bar chart}."}
        qa_dict["CTR"] = [CTR_question]

    #VEC
        # 读取 CSV 文件：跳过第一行，第二行作为列名
        VEC_question = {'Q': "How many bars are in this bar chart?", 'A': f"There are {{{bar_count}}} bars in this bar chart."}
        qa_dict["VEC"] = [VEC_question]

    #SRP
        # qa_dict['SRP'] = []
        # svg_path = os.path.join(svg_folder, base_name + ".svg")
        # API_KEY = "sk-tfaurviuhoondrjozewcgtewsitxdbnenrqlzlqwuqzrvvff"  # api请勿外传！！！！
        # svg_text = read_python_file(svg_path)

        # Question = "Is this bar chart a horizontal bar chart or a vertical bar chart?"
        # Answer = "The bar chart is a {horizontal/vertical} bar chart."#只靠svg似乎检测不出来
        # prompt = f"根据svg文件，回答问题，只需要给出答案。问题是{Question}:\n 回答的模版:{Answer} .\nsvg文件:{svg_text}"
        # raw_content = call_llm_api(prompt, API_KEY)
        # clean_content = extract_text(raw_content)
        # qa_dict['SRP'].append({'Q': Question, 'A':clean_content})

        # if "horizontal" in clean_content:
        #     Question = "Which category does the bottom bar represent?"
        #     Answer = f"The bottom bar represents {{{category_name[0]}}}"
        # elif "vertical" in clean_content:
        #     Question = "Which category does the leftmost bar represent?"
        #     Answer = f"The leftmost bar represents {{{category_name[0]}}}"
        # else:
        #     raise ValueError("LLM的回答中没有显式的说明，柱状图是横向的还是竖向的。")
        # qa_dict['SRP'].append({'Q': Question, 'A': Answer})


        # if "horizontal" in clean_content:
        #     Question = "Which category does the topmost bar represent?"
        #     Answer = f"The topmost bar represents {{{category_name[-1]}}}."
        # elif "vertical" in clean_content:
        #     Question = "Which category does the rightmost bar represent?"
        #     Answer = f"The rightmost bar represents {{{category_name[-1]}}}."
        # else:
        #     raise ValueError("LLM的回答中没有显式的说明，柱状图是横向的还是竖向的。")
        # qa_dict['SRP'].append({'Q': Question, 'A':Answer})

        # idx1, idx2 = random.sample(range(len(df)), 2)
        # # 获取类别名称和对应的数值
        # cat1 = df.iloc[idx1, 0]
        # cat2 = df.iloc[idx2, 0]
        # if "vertical" in clean_content:
        #     Question = f"What is the spatial relationship of bar {{{cat1}}} relative to the bar {{{cat2}}} in terms of horizontal (above/below) direction?"
        #     if( idx1 < idx2 ) : Answer = f"bar {{{cat1}}} is to the {{left}} of the bar {{{cat2}}}."
        #     else: Answer = f"bar {{{cat1}}} is to the {{right}} of the bar {{{cat2}}}."
        # elif "horizontal" in clean_content:
        #     Question = f"What is the spatial relationship of bar {{{cat1}}} relative to the bar {{{cat2}}} in terms of horizontal (left/right) direction??"
        #     if( idx1 < idx2 ) : Answer = f"bar {{{cat1}}} is to the {{below}} of the bar {{{cat2}}}."
        #     else: Answer = f"bar {{{cat1}}} is to the {{above}} of the bar {{{cat2}}}."
        # else:
        #     raise ValueError("LLM的回答中没有显式的说明，柱状图是横向的还是竖向的。")
        # qa_dict['SRP'].append({'Q': Question, 'A':Answer})

    #VPR
        # 提取最大值对应的类别
        max_idx = df.iloc[:, 1].idxmax()  # 数值列中最大值所在的行索引
        max_category = df.iloc[max_idx, 0]  # 该行对应的类别名称
        # 提取最小值对应的类别
        min_idx = df.iloc[:, 1].idxmin()  # 数值列中最小值所在的行索引
        min_category = df.iloc[min_idx, 0]  # 该行对应的类别名称
        VPR_question_1 = {'Q': "Which category has the highest bar in this bar chart?", 'A': f"The category with the highest bar is {{{ str(max_category) }}}."}
        VPR_question_2 = {'Q': "Which category has the lowest bar in this bar chart?", 'A': f"The category with the lowest bar is {{{ str(min_category) }}}."}
        qa_dict["VPR"] = [VPR_question_1,VPR_question_2]

    #VE
        qa_dict['VE'] = []
        for i in random.sample(range(len(category_name)), random.randint(2,len(category_name) - 1)):
            VE_question = {'Q': f"What is the value of {{{category_name[i]}}}?",
                           'A': f"The value of {{{ str(category_name[i]) }}} is {{{ str(df.iloc[i, 1]) }}}."}
            qa_dict['VE'].append(VE_question)
            # write_qa_to_json(csv_path, "VE", VE_question)
        
    #EVJ
        VEJ_question1 = {'Q': f"What is the maximum {{{meta['unit']}}} in the bar chart?", 'A': f"The maximum {{{meta['unit']}}} is {{{ str(df.iloc[:, 1].max()) }}}."}
        VEJ_question2 = {'Q': f"What is the minimum {{{meta['unit']}}} in the bar chart?", 'A': f"The minimum {{{meta['unit']}}} is {{{ str(df.iloc[:, 1].min()) }}}."}
        qa_dict["EVJ"] = [VEJ_question1, VEJ_question2]

    #SC
        idx1, idx2 = random.sample(range(len(df)), 2)
        # 获取类别名称和对应的数值
        cat1 = df.iloc[idx1, 0]
        val1 = df.iloc[idx1, 1]
        cat2 = df.iloc[idx2, 0]
        val2 = df.iloc[idx2, 1]
        # 计算指标
        total = val1 + val2
        SC_question1 = {'Q': f"What is the total value of {{{cat1}}} and {{{cat2}}}?", 'A': f"The total value of {{{cat1}}} and {{{cat2}}} is {{{ str(total) }}}."}
        idx1, idx2 = random.sample(range(len(df)), 2)
        # 获取类别名称和对应的数值
        cat1 = df.iloc[idx1, 0]
        val1 = df.iloc[idx1, 1]
        cat2 = df.iloc[idx2, 0]
        val2 = df.iloc[idx2, 1]
        average = (val1 + val2) / 2
        SC_question2 = {'Q': f"What is the average value of {{{cat1}}} and {{{cat2}}}?", 'A': f"The average value of {{{cat1}}} and {{{cat2}}} is {{{ str(average) }}}."}
        idx1, idx2 = random.sample(range(len(df)), 2)
        # 获取类别名称和对应的数值
        cat1 = df.iloc[idx1, 0]
        val1 = df.iloc[idx1, 1]
        cat2 = df.iloc[idx2, 0]
        val2 = df.iloc[idx2, 1]
        difference = abs(val1 - val2)
        SC_question3 = {'Q': f"What is the difference between {{{cat1}}} and {{{cat2}}}?", 'A': f"The difference between {{{cat1}}} and {{{cat2}}} is {{{ str(difference) }}}."}
        qa_dict["SC"] = [SC_question1, SC_question2, SC_question3]
    #NF
        value_column = df.iloc[:, 1]
        # 计算平均值
        avg_value = value_column.mean()
        # 获取大于平均值的类别和数值
        above_avg = df[value_column > avg_value]
        # 获取小于平均值的类别和数值
        below_avg = df[value_column < avg_value]

        NF_question_1 = {'Q': f"Which categories have {{{meta['unit'] }}} values exceed {{{avg_value:.2f}}}? Please list the categories and corresponding {{{meta['unit'] }}} values.", 
                         'A':", ".join([f"{{{row[0]}}} has {{{row[1]}}} {{{meta['unit'] }}} values" for _, row in above_avg.iterrows()]) or "None"}
        NF_question_2 = {'Q': f"Which categories have {{{meta['unit'] }}} values below {{{avg_value:.2f}}}? Please list the categories and corresponding {{{meta['unit'] }}} values.", 
                         'A':", ".join([f"{{{row[0]}}} has {{{row[1]}}} {{{meta['unit'] }}} values" for _, row in below_avg.iterrows()]) or "None"}
        qa_dict["NF"] = [NF_question_1, NF_question_2]

    #NC
        qa_dict["NC"] = []
        for num in range(2,min(len(df), 6)):
            idx = random.sample(range(len(df)), num)
            # 提取类别和对应的数值
            selected_rows = df.iloc[idx]
            names = selected_rows.iloc[:, 0].tolist()
            names = ['{' + name + '}' for name in names]
            values = selected_rows.iloc[:, 1].tolist()
            # 找出最大值的索引
            max_idx = values.index(max(values))
            max_name = names[max_idx]
            NC_question = {'Q': f"Which is larger, {', '.join(names[:-1])} or {names[-1]} ", 'A': f"The value of the { str(max_name) } is larger."}

            qa_dict["NC"].append(NC_question)


    #MSR
        qa_dict['MSR'] = []
        # 获取数值列
        values = df.iloc[:, 1]
        # 计算平均值
        average_value = values.mean()
        # 统计高于平均值的数量
        above_avg_count = (values > average_value).sum()
        Question = "How many bars in the bar chart have values above the overall average?"
        Answer = f"There are {{{ above_avg_count }}} bars with values above the average."
        qa_dict['MSR'].append({'Q': Question, 'A':Answer})

        # 计算相邻差值
        differences = values.diff().abs()  # 取绝对值
        # 找到最大差值的位置索引
        max_diff_index = differences.idxmax()
        # 获取这对相邻栏的标签和差值
        category_1 = df.iloc[max_diff_index - 1, 0]
        category_2 = df.iloc[max_diff_index, 0]
        Question = "Which pair of adjacent bars has the largest difference in values?"
        Answer = f"The pair of adjacent bars with the largest difference is between {{{ category_1 }}} and {{{ category_2 }}}."
        qa_dict['MSR'].append({'Q': Question, 'A':Answer})

        top_3 = df.sort_values(by=df.columns[1], ascending=False).head(3)
        category_1, category_2, category_3= top_3.iloc[:, 0].tolist()

        Question = "Which {three categories} have the highest combined values? "
        Answer = f"The three categories with the highest combined values are: {{{category_1}}}, {{{category_2}}}, and {{{category_3}}}."
        qa_dict['MSR'].append({'Q': Question, 'A':Answer})

    #VA
        # 获取列名
        category_col = df.iloc[:, 0].name  # 第一列为类别名称
        value_col = df.iloc[:, 1].name     # 第二列为数值

        # 排序后的 DataFrame
        df_desc = df.sort_values(by=value_col, ascending=False)
        df_asc = df.sort_values(by=value_col, ascending=True)

        # 所有类别名称（按排序后）
        sorted_categories_desc = ['{' + col + '}' for col in df_desc[category_col].tolist()]
        sorted_categories_asc = ['{' + col + '}' for col in df_asc[category_col].tolist()]
        
        qa_dict['VA'] = []
        Question = f"Sort the bars by {{{ meta['unit'] }}} values in descending order and list the labels from left to right."
        Answer = f"Sorted by values descending: {', '.join(sorted_categories_desc[:-1])}, and {sorted_categories_desc[-1]}"

        qa_dict['VA'].append({'Q': Question, 'A':Answer})

        Question = f"Sort the bars by {{{ meta['unit'] }}} values in ascending order and list the labels from left to right."
        Answer = f"Sorted by values ascending: {', '.join(sorted_categories_asc[:-1])}, and {sorted_categories_asc[-1]}"
        qa_dict['VA'].append({'Q': Question, 'A':Answer})

        write_all_qa_to_json(csv_path=csv_path, qa_dict=qa_dict)


if __name__ == '__main__':
    main()