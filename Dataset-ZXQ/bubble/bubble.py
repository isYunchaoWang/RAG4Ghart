# File: bubble.py
import os
import numpy as np
import pandas as pd
import random
from typing import Tuple, Dict, List, Any
import re # Import regex for cleaning keys
import math # Import math for isnan check

# --- Configuration Data ---
# Original axis info with potential units in keys
original_axis_info: Dict[str, Tuple[float, float, str]] = {
    # ... (Your original_axis_info dictionary here - OMITTED FOR BREVITY) ...
    # Education and Academics
    'Household income': (20000, 200000, '$'),
    'Parental education': (0.1, 20, 'years'), # e.g., years of schooling
    'School funding': (1000, 20000, '$ per student'),
    'Study hours': (0.1, 40, 'hours/week'),
    'Class size': (5, 50, 'students'),
    'Academic performance': (0.1, 100, 'score'),
    'Graduation rate': (50, 100, '%'),
    'Test scores': (400, 1600, 'points'), # e.g., SAT range
    'College admission rate': (0.1, 100, '%'), # Changed to rate for bubble size
    'Literacy rate': (50, 100, '%'),
    'Student count': (100, 5000, 'students'), # Added for size

    # Transportation and Logistics
    'Distance traveled': (1, 1000, 'miles'),
    'Fuel cost': (2, 5, '$ per gallon'),
    'Delivery time': (1, 30, 'days'),
    'Vehicle age': (0.1, 20, 'years'),
    'Traffic volume': (100, 10000, 'vehicles/hour'),
    'Transport efficiency': (50, 95, '%'),
    'Cost per mile': (0.1, 2.0, '$'),
    'On-time rate': (70, 100, '%'),
    'Fuel efficiency': (10, 50, 'mpg'),
    'Customer satisfaction (Transport)': (1, 5, 'rating'), # Renamed to avoid conflict
    'Shipment volume': (100, 10000, 'units'), # Added for size

    # Tourism and Hospitality
    'Hotel rating': (1, 5, 'stars'),
    'Price per night': (50, 500, '$'),
    'Distance to attractions': (0.1, 20, 'miles'),
    'Season': (1, 4, 'quarter'), # Simplified
    'Tourist reviews': (1, 5, 'rating'),
    'Occupancy rate': (30, 100, '%'),
    'Repeat visits': (0.1, 5, 'count'),
    'Revenue per room': (50, 400, '$'),
    'Online bookings count': (0.1, 1000, 'count/day'), # Renamed
    'Number of rooms': (10, 500, 'rooms'), # Added for size

    # Business and Finance
    'Company revenue': (1000000, 1000000000, '$'), # Example range
    'Market share': (1, 50, '%'),
    'Operating costs': (100000, 500000000, '$'),
    'Employee count': (10, 10000, 'count'),
    'Investment amount': (1000, 1000000, '$'),
    'Profit margin': (0.1, 30, '%'),
    'Stock price': (1, 1000, '$'),
    'ROI': (0.1, 500, '%'),
    'Customer base size': (100, 1000000, 'count'), # Renamed
    'Brand value': (1000000, 10000000000, '$'), # Added for size

    # Real Estate and Housing Market
    'Property size (sqft)': (500, 10000, 'sqft'), # Renamed
    'Location score': (1, 10, 'score'),
    'Age of property': (0, 100, 'years'),
    'Interest rates': (2, 8, '%'),
    'Local amenities count': (0, 10, 'count/mile'), # Renamed
    'Sale price': (100000, 5000000, '$'),
    'Days on market': (1, 365, 'days'),
    'Rental yield': (1, 10, '%'),
    'Price per sqft': (50, 1000, '$'),
    'Demand index': (0.1, 10, 'index'),
    'Number of properties sold': (1, 100, 'count'), # Added for size

    # Healthcare and Health
    'Age': (0.1, 100, 'years'),
    'BMI': (15, 40, 'kg/m^2'),
    'Exercise frequency': (0, 7, 'days/week'),
    'Health insurance coverage': (0.1, 1, 'binary (0/1)'), # Renamed
    'Doctor visits count': (0.1, 20, 'count/year'), # Renamed
    'Life expectancy': (60, 90, 'years'),
    'Recovery rate': (50, 100, '%'),
    'Medical costs': (100, 100000, '$'),
    'Health score': (0.1, 100, 'score'),
    'Hospital stays count': (0.1, 30, 'days/year'), # Renamed
    'Patient volume': (10, 1000, 'patients'), # Added for size

    # Retail and E-commerce
    'Product price': (1, 1000, '$'),
    'Marketing spend': (100, 100000, '$'),
    'Customer reviews rating': (1, 5, 'rating'), # Renamed
    'Inventory level': (0.1, 10000, 'units'),
    'Discount rate': (0.1, 50, '%'),
    'Sales volume': (10, 100000, 'units/day'),
    'Conversion rate (Digital)': (0.1, 10, '%'), # Renamed
    'Customer retention rate': (50, 95, '%'), # Renamed
    'Profit margin (Retail)': (0.1, 50, '%'), # Renamed
    'Click-through rate': (0.1, 20, '%'),
    'Number of transactions': (100, 10000, 'count'), # Added for size

    # Human Resources and Employee Management
    'Years of experience': (0.1, 30, 'years'),
    'Training hours': (0.1, 100, 'hours/year'),
    'Salary': (30000, 200000, '$'),
    'Job satisfaction rating': (1, 5, 'rating'), # Renamed
    'Remote work days': (0, 5, 'days/week'),
    'Productivity index': (50, 150, 'index'), # Renamed
    'Turnover rate': (0.1, 30, '%'),
    'Promotion rate': (0.1, 20, '%'),
    'Employee engagement rating': (1, 5, 'rating'), # Renamed
    'Performance rating': (1, 5, 'rating'),
    'Team size': (2, 50, 'count'), # Added for size

    # Sports and Entertainment
    'Player salary': (100000, 50000000, '$'),
    'Team ranking': (1, 100, 'rank'),
    'Game attendance': (1000, 100000, 'attendees'),
    'Sponsorship amount': (10000, 10000000, '$'), # Renamed
    'Social media followers': (1000, 10000000, 'count'),
    'Win rate': (0.1, 100, '%'),
    'Revenue (Sports/Ent)': (1000000, 1000000000, '$'), # Renamed
    'Fan engagement rating': (1, 5, 'rating'), # Renamed
    'Ticket sales count': (10000, 1000000, 'count'), # Renamed
    'Merchandise sales': (100000, 10000000, '$'),
    'Viewer count': (10000, 10000000, 'count'), # Added for size

    # Food and Beverage Industry
    'Ingredient cost': (0.1, 10, '$ per unit'),
    'Menu price': (1, 50, '$'),
    'Customer rating (Food)': (1, 5, 'rating'), # Renamed
    'Preparation time': (1, 60, 'minutes'),
    'Calorie count': (50, 1000, 'calories'),
    'Sales volume (Food)': (10, 10000, 'units/day'), # Renamed
    'Profit margin (Food)': (0.1, 60, '%'), # Renamed
    'Customer retention rate (Food)': (60, 95, '%'), # Renamed
    'Order frequency': (1, 7, 'times/week'),
    'Social media mentions (Food)': (10, 1000, 'count/day'), # Renamed
    'Number of locations': (1, 500, 'count'), # Added for size

    # Science and Engineering
    'Research funding': (10000, 10000000, '$'),
    'Experiment duration': (1, 365, 'days'),
    'Team size (Sci/Eng)': (2, 50, 'count'), # Renamed
    'Publication count': (0.1, 100, 'count/year'),
    'Patent applications count': (0, 20, 'count/year'), # Renamed
    'Discovery impact score': (1, 10, 'score'), # Renamed
    'Innovation score': (1, 10, 'score'),
    'Citation count': (0.1, 1000, 'count'),
    'Commercial success value': (10000, 100000000, '$'), # Renamed
    'Technical complexity score': (1, 10, 'score'), # Renamed
    'Project budget': (50000, 5000000, '$'), # Added for size

    # Agriculture and Food Production
    'Fertilizer use': (10, 100, 'kg/acre'),
    'Rainfall': (10, 100, 'inches/year'),
    'Land size (acres)': (1, 1000, 'acres'), # Renamed
    'Seed quality rating': (1, 5, 'rating'), # Renamed
    'Labor hours (Agri)': (10, 40, 'hours/week'), # Renamed
    'Crop yield': (1000, 10000, 'kg/acre'),
    'Product quality rating (Agri)': (1, 5, 'rating'), # Renamed
    'Profit per acre': (100, 1000, '$'),
    'Sustainability score (Agri)': (0.1, 100, 'score'), # Renamed
    'Market price (Agri)': (0.5, 5, '$ per unit'), # Renamed
    'Total production volume': (1000, 100000, 'units/season'), # Added for size

    # Energy and Utilities
    'Energy consumption': (100, 10000, 'kWh/month'),
    'Production capacity (MW)': (1000, 1000000, 'MW'), # Renamed
    'Fuel cost (per unit)': (1, 100, '$ per unit'), # Renamed
    'Infrastructure age': (0, 50, 'years'),
    'Renewable ratio': (0.1, 100, '%'),
    'Efficiency score (Energy)': (50, 95, '%'), # Renamed
    'Carbon emissions': (1, 100, 'ton/year'),
    'Cost per kWh': (0.05, 0.2, '$'),
    'Reliability rate': (90, 100, '%'), # Renamed
    'Customer satisfaction (Energy)': (1, 5, 'rating'), # Renamed
    'Number of customers': (1000, 1000000, 'count'), # Added for size

    # Cultural Trends and Influences
    'Social media mentions (Cultural)': (100, 100000, 'count/day'), # Renamed
    'Event attendance': (1000, 1000000, 'attendees'),
    'Artist popularity rank': (1, 100, 'rank'), # Renamed
    'Time period': (1900, 2025, 'year'),
    'Geographic spread index': (1, 10, 'index'), # Renamed
    'Trend duration': (1, 365, 'days'),
    'Adoption rate': (1, 90, '%'),
    'Commercial impact value': (10000, 1000000000, '$'), # Renamed
    'Cultural significance score': (1, 10, 'score'), # Renamed
    'Media coverage count': (100, 10000, 'articles/month'), # Renamed
    'Number of participants': (100, 100000, 'count'), # Added for size

    # Social Media and Digital Media and Streaming
    'Content length': (1, 60, 'minutes'),
    'Posting frequency': (1, 20, 'posts/day'),
    'Hashtag use count': (1, 20, 'count/post'), # Renamed
    'Follower count': (100, 10000000, 'count'),
    'Ad spend': (100, 100000, '$'),
    'Engagement rate': (0, 20, '%'),
    'View count': (100, 10000000, 'count'),
    'Shares count': (10, 100000, 'count'), # Renamed
    'New followers count': (10, 100000, 'count/day'), # Renamed
    'Conversion rate (Digital)': (0.1, 10, '%'), # Renamed
    'Subscriber count': (1000, 10000000, 'count'), # Added for size
}

