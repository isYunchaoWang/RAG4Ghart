# File: stacked_area_QA.py # Renamed for clarity, but keeping original structure for modification
# Description: Generates QA files for stacked area chart data based on CSV output.
from pathlib import Path
import collections
import pandas as pd
import os
import json
import numpy as np
from typing import Dict, Any, Tuple, List, Union, Optional
import re
import random # Import random for selections
from typing import List, Dict, Any, Tuple # Import typing hints
import math # Import math for isnan
from sklearn.neighbors import NearestNeighbors # Import for KNN density calculation # Keep imports, even if not all are used in the final version

# --- Utility Functions (Adapted from scatter_QA.py and heatmap_QA.py) ---
# Keep metadata reading as is, it works for identifying series and overall info
def read_line_metadata(filepath: str) -> Dict[str, Any]:
    """
    读取折线图 CSV 的前三行元数据，返回结构示例：
    {
        'topic'        : 'Agriculture and Food Production',
        'little_theme' : 'Crop Yield',
        'y_info'       : {'unit': 'tons/hectare'},
        'x_info'       : {'name': 'Year', 'unit': ''},
        'series_names' : ['Golden Harvest Cooperative', 'Starfall Organics'],
        'series_trends': {               # 与 series_names 一一对应 - NOTE: Trends are ignored for stacked areas
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

        # 第 3 行：趋势标签；第一个单元格通常是 "trend" - Ignored for stacked area
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
            "series_trends": series_trends, # Keep in metadata, but ignore in QA generation
        }
        return meta

    except Exception as e:
        print(f"[ERROR] 读取元数据失败：{filepath} → {e}")
        return {}

# Keep data reading as is, tidy format is needed for aggregation
def read_line_data_df(filepath: str, metadata: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """
    读取 CSV 中真正的数据区（元数据 3 行之后），并返回 tidy 格式：
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

            def _parse_x(val):
                # 纯数字、介于 1000–3000 ⇒ 认为是年份
                try:
                    num = int(float(val))
                    if 1000 <= num <= 3000:
                        return num
                except Exception:
                    pass
                # 其它情况再尝试解析完整日期
                try:
                    return pd.to_datetime(val, format="%Y-%m-%d", errors="raise")
                except Exception:
                    try:
                        # 只有年份的字符串，如 "1990"
                        return pd.to_datetime(val, format="%Y", errors="raise")
                    except Exception:
                        return val  # 保底：原样返回

            df_long["x"] = df_long["x"].apply(_parse_x)
            df_long["y"] = pd.to_numeric(df_long["y"], errors="coerce")
            df_long = df_long.dropna(subset=["y"])
            return df_long.reset_index(drop=True)

    except Exception as e:
        print(f"[ERROR] 读取数据失败：{filepath} → {e}")
        return None


# --- Calculation Functions (Specific to Stacked Area Chart) ---

