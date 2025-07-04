# File 2: scatter_QA.py (Adjusted output directory to ./scatter/QA)
import pandas as pd
import os
import json
import numpy as np # Import numpy for calculations
import re # Import re for parsing units from axis labels
from typing import List, Dict # Import List and Dict for type hinting

# todo:根据你的csv里首行有的信息进行修改
# 读取文件的第一行，依次返回大标题、子标题、单位、模式
# 修改为读取 scatter.py 生成的 CSV 的第一行
# Expected format: topic,little_theme,trend,correlation_type
def read_metadata(filepath: str) -> dict:
    """
    Reads the first header line of the scatter CSV.
    Returns a dictionary with keys: 'topic', 'little_theme', 'trend', 'correlation_type'.
    """
    # header=None 表示不把任何行当成列名，nrows=1 只读第一行
    try:
        meta_df = pd.read_csv(filepath, header=None, nrows=1, encoding='utf-8')
        if meta_df.empty:
             # print(f"Warning: Metadata line missing in {filepath}") # Keep original print style minimal
             return {}
        meta = meta_df.iloc[0].tolist()
        # Ensure we have enough elements, handle potential missing values gracefully
        keys = ['topic', 'little_theme', 'trend', 'correlation_type']
        # Use zip and slice to handle cases where there might be fewer than expected columns
        return dict(zip(keys, (meta + [None]*(len(keys)-len(meta)))[:len(keys)]))

    except Exception as e:
        print(f"Error reading metadata from {filepath}: {e}")
        return {}

# todo:根据你的csv里首行有的信息进行修改
# 读取文件的第二行，依次返回 x 轴标签和 y 轴标签
# 修改为读取 scatter.py 生成的 CSV 的第二行，包含单位
# Expected format: x_label (x_unit),y_label (y_unit)
def read_axis_labels(filepath: str) -> tuple[str, str, str, str]:
    """
    Reads the second header line of the scatter CSV and parses axis labels and units.
    Returns: x_label, x_unit, y_label, y_unit
    """
    x_label, x_unit, y_label, y_unit = "", "", "", ""
    # skiprows=1 跳过第一行，nrows=1 只读第二行
    try:
        labels_df = pd.read_csv(filepath, header=None, skiprows=1, nrows=1, encoding='utf-8')
        if labels_df.empty:
            # print(f"Warning: Axis labels line missing in {filepath}") # Keep original print style minimal
            return x_label, x_unit, y_label, y_unit

        labels = labels_df.iloc[0].tolist()

        # Function to parse "Label (Unit)" string
        def parse_label_unit(label_str):
            if isinstance(label_str, str): # Ensure it's a string before using regex
                 match = re.match(r'(.+)\s*\((.+)\)', label_str)
                 if match:
                     return match.group(1).strip(), match.group(2).strip()
                 return label_str.strip(), "" # Return label and empty unit if parsing fails or no parentheses
            return str(label_str).strip(), "" # Handle non-string data just in case

        if len(labels) >= 1:
             x_label, x_unit = parse_label_unit(labels[0])
        if len(labels) >= 2:
             y_label, y_unit = parse_label_unit(labels[1])
        else:
             # print(f"Warning: Axis labels line in {filepath} has unexpected format or missing y-label: {labels}") # Keep original print style minimal
             pass # Just pass silently if format is off, return empty strings

    except Exception as e:
        print(f"Error reading axis labels from {filepath}: {e}")

    return x_label, x_unit, y_label, y_unit

# --- Calculation Functions ---
# These functions calculate the data needed for different QA types.

def task_count_points(df: pd.DataFrame) -> int:
    """Calculates the number of data points (rows) in the DataFrame."""
    # Count rows after dropping any row with NaN in the relevant columns (first two for scatter)
    return len(df.iloc[:, [0, 1]].dropna())

