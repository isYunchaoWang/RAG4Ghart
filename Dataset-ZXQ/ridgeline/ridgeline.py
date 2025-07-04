import numpy as np
import pandas as pd
from faker import Faker
import random
import os

def generate_ridgeline_data(num_points, num_categories, value_range):
    min_value, max_value = value_range 
    data = {}
    patterns = []
    
    pattern_options = [
        "Single Peak Distribution",
        "Periodic fluctuation",
        "Random fluctuation"
    ]
    
    for i in range(num_categories):
        selected_pattern = random.choice(pattern_options)
        patterns.append(selected_pattern)
        
        if selected_pattern == "Single Peak Distribution": 
            # 更尖锐的单峰分布（减小标准差）
            x = np.linspace(-3, 3, num_points)
            y = np.exp(-(x**2)/0.5)  # 减小分母使峰值更尖锐
            # 添加一些随机波动使曲线更自然
            y += 0.05 * np.random.randn(num_points)
            
        elif selected_pattern == "Periodic fluctuation": 
            # 更明显的周期性波动（增加振幅和频率范围）
            freq = random.uniform(1.0, 3.0)  # 提高频率范围
            amplitude = random.uniform(0.8, 1.5)  # 增加振幅变化
            y = amplitude * np.sin(np.linspace(0, 4 * np.pi, num_points) * freq)  # 增加周期数
            # 添加适量噪声
            y += 0.1 * np.random.randn(num_points)
            
        elif selected_pattern == "Random fluctuation":  
            # 更明显的随机游走（增加步长）
            y = np.cumsum(0.5 * np.random.randn(num_points))  # 增大随机步长
            # 添加一些趋势项
            trend = np.linspace(0, random.uniform(-1, 1), num_points)
            y += trend
        
        y_min, y_max = y.min(), y.max()
        y_scaled = (y - y_min) / (y_max - y_min) * (max_value - min_value) + min_value
        data[f"Category_{i+1}"] = y_scaled
    
    return pd.DataFrame(data), patterns

def main(num_datasets, num_points):
    save_path = "csv/ridgeline_chart"
    os.makedirs(save_path, exist_ok=True)
    
    for t in range(num_datasets):
        #################################################################################### 生成数据变量部分
        #主题  内容名(小主题)  数据范围  单位  labels
        theme="Social Media and Digital Media and Streaming"
        name="Social Media Usage Time"
        value_range= [0, 10]
        unit="hours/day"
        category_names =["ClipVibe", "SnapFrame", "FaceLink", "Chirper", "ProfConnect", "GhostPic", "ViewTube"]
        #######################################################################################################

        num_categories = random.randint(3, 7)
        category_name = random.sample(category_names, num_categories) 
        
        df, patterns = generate_ridgeline_data(num_points, num_categories, value_range)

        for i in range(num_categories):
            df = df.rename(columns={f"Category_{i+1}": category_name[i]})
        
        # 添加模式信息作为最后一行
        pattern_row = pd.DataFrame([patterns], columns=category_name)
        df = pd.concat([ pattern_row,df], ignore_index=True)
        
        csv_path = os.path.join(save_path, f"ridgeline_{name}_{t+1}.csv")
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(f"{theme},{name},{unit}\n")
            df.to_csv(f, index=False)

        print(f"Data saved to: {csv_path}")

if __name__ == "__main__":
    main(num_points=50, num_datasets=1)