# Clean axis keys
def clean_axis_key(key: str) -> str:
    """Removes trailing parenthesized text like '(unit)' or '(Renamed)' from a key."""
    return re.sub(r'\s*\([^)]*\)$', '', key).strip()

# Sanitize text for use in filenames
def sanitize_filename(text: str) -> str:
    """Sanitizes text to be safe for use in filenames."""
    text = text.strip()
    # Replace spaces and slashes with underscores
    text = re.sub(r'[ /]', '_', text)
    # Remove any characters that are not alphanumeric, underscores, or hyphens
    text = re.sub(r'[^\w-]', '', text)
    # Limit length if necessary (optional)
    # text = text[:50]
    return text

axis_info: Dict[str, Tuple[float, float, str]] = {
    clean_axis_key(k): v for k, v in original_axis_info.items()
}

# Original combinations list
original_bubble_combinations: List[Tuple[str, str, str, str, str]] = [
    ('Education and Academics', 'Study hours', 'Academic performance', 'Class size', 'Number of students in class'),
    ('Education and Academics', 'School funding', 'Graduation rate', 'Student count', 'Total student enrollment'),
    ('Transportation and Logistics', 'Distance traveled', 'Fuel efficiency', 'Shipment volume', 'Size of the shipment'),
    ('Transportation and Logistics', 'Traffic volume', 'On-time rate', 'Vehicle age', 'Age of the vehicle'),
    ('Tourism and Hospitality', 'Price per night', 'Occupancy rate', 'Number of rooms', 'Number of rooms in the hotel'),
    ('Tourism and Hospitality', 'Tourist reviews', 'Customer satisfaction (Transport)', 'Online bookings count', 'Daily online booking volume'),
    ('Business and Finance', 'Company revenue', 'Profit margin', 'Employee count', 'Total number of employees'),
    ('Business and Finance', 'Investment amount', 'ROI', 'Customer base size', 'Size of the customer base'),
    ('Retail and E-commerce', 'Marketing spend', 'Sales volume', 'Inventory level', 'Current stock quantity'),
    ('Retail and E-commerce', 'Product price', 'Conversion rate (Digital)', 'Number of transactions', 'Number of sales transactions'),
    ('Healthcare and Health', 'Age', 'Life expectancy', 'Patient volume', 'Number of patients treated'),
    ('Healthcare and Health', 'Medical costs', 'Recovery rate', 'Hospital stays count', 'Number of hospital stays'),
    ('Human Resources and Employee Management', 'Years of experience', 'Salary', 'Team size', 'Size of the team'),
    ('Human Resources and Employee Management', 'Training hours', 'Productivity index', 'Employee count', 'Number of employees'),
    ('Sports and Entertainment', 'Player salary', 'Win rate', 'Game attendance', 'Number of people attending the game'),
    ('Sports and Entertainment', 'Sponsorship amount', 'Revenue (Sports/Ent)', 'Viewer count', 'Number of viewers'),
    ('Food and Beverage Industry', 'Menu price', 'Sales volume (Food)', 'Number of locations', 'Number of restaurant locations'),
    ('Food and Beverage Industry', 'Ingredient cost', 'Profit margin (Food)', 'Order frequency', 'Average customer order frequency'),
    ('Science and Engineering', 'Research funding', 'Publication count', 'Team size (Sci/Eng)', 'Size of the research team'),
    ('Science and Engineering', 'Innovation score', 'Commercial success value', 'Project budget', 'Total project budget'),
    ('Agriculture and Food Production', 'Land size (acres)', 'Crop yield', 'Labor hours (Agri)', 'Weekly labor hours'),
    ('Agriculture and Food Production', 'Fertilizer use', 'Profit per acre', 'Total production volume', 'Total volume produced'),
    ('Energy and Utilities', 'Production capacity (MW)', 'Efficiency score (Energy)', 'Number of customers', 'Total number of utility customers'),
    ('Energy and Utilities', 'Infrastructure age', 'Reliability rate', 'Energy consumption', 'Average energy consumption'),
    ('Cultural Trends and Influences', 'Social media mentions (Cultural)', 'Adoption rate', 'Event attendance', 'Number of event attendees'),
    ('Cultural Trends and Influences', 'Artist popularity rank', 'Commercial impact value', 'Number of participants', 'Number of people involved/influenced'),
    ('Social Media and Digital Media and Streaming', 'Follower count', 'Engagement rate', 'Shares count', 'Number of shares'),
    ('Social Media and Digital Media and Streaming', 'Ad spend', 'Conversion rate (Digital)', 'Subscriber count', 'Total number of subscribers'),
]