def task_get_correlation_value(df: pd.DataFrame) -> float | None:
    """
    Calculates the Pearson correlation coefficient between the first two data columns.
    Returns the correlation value or None if calculation is not possible.
    """
    # Select the first two columns and drop rows with NaNs
    data_subset = df.iloc[:, [0, 1]].dropna()

    if len(data_subset) < 2:
         return None # Not enough valid data points

    # Check for variance before calculating correlation
    if data_subset.iloc[:, 0].nunique() > 1 and data_subset.iloc[:, 1].nunique() > 1:
        try:
            correlation = data_subset.iloc[:, 0].corr(data_subset.iloc[:, 1])
            return correlation
        except Exception:
             return None # Handle potential calc errors
    else:
        return None # Correlation is undefined if one variable is constant

def task_get_min_max(df: pd.DataFrame) -> Dict[str, float]:
    """Calculates min and max values for the first two data columns (X and Y)."""
    results = {}
    data_subset = df.iloc[:, [0, 1]].dropna() # Use .dropna() specific to these columns

    if not data_subset.empty:
        # Ensure columns exist before trying to access them
        if 0 in data_subset.columns:
             results['x_min'] = data_subset.iloc[:, 0].min()
             results['x_max'] = data_subset.iloc[:, 0].max()
        if 1 in data_subset.columns:
             results['y_min'] = data_subset.iloc[:, 1].min()
             results['y_max'] = data_subset.iloc[:, 1].max()
    return results

def task_get_averages(df: pd.DataFrame) -> Dict[str, float]:
    """Calculates average values for the first two data columns (X and Y)."""
    results = {}
    data_subset = df.iloc[:, [0, 1]].dropna() # Use .dropna() specific to these columns

    if not data_subset.empty:
        # Use .mean() which handles empty Series gracefully by returning NaN
        # Ensure columns exist before trying to access them
        if 0 in data_subset.columns:
             results['x_avg'] = data_subset.iloc[:, 0].mean()
        if 1 in data_subset.columns:
             results['y_avg'] = data_subset.iloc[:, 1].mean()

    return results

def task_get_extreme_points(df: pd.DataFrame, n: int = 3) -> Dict[str, List[float]]:
    """
    Finds the Y values for the top/bottom N X values and X values for the top/bottom N Y values.
    Returns a dictionary of lists.
    """
    results: Dict[str, List[float]] = {
        'top_x_y': [],
        'bottom_x_y': [],
        'top_y_x': [],
        'bottom_y_x': []
    }
    data_subset = df.iloc[:, [0, 1]].dropna() # Use .dropna() specific to these columns

    if data_subset.empty or data_subset.shape[1] < 2:
        return results

    try:
        # Sort by X and get top/bottom N Y values
        # Handle potential duplicate X values by sorting by Y as a tie-breaker
        sorted_by_x = data_subset.sort_values(by=[data_subset.columns[0], data_subset.columns[1]])
        # Use .head(n) and .tail(n) to get at most n points
        results['bottom_x_y'] = sorted_by_x.head(n).iloc[:, 1].tolist()
        results['top_x_y'] = sorted_by_x.tail(n).iloc[:, 1].tolist()

        # Sort by Y and get top/bottom N X values
        # Handle potential duplicate Y values by sorting by X as a tie-breaker
        sorted_by_y = data_subset.sort_values(by=[data_subset.columns[1], data_subset.columns[0]])
        results['bottom_y_x'] = sorted_by_y.head(n).iloc[:, 0].tolist()
        results['top_y_x'] = sorted_by_y.tail(n).iloc[:, 0].tolist()

    except Exception as e:
        print(f"Error calculating extreme points: {e}")
        # Return empty lists on error
        return {
            'top_x_y': [], 'bottom_x_y': [],
            'top_y_x': [], 'bottom_y_x': []
        }

    return results


# --- QA Filling Functions based on 散点QA整理.txt ---
# These functions format the calculated data into the Q&A structure.
# Leave functions empty or return empty lists for QA types not specified in the text file
# or designated as placeholder (e.g., SVG related).

def fill_qa_ctr() -> List[Dict[str, str]]:
    """Generates QA for chart type (CTR). Based on 散点QA整理.txt CTR."""
    # Based on 散点QA整理.txt CTR - Note: This is a generic chart type question.
    # For a scatter plot, the answer should reflect that.
    # The template says "line chart", but for scatter, it should be "scatter plot".
    # Let's generate the scatter plot specific QA and add {} annotation.
    qa_list: List[Dict[str, str]] = []
    qa_list.append({
        "Q": "What type of chart is this?",
        "A": "This chart is a {scatter plot}." # Added {}
    })
    return qa_list


