import os
import csv
import random
import numpy as np

try:
    from data import THEME_METRIC_PARAMS
except ImportError:
    print("Error: data.py not found or THEME_METRIC_PARAMS not defined in data.py.")
    exit()
except NameError:
    print("Error: THEME_METRIC_PARAMS dictionary not found within data.py.")
    exit()

TREND_TYPES = {
    "stable_rising":
        {"slope_pct": 0.05,  "noise_sd": 1.0},  # 5 %/年,
    "stable_falling":
        {"slope_pct": 0.03,  "noise_sd": 1.0},  # 3 %/年
    "exponential_rising":
        {"factor": 1.10, "noise_sd": 1.0},  # 10 %复合
    "exponential_falling":
        {"factor": 0.90, "noise_sd": 1.0},  # -10 %复合
    "periodic_stable":
        {"ampl_pct": 0.25,   "noise_sd": 0.5, "period": 5},  # 振幅=25 %
    "volatile_rising":
        {"slope_pct": 0.08,  "noise_sd": 1.5},  # 8 %/年 + 大噪声
    "volatile_falling":
        {"slope_pct": 0.06,  "noise_sd": 1.5},  # −6%/year ± noise
}

def generate_stable_rising(years, params):
    base = params['base']
    p = TREND_TYPES["stable_rising"]
    slope = base * p["slope_pct"]  # 每年固定增幅
    return [max(0.01 * base, base + slope * (y - years[0]) + base * params.get('noise', 0) * np.random.normal(0, p["noise_sd"])) for y in years]

def generate_stable_falling(years, params):
    base = params['base']
    p = TREND_TYPES["stable_falling"]
    slope = base * p["slope_pct"]  # 每年固定减幅
    return [max(0.01 * base, base + slope * (y - years[0]) - base * params.get('noise', 0) * np.random.normal(0, p["noise_sd"])) for y in years]

def generate_exponential_rising(years, params):
    base = params['base']
    p = TREND_TYPES["exponential_rising"]
    factor = p["factor"]
    noise_sd = p["noise_sd"]
    start_year = years[0]
    return [
        max(0.01 * base, base * (factor ** (year - start_year)) +
        base * params.get('noise', 0) * np.random.normal(0, noise_sd))
        for year in years
    ]

def generate_exponential_falling(years, params):
    base = params['base']
    p = TREND_TYPES["exponential_falling"]
    factor = p["factor"]
    noise_sd = p["noise_sd"]
    start_year = years[0]
    return [
        max(0.01 * base, base * (factor ** (year - start_year)) -
        base * params.get('noise', 0) * np.random.normal(0, noise_sd))
        for year in years
    ]

def generate_periodic_stable(years, params):
    base = params['base']
    p = TREND_TYPES["periodic_stable"]
    amplitude = params.get('amplitude', base * p["ampl_pct"])
    period = params.get('period', p["period"])
    noise_sd = p["noise_sd"]
    start_year = years[0]
    return [
        max(0.01 * base, base + amplitude * np.sin(2 * np.pi * (year - start_year) / period) +
        base * params.get('noise', 0) * np.random.normal(0, noise_sd))
        for year in years
    ]

def generate_volatile_rising(years, params):
    base = params['base']
    p = TREND_TYPES["volatile_rising"]
    slope = base * p["slope_pct"]
    noise_sd = p["noise_sd"]
    start_year = years[0]
    return [
        max(0.01 * base, base + slope * (year - start_year) +
        base * params.get('noise', 0) * np.random.normal(0, noise_sd))
        for year in years
    ]

def generate_volatile_falling(years, params):
    base = params['base']
    p = TREND_TYPES["volatile_falling"]
    slope = -base * p["slope_pct"]
    noise_sd = p["noise_sd"]
    start_year = years[0]
    return [
        max(0.01 * base, base + slope * (year - start_year) -
        base * params.get('noise', 0) * np.random.normal(0, noise_sd))
        for year in years
    ]



def generate_data(years, params, trend_type):
    generators = {
        "stable_rising": generate_stable_rising,
        "stable_falling": generate_stable_falling,
        "exponential_rising": generate_exponential_rising,
        "exponential_falling": generate_exponential_falling,
        "periodic_stable": generate_periodic_stable,
        "volatile_rising": generate_volatile_rising,
        "volatile_falling": generate_volatile_falling
    }
    return generators[trend_type](years, params)


# 创建输出目录
os.makedirs('csv', exist_ok=True)

# 遍历每个主题和指标
for theme, metrics in THEME_METRIC_PARAMS.items():
    for metric_idx, metric in enumerate(metrics, 1):
        # 提取指标参数
        metric_name = metric['name']
        unit = metric['unit']
        subjects = metric['subject']
        params = metric['params']

        # 随机选择1-7个subject
        k = random.randint(1, min(7, len(subjects)))
        selected_subjects = random.sample(subjects, k)

        # 生成趋势类型（允许重复）
        trends = random.choices(list(TREND_TYPES.keys()), k=k)

        # 生成年份数据（随机3-30个连续年份）
        num_years = random.randint(3, 30)
        start_year = random.randint(1950, 2025 - num_years)
        years = list(range(start_year, start_year + num_years))

        # 生成每个subject的数据
        all_data = []
        for trend in trends:
            values = generate_data(years, params, trend)
            # 根据单位类型处理数据
            if unit == '%':
                values = [max(0, min(100, v)) for v in values]  # 限制在0-100%
            elif unit == 'ratio':
                values = [max(0, v) for v in values]  # 比率不能为负
            all_data.append([round(v, 2) for v in values])

        # 转置数据为按年排列
        data_by_year = list(zip(*all_data))

        # 构建文件名
        theme_slug = theme.lower().replace(' ', '_')
        filename = f'csv/area_{theme_slug}_{metric_idx}.csv'

        # 写入CSV文件
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            # 第一行：主题，指标，单位
            writer.writerow([theme, metric_name, unit])
            # 第二行：年份头
            writer.writerow(['Year'] + selected_subjects)
            # 第三行：趋势类型
            writer.writerow(['trend'] + trends)
            # 数据行
            for year, values in zip(years, data_by_year):
                writer.writerow([year] + list(values))