bubble_combinations: List[Tuple[str, str, str, str, str]] = [
    (topic,
     clean_axis_key(x),      # Clean X axis name
     clean_axis_key(y),      # Clean Y axis name
     clean_axis_key(size),   # Clean Size axis name
     clean_axis_key(desc))   # Clean Size description
    for topic, x, y, size, desc in original_bubble_combinations
]


# Distribution types for bubble size
BUBBLE_SIZE_DISTRIBUTIONS = ['random', 'normal', 'long_tail', 'linear']

# Define diverse English descriptors for constructing the little theme "the xx of main theme"
ENGLISH_DESCRIPTORS = [
    "Relationship", "Correlation", "Distribution", "Analysis", "Overview",
    "Comparison", "Interaction", "Influence", "Pattern", "Dynamics"
]

# Define maximum allowed ratio between max and min generated size value *within a single file's data*
# This helps avoid cases like 0.1 and 10000 in the same file.
# Adjust this value based on how much variation you want within a file.
MAX_GENERATED_SIZE_RATIO = 50.0 # Example: Max value is at most 50 times the min value

# --- Data Generation Functions ---
def random_distribution(count: int) -> np.ndarray: return np.random.rand(count) * 100
def normal_distribution(count: int) -> np.ndarray: return np.random.normal(50, 20, count)
def long_tail_distribution(count: int) -> np.ndarray:
    values = np.random.pareto(3, count) * 50 + 10
    max_clip = np.percentile(values, 99) if len(values) > 1 else values.max() if len(values) > 0 else 100
    values = np.clip(values, 10, max_clip)
    return values