def fill_qa_vec(point_count: int) -> List[Dict[str, str]]:
    """Generates QA for the number of points (VEC). Based on 散点QA整理.txt VEC."""
    # Based on 散点QA整理.txt VEC
    qa_list: List[Dict[str, str]] = []
    question = "How many points are in this scatter plot?"
    answer = f"There are {{{point_count}}} points." # Added {} around the number
    qa_list.append({"Q": question, "A": answer})
    return qa_list

def fill_qa_srp() -> List[Dict[str, str]]:
    """Generates QA for SRP (SVG related). Currently empty as per request."""
    # TODO: Implement QA generation for SRP (SVG related)
    return []

def fill_qa_vpr(correlation_value: float | None) -> List[Dict[str, str]]:
    """Generates QA for the correlation pattern (VPR). Based on 散点QA整理.txt VPR."""
    # Based on 散点QA整理.txt VPR
    qa_list: List[Dict[str, str]] = []
    question = "What pattern does the correlation in the scatter plot show?"
    # Interpret correlation value to a pattern description
    pattern = "no clear linear correlation" # Default
    if correlation_value is not None and not np.isnan(correlation_value):
        abs_corr = abs(correlation_value)
        # Using thresholds (e.g., 0.4) to determine if a pattern is clear enough to mention
        # Let's use slightly lower thresholds for pattern description than for "strong/moderate" in SC QA
        if abs_corr >= 0.4: # Moderate to strong
             if correlation_value > 0:
                 pattern = "a positive linear correlation"
             else:
                 pattern = "a negative linear correlation"
        elif abs_corr >= 0.1: # Weak, but might still show a hint of direction
             if correlation_value > 0:
                  pattern = "a weak positive linear correlation"
             else:
                  pattern = "a weak negative linear correlation"
        # If abs_corr < 0.1, pattern remains "no clear linear correlation"

    answer = f"The scatter plot shows {{{pattern}}}." # Added {} around the pattern description
    qa_list.append({"Q": question, "A": answer})
    return qa_list

def fill_qa_ve() -> List[Dict[str, str]]:
    """Generates QA for VE. Currently empty as per template/request."""
    # TODO: Implement QA generation for VE
    return []

def fill_qa_evj(min_max_values: Dict[str, float], x_label: str, y_label: str) -> List[Dict[str, str]]:
    """Generates QA for min/max values (EVJ). Based on 散点QA整理.txt EVJ."""
    # Based on 散点QA整理.txt EVJ
    qa_list: List[Dict[str, str]] = []
    # Use .get() with a default to handle cases where min_max_values might be missing keys
    x_min = min_max_values.get('x_min')
    x_max = min_max_values.get('x_max')
    y_min = min_max_values.get('y_min')
    y_max = min_max_values.get('y_max')

    # Format values to 2 decimal places if they exist and are not NaN, otherwise use a placeholder
    x_min_formatted = f"{x_min:.2f}" if x_min is not None and not np.isnan(x_min) else "N/A"
    x_max_formatted = f"{x_max:.2f}" if x_max is not None and not np.isnan(x_max) else "N/A"
    y_min_formatted = f"{y_min:.2f}" if y_min is not None and not np.isnan(y_min) else "N/A"
    y_max_formatted = f"{y_max:.2f}" if y_max is not None and not np.isnan(y_max) else "N/A"


    qa_list.append({
        "Q": f"What is the maximum observed value in dimension {x_label} in the scatter plot?",
        "A": f"The maximum observed value in the {x_label} dimension is {{{x_max_formatted}}}." # Added {}
    })
    qa_list.append({
        "Q": f"What is the minimum observed value in dimension {x_label} in the scatter plot?",
        "A": f"The minimum observed value in the {x_label} dimension is {{{x_min_formatted}}}." # Added {}
    })
    qa_list.append({
        "Q": f"What is the maximum observed value in dimension {y_label} in the scatter plot?",
        "A": f"The maximum observed value in the {y_label} dimension is {{{y_max_formatted}}}." # Added {}
    })
    qa_list.append({
        "Q": f"What is the minimum observed value in dimension {y_label} in the scatter plot?",
        "A": f"The minimum observed value in the {y_label} dimension is {{{y_min_formatted}}}." # Added {}
    })

    return qa_list

