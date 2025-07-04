# File: bubble_QA.py
# Description: Generates QA files for bubble chart data based on bubble.py CSV output and 气泡图QA整理.txt template.
from pathlib import Path

import pandas as pd
import os
import json
import numpy as np
from typing import Dict, Any, Tuple, List, Union, Optional
import re
import random # Import random for selections
from typing import List, Dict, Any, Tuple # Import typing hints
import math # Import math for isnan
from sklearn.neighbors import NearestNeighbors # Import for KNN density calculation

# --- Utility Functions (Adapted from scatter_QA.py and heatmap_QA.py) ---
def read_line_metadata(filepath: str) -> Dict[str, Any]:
    """
    读取折线图 CSV 的前三行元数据，返回结构示例：
    {
        'topic'        : 'Agriculture and Food Production',
        'little_theme' : 'Crop Yield',
        'y_info'       : {'unit': 'tons/hectare'},
        'x_info'       : {'name': 'Year', 'unit': ''},
        'series_names' : ['Golden Harvest Cooperative', 'Starfall Organics'],
        'series_trends': {               # 与 series_names 一一对应
            'Golden Harvest Cooperative': 'stable_falling',
            'Starfall Organics'         : 'periodic_stable'
        }
    }
    """
    try:
        import csv
        with open(filepath, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = [next(reader) for _ in range(3)]
        meta_df = pd.DataFrame(rows)    # 不同长度的行也能放进来

        if len(meta_df) < 3:
            print(f"[WARN] 元数据不足 3 行 → {filepath}")
            return {}

        # 第 1 行：大标题、小标题、Y 轴单位
        line1: List[Any] = meta_df.iloc[0].tolist()
        topic        = (line1[0] or "").strip() if len(line1) > 0 else ""
        little_theme = (line1[1] or "").strip() if len(line1) > 1 else ""
        y_unit       = (line1[2] or "").strip() if len(line1) > 2 else ""

        # 第 2 行：X 轴名称 + 各折线系列名称
        line2: List[Any] = meta_df.iloc[1].tolist()
        x_name       = (line2[0] or "").strip() if len(line2) > 0 else ""
        series_names = [str(c).strip() for c in line2[1:] if pd.notna(c)]

        # 第 3 行：趋势标签；第一个单元格通常是 "trend"
        line3: List[Any] = meta_df.iloc[2].tolist()
        trend_values = line3[1:] if len(line3) > 1 else []
        # 若趋势数量不足，用 None 补齐
        trend_values += [None] * (len(series_names) - len(trend_values))
        series_trends = dict(zip(series_names, [str(t).strip() if pd.notna(t) else None
                                                for t in trend_values]))

        # 组装输出字典
        meta: Dict[str, Any] = {
            "topic": topic,
            "little_theme": little_theme,
            "y_info": {"unit": y_unit},
            "x_info": {"name": x_name, "unit": ""},
            "series_names": series_names,
            "series_trends": series_trends,
        }
        return meta

    except Exception as e:
        print(f"[ERROR] 读取折线图元数据失败：{filepath} → {e}")
        return {}
def read_line_data_df(filepath: str, metadata: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    读取折线图 CSV 中真正的数据区（元数据 3 行之后），并返回 tidy 格式：
        series | x | y

    兼容两种常见排布：
      ① 列式  Year,SeriesA,SeriesB,...
      ② 行式  SeriesA,1990,1991,1992,...

    解析逻辑：
      - 跳过前 3 行
      - 尝试判断列式 / 行式
      - 统一转换为长表，列名固定为 ['series','x','y']
    """
    try:
        # ---------- 1. 读取原始数据 ----------
        raw = pd.read_csv(filepath, header=None, skiprows=3, encoding="utf-8")
        if raw.empty:
            print(f"[WARN] 文件无数据区 → {filepath}")
            return None

        # ---------- 2. 判断排布方式 ----------
        # 尝试把第一列整体转换成数字，若成功率较高 → 认为是“列式”
        first_col_numeric = pd.to_numeric(raw.iloc[:, 0], errors="coerce")
        col_layout = "column" if first_col_numeric.notna().sum() >= len(raw) * 0.8 else "row"

        if col_layout == "column":
            # ====== 3A. 列式处理 ======
            # 给 DataFrame 起列名：X 名称 + 系列列表
            x_name = metadata.get("x_info", {}).get("name", "X")
            series_names = metadata.get("series_names", [])
            # 若列数对不上，补足或截断
            col_names = [x_name] + series_names
            if len(col_names) < raw.shape[1]:
                col_names += [f"series_{i}" for i in range(len(col_names), raw.shape[1])]
            col_names = col_names[: raw.shape[1]]
            raw.columns = col_names

            # melt 成长表
            df_long = raw.melt(id_vars=[x_name], var_name="series", value_name="y")

            # 清洗数值列
            df_long["y"] = pd.to_numeric(df_long["y"], errors="coerce")
            df_long = df_long.dropna(subset=["y"])

            # 统一列名
            df_long = df_long.rename(columns={x_name: "x"})
            return df_long.reset_index(drop=True)

        else:
            # ====== 3B. 行式处理 ======
            # 第 1 行作为“x 轴表头”，其余行每行一个 series
            header = raw.iloc[0].tolist()
            x_vals = header[1:]                                    # e.g. 年份们
            rows = []
            for idx in range(1, len(raw)):
                row = raw.iloc[idx].tolist()
                series_name = str(row[0])
                y_vals = row[1:]
                # 补齐 / 截断
                y_vals += [None] * (len(x_vals) - len(y_vals))
                for x, y in zip(x_vals, y_vals):
                    rows.append({"series": series_name, "x": x, "y": y})

            df_long = pd.DataFrame(rows)
            df_long["x"] = pd.to_datetime(df_long["x"], errors="ignore")
            df_long["y"] = pd.to_numeric(df_long["y"], errors="coerce")
            df_long = df_long.dropna(subset=["y"])
            return df_long.reset_index(drop=True)

    except Exception as e:
        print(f"[ERROR] 读取折线图数据失败：{filepath} → {e}")
        return None


# --- Calculation Functions (Specific to Bubble Chart) ---
# These functions calculate the data needed for different QA types.

def task_count_points(df_long: pd.DataFrame, by_series: bool = False):
    """
    统计折线图的数据点数量。
    如果 by_series=True，返回 {series: count, ...}
    否则返回整数总数。
    """
    if df_long is None or df_long.empty:
        return 0 if not by_series else {}

    if by_series:
        return df_long.groupby("series").size().to_dict()
    return len(df_long)

def task_get_global_min_max(df_long: pd.DataFrame, by_series: bool = False) -> Dict[str, Any]:
    """
    计算 X、Y 的最小 / 最大值。
    - by_series=False（默认）：返回整体极值
        {'x_min': ..., 'x_max': ..., 'y_min': ..., 'y_max': ...}
    - by_series=True ：返回分系列极值
        {series1: {'x_min': ..., 'x_max': ..., 'y_min': ..., 'y_max': ...}, ...}
    """
    if df_long is None or df_long.empty:
        return {} if not by_series else {}

    def _calc(group):
        return {
            "x_min": group["x"].min(),
            "x_max": group["x"].max(),
            "y_min": group["y"].min(),
            "y_max": group["y"].max(),
        }

    if by_series:
        return df_long.groupby("series", group_keys=False).apply(_calc, include_groups=False).to_dict()


    return _calc(df_long)

def task_get_average_y(df_long: pd.DataFrame,
                       by_series: bool = False) -> Optional[Dict[str, float] | float]:
    """
    计算 y 值平均数。
    - df_long：必须是 ['series','x','y'] 三列的长表
    - by_series=False（默认）→ 返回整体平均（float）
    - by_series=True           → 返回 {series: avg, …}
    """
    if df_long is None or df_long.empty:
        return None if not by_series else {}

    if by_series:
        return df_long.groupby("series")["y"].mean().to_dict()

    return df_long["y"].mean()

def task_get_extreme_y_points(df_long: pd.DataFrame,
                              n: int = 1,
                              by_series: bool = True) -> List[Dict[str, Any]]:
    """
    找到 y 值最大的前 n 个点和最小的前 n 个点。
    返回列表，每个元素包含：series, type('largest'/'smallest'), x, y
    - by_series=True 时：在每条线内部各取 n 个最大 & n 个最小
    - by_series=False 时：在整体数据里取 n 个最大 & n 个最小
    """
    results: List[Dict[str, Any]] = []
    if df_long is None or df_long.empty:
        return results

    if by_series:
        grouped = df_long.groupby("series")
        for series_name, g in grouped:
            # 最小 n
            bottom = g.nsmallest(n, "y")
            for _, row in bottom.iterrows():
                results.append({"series": series_name,
                                "type": "smallest",
                                "x": row["x"], "y": row["y"]})
            # 最大 n
            top = g.nlargest(n, "y")
            for _, row in top.iterrows():
                results.append({"series": series_name,
                                "type": "largest",
                                "x": row["x"], "y": row["y"]})
    else:
        # 整体最小 n
        bottom = df_long.nsmallest(n, "y")
        for _, row in bottom.iterrows():
            results.append({"series": row["series"],
                            "type": "smallest",
                            "x": row["x"], "y": row["y"]})
        # 整体最大 n
        top = df_long.nlargest(n, "y")
        for _, row in top.iterrows():
            results.append({"series": row["series"],
                            "type": "largest",
                            "x": row["x"], "y": row["y"]})

    return results

def _pick_two_series(series_list: List[str]) -> Tuple[str, str]:
    """随机选取两个不同的主体"""
    if len(series_list) < 2:
        raise ValueError("主体数量不足 2 个，无法比较")
    return tuple(random.sample(series_list, 2))


def _random_interval(common_x_vals: pd.Series) -> Tuple[Any, Any]:
    """在共同的 X 值范围内随机选取一个非空区间（start < end）"""
    xs_sorted = np.sort(common_x_vals.unique())
    if len(xs_sorted) < 2:
        raise ValueError("共同的时间点不足 2 个，无法构造区间")
    start_idx, end_idx = sorted(random.sample(range(len(xs_sorted)), 2))
    return xs_sorted[start_idx], xs_sorted[end_idx]


def _compute_slope(df_sub: pd.DataFrame) -> float:
    """最简单的斜率：y 对 x 做一次线性拟合，返回系数。"""
    # 将 x 转成可运算的数字
    x_vals = pd.to_numeric(df_sub["x"], errors="coerce")
    mask = x_vals.notna() & df_sub["y"].notna()
    if mask.sum() < 2:
        return np.nan
    slope, _ = np.polyfit(x_vals[mask], df_sub.loc[mask, "y"], 1)
    return slope

def task_compare_subjects(df_long: pd.DataFrame,
                          metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    一次性完成 4 种比较：
      1. 同一年两个主体谁更大
      2. 随机区间内平均值谁更大
      3. 随机区间内斜率谁更大
      4. 一个主体两年对比（更大 / 更小 / 相等）
    返回统一字典，便于 fill_qa_* 调用。
    """
    results: Dict[str, Any] = {}

    # ---------- 基本健壮性检查 ----------
    if df_long is None or df_long.empty or len(df_long["series"].unique()) < 2:
        return results

    series_names = metadata.get("series_names") or df_long["series"].unique().tolist()
    s1, s2 = _pick_two_series(series_names)

    # 1️⃣ 两主体同一年比较 -----------------------------------------
    df_s1 = df_long[df_long["series"] == s1]
    df_s2 = df_long[df_long["series"] == s2]
    common_years = np.intersect1d(df_s1["x"], df_s2["x"])
    if common_years.size > 0:
        year_choice = random.choice(common_years.tolist())
        v1 = df_s1.loc[df_s1["x"] == year_choice, "y"].iloc[0]
        v2 = df_s2.loc[df_s2["x"] == year_choice, "y"].iloc[0]
        comparison = "equal" if v1 == v2 else (s1 if v1 > v2 else s2)
        results["same_year"] = {
            "series_pair": (s1, s2),
            "year": year_choice,
            "value_pair": {s1: v1, s2: v2},
            "larger": comparison
        }

    # 2️⃣ 区间平均值比较 ------------------------------------------
    try:
        start, end = _random_interval(common_years if common_years.size > 1
                                      else df_long["x"])
        mask_interval = (df_long["x"] >= start) & (df_long["x"] <= end)
        avg1 = df_long.loc[mask_interval & (df_long["series"] == s1), "y"].mean()
        avg2 = df_long.loc[mask_interval & (df_long["series"] == s2), "y"].mean()
        comparison = "equal" if avg1 == avg2 else (s1 if avg1 > avg2 else s2)
        results["interval_avg"] = {
            "series_pair": (s1, s2),
            "interval": (start, end),
            "avg_pair": {s1: avg1, s2: avg2},
            "larger": comparison
        }
    except Exception:
        pass  # 区间构造失败就跳过

    # 3️⃣ 区间斜率比较 -------------------------------------------
    try:
        slope1 = _compute_slope(df_long[mask_interval & (df_long["series"] == s1)])
        slope2 = _compute_slope(df_long[mask_interval & (df_long["series"] == s2)])
        comparison = "equal" if slope1 == slope2 else (s1 if slope1 > slope2 else s2)
        results["interval_slope"] = {
            "series_pair": (s1, s2),
            "interval": (start, end),
            "slope_pair": {s1: slope1, s2: slope2},
            "larger": comparison
        }
    except Exception:
        pass

    # 4️⃣ 单主体两年对比 ------------------------------------------
    subject = random.choice(series_names)
    df_sub = df_long[df_long["series"] == subject]
    years_sub = df_sub["x"].unique()
    if len(years_sub) >= 2:
        year1, year2 = sorted(random.sample(list(years_sub), 2))
        val1 = df_sub.loc[df_sub["x"] == year1, "y"].iloc[0]
        val2 = df_sub.loc[df_sub["x"] == year2, "y"].iloc[0]
        comparison = "equal" if val1 == val2 else ("larger" if val1 > val2 else "smaller")
        results["subject_year_compare"] = {
            "subject": subject,
            "year1": year1, "value1": val1,
            "year2": year2, "value2": val2,
            "comparison": comparison   # 对 year1 相对 year2
        }

    return results

def task_get_rate_of_change(df_long: pd.DataFrame,
                            by_series: bool = False
                            ) -> Optional[Dict[str, float] | float]:
    """
    计算首年 → 末年百分变化率 (%):
        (y_last - y_first) / y_first * 100
    - by_series=True  → {series: pct_change, …}
    - by_series=False → 整体变化率
    """
    if df_long is None or df_long.empty:
        return {} if by_series else None

    def _roc(df):
        first, last = df.sort_values("x").iloc[[0, -1]]["y"]
        return (last - first) / first * 100 if first != 0 else None

    if by_series:
        return (df_long.groupby("series")
                       .apply(_roc, include_groups=False)
                       .dropna()
                       .to_dict())
    return _roc(df_long)



# --- QA Filling Functions based on QA整理.txt ---
# These functions format the calculated data into the Q&A structure.
# Leave functions empty or return empty lists for QA types not specified in the text file
# or designated as placeholder.

def fill_qa_ctr() -> List[Dict[str, str]]:
    qa_list: List[Dict[str, str]] = []
    qa_list.append({
        "Q": "What type of chart is this?",
        "A": "This chart is a {stream chart}." # Corrected type and added {}
    })
    return qa_list


def fill_qa_vec(line_count: int) -> List[Dict[str, str]]:
    qa_list: List[Dict[str, str]] = []
    question = "How many streams are in this stream chart?"
    answer = f"There are {{{line_count}}} streams." # Added {}
    qa_list.append({"Q": question, "A": answer})

    return qa_list

def fill_qa_srp() -> List[Dict[str, str]]:
    """Generates QA for SRP (SVG related). Currently empty as per request."""
    # TODO: Implement QA generation for SRP (SVG related)
    return []

def _pretty_trend(label: str) -> str:
    """
    把 snake_case / camelCase 的趋势标签，转成人能读的短语：
      'stable_falling'  → 'stable falling'
      'periodicStable'  → 'periodic stable'
    """
    if not label:
        return ""
    if "_" in label:
        return label.replace("_", " ")
    # camelCase → 加空格并小写
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", label).lower()

def fill_qa_trend(metadata: Dict[str, Dict]) -> List[Dict[str, str]]:
    """
    根据 metadata['series_trends'] 生成两类 QA：
      ① 每条线自己的趋势问答
         Q: What is the trend of {series}'s {little_theme} levels?
         A: {series}'s ... levels show a {trend_phrase} trend.
      ② 给定某一种趋势，问“哪条线呈现这种趋势？”
         Q: Which line shows a {trend_phrase} trend in {little_theme} levels?
         A: {series}.
    """
    qa_list: List[Dict[str, str]] = []

    little_theme = metadata.get("little_theme", "")
    series_trends: Dict[str, str] = metadata.get("series_trends", {})

    # ------ ① 每个主体自身的趋势 ------
    for series, trend in series_trends.items():
        if not trend:
            continue
        trend_phrase = _pretty_trend(trend)
        q = f"What is the trend of {series}'s {little_theme} levels?"
        a = f"{series}'s {little_theme} levels show a {{{trend_phrase}}} trend."
        qa_list.append({"Q": q, "A": a})

    # ------ ② “哪条线是某趋势？” ------
    # 先把 trend → 列表[series] 的映射聚合
    trend_to_series: Dict[str, List[str]] = {}
    for series, trend in series_trends.items():
        if not trend:
            continue
        trend_to_series.setdefault(trend, []).append(series)

    for trend, s_list in trend_to_series.items():
        trend_phrase = _pretty_trend(trend)
        # 如果多条线同属一个趋势，可随机取 1 条，也可以全部列出。这里取首条
        chosen_series = s_list[0]
        q = f"Which {series}'s shows a {trend_phrase} trend?"
        a = f"{{{chosen_series}}}."
        qa_list.append({"Q": q, "A": a})

    # ------ ③ 持续主导时间最长的线 ------
    dominant_series = metadata.get("dominant_series_longest", "")
    if dominant_series:
        q = "Which stream has been dominant for the longest time period?"
        a = f"The stream that has been dominant for the longest time period is {dominant_series}."
        qa_list.append({"Q": q, "A": a})

    return qa_list

def fill_qa_ve_values(df_long: pd.DataFrame,
                      metadata: Dict[str, Any],
                      num_single: int = 3,
                      num_multi: int = 2) -> List[Dict[str, str]]:
    """
    生成 VE-类问答（Value Extraction）：

    ① 单主体：
       Q: What is {series}'s {little_theme} in {year}?
       A: {series}'s ... in {year} is {value} {unit}.

    ② 多主体（默认 3 条线）：
       Q: What are the {little_theme} of {series1}, {series2}, and {series3} in {year}?
       A: 列出三个数值。

    参数
    ----
    df_long    : tidy 格式 DataFrame（series | x | y）
    metadata   : read_line_metadata 返回的 dict
    num_single : 生成单主体问答数量上限
    num_multi  : 生成多主体问答数量上限
    """
    qa_list: List[Dict[str, str]] = []
    if df_long is None or df_long.empty:
        return qa_list

    little_theme = metadata.get("little_theme", "")
    unit         = metadata.get("y_info", {}).get("unit", "")

    # ---------- 预处理 ----------
    # 把 x 列统一成整数年份或字符串
    years = pd.to_datetime(df_long["x"], errors="coerce").dt.year.fillna(df_long["x"])
    df_long = df_long.assign(year=years)

    # ------------ ① 单主体 ----------------
    candidates = df_long.dropna(subset=["y"]).sample(frac=1)   # 打乱顺序
    taken = 0
    for _, row in candidates.iterrows():
        if taken >= num_single:
            break
        series = row["series"]
        year   = row["year"]
        value  = row["y"]
        q = f"What is {series}'s {little_theme} in {year}?"
        a = f"{series}'s {little_theme.lower()} in {year} is {{{value:.2f}}} {unit}."
        qa_list.append({"Q": q, "A": a})
        taken += 1

    # ------------ ② 多主体 ----------------
    # 找出“同一年至少有 3 个主体都有数值”的年份
    group = df_long.dropna(subset=["y"]).groupby("year")["series"].nunique()
    valid_years = group[group >= 3].index.tolist()
    random.shuffle(valid_years)

    taken = 0
    for yr in valid_years:
        if taken >= num_multi:
            break
        rows = df_long[(df_long["year"] == yr) & df_long["y"].notna()]
        sample_series = rows["series"].unique().tolist()[:3]   # 取前 3 个主体
        if len(sample_series) < 3:
            continue
        parts_q, parts_a = [], []
        for s in sample_series:
            val = rows.loc[rows["series"] == s, "y"].iloc[0]
            parts_q.append(s)
            parts_a.append(f"{{{s}}}'s {little_theme.lower()} is {{{val:.2f}}} {unit}")
        series_q = ", ".join(parts_q[:-1]) + f", and {parts_q[-1]}"
        series_a = ", ".join(parts_a[:-1]) + f", {parts_a[-1]}"
        q = f"What are the {little_theme.lower()} of {series_q} in {yr}?"
        a = series_a + "."
        qa_list.append({"Q": q, "A": a})
        taken += 1

    return qa_list

def fill_qa_ve(extreme_points_n1: List[Dict[str, Any]],
               metadata: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    根据 task_get_extreme_y_points(n=1, by_series=True) 的结果，
    为每条折线生成两类 QA：
      ① 最高值  Q: What is the highest {little_theme} level recorded for {series}?
      ② 最低值  Q: What is the lowest  {little_theme} level recorded for {series}?
    """
    qa_list: List[Dict[str, str]] = []
    if not extreme_points_n1:
        return qa_list

    little_theme = metadata.get("little_theme", "")
    y_unit       = metadata.get("y_info", {}).get("unit", "")

    # 先聚合出各 series 的最大 / 最小点
    series_extremes: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for item in extreme_points_n1:
        series = item.get("series")
        typ    = item.get("type")        # 'largest' / 'smallest'
        if series and typ in ("largest", "smallest"):
            series_extremes.setdefault(series, {})[typ] = item

    for series, ext_dict in series_extremes.items():
        # ---------- ① 最高 ----------
        if "largest" in ext_dict:
            pt = ext_dict["largest"]
            y_val = pt["y"]
            x_val = pt["x"]
            y_fmt = f"{y_val:.2f}" if isinstance(y_val, (float, int)) else y_val
            x_fmt = pd.to_datetime(x_val).year if isinstance(x_val, (pd.Timestamp, pd.DatetimeIndex)) else x_val

            q = f"What is the highest {little_theme} level recorded for {series}?"
            a = f"{series} reached approximately {{{y_fmt}}} {y_unit} in {x_fmt}."
            qa_list.append({"Q": q, "A": a})

        # ---------- ② 最低 ----------
        if "smallest" in ext_dict:
            pt = ext_dict["smallest"]
            y_val = pt["y"]
            x_val = pt["x"]
            y_fmt = f"{y_val:.2f}" if isinstance(y_val, (float, int)) else y_val
            x_fmt = pd.to_datetime(x_val).year if isinstance(x_val, (pd.Timestamp, pd.DatetimeIndex)) else x_val

            q = f"What is the lowest {little_theme} level recorded for {series}?"
            a = f"{series}'s lowest recorded level is approximately {{{y_fmt}}} {y_unit} in {x_fmt}."
            qa_list.append({"Q": q, "A": a})

    return qa_list

def fill_qa_evj(global_extremes: Dict[str, Any],
                metadata: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    根据 task_get_global_min_max(df_long) 的结果，生成：
      • 全局最小值 QA
      • 全局最大值 QA
    例：
      Q: What is the global minimum Crop Yield in the line chart?
      A: The global minimum crop yield is {2.45} tons/hectare.
    """
    qa_list: List[Dict[str, str]] = []
    little_theme = metadata.get("little_theme", "")
    y_unit       = metadata.get("y_info", {}).get("unit", "")

    # ---------- 全局最小 ----------
    if "y_min" in global_extremes:
        y_min = global_extremes["y_min"]
        y_min_fmt = f"{y_min:.2f}" if isinstance(y_min, (int, float)) else y_min
        q = f"What is the global minimum {little_theme} in the line chart?"
        a = f"The global minimum {little_theme.lower()} is {{{y_min_fmt}}} {y_unit}."
        qa_list.append({"Q": q, "A": a})

    # ---------- 全局最大 ----------
    if "y_max" in global_extremes:
        y_max = global_extremes["y_max"]
        y_max_fmt = f"{y_max:.2f}" if isinstance(y_max, (int, float)) else y_max
        q = f"What is the global maximum {little_theme} in the line chart?"
        a = f"The global maximum {little_theme.lower()} is {{{y_max_fmt}}} {y_unit}."
        qa_list.append({"Q": q, "A": a})

    return qa_list

def fill_qa_sc(average_y: Dict[str, float],
               rate_of_change: Dict[str, float],
               metadata: Dict[str, Any]) -> List[Dict[str, str]]:
    """
        折线图 SC（Statistical Comparison）问答：
          • 平均值 (AVG)
          • 首年→末年变化率 (ROC)
        参数
        ----
        average_y     : {series: avg_value, ...}
        rate_of_change: {series: pct_change (0-100), ...}
        metadata      : read_line_metadata() 生成的 dict
        """
    qa_list: List[Dict[str, str]] = []

    little_theme = metadata.get("little_theme", "")
    y_unit = metadata.get("y_info", {}).get("unit", "")

    # ---------- 平均值 ----------
    for series, avg in average_y.items():
        if avg is None:
            continue
        avg_fmt = f"{avg:.2f}"
        q = f"What is the average height of {series}'s {little_theme}?"
        a = f"The average height of {series}'s {little_theme} is {{{avg_fmt}}} {y_unit}."
        qa_list.append({"Q": q, "A": a})

    return qa_list

def _safe_year(val):
    """
    如果 val 本身就是 4 位年份（或可转为 4 位整数），直接返回；
    否则尝试用 pd.to_datetime 解析，失败就返回原值。
    """
    try:
        num = int(float(val))
        if 1000 <= num <= 3000:
            return num
    except Exception:
        pass
    ts = pd.to_datetime(str(val), errors="coerce", format="%Y")
    return ts.year if not pd.isna(ts) else val

def _ensure_year_col(df: pd.DataFrame) -> pd.Series:
    return df["x"].apply(_safe_year)

def _to_year(col):
    return pd.Series(col).apply(_safe_year)

def _pair_str(val: float, unit: str, year) -> str:
    """格式化 ‘300 million barrels in {2000} year’ 片段"""
    v_fmt = f"{val:.0f}" if val == int(val) else f"{val:.2f}"
    return f"{v_fmt} {unit} in {{{year}}} year"


def fill_qa_nf(df_long: pd.DataFrame,
               metadata: Dict[str, Any],
               seed: int | None = None) -> List[Dict[str, str]]:
    """
    生成 6 种数值筛选 QA：
      A) 单主体  > threshold
      B) 单主体  < threshold
      C) 单主体  between low & high
      D) 单年份  > threshold
      E) 单年份  < threshold
      F) 单年份  between low & high
    每类随机生成 1 题（若数据不足则跳过）。返回 [{'Q':..., 'A':...}, ...]
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    qa_list: List[Dict[str, str]] = []
    if df_long is None or df_long.empty:
        return qa_list

    little_theme = metadata.get("little_theme", "")
    unit = metadata.get("y_info", {}).get("unit", "")

    # 预处理：加 year 列
    df = df_long.copy()
    df["year"] = _ensure_year_col(df)
    df = df.dropna(subset=["y"])        # 确保 y 有值

    # ---------- A/B/C：按主体过滤 ----------
    series_names = df["series"].unique().tolist()
    if series_names:
        series = random.choice(series_names)
        df_s = df[df["series"] == series]

        if not df_s.empty:
            vals = df_s["y"]
            lo, hi = np.percentile(vals, [30, 70])  # 选两个分位数作阈值

            # A) >
            years_vals = df_s[df_s["y"] > hi][["year", "y"]].head(3).values
            if len(years_vals) >= 1:
                threshold = hi
                q = f"Which years did {series}'s {little_theme} exceed {threshold:.0f} {unit}? Please list the years and corresponding values."
                parts = [_pair_str(v, unit, y) for y, v in years_vals]
                a = ", ".join(parts) + "."
                qa_list.append({"Q": q, "A": a})

            # B) <
            years_vals = df_s[df_s["y"] < lo][["year", "y"]].head(3).values
            if len(years_vals) >= 1:
                threshold = lo
                q = f"Which years did {series}'s {little_theme} below {threshold:.0f} {unit}? Please list the years and corresponding values."
                parts = [_pair_str(v, unit, y) for y, v in years_vals]
                a = ", ".join(parts) + "."
                qa_list.append({"Q": q, "A": a})

            # C) between
            mid_low = (lo + hi) / 2 * 0.9
            mid_high = (lo + hi) / 2 * 1.1
            cond = (df_s["y"] >= mid_low) & (df_s["y"] <= mid_high)
            years_vals = df_s[cond][["year", "y"]].head(3).values
            if len(years_vals) >= 1:
                q = (f"Which years did {series}'s {little_theme} between "
                     f"{mid_low:.0f} and {mid_high:.0f} {unit}? Please list the years and corresponding values.")
                parts = [_pair_str(v, unit, y) for y, v in years_vals]
                a = ", ".join(parts) + "."
                qa_list.append({"Q": q, "A": a})

    # ---------- D/E/F：按年份过滤 ----------
    years_all = df["year"].unique().tolist()
    if years_all:
        year = random.choice(years_all)
        df_y = df[df["year"] == year]
        if not df_y.empty:
            vals = df_y["y"]
            lo, hi = np.percentile(vals, [30, 70])

            # > threshold
            over = df_y[df_y["y"] > hi][["series", "y"]].head(3).values
            if len(over) >= 1:
                q = (f"In the year {year}, which line had {little_theme} exceed {hi:.0f} {unit}? "
                     f"Please list the lines and corresponding values.")
                parts = [f"{{{s}}} had {v:.0f} {unit}" for s, v in over]
                a = ", ".join(parts) + "."
                qa_list.append({"Q": q, "A": a})

            # < threshold
            under = df_y[df_y["y"] < lo][["series", "y"]].head(3).values
            if len(under) >= 1:
                q = (f"In the year {year}, which lines had {little_theme} below {lo:.0f} {unit}? "
                     f"Please list the lines and corresponding values.")
                parts = [f"{{{s}}} had {v:.0f} {unit}" for s, v in under]
                a = ", ".join(parts) + "."
                qa_list.append({"Q": q, "A": a})

            # between
            mid_low = (lo + hi) / 2 * 0.9
            mid_high = (lo + hi) / 2 * 1.1
            between = df_y[(df_y["y"] >= mid_low) & (df_y["y"] <= mid_high)][["series", "y"]].head(3).values
            if len(between) >= 1:
                q = (f"In the year {year}, which lines had {little_theme} between "
                     f"{mid_low:.0f} and {mid_high:.0f} {unit}? Please list the lines and corresponding values.")
                parts = [f"{{{s}}} had {v:.0f} {unit}" for s, v in between]
                a = ", ".join(parts) + "."
                qa_list.append({"Q": q, "A": a})

    return qa_list

def _to_year(col):
    yr = pd.to_datetime(col, errors="coerce").dt.year
    return yr.where(yr.notna(), col)          # 解析失败就保留原字符串


def fill_qa_nc(df_long: pd.DataFrame,
               metadata: Dict[str, Any],
               seed: int | None = None) -> List[Dict[str, str]]:
    """
    生成 NC（Numerical Comparison）问答：
      • same-year higher/hottest (≥2 主体)
      • interval average higher
      • interval change (delta) larger
      • same subject two-year higher/lower
    返回 [{'Q':..., 'A':...}, ...]
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    qa_list: List[Dict[str, str]] = []
    if df_long is None or df_long.empty:
        return qa_list

    little_theme = metadata.get("little_theme", "")
    unit = metadata.get("y_info", {}).get("unit", "")

    # 预处理：加 year 列
    df = df_long.copy()
    df["year"] = _to_year(df["x"])
    df = df.dropna(subset=["y"])

    # -------- 1) 同一年比较 ---------------------------------
    years = df["year"].unique().tolist()
    if years:
        year = random.choice(years)
        rows_year = df[df["year"] == year]
        series_vals = rows_year.groupby("series")["y"].first()
        if len(series_vals) >= 2:
            k = min(len(series_vals), random.choice([2, 3, 4]))
            sampled = series_vals.sample(k, replace=False)
            winner = sampled.idxmax()
            series_list = sampled.index.tolist()

            if k == 2:
                s1, s2 = series_list
                q = (f"In {year}, which country had a higher {little_theme}, "
                     f"{s1} or {s2}?")
                a = f"In {year}, {{{winner}}} had a higher {little_theme.lower()}."
            else:
                others = ", ".join(series_list[:-1]) + f", or {series_list[-1]}"
                q = (f"In {year}, which country had the highest {little_theme}, "
                     f"{others}?")
                a = f"In {year}, {{{winner}}} had the highest {little_theme.lower()}."
            qa_list.append({"Q": q, "A": a})

    # -------- 2) 区间平均值比较 ------------------------------
    if len(years) >= 2:
        start, end = sorted(random.sample(years, 2))
        mask = (df["year"] >= start) & (df["year"] <= end)
        df_int = df[mask]
        means = df_int.groupby("series")["y"].mean()
        if len(means) >= 2:
            k = min(len(means), random.choice([2, 3, 4]))
            sampled = means.sample(k, replace=False)
            winner = sampled.idxmax()
            series_list = sampled.index.tolist()

            if k == 2:
                s1, s2 = series_list
                q = (f"Between {start} and {end}, which country had a higher average "
                     f"{little_theme}, {s1} or {s2}?")
                a = f"{{{winner}}} had a higher average {little_theme.lower()}."
            else:
                others = ", ".join(series_list[:-1]) + f", or {series_list[-1]}"
                q = (f"Between {start} and {end}, which country had the highest average "
                     f"{little_theme}, {others}?")
                a = f"{{{winner}}} had the highest average {little_theme.lower()}."
            qa_list.append({"Q": q, "A": a})

    # -------- 3) 区间变化幅度比较 ----------------------------
    if len(years) >= 2:
        start, end = sorted(random.sample(years, 2))
        df_start = df[df["year"] == start].set_index("series")["y"]
        df_end   = df[df["year"] == end].set_index("series")["y"]
        common_series = df_start.index.intersection(df_end.index)
        if len(common_series) >= 2:
            deltas = (df_end[common_series] - df_start[common_series]).abs()
            k = min(len(deltas), random.choice([2, 3, 4]))
            sampled = deltas.sample(k, replace=False)
            winner = sampled.idxmax()
            series_list = sampled.index.tolist()

            if k == 2:
                s1, s2 = series_list
                q = (f"Between {start} and {end}, which country experienced a larger "
                     f"change in {little_theme}, {s1} or {s2}?")
                a = f"{{{winner}}} experienced a larger change in {little_theme.lower()}."
            else:
                others = ", ".join(series_list[:-1]) + f", or {series_list[-1]}"
                q = (f"Between {start} and {end}, which country experienced the largest "
                     f"change in {little_theme}, {others}?")
                a = f"{{{winner}}} experienced the largest change in {little_theme.lower()}."
            qa_list.append({"Q": q, "A": a})

    # -------- 4) 单主体两年对比 ------------------------------
    series_names = df["series"].unique().tolist()
    if series_names:
        series = random.choice(series_names)
        df_s = df[df["series"] == series]
        yrs_s = df_s["year"].unique()
        if len(yrs_s) >= 2:
            y1, y2 = sorted(random.sample(list(yrs_s), 2))
            v1 = df_s.loc[df_s["year"] == y1, "y"].iloc[0]
            v2 = df_s.loc[df_s["year"] == y2, "y"].iloc[0]
            relation = "higher" if v1 > v2 else ("lower" if v1 < v2 else "the same")
            q = (f"Was {series}'s {little_theme} in {y1} higher or lower than in {y2}?")
            a = f"The {little_theme.lower()} in {y1} was {relation} than in {y2}."
            qa_list.append({"Q": q, "A": a})

    return qa_list


def fill_qa_msr() -> List[Dict[str, str]]:
    """Generates QA for MSR (SVG related). Currently empty as per request."""
    # TODO: Implement QA generation for MSR (SVG related)
    return []

def fill_qa_va() -> List[Dict[str, str]]:
    """Generates QA for VA (SVG related). Currently empty as per request."""
    # TODO: Implement QA generation for VA (SVG related)
    return []


# 写入json，使用新的模板初始化结构并合并现有数据 (Adapted from heatmap_QA.py)
def write_qa_to_json(csv_path: str, qa_type: str, qa_items: List[Dict[str, str]]):

    json_dir = 'QA'
    os.makedirs(json_dir, exist_ok=True)

    # Construct JSON file full path using the CSV base name
    # Take the basename and remove the .csv suffix
    base_name_with_suffix = os.path.basename(csv_path) # e.g., bubble_Topic_1.csv
    base_name = os.path.splitext(base_name_with_suffix)[0] # e.g., bubble_Topic_1

    # The JSON filename should be the same as the CSV base name
    json_path = os.path.join(json_dir, base_name + '.json')
    # --- END MODIFICATION FOR OUTPUT PATH ---


    # Define the complete template structure (Matching pasted_text_0.txt)
    template_data: Dict[str, List[Dict[str, str]]] = {
        "CTR": [], "VEC": [], "SRP": [], "VPR": [], "VE": [],
        "EVJ": [], "SC": [], "NF": [], "NC": [], "MSR": [], "VA": []
    }

    # Load existing data if file exists
    existing_data: Dict[str, List[Dict[str, str]]] = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            # Ensure loaded data is a dictionary, fallback if not
            if isinstance(loaded_data, dict):
                 existing_data = loaded_data
            else:
                 print(f"Warning: Existing JSON data in {json_path} is not a dictionary. Overwriting with template structure.")

        except (json.JSONDecodeError, FileNotFoundError):
            # File not found is handled by os.path.exists, but keeping it here as a safeguard
            print(f"Warning: Could not load or decode JSON from {json_path}. Starting with template structure.")
        except Exception as e:
             print(f"Warning: Could not read JSON from {json_path}: {e}. Starting with template structure.")


    # Merge existing data into the template structure
    # Start with the template, then copy over the lists from the existing data for any keys that exist and are lists
    data_to_save = template_data.copy() # Start with all keys from the template
    for key in template_data.keys():
         if key in existing_data and isinstance(existing_data[key], list):
             # Copy the existing list for this key
             data_to_save[key] = existing_data[key]


    # Append new QA items to the appropriate list in the merged data
    # Ensure the qa_type exists in the template (which it will now) and is a list
    if qa_type in data_to_save and isinstance(data_to_save[qa_type], list):
         # Avoid adding duplicate QAs if the script is run multiple times on the same CSV
         # This is a simple check - assumes Q and A together are unique within a type
         new_items_to_add = []
         # Create a set of existing Q/A tuples for quick lookup
         existing_qa_pairs = {(item.get('Q'), item.get('A')) for item in data_to_save[qa_type] if isinstance(item, dict) and 'Q' in item and 'A' in item}

         for item in qa_items:
              # Check if the item is a valid QA dictionary before trying to get Q and A
              if isinstance(item, dict) and 'Q' in item and 'A' in item:
                   if (item.get('Q'), item.get('A')) not in existing_qa_pairs:
                        new_items_to_add.append(item)
                        # Add to set to prevent duplicates within the new list and against existing ones
                        existing_qa_pairs.add((item.get('Q'), item.get('A')))
              else:
                   print(f"Warning: Skipping invalid QA item format for type {qa_type}: {item}")


         data_to_save[qa_type].extend(new_items_to_add)

    else:
         # This case should really not happen with the template initialization,
         # but as a safeguard, print a warning.
         print(f"Error: Attempted to write to invalid QA type '{qa_type}' in {json_path}. This type might be missing from the template.")


    # Write back to file
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        # print(f"Wrote QA to {json_path} under type {qa_type}") # Optional: confirmation print
    except Exception as e:
         print(f"Error writing QA to {json_path} for type {qa_type}: {e}")

def compute_all_tasks(df_long: pd.DataFrame,
                      meta: Dict[str, Any]) -> Dict[str, Any]:
    stats : Dict[str, Any] = {}

    stats["extreme_points_1"] = task_get_extreme_y_points(df_long, n=1, by_series=True)
    stats["extreme_points_3"] = task_get_extreme_y_points(df_long, n=3, by_series=True)

    # ① 数据点数量
    stats["point_counts_total"] = task_count_points(df_long)
    stats["point_counts_each"] = task_count_points(df_long, by_series=True)

    # ② 全局 / 分系列极值
    stats["global_extremes"] = task_get_global_min_max(df_long)
    stats["series_extremes"] = task_get_global_min_max(df_long, by_series=True)

    # ③ 平均值
    stats["avg_y_overall"] = task_get_average_y(df_long)
    stats["avg_y_each"] = task_get_average_y(df_long, by_series=True)

    # ④ 首年→末年变化率
    stats["roc_overall"] = task_get_rate_of_change(df_long)
    stats["roc_each"] = task_get_rate_of_change(df_long, by_series=True)

    # ⑤ 每条线的最高 / 最低点（n=1）
    stats["extreme_points"] = task_get_extreme_y_points(df_long, n=1, by_series=True)

    # ⑥ 随机比较（同年、区间平均、区间斜率、单线两年对比）
    stats["compare"] = task_compare_subjects(df_long, meta)

    return stats

def main():
    # todo 修改路径和任务类型
    csv_folder = './csv'

    # 检查 CSV 文件夹是否存在
    if not os.path.exists(csv_folder):
        print(f"错误：未找到 CSV 文件夹 {csv_folder}。请先运行 line.py 生成数据。")
        return

    for csv_path in Path(csv_folder).glob("*.csv"):
        print(f"\n正在处理文件：{csv_path} ...")

        # ---------- 读取 ----------
        meta = read_line_metadata(csv_path)
        df_long = read_line_data_df(csv_path, meta)

        if df_long is None or df_long.empty:
            print(f"跳过 {csv_path.name} —— 无有效数据")
            continue

        # ---------- 统计 ----------
        stats = compute_all_tasks(df_long, meta)
        avg_y_overall = stats["avg_y_overall"]  # compute_all_tasks 已经算好
        roc_overall = stats["roc_overall"]

        # ---------- 生成 QA ----------
        qa_ctr = fill_qa_ctr()  # 图表类型
        qa_vec = fill_qa_vec(len(meta["series_names"]))  # 线数
        qa_trd = fill_qa_trend(meta)  # 趋势（复用 VPR 键）
        qa_ve = fill_qa_ve(stats["extreme_points_1"], meta)  # 最高/最低
        qa_vev = fill_qa_ve_values(df_long, meta)  # 指定年份取值
        qa_evj = fill_qa_evj(stats["global_extremes"], meta)  # 全局极值
        qa_sc = fill_qa_sc(stats["avg_y_each"], stats["roc_each"], meta)  # 平均 / 增率
        qa_nf = fill_qa_nf(df_long, meta)  # 数值筛选
        qa_nc = fill_qa_nc(df_long, meta)  # 数值比较

        # ---------- 写入 JSON ----------
        write_qa_to_json(csv_path, "CTR", qa_ctr)
        write_qa_to_json(csv_path, "VEC", qa_vec)
        write_qa_to_json(csv_path, "VPR", qa_trd)  # 用 VPR 键存“趋势”
        write_qa_to_json(csv_path, "VE", qa_ve + qa_vev)  # 合并两类 VE
        write_qa_to_json(csv_path, "EVJ", qa_evj)
        write_qa_to_json(csv_path, "SC", qa_sc)
        write_qa_to_json(csv_path, "NF", qa_nf)
        write_qa_to_json(csv_path, "NC", qa_nc)

        # 占位（保持原键，避免前端报缺）
        write_qa_to_json(csv_path, "SRP", [])
        write_qa_to_json(csv_path, "MSR", [])
        write_qa_to_json(csv_path, "VA", [])

    print("\n折线图 QA 文件生成完毕。")

if __name__ == "__main__":
    main()