def linear_distribution(count: int) -> np.ndarray: return np.linspace(10, 100, count)

def generate_bubble_data(num_records: int, x_range_orig: Tuple[float, float],
                         y_range_orig: Tuple[float, float], size_range_orig: Tuple[float, float],
                         overlap_degree: float, distribution_type: str,
                         x_col_name: str, y_col_name: str, size_col_name: str) -> pd.DataFrame:
    """Generates bubble chart data. Uses CLEANED column names."""
    if num_records < 1: raise ValueError("Number of records must be at least 1")
    if not 0 <= overlap_degree <= 1: raise ValueError("Overlap degree must be between 0 and 1")
    if distribution_type not in BUBBLE_SIZE_DISTRIBUTIONS: raise ValueError(f"Invalid distribution type. Must be one of {BUBBLE_SIZE_DISTRIBUTIONS}")

    x_values = np.random.uniform(x_range_orig[0], x_range_orig[1], num_records)
    y_values = np.random.uniform(y_range_orig[0], y_range_orig[1], num_records)

    x_noise_scale = (x_range_orig[1] - x_range_orig[0]) * overlap_degree * 0.1 if (x_range_orig[1] - x_range_orig[0]) > 0 else 0.1
    y_noise_scale = (y_range_orig[1] - y_range_orig[0]) * overlap_degree * 0.1 if (y_range_orig[1] - y_range_orig[0]) > 0 else 0.1
    x_values += np.random.normal(0, x_noise_scale, num_records)
    y_values += np.random.normal(0, y_noise_scale, num_records)

    x_margin = (x_range_orig[1] - x_range_orig[0]) * 0.05 if (x_range_orig[1] - x_range_orig[0]) > 0 else 0.1
    y_margin = (y_range_orig[1] - y_range_orig[0]) * 0.05 if (y_range_orig[1] - y_range_orig[0]) > 0 else 0.1
    x_values = np.clip(x_values, x_range_orig[0] - x_margin, x_range_orig[1] + x_margin)
    y_values = np.clip(y_values, y_range_orig[0] - y_margin, y_range_orig[1] + y_margin)

    x_values = np.clip(x_values, max(0.0, x_range_orig[0]), None)
    y_values = np.clip(y_values, max(0.0, y_range_orig[0]), None)

    if distribution_type == 'random': size_values_base = random_distribution(num_records)
    elif distribution_type == 'normal': size_values_base = normal_distribution(num_records)
    elif distribution_type == 'long_tail': size_values_base = long_tail_distribution(num_records)
    elif distribution_type == 'linear': size_values_base = linear_distribution(num_records)
    else: size_values_base = random_distribution(num_records)

    size_values_base[size_values_base <= 0] = 1e-9

    base_min_actual = np.min(size_values_base)
    base_max_actual = np.max(size_values_base)

    if base_min_actual > 0 and base_max_actual / base_min_actual > MAX_GENERATED_SIZE_RATIO:
        effective_base_max = base_min_actual * MAX_GENERATED_SIZE_RATIO
        size_values_base = np.clip(size_values_base, base_min_actual, effective_base_max)
        # print(f"  Note: Clipped size_values_base ratio from ~{base_max_actual/base_min_actual:.1f} to {MAX_GENERATED_SIZE_RATIO:.1f}") # Optional print
        base_min_actual = np.min(size_values_base)
        base_max_actual = np.max(size_values_base)

    size_min_target, size_max_target = size_range_orig

    if base_min_actual == base_max_actual or size_min_target == size_max_target or (size_max_target - size_min_target) <= 0 or (base_max_actual - base_min_actual) <= 0:
        size_values_scaled = np.full_like(size_values_base, (size_min_target + size_max_target) / 2.0)
    else:
        scale_factor = (size_max_target - size_min_target) / (base_max_actual - base_min_actual)
        size_values_scaled = size_min_target + (size_values_base - base_min_actual) * scale_factor

    size_values_scaled = np.clip(size_values_scaled, size_min_target, size_max_target)
    size_values_scaled[size_values_scaled <= 0] = size_min_target if size_min_target > 0 else 1e-9

    data = pd.DataFrame({ x_col_name: x_values, y_col_name: y_values, size_col_name: size_values_scaled })
    return data