def fill_qa_sc(average_values: Dict[str, float], x_label: str, y_label: str) -> List[Dict[str, str]]:
    """Generates QA for average values (SC). Based on 散点QA整理.txt SC."""
    # Based on 散点QA整理.txt SC
    qa_list: List[Dict[str, str]] = []
    x_avg = average_values.get('x_avg')
    y_avg = average_values.get('y_avg')

    # Format values to 2 decimal places if they exist and are not NaN
    x_avg_formatted = f"{x_avg:.2f}" if x_avg is not None and not np.isnan(x_avg) else "N/A"
    y_avg_formatted = f"{y_avg:.2f}" if y_avg is not None and not np.isnan(y_avg) else "N/A"


    qa_list.append({
        "Q": f"What is the average value of the {x_label} for all points?",
        "A": f"The average value of {x_label} for all points is {{{x_avg_formatted}}}." # Added {}
    })
    qa_list.append({
        "Q": f"What is the average value of the {y_label} for all points?",
        "A": f"The average value of {y_label} for all points is {{{y_avg_formatted}}}." # Added {}
    })
    return qa_list


def fill_qa_nf(extreme_points_data: Dict[str, List[float]], x_label: str, y_label: str) -> List[Dict[str, str]]:
    """Generates QA for extreme points (NF). Based on 散点QA整理.txt NF."""
    # Based on 散点QA整理.txt NF
    qa_list: List[Dict[str, str]] = []

    # Helper to format a list of numbers to a comma-separated string (2 decimal places)
    def format_values_list(values_list):
        if not values_list:
            return "N/A"
        # Filter out None/NaN before formatting and joining
        valid_values = [v for v in values_list if v is not None and not np.isnan(v)]
        if not valid_values:
             return "N/A"
        return ", ".join([f"{v:.2f}" for v in valid_values])

    top_x_y_formatted = format_values_list(extreme_points_data.get('top_x_y', []))
    bottom_x_y_formatted = format_values_list(extreme_points_data.get('bottom_x_y', []))
    top_y_x_formatted = format_values_list(extreme_points_data.get('top_y_x', []))
    bottom_y_x_formatted = format_values_list(extreme_points_data.get('bottom_y_x', []))


    qa_list.append({
        "Q": f"What are the {y_label} values corresponding to the top 3 {x_label} values in the scatter plot?",
        "A": f"{{{top_x_y_formatted}}}." # Added {} around the list
    })
    qa_list.append({
        "Q": f"What are the {y_label} values corresponding to the bottom 3 {x_label} values in the scatter plot?",
        "A": f"{{{bottom_x_y_formatted}}}." # Added {} around the list
    })
    qa_list.append({
        "Q": f"What are the {x_label} values corresponding to the top 3 {y_label} values in the scatter plot?",
        "A": f"{{{top_y_x_formatted}}}." # Added {} around the list
    })
    qa_list.append({
        "Q": f"What are the {x_label} values corresponding to the bottom 3 {y_label} values in the scatter plot?",
        "A": f"{{{bottom_y_x_formatted}}}." # Added {} around the list
    })

    return qa_list

def fill_qa_nc() -> List[Dict[str, str]]:
    """Generates QA for NC. Currently empty as per template/request."""
    # TODO: Implement QA generation for NC
    return []

def fill_qa_msr() -> List[Dict[str, str]]:
    """Generates QA for MSR (SVG related). Currently empty as per request."""
    # TODO: Implement QA generation for MSR (SVG related)
    return []

def fill_qa_va() -> List[Dict[str, str]]:
    """Generates QA for VA (SVG related). Currently empty as per request."""
    # TODO: Implement QA generation for VA (SVG related)
    return []


