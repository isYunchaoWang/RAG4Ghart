      
import os
import pandas as pd
import json
from io import StringIO
from scipy.stats import gaussian_kde
import numpy as np
import random

input_dir = 'csv/parallel_coordinates'
output_dir = 'QA'


def max_by_dim(data,index):
    max_num=0
    for i in range(0,len(data)):
        max_num=max(max_num,data[i][index])
    return max_num

def max_by_lab(data,index):
    max_num=0
    for i in range(0,len(data[0])):
        max_num=max(max_num,data[index][i])
    return max_num

def min_by_dim(data,index):
    min_num=data[0][index]
    for i in range(1,len(data)):
        min_num=min(min_num,data[i][index])
    return min_num

def min_by_lab(data,index):
    min_num=data[index][0]
    for i in range(1,len(data[0])):
        min_num=min(min_num,data[index][i])
    return min_num

def average_by_dim(data,index):
    sum=0
    for i in range(0,len(data)):
        sum=sum+data[i][index]
    return sum/len(data)

def top_n_values_by_dim(data, index, num):
    if not data or index < 0 or index >= len(data[0]):
        raise ValueError("输入数据无效或索引超出范围")
    
    sorted_data = sorted(data, key=lambda x: x[index], reverse=True)
    return [row[index] for row in sorted_data[:num]]

def bottom_n_values_by_dim(data,index,num):
    if not data or index < 0 or index >= len(data[0]):
        raise ValueError("输入数据无效或索引超出范围")
    
    sorted_data = sorted(data, key=lambda x: x[index], reverse=False)
    return [row[index] for row in sorted_data[:num]]

def max_variance_column(data):
    arr = np.array(data, dtype=float)
    variances = np.var(arr, axis=0)
    max_idx = np.argmax(variances)
    max_var = variances[max_idx]
    return max_idx, max_var