# --- MODIFICATION: save_bubble_to_csv returns filename AND little_theme ---
def save_bubble_to_csv(data: pd.DataFrame, topic: str, topic_seq_num: int,
                       x_col_name: str, y_col_name: str, size_col_name: str,
                       x_unit: str, y_unit: str, size_unit: str,
                       distribution_type: str, bubble_size_description: str) -> Tuple[str, str]: # Return type changed
    """
    Saves bubble chart data to CSV. Uses CLEANED column names and description.
    Revised header format: topic, little theme, x(x_unit), y(y_unit), size_meaning(size_unit), pattern
    Returns the filename and the generated little_theme.
    """
    output_dir = './bubble/csv'
    os.makedirs(output_dir, exist_ok=True)

    sanitized_topic = sanitize_filename(topic)
    filename = os.path.join(output_dir, f"bubble_{sanitized_topic}_{topic_seq_num}.csv")

    selected_descriptor = random.choice(ENGLISH_DESCRIPTORS)
    little_theme = f"the {selected_descriptor} of {topic}" # Define little_theme here

    header_line = f"{topic},{little_theme},"
    header_line += f"{x_col_name} ({x_unit}),"
    header_line += f"{y_col_name} ({y_unit}),"
    header_line += f"{bubble_size_description} ({size_unit})," # Combined field
    header_line += f"{distribution_type.replace('_', ' ').title()}"

    data_to_save = data.copy()
    cols_to_process = [x_col_name, y_col_name, size_col_name]
    rows_before_cleaning = len(data_to_save)

    for col in cols_to_process:
        if col in data_to_save.columns:
            data_to_save[col] = pd.to_numeric(data_to_save[col], errors='coerce')
            # Drop rows only if critical columns (X, Y, Size) become NaN
            if col in [x_col_name, y_col_name, size_col_name]:
                initial_len = len(data_to_save)
                data_to_save.dropna(subset=[col], inplace=True)
                if len(data_to_save) < initial_len:
                    print(f"  Note: Removed {initial_len - len(data_to_save)} rows from {os.path.basename(filename)} due to NaN in '{col}'.")

            if not data_to_save.empty and data_to_save[col].notna().any():
                try:
                    data_to_save[col] = data_to_save[col].round(2)
                except Exception as e:
                    print(f"Warning: Could not round column '{col}' in {os.path.basename(filename)}: {e}.")

    if rows_before_cleaning > 0 and len(data_to_save) == 0:
        print(f"  Warning: All {rows_before_cleaning} records removed from {os.path.basename(filename)} after cleaning. File will only contain header.")

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        f.write(header_line + "\n")
        if not data_to_save.empty:
            try:
                cols_to_write = [x_col_name, y_col_name, size_col_name]
                if all(c in data_to_save.columns for c in cols_to_write):
                    data_to_save[cols_to_write].to_csv(f, index=False, header=False)
                else:
                    missing_cols = [c for c in cols_to_write if c not in data_to_save.columns]
                    print(f"Error: DataFrame for {os.path.basename(filename)} is missing columns: {missing_cols}. Cannot write data rows.")
            except Exception as e:
                print(f"Error writing data rows to CSV {os.path.basename(filename)}: {e}")

    return filename, little_theme # Return both filename and little_theme