# 写入json，使用新的模板初始化结构并合并现有数据
def write_qa_to_json(csv_path: str, qa_type: str, qa_items: List[Dict[str, str]]):
    """
    将单条或多条 QA (qa_items) 按类别 qa_type 写入到 ./scatter/QA/ 下对应文件。
    例如 ./scatter/csv/scatter_Topic_1.csv → ./scatter/QA/scatter_Topic_1.json
    此函数采用新的模板中的 JSON 文件初始化结构，并合并现有数据。
    """
    # --- START MODIFICATION FOR OUTPUT PATH ---
    # The target directory is simply ./scatter/QA/
    json_dir = './scatter/QA'
    os.makedirs(json_dir, exist_ok=True)

    # Construct JSON file full path using the CSV base name
    # We need to remove the './scatter/csv/' prefix and the '.csv' suffix
    # Or just take the basename and remove the .csv suffix
    base_name_with_suffix = os.path.basename(csv_path) # e.g., scatter_Topic_1.csv
    base_name = os.path.splitext(base_name_with_suffix)[0] # e.g., scatter_Topic_1

    # The JSON filename should be the same as the CSV base name
    json_path = os.path.join(json_dir, base_name + '.json')
    # --- END MODIFICATION FOR OUTPUT PATH ---


    # Define the complete template structure
    template_data = {
        "CTR": [], "VEC": [], "SRP": [], "VPR": [], "VE": [],
        "EVJ": [], "SC": [], "NF": [], "NC": [], "MSR": [], "VA": []
    }

    # Load existing data if file exists
    existing_data = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            # Ensure loaded data is a dictionary, fallback if not
            if not isinstance(existing_data, dict):
                 print(f"Warning: Existing JSON data in {json_path} is not a dictionary. Overwriting with template structure.")
                 existing_data = {}
        except (json.JSONDecodeError, FileNotFoundError):
            # File not found is handled by os.path.exists, but keeping it here as a safeguard
            print(f"Warning: Could not load or decode JSON from {json_path}. Starting with template structure.")
            existing_data = {}
        except Exception as e:
             print(f"Warning: Could not read JSON from {json_path}: {e}. Starting with template structure.")
             existing_data = {}

    # Merge existing data into the template structure
    # Start with the template, then copy over the lists from the existing data for any keys that exist and are lists
    data_to_save = template_data.copy() # Start with all keys from the template
    for key in template_data.keys():
         if key in existing_data and isinstance(existing_data[key], list):
             # Only copy if the existing list is not empty. This prevents overwriting
             # a potentially empty list in the template with an empty list from existing data,
             # which is redundant, but more importantly, ensures we start with the template's
             # empty list if the key didn't exist or was empty in the old file.
             # Correction: We *do* want to copy the existing list if it's empty, to preserve
             # any specific state (though for empty lists, it doesn't matter).
             # The main goal is to preserve *non-empty* lists and ensure all keys are present.
             data_to_save[key] = existing_data[key] # Copy the existing list for this key


    # Append new QA items to the appropriate list in the merged data
    # Ensure the qa_type exists in the template (which it will now) and is a list
    if qa_type in data_to_save and isinstance(data_to_save[qa_type], list):
         data_to_save[qa_type].extend(qa_items)
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


