      
import os
import pandas as pd
import json
from io import StringIO
from scipy.stats import gaussian_kde
import numpy as np
import random

input_dir = 'csv/ridgeline_chart'
output_dir = 'QA'

#计算核密度并输出
def precompute_kde(filename):
    df = pd.read_csv(filename, skiprows=3)
    kde_dict = {}

    for label in range(df.shape[1]):
        data = df.iloc[:, label].dropna() 
        if data.empty:
            print(f"[WARNING] 列 {label} 没有有效数据，跳过")
            continue
        kde_dict[label] = gaussian_kde(data) 
    return kde_dict

#x值下核密度计算
def density_at_x(kde_dict, label, x):
    if label not in kde_dict:
        raise ValueError(f"Label {label} 的核密度估计器未缓存")
    kde = kde_dict[label]
    return kde(x)

#计算x值下密度最大列序号-哪个label在这个x下密度最大
def label_with_highest_density(kde_dict, x):
    max_density = -float('inf')
    max_label = None
    for label, kde in kde_dict.items():
        try:
            density = kde(x)
            if density > max_density:
                max_density = density
                max_label = label
        except Exception as e:
            print(f"[ERROR] 处理列 {label} 时发生错误: {e}")

    return max_label

#计算密度大于阈值的标签——已取消
def labels_over_density(kde_dict, threshold):
    result = []
    for label, kde in kde_dict.items():
        try:
            x_vals = np.linspace(kde.dataset.min(), kde.dataset.max(), 1000)
            y_vals = kde(x_vals)
            max_density = y_vals.max()
            if max_density > threshold:
                result.append((label, max_density))
        except Exception as e:
            print(f"[ERROR] 处理 label {label} 时发生错误: {e}")

    return result

def labels_below_density(kde_dict, threshold):
    result = []
    for label, kde in kde_dict.items():
        try:
            x_vals = np.linspace(kde.dataset.min(), kde.dataset.max(), 1000)
            y_vals = kde(x_vals)
            max_density = y_vals.max()
            if max_density < threshold:
                result.append((label, max_density))
        except Exception as e:
            print(f"[ERROR] 处理 label {label} 时发生错误: {e}")

    return result

#输出所有峰值大于limit的索引
def labels_peak_x_over_limit(kde_dict, limit):
    result = []
    for label, kde in kde_dict.items():
        try:
            x_vals = np.linspace(kde.dataset.min(), kde.dataset.max(), 1000)
            y_vals = kde(x_vals)
            peak_idx = np.argmax(y_vals)
            peak_x = x_vals[peak_idx]
            if peak_x > limit:
                result.append((label,peak_x))
        except Exception as e:
            print(f"[ERROR] 处理 label {label} 时发生错误: {e}")
    return result

#输出所有峰值小于limit的索引
def labels_peak_x_below_limit(kde_dict, limit):

    result = []
    for label, kde in kde_dict.items():
        try:
            x_vals = np.linspace(kde.dataset.min(), kde.dataset.max(), 1000)
            y_vals = kde(x_vals)
            peak_idx = np.argmax(y_vals)
            peak_x = x_vals[peak_idx]
            if peak_x < limit:
                result.append((label,peak_x))
        except Exception as e:
            print(f"[ERROR] 处理 label {label} 时发生错误: {e}")
    return result

#计算拥有最高核密度的标签
def hightest_peak(kde_dict):
    max_label = None
    max_density = -float('inf') 

    for label, kde in kde_dict.items():
        try:
            x_vals = np.linspace(kde.dataset.min(), kde.dataset.max(), 1000)
            y_vals = kde(x_vals)

            peak_density = y_vals.max()

            if peak_density > max_density:
                max_density = peak_density
                max_label = label
        except Exception as e:
            print(f"[ERROR] 处理 label {label} 时发生错误: {e}")

    return max_label, max_density

#计算核密度最大值的中值
def median_of_peak_densities(kde_dict):
    peak_densities = []
    for label, kde in kde_dict.items():
        try:
            x_vals = np.linspace(kde.dataset.min(), kde.dataset.max(), 1000)
            y_vals = kde(x_vals)
            peak_density = y_vals.max()
            peak_densities.append(peak_density)
        except Exception as e:
            print(f"[ERROR] 处理 label {label} 时发生错误: {e}")

    if peak_densities:
        median_density = np.median(peak_densities)
        return median_density
    else:
        print("[WARNING] 没有有效的核密度最大值")
        return None

#找到给定label的核密度最大值
def peak_density_for_label(kde_dict, label):
    kde = kde_dict[label]
    x_vals = np.linspace(kde.dataset.min(), kde.dataset.max(), 1000)
    y_vals = kde(x_vals)
    peak_idx = np.argmax(y_vals)
    peak_density = y_vals[peak_idx]
    peak_x = x_vals[peak_idx]
    return peak_density, peak_x

#比较两个标签的峰值
#返回峰值较大的标签
def compare_peak_x(kde_dict, idx1, idx2):
    x_vals1 = np.linspace(kde_dict[idx1].dataset.min(), kde_dict[idx1].dataset.max(), 1000)
    y_vals1 = kde_dict[idx1](x_vals1)
    peak_x1 = x_vals1[np.argmax(y_vals1)]

    x_vals2 = np.linspace(kde_dict[idx2].dataset.min(), kde_dict[idx2].dataset.max(), 1000)
    y_vals2 = kde_dict[idx2](x_vals2)
    peak_x2 = x_vals2[np.argmax(y_vals2)]

    return idx1 if peak_x1 > peak_x2 else idx2