# --- Main Execution ---
if __name__ == "__main__":
    NUM_FILES_TO_GENERATE = 10
    FIXED_NUM_RECORDS = None
    RECORDS_RANGE = (10, 15)
    FIXED_OVERLAP_DEGREE = None
    OVERLAP_RANGE = (0.0, 0.7)
    FIXED_DISTRIBUTION_TYPE = None

    topic_file_counters: Dict[str, int] = {}
    generated_files = 0
    print(f"Starting data generation for {NUM_FILES_TO_GENERATE} bubble chart files.")
    output_dir_main = './bubble/csv' # Renamed to avoid conflict with local output_dir
    os.makedirs(output_dir_main, exist_ok=True)

    while generated_files < NUM_FILES_TO_GENERATE:
        # Define little_theme_for_print here to ensure it's always available for the except block
        little_theme_for_print = "N/A (Error before generation)"
        current_output_file = "N/A (Error before generation)"
        try:
            selected_combo = random.choice(bubble_combinations)
            topic, x_name, y_name, size_name, size_description = selected_combo

            if topic not in topic_file_counters:
                topic_file_counters[topic] = 0
            topic_file_counters[topic] += 1
            current_topic_seq_num = topic_file_counters[topic]

            x_info = axis_info.get(x_name, (0, 100, 'unit'))
            x_range_orig, x_unit = x_info[0:2], x_info[2]
            y_info = axis_info.get(y_name, (0, 100, 'unit'))
            y_range_orig, y_unit = y_info[0:2], y_info[2]
            size_info = axis_info.get(size_name, (0, 100, 'unit'))
            size_range_orig, size_unit = size_info[0:2], size_info[2]

            num_records_initial = FIXED_NUM_RECORDS if FIXED_NUM_RECORDS is not None else random.randint(*RECORDS_RANGE)
            overlap_degree = FIXED_OVERLAP_DEGREE if FIXED_OVERLAP_DEGREE is not None else random.uniform(*OVERLAP_RANGE)
            distribution_type = FIXED_DISTRIBUTION_TYPE if FIXED_DISTRIBUTION_TYPE is not None else random.choice(BUBBLE_SIZE_DISTRIBUTIONS)

            data_generated = generate_bubble_data(
                num_records=num_records_initial, x_range_orig=x_range_orig, y_range_orig=y_range_orig, size_range_orig=size_range_orig,
                overlap_degree=overlap_degree, distribution_type=distribution_type,
                x_col_name=x_name, y_col_name=y_name, size_col_name=size_name
            )

            # Save data and get the actual little_theme used
            current_output_file, little_theme_for_print = save_bubble_to_csv( # Assign to little_theme_for_print
                data=data_generated, topic=topic, topic_seq_num=current_topic_seq_num,
                x_col_name=x_name, y_col_name=y_name, size_col_name=size_name,
                x_unit=x_unit, y_unit=y_unit, size_unit=size_unit,
                distribution_type=distribution_type,
                bubble_size_description=size_description
            )
            current_output_file_basename = os.path.basename(current_output_file)


            # Read the data part of the saved CSV to get actual ranges after cleaning/rounding
            actual_x_min_str, actual_x_max_str = 'N/A', 'N/A'
            actual_y_min_str, actual_y_max_str = 'N/A', 'N/A'
            actual_size_min_str, actual_size_max_str = 'N/A', 'N/A'
            num_records_after_save = 0

            try:
                data_after_save = pd.read_csv(current_output_file, skiprows=1, header=None, encoding='utf-8')
                if not data_after_save.empty and data_after_save.shape[1] >= 3:
                    temp_cols = [x_name, y_name, size_name]
                    data_after_save.columns = temp_cols[:data_after_save.shape[1]]

                    def get_formatted_stat(series):
                        if series.notna().any():
                            return f"{series.min():.2f}", f"{series.max():.2f}"
                        return 'N/A', 'N/A'

                    if x_name in data_after_save.columns:
                        actual_x_min_str, actual_x_max_str = get_formatted_stat(data_after_save[x_name])
                    if y_name in data_after_save.columns:
                        actual_y_min_str, actual_y_max_str = get_formatted_stat(data_after_save[y_name])
                    if size_name in data_after_save.columns:
                        actual_size_min_str, actual_size_max_str = get_formatted_stat(data_after_save[size_name])
                    num_records_after_save = len(data_after_save)
                elif not data_after_save.empty:
                     print(f"Warning: Data section in {current_output_file_basename} has < 3 columns ({data_after_save.shape[1]}).")


            except FileNotFoundError:
                 print(f"Error: Could not re-read {current_output_file_basename} for stats.")
            except Exception as e_read:
                 print(f"Error re-reading/processing {current_output_file_basename}: {e_read}")

            print(f"Generated file {generated_files + 1}/{NUM_FILES_TO_GENERATE} ({current_output_file_basename}):")
            print(f"  Topic: {topic}")
            print(f"  Little Theme: {little_theme_for_print}") # Use the returned little_theme
            print(f"  X-axis: {x_name} ({x_unit}), Range: [{x_range_orig[0]}, {x_range_orig[1]}] -> Generated: [{actual_x_min_str}, {actual_x_max_str}]")
            print(f"  Y-axis: {y_name} ({y_unit}), Range: [{y_range_orig[0]}, {y_range_orig[1]}] -> Generated: [{actual_y_min_str}, {actual_y_max_str}]")
            print(f"  Size-axis: {size_description} ({size_unit}), Range: [{size_range_orig[0]}, {size_range_orig[1]}] -> Generated: [{actual_size_min_str}, {actual_size_max_str}]")
            print(f"  Size Distribution: {distribution_type}")
            print(f"  Number of records: {num_records_initial} (initial) -> {num_records_after_save} (saved)")
            print(f"  Overlap Degree: {overlap_degree:.2f}")
            print("")

            generated_files += 1 # Increment only if try block was successful

        except ValueError as e_val:
            print(f"ValueError during generation for file {os.path.basename(current_output_file)}: {e_val}. Skipping this file.\n")
            # Do not increment generated_files for ValueErrors that prevent file creation
        except Exception as e_main:
            import traceback
            print(f"An unexpected error occurred during generation for file {os.path.basename(current_output_file)}: {e_main}. Skipping this file.\n")
            traceback.print_exc()
            # Do not increment generated_files for other critical errors

    print(f"Finished. Successfully generated {generated_files} out of {NUM_FILES_TO_GENERATE} requested bubble chart data files.")