def main():
    # todo 修改路径和任务类型
    # 设定 CSV 文件夹路径
    csv_folder = './scatter/csv'
    # 设定 QA 类型 (现在有多种类型，将在 write_qa_to_json 中区分)
    # QA_type = "SC" # This variable is no longer used directly here

    # 检查 CSV 文件夹是否存在
    if not os.path.exists(csv_folder):
        print(f"错误：未找到 CSV 文件夹 {csv_folder}。请先运行 scatter.py 生成数据。")
        return

    # 遍历文件夹下所有文件（全部都是 .csv）
    for fname in os.listdir(csv_folder):
        # 只处理 CSV 文件
        if fname.endswith('.csv'):
            # 构造完整路径
            csv_path = os.path.join(csv_folder, fname)

            print(f"正在处理文件：{csv_path}...")

            # 读取元数据 (可选，但保留函数调用)
            # meta = read_metadata(csv_path) # 元信息，当前 QA 任务不需要用于生成问答，但可以读取

            # 读取 x 轴和 y 轴标签及单位
            x_label, x_unit, y_label, y_unit = read_axis_labels(csv_path)

            # 检查是否成功读取了标签
            if not x_label or not y_label:
                 # print(f"跳过文件 {fname} 的 QA 生成，因为无法读取坐标轴标签。") # Keep original print style minimal
                 continue

            # --- 读取数据并进行各种计算 ---
            # skiprows=2 跳过前两行，header=None 保留原始数据
            try:
                # Read data, coercing non-numeric values to NaN
                df_data = pd.read_csv(csv_path, header=None, skiprows=2, encoding='utf-8').apply(pd.to_numeric, errors='coerce')

                # Ensure we have at least 2 columns for scatter data
                if df_data.shape[1] < 2:
                     # print(f"跳过文件 {fname} 的 QA 生成，数据列不足。") # Keep original print style minimal
                     continue

            except Exception as e:
                 print(f"读取或处理文件 {fname} 数据时发生错误: {e}. 跳过。")
                 continue


            # --- 生成不同类型的 QA ---
            # 根据 散点QA整理.txt 和新的原始模板，生成已指定或需要保留的 QA 类型

            # CTR: Chart type (Implemented based on scatter plot)
            qa_ctr_list = fill_qa_ctr()
            if qa_ctr_list:
                 write_qa_to_json(csv_path, "CTR", qa_ctr_list)

            # VEC: Number of points
            point_count = task_count_points(df_data)
            qa_vec_list = fill_qa_vec(point_count)
            if qa_vec_list:
                 write_qa_to_json(csv_path, "VEC", qa_vec_list)

            # SRP: SVG related (Placeholder)
            qa_srp_list = fill_qa_srp() # Returns []
            if qa_srp_list: # This will be false, so nothing is written for SRP yet
                 write_qa_to_json(csv_path, "SRP", qa_srp_list)

            # VPR: Correlation pattern
            correlation_value = task_get_correlation_value(df_data)
            qa_vpr_list = fill_qa_vpr(correlation_value)
            if qa_vpr_list:
                 write_qa_to_json(csv_path, "VPR", qa_vpr_list)

            # VE: Placeholder from new template
            qa_ve_list = fill_qa_ve() # Returns []
            if qa_ve_list: # This will be false
                 write_qa_to_json(csv_path, "VE", qa_ve_list)

            # EVJ: Min/Max values
            min_max_values = task_get_min_max(df_data)
            qa_evj_list = fill_qa_evj(min_max_values, x_label, y_label)
            if qa_evj_list:
                write_qa_to_json(csv_path, "EVJ", qa_evj_list)

            # SC: Average values
            average_values = task_get_averages(df_data)
            qa_sc_list = fill_qa_sc(average_values, x_label, y_label)
            if qa_sc_list:
                 write_qa_to_json(csv_path, "SC", qa_sc_list)

            # NF: Extreme points values (for top/bottom 3)
            extreme_points_data = task_get_extreme_points(df_data, n=3) # Get data for top/bottom 3
            qa_nf_list = fill_qa_nf(extreme_points_data, x_label, y_label)
            if qa_nf_list:
                 write_qa_to_json(csv_path, "NF", qa_nf_list)

            # NC: Placeholder from new template
            qa_nc_list = fill_qa_nc() # Returns []
            if qa_nc_list: # This will be false
                 write_qa_to_json(csv_path, "NC", qa_nc_list)

            # MSR: SVG related (Placeholder)
            qa_msr_list = fill_qa_msr() # Returns []
            if qa_msr_list: # This will be false
                 write_qa_to_json(csv_path, "MSR", qa_msr_list)

            # VA: SVG related (Placeholder)
            qa_va_list = fill_qa_va() # Returns []
            if qa_va_list: # This will be false
                 write_qa_to_json(csv_path, "VA", qa_va_list)


    print("散点图 QA 文件生成完毕。")

    # 输出结果 (原注释块，保留)
    # print("元信息：")
    # print(f"  大标题  : {meta['title']}")
    # print(f"  子标题  : {meta['subtitle']}")
    # print(f"  单位    : {meta['unit']}")
    # print(f"  模式    : {meta['mode']}\n")
    #
    # print("轴 标签：")
    # print(f"  x 轴标签: {x_label}")
    # print(f"  y 轴标签: {y_label}\n")

if __name__ == '__main__':
    main()