def NF_answer(input):
    result = []
    if len(input)==0:
        result.append("No matching label.")
    else:
        for i in range(len(input)):
            result.append(f"{{{labels[input[i][0]]}}}'s peak at {{{round(input[i][1])}}}")
    return result

os.makedirs(output_dir, exist_ok=True)
for filename in os.listdir(input_dir):

    csv_path = os.path.join(input_dir, filename)
    print(f"\n[INFO] 正在处理文件: {filename}")
    print(csv_path)
    if not os.path.exists(csv_path):
        print(f"[ERROR] 文件不存在: {csv_path}")
        continue
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            lines = f.readlines()

        #类别名
        labels=pd.read_csv(csv_path, header=None, skiprows=1, nrows=1).iloc[0].tolist()
        #模式
        patterns=pd.read_csv(csv_path, header=None, skiprows=2,nrows=1).iloc[0].tolist()
        #核密度计算
        kde= precompute_kde(csv_path)
        #计算x范围
        x_min= pd.read_csv(csv_path, header=None, skiprows=3).iloc[:, 1].min()
        x_max= pd.read_csv(csv_path, header=None, skiprows=3).iloc[:, 1].max()
        #设置问题参数
        VPR_idx_lab_1=random.randint(0, len(labels)-1)
        VPR_idx_lab_2=random.randint(0, len(labels)-1)
        VPR_max_y,VPR_max_x=peak_density_for_label(kde,VPR_idx_lab_2)

        EVJ_highest_lab,EVJ_highest_y= hightest_peak(kde)
        EVJ_idx= round(random.uniform(x_min,x_max), 1)

        NF_limit_1 = random.randint(
            round(x_min + (x_max - x_min) / 4),
            round(x_min + (x_max - x_min) * 3 / 4)
        )
        NF_limit_2 = random.randint(
            round(x_min + (x_max - x_min) / 4),
            round(x_min + (x_max - x_min) * 3 / 4)
        )
        NF_answer_over=NF_answer(labels_peak_x_over_limit(kde,NF_limit_1))
        NF_answer_below=NF_answer(labels_peak_x_below_limit(kde,NF_limit_2))


        NC_idx_1=random.randint(0, len(labels)-1)
        NC_idx_2=random.randint(0, len(labels)-1)
        while NC_idx_1 == NC_idx_2:
            NC_idx_2=random.randint(0, len(labels)-1)
        NC_list=[]
        NC_num=random.randint(2, 4)
        for i in range(NC_num):
            NC_idx_label_1=random.randint(0, len(labels)-1)
            NC_idx_label_2=random.randint(0, len(labels)-1)
            while NC_idx_label_1 == NC_idx_label_2:
                NC_idx_label_2=random.randint(0, len(labels)-1)
            NC_greater=compare_peak_x(kde,NC_idx_label_1,NC_idx_label_2)
            NC_list.append(
                {
                "Q":f"Which one has a larger X value at the peak of its ridgeline: {labels[NC_idx_label_1]} or {labels[NC_idx_label_2]}?",
                 "A":f"{{{labels[NC_greater]}}} has a larger X value at the peak of its ridgeline."
                 }
                )
        
        
            

        qa_data = {
            "CTR": [
                {"Q": "What type of chart is this?", 
                 "A": "This chart is a {ridgeline}."}
            ],
            "VEC": [
                {"Q": "How many ridgelines are in this ridgeline chart?",
                 "A": f"There are {{{len(labels)}}} slices in this chart."}
            ],
            "SRP": [],
            "VPR": [
                {"Q": f"What distribution pattern does the ridgeline representing {labels[VPR_idx_lab_1]} show?",
                 "A": f"The ridgeline representing {labels[VPR_idx_lab_1]} shows a {{{patterns[VPR_idx_lab_1]}}}."},
                {"Q": f"At what value do  {labels[VPR_idx_lab_2]} reach its peaks?",
                 "A": f"At {{{round(VPR_max_x,2)}}}."}
            ],
            "VE": [
            ],
            "EVJ": [
                {"Q": "Which ridgeline has the highest peak",
                 "A": f"The ridgeline representing {{{labels[EVJ_highest_lab]}}} has the highest peak."},
                {"Q": f"Which label has the highest density at X ={(EVJ_idx)}?",
                 "A": f"At X ={EVJ_idx},the label with the highest density is {{{labels[label_with_highest_density(kde,EVJ_idx)]}}}"}
            ],
            "SC": [],
            "NF": [
                {"Q": f"Which countries in the ridgeline chart have ridgeline peaks exceed {NF_limit_1}? Please list the countries and corresponding peak values.",
                 "A": ",".join(NF_answer_over)},
                {"Q": f"Which countries in the ridgeline chart have ridgeline peaks below {NF_limit_2}? Please list the countries and corresponding peak values.",
                 "A": ",".join(NF_answer_below)}
            ],
            "NC": NC_list,
            "MSR": [
            ],
            "VA": [

            ]
        }

        json_name = os.path.splitext(filename)[0] + '.json'
        json_path = os.path.join(output_dir, json_name)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, indent=4, ensure_ascii=False)

        print(f"[SUCCESS] 生成QA JSON: {json_path}")

    except Exception as e:
        print(f"[EXCEPTION] 处理文件 {filename} 时发生错误: {e}")

    