# New function to calculate the total value at each x point
def task_compute_total_value(df_long: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    计算每个 x 值对应的总 y 值 (堆叠面积图的总高度)。
    返回 DataFrame: ['x', 'total_y']
    """
    if df_long is None or df_long.empty:
        return None
    # Group by x and sum y, dropping NaN sums
    df_total = df_long.groupby("x")["y"].sum().reset_index()
    df_total = df_total.rename(columns={"y": "total_y"}).dropna(subset=["total_y"])
    return df_total

# New function to calculate total contribution per series
def task_compute_total_contribution_per_series(df_long: pd.DataFrame) -> Dict[str, float]:
    """
    计算每个 series 的总贡献 (所有 x 值的 y 之和)。
    返回 {series_name: total_contribution}
    """
    if df_long is None or df_long.empty:
        return {}
    # Group by series and sum y, dropping NaN sums
    contribution = df_long.groupby("series")["y"].sum().dropna()
    return contribution.to_dict()


# Keep task_count_points - gives total points and points per series
def task_count_points(df_long: pd.DataFrame, by_series: bool = False):
    """
    统计数据点数量。
    如果 by_series=True，返回 {series: count, ...}
    否则返回整数总数。
    """
    if df_long is None or df_long.empty:
        return 0 if not by_series else {}

    if by_series:
        return df_long.groupby("series").size().to_dict()
    return len(df_long)

# Modify task_get_global_min_max to work on total value or individual series
def task_get_global_min_max(df: pd.DataFrame, value_col: str = 'y', by_series: bool = False) -> Dict[str, Any]:
    """
    计算指定数值列的最小 / 最大值。
    - df: 输入 DataFrame (可以是 df_long 或 df_total)
    - value_col: 要计算极值的列名 ('y' 或 'total_y')
    - by_series=False（默认）：返回整体极值
        {'x_min': ..., 'x_max': ..., 'value_min': ..., 'value_max': ...}
    - by_series=True （仅用于 df_long）：返回分系列极值 (不再用于 EVJ in stacked area)
        {series1: {'x_min': ..., 'x_max': ..., 'y_min': ..., 'y_max': ...}, ...}
    """
    if df is None or df.empty or value_col not in df.columns:
        return {}

    def _calc(group):
        return {
            "x_min": group["x"].min(),
            "x_max": group["x"].max(),
            f"{value_col}_min": group[value_col].min(),
            f"{value_col}_max": group[value_col].max(),
        }

    if by_series and 'series' in df.columns:
        # Note: This path is kept but won't be used for EVJ in main for stacked area
        return df.groupby("series", group_keys=False).apply(lambda g: _calc(g.rename(columns={value_col: 'y'})), include_groups=False).to_dict()

    # Overall calculation
    return _calc(df)


# Modify task_get_average_y to work on total value or individual series
def task_get_average_y(df: pd.DataFrame,
                       value_col: str = 'y',
                       by_series: bool = False) -> Optional[Dict[str, float] | float]:
    """
    计算指定数值列平均数。
    - df：输入 DataFrame (可以是 df_long 或 df_total)
    - value_col: 要计算平均值的列名 ('y' 或 'total_y')
    - by_series=False（默认）→ 返回整体平均（float）
    - by_series=True           → 返回 {series: avg, …} (仅用于 df_long)
    """
    if df is None or df.empty or value_col not in df.columns:
        return None if not by_series else {}

    if by_series and 'series' in df.columns:
        return df.groupby("series")[value_col].mean().dropna().to_dict()

    # Overall average
    return df[value_col].mean()


# task_get_extreme_y_points is used by fill_qa_ve, which we keep for individual points.
# It's also used by fill_qa_evj in the line chart version, but we'll remove that call for stacked area EVJ.
def task_get_extreme_y_points(df_long: pd.DataFrame,
                              n: int = 1,
                              by_series: bool = True) -> List[Dict[str, Any]]:
    """
    找到 y 值最大的前 n 个点和最小的前 n 个点。
    返回列表，每个元素包含：series, type('largest'/'smallest'), x, y
    - by_series=True 时：在每条线内部各取 n 个最大 & n 个最小 (Used for VE)
    - by_series=False 时：在整体数据里取 n 个最大 & n 个最小 (Not used currently)
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
        # Overall min/max points - Not used in current stacked area QA
        pass

    return results

# task_get_rate_of_change is not used for individual series in SC anymore,
# and overall ROC on total value is not explicitly requested. Keep for completeness but won't be used.
def task_get_rate_of_change(df: pd.DataFrame,
                            value_col: str = 'y',
                            by_series: bool = False
                            ) -> Optional[Dict[str, float] | float]:
    """
    计算首个有效点 → 末个有效点百分变化率 (%):
        (y_last - y_first) / y_first * 100
    - df: Input DataFrame (df_long or df_total)
    - value_col: Column to calculate ROC on ('y' or 'total_y')
    - by_series=True  → {series: pct_change, …} (Only for df_long)
    - by_series=False → Overall change rate (on df_long or df_total)
    """
    if df is None or df.empty or value_col not in df.columns:
        return {} if by_series else None

    def _roc(df_subset):
        # Sort by x, drop NaNs in the value column
        sorted_df = df_subset.sort_values("x").dropna(subset=[value_col])
        if len(sorted_df) < 2:
            return np.nan
        first = sorted_df.iloc[0][value_col]
        last = sorted_df.iloc[-1][value_col]
        return (last - first) / first * 100 if first != 0 else np.nan

    if by_series and 'series' in df.columns:
        return (df.groupby("series")
                       .apply(_roc, value_col=value_col, include_groups=False) # Pass value_col
                       .dropna()
                       .to_dict())

    # Overall ROC (on df_long or df_total)
    return _roc(df)


# --- QA Filling Functions based on QA整理.txt ---

def fill_qa_ctr() -> List[Dict[str, str]]:
    qa_list: List[Dict[str, str]] = []
    # Modified chart type
    qa_list.append({
        "Q": "What type of chart is this?",
        "A": "This chart is a {area chart}." # Changed type
    })
    return qa_list


def fill_qa_vec(series_count: int) -> List[Dict[str, str]]:
    qa_list: List[Dict[str, str]] = []
    # Modified wording from lines to series
    question = "How many series are represented in this stacked area chart?"
    answer = f"There are {{{series_count}}} series." # Added {} and changed wording
    qa_list.append({"Q": question, "A": answer})
    return qa_list

def fill_qa_srp() -> List[Dict[str, str]]:
    """Generates QA for SRP (SVG related). Currently empty as per request."""
    return []

# New function for VPR (Contribution)
def fill_qa_vpr_contribution(series_total_contribution: Dict[str, float],
                             metadata: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    根据每个 series 的总贡献，生成：
      • 贡献最大的 series QA
      • 贡献最小的 series QA
    例：
    Q: Which country contributes the largest portion to total area in this area chart?
    A: The country with the largest area is {China}.
    Q: Which country contributes the smallest portion to total area in this area chart?
    A: The country with the smallest area is {China}.
    """
    qa_list: List[Dict[str, str]] = []
    if not series_total_contribution:
        return qa_list

    little_theme = metadata.get("little_theme", "") # Use little_theme in answer? Or just series name? The example uses series name.

    # Find series with max and min total contribution
    max_series = max(series_total_contribution, key=series_total_contribution.get)
    min_series = min(series_total_contribution, key=series_total_contribution.get)

    # Ensure max and min are not the same if there's more than one series
    if len(series_total_contribution) > 1 and max_series == min_series:
         # This can happen if all contributions are zero or NaN, or only one series exists,
         # although the check len() > 1 should prevent the latter. If all are same/zero, skip.
         pass
    else:
        # Largest contribution
        q_max = f"Which series contributes the largest portion to the total {little_theme.lower()}?"
        a_max = f"The series with the largest contribution is {{{max_series}}}."
        qa_list.append({"Q": q_max, "A": a_max})

        # Smallest contribution (only add if different from max, or if only one series)
        if max_series != min_series or len(series_total_contribution) == 1:
            q_min = f"Which series contributes the smallest portion to the total {little_theme.lower()}?"
            a_min = f"The series with the smallest contribution is {{{min_series}}}."
            qa_list.append({"Q": q_min, "A": a_min})

    return qa_list


# Keep fill_qa_ve_values for individual point lookups
def fill_qa_ve_values(df_long: pd.DataFrame,
                      metadata: Dict[str, Any],
                      num_single: int = 3,
                      num_multi: int = 1) -> List[Dict[str, str]]:
    """
    生成 VE-类问答（Value Extraction）：关于单个 series 在某个时间点的数值。

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
    df = df_long.copy()
    df["year"] = _to_year(df["x"])
    df = df.dropna(subset=["y"])        # 确保 y 有值

    # ------------ ① 单主体 ----------------
    # Sample points randomly across all series and years
    candidates = df.sample(frac=1).reset_index(drop=True) # 打乱顺序
    taken = 0
    # Keep track of (series, year) pairs already used for single questions
    used_single_points = set()

    for _, row in candidates.iterrows():
        if taken >= num_single:
            break
        series = row["series"]
        year   = row["year"]
        # Ensure we don't ask about the exact same point multiple times in single questions
        if (series, year) in used_single_points:
            continue
        used_single_points.add((series, year))

        value  = row["y"]
        # Format value: use .0f if it's an integer, otherwise .2f
        value_fmt = f"{value:.0f}" if value == int(value) else f"{value:.2f}"
        year_fmt = _safe_year(year) # Use safe year formatting

        q = f"What is {series}'s {little_theme} in {year_fmt}?"
        a = f"{series}'s {little_theme.lower()} in {year_fmt} is {{{value_fmt}}} {unit}."
        qa_list.append({"Q": q, "A": a})
        taken += 1

    # ------------ ② 多主体 ----------------
    # Find years where at least 3 series have data
    group = df.groupby("year")["series"].nunique()
    valid_years_for_multi = group[group >= 3].index.tolist()
    random.shuffle(valid_years_for_multi)

    taken = 0
    # Keep track of years already used for multi questions
    used_multi_years = set()

    for yr in valid_years_for_multi:
        if taken >= num_multi:
            break
        # Ensure we don't ask about the exact same year multiple times in multi questions
        if yr in used_multi_years:
            continue
        used_multi_years.add(yr)

        rows_year = df[(df["year"] == yr) & df["y"].notna()]
        # Get series names with data in this year and sample 3 randomly
        available_series = rows_year["series"].unique().tolist()
        if len(available_series) < 3:
             continue # Should not happen due to valid_years_for_multi filter, but safeguard

        sample_series = random.sample(available_series, 3) # Randomly sample 3 series

        parts_q, parts_a = [], []
        for s in sample_series:
            val = rows_year.loc[rows_year["series"] == s, "y"].iloc[0]
            # Format value: use .0f if it's an integer, otherwise .2f
            val_fmt = f"{val:.0f}" if val == int(val) else f"{val:.2f}"
            parts_q.append(s)
            parts_a.append(f"{s}'s {little_theme.lower()} is {{{val_fmt}}} {unit}")

        year_fmt = _safe_year(yr) # Use safe year formatting
        series_q = ", ".join(parts_q[:-1]) + (f", and {parts_q[-1]}" if len(parts_q) > 1 else parts_q[0])
        series_a = ", ".join(parts_a) # No 'and' needed in answer list

        q = f"What are the {little_theme.lower()} of {series_q} in {year_fmt}?"
        a = series_a + "."
        qa_list.append({"Q": q, "A": a})
        taken += 1

    return qa_list


# Modify fill_qa_evj to use total extremes only
def fill_qa_evj(total_extremes: Dict[str, Any],
                metadata: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    根据 task_get_global_min_max(df_total) 的结果，生成：
      • 全局最小值 QA (基于总值)
      • 全局最大值 QA (基于总值)
    例：
      Q: What is the global minimum total Crop Yield in the stacked area chart?
      A: The global minimum total crop yield is {2.45} tons/hectare.
    """
    qa_list: List[Dict[str, str]] = []
    little_theme = metadata.get("little_theme", "")
    y_unit       = metadata.get("y_info", {}).get("unit", "")

    # ---------- 全局最小 (基于总值) ----------
    # Use 'total_y_min' key from task_get_global_min_max(df_total)
    if "total_y_min" in total_extremes and pd.notna(total_extremes["total_y_min"]):
        y_min = total_extremes["total_y_min"]
        y_min_fmt = f"{y_min:.2f}" if isinstance(y_min, (int, float)) else y_min
        q = f"What is the global minimum total {little_theme} in the stacked area chart?"
        a = f"The global minimum total {little_theme.lower()} is {{{y_min_fmt}}} {y_unit}."
        qa_list.append({"Q": q, "A": a})

    # ---------- 全局最大 (基于总值) ----------
    # Use 'total_y_max' key from task_get_global_min_max(df_total)
    if "total_y_max" in total_extremes and pd.notna(total_extremes["total_y_max"]):
        y_max = total_extremes["total_y_max"]
        y_max_fmt = f"{y_max:.2f}" if isinstance(y_max, (int, float)) else y_max
        q = f"What is the global maximum total {little_theme} in the stacked area chart?"
        a = f"The global maximum total {little_theme.lower()} is {{{y_max_fmt}}} {y_unit}."
        qa_list.append({"Q": q, "A": a})

    # Per-series extremes are removed from EVJ for stacked area

    return qa_list

# fill_series_extremes is no longer needed as per-series extremes are removed from EVJ.
# def fill_series_extremes(...): pass # Remove or comment out

# Modify fill_qa_sc for stacked area (average height of specific series)
def fill_qa_sc(avg_each_series: Dict[str, float] | None,
               metadata: Dict[str, Any],
               max_q: int = 4) -> List[Dict[str, str]]:
    """
    为每条 series 生成【平均值 (平均高度)】问答。
    然后截断，只返回前 max_q 个 QA（默认 4 个）。
    """
    qa_list: List[Dict[str, str]] = []
    y_unit = metadata.get("y_info", {}).get("unit", "")
    little_theme = metadata.get("little_theme", "")

    if not avg_each_series:
        return qa_list

    # Get series names with average data, shuffle for randomness
    available_series = list(avg_each_series.keys())
    random.shuffle(available_series)

    for name in available_series:
        # ---- ① 平均值 (Average Height) ----
        if pd.notna(avg_each_series[name]):
            avg_fmt = f"{avg_each_series[name]:.2f}"
            # Question wording changed to reflect "average height" or "average value" of the series
            q_avg = f"What is the average height of {name}'s {little_theme} area?" # Or "average value"? Let's use "average height" to fit the visual.
            a_avg = f"The average height of {name}'s {little_theme.lower()} area is {{{avg_fmt}}} {y_unit}."
            qa_list.append({"Q": q_avg, "A": a_avg})

        # Stop if we have enough questions
        if len(qa_list) >= max_q:
            break

    # Ensure we don't exceed max_q
    return qa_list[:max_q]


# Utility functions for year/date handling
def _safe_year(val):
    """
    如果 val 本身就是 4 位年份（或可转为 4 位整数），直接返回；
    否则尝试用 pd.to_datetime 解析，失败就返回原值。
    """
    if pd.isna(val): return val
    try:
        # Check for integer year representation (e.g., 2000, 2000.0)
        num = int(float(val))
        if 1000 <= num <= 3000:
            return num
    except (ValueError, TypeError):
        pass # Not a simple number

    # Try parsing as a datetime
    ts = pd.to_datetime(str(val), errors="coerce")
    if pd.notna(ts):
        # Return year if it's a valid date/year
        return ts.year
    else:
        # Fallback: return original value if parsing fails
        return val

def _to_year(col):
    # Ensure this function handles potential non-numeric or non-date values gracefully
    return pd.Series(col).apply(_safe_year)

# Modify _pair_str for NF/NC questions based on total value
def _pair_str_total(val: float, unit: str, year) -> str:
    """格式化 ‘total value is 300 million barrels in {2000} year’ 片段"""
    year_fmt = _safe_year(year)

    # Format value: use .0f if it's an integer, otherwise .2f
    v_fmt = f"{val:.0f}" if val == int(val) else f"{val:.2f}"

    return f"total value was {{{v_fmt}}} {unit} in {{{year_fmt}}}"


# Modify fill_qa_nf to only ask about total value
def fill_qa_nf_total(df_total: pd.DataFrame,
                     metadata: Dict[str, Any],
                     seed: int | None = None,
                     max_q: int = 4) -> List[Dict[str, str]]:
    """
    生成数值筛选 QA，仅对【堆叠起来的总值】提问。
    随机选取年份，避免重复。
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    qa_set: "collections.OrderedDict[str, Dict[str,str]]" = collections.OrderedDict() # Use OrderedDict to store unique QAs
    if df_total is None or df_total.empty or len(df_total) < 2:
        return []

    little_theme = metadata.get("little_theme", "")
    unit = metadata.get("y_info", {}).get("unit", "")

    # Use the df_total DataFrame directly
    df = df_total.copy()
    df["year"] = _to_year(df["x"])
    df = df.dropna(subset=["total_y"]) # Ensure total_y has value

    years_all = df["year"].unique().tolist()

    # Define possible question types (all based on total value over years)
    q_types = ['total_gt', 'total_lt', 'total_between']

    tries = 0
    # Try to generate up to max_q unique questions
    while len(qa_set) < max_q and tries < 30: # Limit tries
        tries += 1
        # Randomly pick a type for THIS question attempt
        q_type = random.choice(q_types)

        try:
            # Need years with total data
            if not years_all: continue
            # Calculate thresholds based on total values
            vals = df["total_y"]
            if len(vals) < 2: continue # Need at least 2 points for percentiles
            lo, hi = np.percentile(vals, [30, 70])
            mid_low = (lo + hi) / 2 * 0.95 # Adjust interval slightly
            mid_high = (lo + hi) / 2 * 1.05

            if q_type == 'total_gt' and hi < vals.max(): # Ensure threshold is meaningful (not above max)
                threshold = hi
                # Find years and total values exceeding threshold
                results_df = df[df["total_y"] > threshold]
                if not results_df.empty:
                     # Sample up to 3 results randomly
                     years_vals = results_df[["year", "total_y"]].sample(min(3, len(results_df))).values
                     q = f"Which years did the total {little_theme} exceed {threshold:.0f} {unit}? Please list the years and corresponding total values."
                     parts = [_pair_str_total(v, unit, y) for y, v in years_vals]
                     a = ", ".join(parts) + "."
                     # Add to set to ensure uniqueness
                     qa_set.setdefault(q, {"Q": q, "A": a})

            elif q_type == 'total_lt' and lo > vals.min(): # Ensure threshold is meaningful (not below min)
                 threshold = lo
                 # Find years and total values below threshold
                 results_df = df[df["total_y"] < threshold]
                 if not results_df.empty:
                     # Sample up to 3 results randomly
                     years_vals = results_df[["year", "total_y"]].sample(min(3, len(results_df))).values
                     q = f"Which years did the total {little_theme} go below {threshold:.0f} {unit}? Please list the years and corresponding total values."
                     parts = [_pair_str_total(v, unit, y) for y, v in years_vals]
                     a = ", ".join(parts) + "."
                     qa_set.setdefault(q, {"Q": q, "A": a})

            elif q_type == 'total_between' and mid_low < mid_high: # Ensure interval is valid
                 # Find years and total values within interval
                 cond = (df["total_y"] >= mid_low) & (df["total_y"] <= mid_high)
                 results_df = df[cond]
                 if not results_df.empty:
                     # Sample up to 3 results randomly
                     years_vals = results_df[["year", "total_y"]].sample(min(3, len(results_df))).values
                     q = (f"Which years did the total {little_theme} fall between "
                          f"{mid_low:.0f} and {mid_high:.0f} {unit}? Please list the years and corresponding total values.")
                     parts = [_pair_str_total(v, unit, y) for y, v in years_vals]
                     a = ", ".join(parts) + "."
                     qa_set.setdefault(q, {"Q": q, "A": a})

        except Exception as e:
            # Catch potential errors during sampling or percentile calculation on small datasets
            # print(f"Warning: Could not generate NF question of type {q_type} (try {tries}): {e}") # Uncomment for debugging
            continue # Try generating another question

    return list(qa_set.values())


# Modify fill_qa_nc to only compare total value over time
def fill_qa_nc_total(df_total: pd.DataFrame,
                   metadata: Dict[str, Any],
                   seed: int | None = None,
                   max_q: int = 4) -> List[Dict[str, str]]:
    """
    生成 NC（Numerical Comparison）问答，仅对【堆叠起来的总值】提问。
    比较总值在不同年份或区间的差异。
    """
    if df_total is None or df_total.empty or len(df_total) < 2:
        return []

    if seed is not None:
        random.seed(seed); np.random.seed(seed)

    qa_set: "collections.OrderedDict[str, Dict[str,str]]" = collections.OrderedDict() # Use OrderedDict for unique QAs
    little_theme = metadata.get("little_theme", "")
    # unit = metadata.get("y_info", {}).get("unit", "") # Unit is not typically in NC answers

    # Use df_total directly
    df = df_total.copy()
    df["year"] = _to_year(df["x"])
    df = df.dropna(subset=["total_y"])

    years_all = df["year"].unique().tolist()
    # Need at least 2 years for comparison
    if len(years_all) < 2:
        return []

    # Define possible comparison types for the TOTAL value
    comparison_types = ['total_year_compare', 'total_interval_avg_compare', 'total_interval_change_compare']

    tries = 0
    # Try to generate up to max_q unique questions
    while len(qa_set) < max_q and tries < 30: # Limit tries
        tries += 1
        # Randomly pick a comparison type for THIS question attempt
        comp_type = random.choice(comparison_types)

        try:
            if comp_type == 'total_year_compare':
                # Sample 2 distinct years
                y1, y2 = sorted(random.sample(years_all, 2))
                v1 = df[df["year"] == y1]["total_y"].iloc[0]
                v2 = df[df["year"] == y2]["total_y"].iloc[0]

                if pd.isna(v1) or pd.isna(v2): continue

                rel = "higher" if v1 > v2 else ("lower" if v1 < v2 else "the same")
                q = (f"Was the total {little_theme} in {y1} higher or lower than in "
                     f"{y2}?")
                a = (f"The total {little_theme.lower()} in {{{y1}}} was {{{rel}}} than in {{{y2}}}." ) # Added {} around years and rel
                # Use setdefault to avoid duplicates based on the question string
                qa_set.setdefault(q, {"Q": q, "A": a})

            elif comp_type == 'total_interval_avg_compare':
                 # Sample 2 distinct intervals
                 if len(years_all) < 4: continue # Need at least 4 years to get 2 distinct intervals of size >= 2
                 # Get all possible start/end year pairs
                 year_pairs = [(years_all[i], years_all[j]) for i in range(len(years_all)) for j in range(i + 1, len(years_all))]
                 if len(year_pairs) < 2: continue # Need at least 2 intervals
                 # Sample two distinct intervals
                 (s1, e1), (s2, e2) = random.sample(year_pairs, 2)

                 mask1 = (df["year"] >= s1) & (df["year"] <= e1)
                 mask2 = (df["year"] >= s2) & (df["year"] <= e2)

                 avg1 = df[mask1]["total_y"].mean()
                 avg2 = df[mask2]["total_y"].mean()

                 if pd.isna(avg1) or pd.isna(avg2): continue

                 rel = "higher" if avg1 > avg2 else ("lower" if avg1 < avg2 else "about the same")
                 q = (f"Between {s1} and {e1}, was the average total {little_theme} higher or lower "
                      f"than between {s2} and {e2}?")
                 a = (f"The average total {little_theme.lower()} between {{{s1}}} and {{{e1}}} was "
                      f"{{{rel}}} than between {{{s2}}} and {{{e2}}}." ) # Added {}

                 qa_set.setdefault(q, {"Q": q, "A": a})

            elif comp_type == 'total_interval_change_compare':
                 # Sample 2 distinct intervals to compare change in total value
                 if len(years_all) < 4: continue # Need at least 4 years
                 year_pairs = [(years_all[i], years_all[j]) for i in range(len(years_all)) for j in range(i + 1, len(years_all))]
                 if len(year_pairs) < 2: continue # Need at least 2 intervals
                 # Sample two distinct intervals
                 (s1, e1), (s2, e2) = random.sample(year_pairs, 2)

                 # Get start and end values for each interval
                 v_s1 = df[df["year"] == s1]["total_y"].iloc[0] if s1 in df["year"].values else np.nan
                 v_e1 = df[df["year"] == e1]["total_y"].iloc[0] if e1 in df["year"].values else np.nan
                 v_s2 = df[df["year"] == s2]["total_y"].iloc[0] if s2 in df["year"].values else np.nan
                 v_e2 = df[df["year"] == e2]["total_y"].iloc[0] if e2 in df["year"].values else np.nan

                 if pd.isna(v_s1) or pd.isna(v_e1) or pd.isna(v_s2) or pd.isna(v_e2): continue

                 change1 = abs(v_e1 - v_s1)
                 change2 = abs(v_e2 - v_s2)

                 if change1 == change2:
                     rel = "about the same"
                 else:
                     rel = "larger" if change1 > change2 else "smaller"

                 q = (f"Between {s1} and {e1}, did the total {little_theme} experience a larger or smaller change "
                      f"than between {s2} and {e2}?")
                 a = (f"The change in total {little_theme.lower()} between {{{s1}}} and {{{e1}}} was "
                      f"{{{rel}}} than between {{{s2}}} and {{{e2}}}." ) # Added {}

                 qa_set.setdefault(q, {"Q": q, "A": a})


        except Exception as e:
            # Catch potential errors during sampling or calculations
            # print(f"Warning: Could not generate NC question of type {comp_type} (try {tries}): {e}") # Uncomment for debugging
            continue # Try generating another question

    return list(qa_set.values())


def fill_qa_msr() -> List[Dict[str, str]]:
    """Generates QA for MSR (SVG related). Currently empty as per request."""
    return []

def fill_qa_va() -> List[Dict[str, str]]:
    """Generates QA for VA (SVG related). Currently empty as per request."""
    return []


# Keep write_qa_to_json as is, it handles the file structure and merging correctly
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

    if df_long is None or df_long.empty:
        return stats

    # Calculate the total value at each x point
    df_total = task_compute_total_value(df_long)
    stats["df_total"] = df_total # Store total data for NF/NC

    # ① 数据点数量 (for individual series)
    stats["point_counts_total"] = task_count_points(df_long)
    stats["point_counts_each"] = task_count_points(df_long, by_series=True)

    # ② 全局极值 (based on total value)
    stats["total_extremes"] = task_get_global_min_max(df_total, value_col='total_y')
    # Per-series extremes are not used for EVJ in stacked area

    # ③ 平均值 (per series, for SC)
    stats["avg_y_each"] = task_get_average_y(df_long, by_series=True)
    # Overall average is not used for QA currently

    # ④ 首年→末年变化率 (not used for QA currently)
    # stats["roc_overall"] = task_get_rate_of_change(df_total, value_col='total_y') # ROC on total
    # stats["roc_each"] = task_get_rate_of_change(df_long, by_series=True) # ROC per series

    # ⑤ 每条线的最高 / 最低点（n=1） (Used by fill_qa_ve)
    stats["extreme_points_1_series"] = task_get_extreme_y_points(df_long, n=1, by_series=True) # Renamed key for clarity

    # ⑥ 总贡献度 (Per series, for VPR)
    stats["series_total_contribution"] = task_compute_total_contribution_per_series(df_long)

    return stats

def main():
    # todo 修改路径和任务类型
    csv_folder = './csv'

    # 检查 CSV 文件夹是否存在
    if not os.path.exists(csv_folder):
        print(f"错误：未找到 CSV 文件夹 {csv_folder}。请先运行生成数据的脚本。") # Adjusted message
        return

    # Identify the target chart type (used in CTR QA)
    chart_type_name = "stacked area chart"

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

        # Get required data from stats
        df_total = stats.get("df_total")
        total_extremes = stats.get("total_extremes", {})
        avg_y_each = stats.get("avg_y_each")
        series_total_contribution = stats.get("series_total_contribution", {})
        # extreme_points_1_series is used by fill_qa_ve but it's called internally there.

        # ---------- 生成 QA ----------
        # CTR: Chart Type
        qa_ctr = fill_qa_ctr() # This function now hardcodes "stacked area chart"

        # VEC: Series Count
        # Use the count from metadata for consistency, though stats also has it
        series_count = len(meta.get("series_names", []))
        qa_vec = fill_qa_vec(series_count)

        # VPR: Contribution (replaces trend)
        qa_vpr = fill_qa_vpr_contribution(series_total_contribution, meta)

        # VE: Value Extraction (individual points)
        # fill_qa_ve_values works on df_long
        qa_ve = fill_qa_ve_values(df_long, meta, num_single=3, num_multi=1) # Generate 3 single + 1 multi VE questions

        # EVJ: Extremes (global total only)
        # fill_qa_evj now uses total_extremes
        qa_evj = fill_qa_evj(total_extremes, meta) # No series extremes added here

        # SC: Statistical Comparison (average height per series)
        # fill_qa_sc now uses avg_y_each and updated wording
        qa_sc = fill_qa_sc(avg_y_each, meta, max_q=4) # Take up to 4 SC questions

        # NF: Numerical Filtering (total value only)
        # fill_qa_nf_total works on df_total
        qa_nf = fill_qa_nf_total(df_total, meta, max_q=4) # Generate up to 4 random NF questions on total

        # NC: Numerical Comparison (total value over time)
        # fill_qa_nc_total works on df_total
        qa_nc = fill_qa_nc_total(df_total, meta, max_q=4) # Generate up to 4 random NC questions on total


        # ---------- 写入 JSON ----------
        write_qa_to_json(csv_path, "CTR", qa_ctr)
        write_qa_to_json(csv_path, "VEC", qa_vec)
        write_qa_to_json(csv_path, "VPR", qa_vpr)  # Use VPR key for contribution
        write_qa_to_json(csv_path, "VE", qa_ve)
        write_qa_to_json(csv_path, "EVJ", qa_evj)
        write_qa_to_json(csv_path, "SC", qa_sc)
        write_qa_to_json(csv_path, "NF", qa_nf)
        write_qa_to_json(csv_path, "NC", qa_nc)

        # 占位（保持原键，避免前端报缺）
        write_qa_to_json(csv_path, "SRP", [])
        write_qa_to_json(csv_path, "MSR", [])
        write_qa_to_json(csv_path, "VA", [])

    print(f"\n{chart_type_name.capitalize()} QA 文件生成完毕。")

if __name__ == "__main__":
    main()