def compare_two_rows_by_col(data, col_idx, row_idx1, row_idx2):
    if data[row_idx1][col_idx] >= data[row_idx2][col_idx]:
        return row_idx1
    else:
        return row_idx2
    
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
        
        #维度名
        dimensions=pd.read_csv(csv_path, header=None, skiprows=1, nrows=1).iloc[0,1:].tolist()
        #模式名
        patterns=pd.read_csv(csv_path, header=None, skiprows=2, nrows=1).iloc[0,1:].tolist()
        #类别名
        labels=pd.read_csv(csv_path, header=None, skiprows=3,usecols=[0]).iloc[:,0].tolist()
        #数据
        data=pd.read_csv(csv_path, header=None, skiprows=3).iloc[:, 1:].values.tolist()
        #
        VPR_idx_dim_1=random.randint(0,len(dimensions)-2)
        VPR_highest_variability_dim,VPR_num=max_variance_column(data)

        VE_list = []
        VE_num=random.randint(1,3)
        for i in range(VE_num):
            VE_idx_lab=random.randint(0,len(labels)-1)
            VE_idx_dim=random.randint(0,len(dimensions)-1)
            VE_list.append({
                "Q": f"What is the value of {labels[VE_idx_lab]} on the {dimensions[VE_idx_dim]} dimension in the parallel-coordinates chart?",
                "A": f"The value of {labels[VE_idx_lab]} on the {dimensions[VE_idx_dim]} dimension is {{{data[VE_idx_lab][VE_idx_dim]}}}"
            })

        EVJ_idx_lab_1=random.randint(0,len(labels)-1)
        EVJ_idx_lab_2=random.randint(0,len(labels)-1)

        SC_idx_dim_1=random.randint(0,len(dimensions)-1)
        SC_idx_dim_2=random.randint(0,len(dimensions)-1)
        SC_dx_lab_1=random.randint(0,len(labels)-1)
        SC_dx_lab_2=random.randint(0,len(labels)-1)
        while SC_dx_lab_1==SC_dx_lab_2:
            SC_dx_lab_2=random.randint(0,len(labels)-1)

        NF_idx_dim_1=random.randint(0,len(dimensions)-1)
        NF_idx_dim_2=random.randint(0,len(dimensions)-1)


        NC_num=random.randint(2,4)
        NC_list = []
        for i in range(NC_num):
            NC_idx_lab_1=random.randint(0,len(labels)-1)
            NC_idx_lab_2=random.randint(0,len(labels)-1)
            while NC_idx_lab_1==NC_idx_lab_2:
                NC_idx_lab_2=random.randint(0,len(labels)-1)
            NC_idx_dim_1=random.randint(0,len(dimensions)-1)
            NC_idx_lab_3=compare_two_rows_by_col(data,NC_idx_dim_1,NC_idx_lab_1,NC_idx_lab_2)
            NC_list.append({
                "Q": f"On {dimensions[NC_idx_dim_1]}, which label has a higher score: {labels[NC_idx_lab_1]} or {labels[NC_idx_lab_2]}?",
                "A": f"{{{labels[NC_idx_lab_3]}}} has a higher score on {dimensions[NC_idx_dim_1]}."
            })

        qa_data = {
            "CTR": [
                {"Q": "What type of chart is this?", 
                 "A": "This chart is a {Parallel Chart}."}
            ],
            "VEC": [
                {"Q": "How many lines are in this parallel-coordinates chart",
                 "A": f"There are {{{len(labels)}}} lines."},
                {"Q": f"How many dimensions are in this parallel-coordinates chart?",
                "A": f"There are {{{len(dimensions)}}} dimensions."},
            ],
            "SRP": [],
            "VPR": [

                {"Q": f"Which dimension has the highest variability in the parallel-coordinates chart?",
                 "A": f" {{{dimensions[VPR_highest_variability_dim]}}} shows the highest variability."},

                {"Q": f"What kind of correlation exists between {dimensions[VPR_idx_dim_1]} and dimension {dimensions[VPR_idx_dim_1+1]}",
                 "A": f"There is {{{patterns[VPR_idx_dim_1]}}} between {dimensions[VPR_idx_dim_1]} and {dimensions[VPR_idx_dim_1+1]}."},
            ],
            "VE": VE_list,
            "EVJ": [
                {"Q": f"What is the maximum value of label {labels[EVJ_idx_lab_1]} across all dimensions in the parallel-coordinates chart?",
                 "A": f"The maximum value of {labels[EVJ_idx_lab_1]} across all dimensions is {{{max_by_lab(data,EVJ_idx_lab_1)}}}"},
                {"Q": f"What is the minimum value of label {labels[EVJ_idx_lab_2]} across all dimensions in the parallel-coordinates chart?",
                 "A": f"The minimum value of {labels[EVJ_idx_lab_2]} across all dimensions is {{{min_by_lab(data,EVJ_idx_lab_2)}}}."},
            ],
            "SC": [
                {"Q": f"What is the average value of {dimensions[SC_idx_dim_1]}?",
                 "A": f"The average value of {dimensions[SC_idx_dim_1]} is {{{round(average_by_dim(data,SC_idx_dim_1),2)}}}"},
                {"Q": f"What is the difference in coding {dimensions[SC_idx_dim_2]} between label {labels[SC_dx_lab_1]} and label {labels[SC_dx_lab_2]}",
                 "A": f"The difference in coding {dimensions[SC_idx_dim_2]} between {labels[SC_dx_lab_1]} and {labels[SC_dx_lab_2]} is {{{round(abs(data[SC_dx_lab_1][SC_idx_dim_2]-data[SC_dx_lab_2][SC_idx_dim_2]),2)}}}."}
            ],
            "NF": [
                {"Q": f"What are the top 3 values for {dimensions[NF_idx_dim_1]} dimension in the parallel coordinates?",
                 "A": f"{{{top_n_values_by_dim(data,NF_idx_dim_1,3)}}}"},
                {"Q": f"What are the bottom 3 values for {dimensions[NF_idx_dim_2]} dimension in the parallel coordinates?",
                 "A": f"{{{bottom_n_values_by_dim(data,NF_idx_dim_2,3)}}}"},
            ],
            "NC": NC_list,
            "MSR": [],
            "VA": []
        }

        json_name = os.path.splitext(filename)[0] + '.json'
        json_path = os.path.join(output_dir, json_name)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, indent=4, ensure_ascii=False)

        print(f"[SUCCESS] 生成QA JSON: {json_path}")

    except Exception as e:
        print(f"[EXCEPTION] 处理文件 {filename} 时发生错误: {e}")

    