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
    json_dir = "./QA/box_plot/"
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
        data = {key: [] for key in ["CTR", "VEC", "SRP", "VPR", "VE", "EVJ", "SC", "NF", "NC", "MSR", "VA"]}
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
    json_dir = "./QA/box_plot/"
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
        # print(k)
        # print(v)
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
    csv_folder = './csv/box_plot/'
    svg_folder = './svg/box_plot/'
    # 遍历文件夹下所有文件（全部都是 .csv）
    for fname in os.listdir(csv_folder):
    # for fname in ['box_plot_Business_and_Finance_1.csv','box_plot_Business_and_Finance_3.csv']:
        # 构造完整路径
        csv_path = os.path.join(csv_folder, fname)
        base_name = os.path.splitext(os.path.basename(csv_path))[0]
        # 读取首行信息
        meta = read_metadata(csv_path)

        qa_dict = {key: [] for key in ["CTR", "VEC", "SRP", "VPR", "VE", "EVJ", "SC", "NF", "NC", "MSR", "VA"]}

        df = pd.read_csv(csv_path, skiprows=1, header=0)
        column_names = df.columns.tolist()
        # 初始化一个字典来保存结果
        summary_results = {}

        for col in column_names:
            q1 = df[col].quantile(0.25)
            median = df[col].median()
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            
            # 计算理论上下须极限
            upper_limit_theory = q3 + 1.5 * iqr
            lower_limit_theory = q1 - 1.5 * iqr
            
            # 找出实际的上下须界限
            upper_whisker = df[df[col] <= upper_limit_theory][col].max()
            lower_whisker = df[df[col] >= lower_limit_theory][col].min()
            
            # 找出所有异常值，并找到最大异常值
            outliers = df[ df[col] > upper_limit_theory ] [col]
            largest_outlier = outliers.max() if not outliers.empty else None
            outliers = df[ df[col] < lower_limit_theory ][col]
            lowest_outlier = outliers.min() if  not outliers.empty else None
            
            summary_results[col] = {
                'Q1': q1,
                'Median': median,
                'Q3': q3,
                'IQR': iqr,
                'Upper Whisker Limit Theory': upper_limit_theory,
                'Lower Whisker Limit Theory': lower_limit_theory,
                'Upper Whisker': upper_whisker,
                'Lower Whisker': lower_whisker,
                'Largest Outlier': largest_outlier,
                'Lowest Outlier' : lowest_outlier
            }     

    #CTR
        CTR_question = {'Q': "What type of plot is this?", 'A': "This chart is a {box plot}."}
        qa_dict["CTR"] = [CTR_question]

    #VEC
        VEC_question1 = {'Q': "How many boxes are in this box plot?", 
                         'A': f"There are {{{len(column_names)}}} boxes."}

        qa_dict["VEC"] = [VEC_question1]

    # #SRP
    #     qa_dict['SRP'] = []
    #     svg_path = os.path.join(svg_folder, base_name + ".svg")
    #     API_KEY = "sk-tfaurviuhoondrjozewcgtewsitxdbnenrqlzlqwuqzrvvff"  # api请勿外传！！！！
    #     svg_text = read_python_file(svg_path)

    #     Question = "Is this bar chart a horizontal box plot or a vertical box plot?"
    #     Answer = "The box plot is a horizontal/vertical box plot."#只靠svg似乎检测不出来
    #     prompt = f"根据svg文件，回答问题，只需要给出答案。问题是{Question}:\n 回答的模版:{Answer} .\nsvg文件:{svg_text}"
    #     raw_content = call_llm_api(prompt, API_KEY)
    #     clean_content = extract_text(raw_content)
    #     qa_dict['SRP'].append({'Q': Question, 'A':clean_content})

    #     if "horizontal" in clean_content:
    #         Question = "Which category does the bottom box represent?"
    #         Answer = f"The bottom bar represents {{{column_names[0]}}}"
    #     elif "vertical" in clean_content:
    #         Question = "Which category does the leftmost box represent?"
    #         Answer = f"The leftmost bar represents {{{column_names[0]}}}"
    #     else:
    #         raise ValueError("LLM的回答中没有显式的说明，柱状图是横向的还是竖向的。")
    #     qa_dict['SRP'].append({'Q': Question, 'A': Answer})

    #     if "horizontal" in clean_content:
    #         Question = "Which category does the topmost box represent?"
    #         Answer = f"The topmost box represents {{{column_names[-1]}}}."
    #     elif "vertical" in clean_content:
    #         Question = "Which category does the rightmost box represent?"
    #         Answer = f"The rightmost box represents {{{column_names[-1]}}}."
    #     else:
    #         raise ValueError("LLM的回答中没有显式的说明，柱状图是横向的还是竖向的。")
    #     qa_dict['SRP'].append({'Q': Question, 'A':Answer})

    #     cat_id = random.randint(1, len(column_names) - 2)
    #     cat = column_names[cat_id]
    #     cat_left_id = random.randint(max(0, cat_id - 4), cat_id - 1)
    #     cat_right_id = random.randint( cat_id + 1, min( len(column_names) - 1 , cat_id + 4) )
    #     position = ['first', 'second', 'third']
    #     direction = [['left', 'right'],['underneath', 'top']]
    #     num = 0 if "horizontal" in clean_content else 1
    #     Question = {'Q': f"Which category is the {position[cat_id - cat_left_id - 1]} position to the {direction[num][0]} of box {{{cat}}}?",
    #                 'A': f"The {position[cat_id - cat_left_id - 1]} position to the left of {{{cat}}} is {{{column_names[cat_left_id]}}}."}
    #     qa_dict['SRP'].append(Question)
    #     Question = {'Q': f"Which category is the {position[cat_right_id - cat_id - 1]} position to the {direction[num][1]} of box {{{cat}}}?",
    #                 'A': f"The {position[cat_right_id - cat_id - 1]} position to the right of {{{cat}}} is {{{column_names[cat_right_id]}}}."}
    #     qa_dict['SRP'].append(Question)
        

    #VPR
        max_median_col = max(summary_results.keys(), key=lambda x: summary_results[x]['Median'])
        VPR_question_1 = {'Q': "Which category has the largest median in this box plot?", 
                         'A': f"The category with the largest median is {{{max_median_col}}}."}
        max_Q3_col = max(summary_results.keys(), key=lambda x: summary_results[x]['Q3'])
        VPR_question_2 = {'Q': "Which category has the highest upper quartile (Q3) in this box plot?", 
                         'A': f"The category with the highest Q3 is {{{max_Q3_col}}}."}
        min_IQR_col = min(summary_results.keys(), key = lambda x:summary_results[x]['IQR'])
        VPR_question_3 = {'Q': f"Which category has the Minimum IQR of data?", 
                         'A': f"The category with the Minimum IQR is {{{min_IQR_col}}}."}
        qa_dict["VPR"] = [VPR_question_1,VPR_question_2 , VPR_question_3]

    #VE
        qa_dict["VE"] = []
        category = random.choice(column_names)
        # for i,category in enumerate(categories):
        VE_question_1 = {'Q': f"What is the median of {{{category}}} in the box plot?", 
                        'A': f"The median of {{{category}}} is {{{summary_results[category]['Median']} {meta['unit']}}}."}
        category = random.choice(column_names)
        VE_question_2 = {'Q': f"What is the upper quartile (Q3) of {{{category}}} in the box plot?", 
                        'A': f"The upper quartile (Q3) of {{{category}}} is {{{summary_results[category]['Q3']} {meta['unit']}}}."}
        category = random.choice(column_names)
        VE_question_3 = {'Q': f"What is the lower quartile (Q1) of {{{category}}} in the box plot?", 
                        'A': f"The lower quartile (Q1) of {{{category}}} is {{{summary_results[category]['Q1']} {meta['unit']}}}."}
        category = random.choice(column_names)
        VE_question_4 = {'Q': f"What is the upper whisker limit of {{{category}}} in the box plot?", 
                        'A': f"The upper whisker limit of {{{category}}} is {{{summary_results[category]['Upper Whisker']} {meta['unit']}}}."}
        category = random.choice(column_names)
        VE_question_5 = {'Q': f"What is the lower whisker limit of {{{category}}} in the box plot?", 
                        'A': f"The lower whisker limit of {{{category}}} is {{{summary_results[category]['Lower Whisker']} {meta['unit']}}}."}
        qa_dict["VE"].extend([VE_question_1, VE_question_2, VE_question_3, VE_question_4, VE_question_5])
        
        have_upper_outliers = [col for col in column_names if summary_results[col]['Largest Outlier'] is not None]
        if len(have_upper_outliers) > 0:
            idx = random.randint(0, len(have_upper_outliers) - 1)
            VE_question_6 = {'Q': f"What is the largest upper outlier value in {{{column_names[idx]}}} in the box plot?", 
                             'A': f"The largest upper outlier value in {{{column_names[idx]}}} is {{{ summary_results[column_names[idx]]['Largest Outlier'] }}}."}
            qa_dict['VE'].append(VE_question_6)

        have_lower_outliers = [col for col in column_names if summary_results[col]['Lowest Outlier'] is not None]
        if len(have_lower_outliers) > 0:
            idx = random.randint(0, len(have_lower_outliers) - 1)
            VE_question_6 = {'Q': f"What is the lowest upper outlier value in {{{column_names[idx]}}} in the box plot?", 
                             'A': f"The lowest upper outlier value in {{{column_names[idx]}}} is {{{ summary_results[column_names[idx]]['Lowest Outlier'] }}}."}
            qa_dict['VE'].append(VE_question_6)
            
    #EVJ
        all_values = []
        for column in column_names:
            all_values.extend(df[column].tolist())
        
        min_val = min(all_values)
        max_val = max(all_values)
        EVJ_question_1 = {'Q': f"What is the global maximum {meta['unit']} value in the box plot?",
                          'A': f"The global maximum {meta['unit']} value in the box plot is {{{max_val:.2f} {meta['unit']}}}."}
        EVJ_question_2 = {'Q': f"What is the global minimum {meta['unit']} value in the box plot?",
                          'A': f"The global minimum {meta['unit']} value in the box plot is {{{min_val:.2f} {meta['unit']}}}."}
        qa_dict['EVJ'] = [EVJ_question_1, EVJ_question_2]

    #SC
        
        qa_dict["SC"] =[]
        for formula in ['Median', 'Q1', 'Q3']:
            column1, column2 = random.sample(column_names, 2)
            num1 = summary_results[column1][formula]
            num2 = summary_results[column2][formula]
            # 计算指标
            difference = abs(num1 - num2)
            SC_question1 = {'Q': f"What is the {{{formula}}} difference between box {{{column1}}} and {{{column2}}}?", 
                            'A': f"The {{{formula}}} difference between box {{{column1}}} and {{{column2}}} is {{{difference} {meta['unit']}}}."}
            column1, column2 = random.sample(column_names, 2)
            num1 = summary_results[column1][formula]
            num2 = summary_results[column2][formula]
            val_sum = num1 + num2
            SC_question2 = {'Q': f"What is the toal {{{formula}}} value of box {{{column1}}} and {{{column2}}}?",
                            'A': f"The total {{{formula}}} value of box {{{column1}}} and {{{column2}}} is {{{val_sum} {meta['unit']}}}."}
            column1, column2 = random.sample(column_names, 2)
            num1 = summary_results[column1][formula]
            num2 = summary_results[column2][formula]
            val_avg = (num1 + num2) / 2
            SC_question3 = {'Q': f"What is the average {{{formula}}} value of box {{{column1}}} and {{{column2}}}?",
                            'A': f"The average {{{formula}}} value of box {{{column1}}} and {{{column2}}} is {{{val_avg} {meta['unit']}}}."}
            qa_dict["SC"].extend( [SC_question1, SC_question2, SC_question3] )
            

    #NF
        qa_dict['NF'] = []
        if len(have_upper_outliers) > 0:
            random_col = random.choice(have_upper_outliers)
            val = summary_results[random_col]['Largest Outlier'] * 0.9
            filter_col = [col for col in have_upper_outliers if summary_results[col]['Largest Outlier'] > val]
            NF_question = {'Q': f"Which boxes in the box plot have outliers that exceed {{{val} {meta['unit']}}}?",
                           'A': "Box"+','.join([ col for col in filter_col] ) +f" have the outliers exceed {{{val} {meta['unit']}}}."}
            qa_dict['NF'].append(NF_question)
        

        # 计算平均值
        median_value = [summary_results[col]['Median'] for col in column_names]
        sorted_col = sorted(column_names, key= lambda col: summary_results[col]['Median'])
        median_avg = [(summary_results[sorted_col[i]]['Median'] + summary_results[sorted_col[i + 1]]['Median'] )/2 for i in range(len(sorted_col) - 1)]
        idx = min(random.randint(0,2), len(median_avg) - 1)
        avg_value = median_avg[idx]
        # 获取大于选择的相对平均值的类别
        # above_avg = [col for col in column_names if summary_results[col]['Median'] > average]
        # 获取小于平均值的类别
        below_avg = [col for col in column_names if summary_results[col]['Median'] < avg_value]

        NF_question_2 = {'Q': f"Which boxes have median values below {{{avg_value:.2f} {meta['unit']}}}? Please list the boxes and corresponding values.", 
                         'A':", ".join([f"{col} has {{{summary_results[col]['Median']} {meta['unit']}}} " for col in below_avg]) }
        
        idx = max(random.randint( len(median_avg) - 3 , len(median_avg) - 1 ), 0)
        avg_value = median_avg[idx]
        above_avg = [col for col in column_names if summary_results[col]['Median'] > avg_value]
        NF_question_1 = {'Q': f"Which boxes have median values exceed {{{avg_value:.2f} {meta['unit']}}}? Please list the boxes and corresponding values.", 
                         'A':", ".join([f"{col} has {{{summary_results[col]['Median']} {meta['unit']}}} " for col in above_avg]) }
        qa_dict["NF"].append(NF_question_1)
        qa_dict["NF"].append(NF_question_2)



    #NC
        qa_dict["NC"] = []
        for num in range(2,min(len(column_names) + 1, 5)):
            columns = random.sample(column_names, num)
            max_median_col = max(columns, key=lambda x: summary_results[x]['Median'])
            NC_question = {'Q': f"Which is larger, the median value of {', '.join(columns[ : -1])} or {columns[-1]} ",
                           'A': f"The median value of the {{{ str(max_median_col) }}} is larger."}
            qa_dict["NC"].append(NC_question)
        
    #MSR
        max_span = max(summary_results.keys(), key=lambda x: summary_results[x]['Upper Whisker'] - summary_results[x]['Lower Whisker'])
        MSR_question_1 = {'Q': "In the box plot, which group has the {largest} difference between the maximum non-outlier value (upper whisker) and the minimum non-outlier value (lower whisker)?",
                          'A': f"The group with the largest whisker span is {{{max_span}}}."}
        if max_median_col == min_IQR_col:
            MSR_question_2 = {'Q': "Which group has both the highest median and the smallest interquartile range (IQR)?",
                              'A': f"The group with the highest median and smallest IQR is {{{max_median_col}}}."}
        else:
            MSR_question_2 = {'Q': "Which group has both the highest median and the smallest interquartile range (IQR)?",
                              'A': f"There is no group with the highest median and smallest IQR."}
        qa_dict['MSR'] = [MSR_question_1, MSR_question_2]

        write_all_qa_to_json(csv_path=csv_path, qa_dict=qa_dict)

if __name__ == '__main__':
    main()