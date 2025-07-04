import os
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt # Removed, not needed for data generation
import random
from typing import Tuple, Dict, Any, List # Added List
import re # Import re for sanitizing filename

# Constants for trend and correlation types
TREND_TYPES = ['linear', 'exponential', 'u_shape']
CORRELATION_TYPES = ['positive', 'negative', 'none']

# 主题和对应的坐标轴标签 (Keep as is)
topics_axes = {
    'Education and Academics': {
        'x_axis': ['Household income', 'Parental education', 'School funding', 'Study hours', 'Class size'],
        'y_axis': ['Academic performance', 'Graduation rate', 'Test scores', 'College admission', 'Literacy rate']
    },
    'Transportation and Logistics': {
        'x_axis': ['Distance traveled', 'Fuel cost', 'Delivery time', 'Vehicle age', 'Traffic volume'],
        'y_axis': ['Transport efficiency', 'Cost per mile', 'On-time rate', 'Fuel efficiency', 'Customer satisfaction']
    },
    'Healthcare and Medicine': {
        'x_axis': ['Patient age', 'BMI', 'Blood pressure', 'Treatment dosage', 'Hospital stay duration'],
        'y_axis': ['Recovery time', 'Treatment cost', 'Patient satisfaction', 'Readmission rate', 'Survival rate']
    },
    'Finance and Economics': {
        'x_axis': ['Interest rate', 'Inflation rate', 'GDP growth', 'Unemployment rate', 'Stock price'],
        'y_axis': ['Consumer spending', 'Investment rate', 'Business confidence', 'Housing starts', 'Exchange rate']
    },
     'Environmental Science and Ecology': {
        'x_axis': ['CO2 emissions', 'Average temperature', 'Rainfall amount', 'Forest cover', 'Pollution level'],
        'y_axis': ['Species diversity', 'Crop yield', 'Water quality', 'Air quality', 'Glacier size']
    },
    'Technology and Innovation': {
        'x_axis': ['R&D investment', 'Patent count', 'Internet speed', 'Smartphone penetration', 'Data usage'],
        'y_axis': ['Productivity growth', 'Startup success rate', 'Digital literacy', 'E-commerce sales', 'Innovation index']
    },
    'Marketing and Sales': {
        'x_axis': ['Advertising spend', 'Customer acquisition cost', 'Website traffic', 'Email open rate', 'Sales team size'],
        'y_axis': ['Conversion rate', 'Customer lifetime value', 'Bounce rate', 'Click-through rate', 'Revenue']
    },
    'Human Resources and Workplace': {
        'x_axis': ['Employee training hours', 'Years of experience', 'Salary', 'Commute time', 'Team size'],
        'y_axis': ['Job satisfaction', 'Employee retention', 'Productivity', 'Absenteeism', 'Promotion rate']
    },
    'Agriculture and Food Production': {
        'x_axis': ['Fertilizer usage', 'Irrigation amount', 'Sunlight hours', 'Pest control spending', 'Farm size'],
        'y_axis': ['Crop yield', 'Food production cost', 'Soil quality', 'Product freshness', 'Livestock health']
    },
    'Energy and Utilities': {
        'x_axis': ['Energy consumption', 'Renewable energy share', 'Electricity price', 'Grid stability', 'Infrastructure age'],
        'y_axis': ['Carbon footprint', 'Energy efficiency', 'Customer outage duration', 'Service cost', 'Reliability index']
    },
    'Retail and Consumer Behavior': {
        'x_axis': ['Store size', 'Product price', 'Promotional spending', 'Customer reviews count', 'Checkout time'],
        'y_axis': ['Sales volume', 'Customer satisfaction', 'Average transaction value', 'Return rate', 'Foot traffic']
    },
    'Sports and Fitness': {
        'x_axis': ['Training hours', 'Athlete age', 'Nutrition intake', 'Sleep duration', 'Injury frequency'],
        'y_axis': ['Performance score', 'Recovery time', 'Endurance level', 'Strength gain', 'Win rate']
    },
     'Tourism and Hospitality': {
        'x_axis': ['Hotel price', 'Attraction popularity', 'Travel distance', 'Marketing budget', 'Seasonality index'],
        'y_axis': ['Occupancy rate', 'Customer reviews score', 'Visitor spending', 'Booking conversion', 'Repeat visitor rate']
    },
    'Real Estate and Construction': {
        'x_axis': ['Property size', 'Construction cost', 'Location score', 'Interest rate', 'Development density'],
        'y_axis': ['Property value', 'Rental yield', 'Construction time', 'Vacancy rate', 'Sales price per m³']
    },
     'Social Media and Digital Media and Streaming': {
        'x_axis': ['Content length', 'Posting frequency', 'Hashtag use count', 'Follower count', 'Ad spend'],
        'y_axis': ['Engagement rate', 'View count', 'Shares', 'New followers', 'Conversion rate']
    }
}

# 坐标轴标签对应的典型范围和单位 (Keep as is)
axis_info: Dict[str, Tuple[float, float, str]] = {
    'Household income': (20000, 200000, '$'),
    'Parental education': (0, 20, 'years'),
    'School funding': (5000, 25000, '$/student'),
    'Study hours': (1, 40, 'hours/week'),
    'Class size': (10, 40, 'students'),
    'Academic performance': (0, 100, 'score'),
    'Graduation rate': (50, 100, '%'),
    'Test scores': (400, 1600, 'score'), # e.g., SAT
    'College admission': (0, 100, '%'),
    'Literacy rate': (70, 100, '%'),

    'Distance traveled': (1, 1000, 'miles'),
    'Fuel cost': (2, 5, '$/gallon'),
    'Delivery time': (0.5, 10, 'hours'),
    'Vehicle age': (0, 15, 'years'),
    'Traffic volume': (1000, 100000, 'vehicles/day'),
    'Transport efficiency': (50, 95, '%'),
    'Cost per mile': (0.5, 5, '$'),
    'On-time rate': (70, 100, '%'),
    'Fuel efficiency': (15, 50, 'mpg'),
    'Customer satisfaction': (1, 5, 'rating'),

    'Patient age': (0, 100, 'years'),
    'BMI': (15, 40, 'kg/m²'),
    'Blood pressure': (80, 180, 'mmHg'),
    'Treatment dosage': (10, 1000, 'mg'),
    'Hospital stay duration': (1, 30, 'days'),
    'Recovery time': (1, 90, 'days'),
    'Treatment cost': (100, 50000, '$'),
    'Patient satisfaction': (1, 5, 'rating'),
    'Readmission rate': (0, 30, '%'),
    'Survival rate': (50, 100, '%'),

    'Interest rate': (0.1, 10, '%'),
    'Inflation rate': (-2, 10, '%'),
    'GDP growth': (-5, 10, '%'),
    'Unemployment rate': (2, 20, '%'),
    'Stock price': (1, 5000, '$'),
    'Consumer spending': (1000, 100000, '$'),
    'Investment rate': (5, 50, '%'),
    'Business confidence': (0, 100, 'index'),
    'Housing starts': (50000, 200000, 'units/month'),
    'Exchange rate': (0.5, 2.0, 'currency/USD'),

    'CO2 emissions': (1, 100, 'tons/year'),
    'Average temperature': (0, 30, '°C'),
    'Rainfall amount': (100, 2000, 'mm/year'),
    'Forest cover': (10, 90, '%'),
    'Pollution level': (10, 100, 'index'),
    'Species diversity': (1, 1000, 'count'),
    'Crop yield': (1, 10, 'tons/hectare'), # Duplicate, already added above
    'Water quality': (0, 100, 'index'),
    'Air quality': (0, 100, 'index'),
    'Glacier size': (1, 1000, 'km²'),

    'R&D investment': (100000, 100000000, '$'),
    'Patent count': (1, 1000, 'count'),
    'Internet speed': (10, 1000, 'Mbps'),
    'Smartphone penetration': (20, 95, '%'),
    'Data usage': (1, 1000, 'GB/month'),
    'Productivity growth': (0, 10, '%'),
    'Startup success rate': (5, 50, '%'),
    'Digital literacy': (0, 100, 'index'),
    'E-commerce sales': (10000, 1000000000, '$'),
    'Innovation index': (0, 100, 'score'),

    'Advertising spend': (1000, 1000000, '$'),
    'Customer acquisition cost': (10, 500, '$'),
    'Website traffic': (1000, 10000000, 'visits/month'),
    'Email open rate': (5, 50, '%'),
    'Sales team size': (1, 100, 'people'),
    'Conversion rate': (0, 10, '%'),
    'Customer lifetime value': (50, 5000, '$'),
    'Bounce rate': (10, 80, '%'),
    'Click-through rate': (0.1, 10, '%'),
    'Revenue': (10000, 1000000000, '$'),

    'Employee training hours': (1, 50, 'hours/year'),
    'Years of experience': (0, 30, 'years'),
    'Salary': (30000, 200000, '$/year'),
    'Commute time': (5, 90, 'minutes'),
    'Team size': (2, 20, 'people'),
    'Job satisfaction': (1, 5, 'rating'),
    'Employee retention': (50, 95, '%'),
    'Productivity': (50, 150, 'index'),
    'Absenteeism': (0, 10, 'days/year'),
    'Promotion rate': (0, 20, '%'),

    'Fertilizer usage': (10, 500, 'kg/hectare'),
    'Irrigation amount': (100, 2000, 'mm/season'),
    'Sunlight hours': (4, 12, 'hours/day'),
    'Pest control spending': (10, 500, '$/hectare'),
    'Farm size': (1, 1000, 'hectares'),
    'Crop yield': (1, 10, 'tons/hectare'), # Duplicate, already added above
    'Food production cost': (100, 2000, '$/ton'),
    'Soil quality': (0, 100, 'index'),
    'Product freshness': (1, 5, 'rating'),
    'Livestock health': (1, 5, 'rating'),

    'Energy consumption': (1000, 1000000, 'kWh/month'),
    'Renewable energy share': (0, 100, '%'),
    'Electricity price': (0.1, 0.5, '$/kWh'),
    'Grid stability': (0, 100, 'index'),
    'Infrastructure age': (0, 50, 'years'),
    'Carbon footprint': (1, 50, 'tons CO2e/year'),
    'Energy efficiency': (0, 100, '%'),
    'Customer outage duration': (0, 24, 'hours/year'),
    'Service cost': (50, 500, '$/month'),
    'Reliability index': (0, 100, 'score'),

    'Store size': (100, 10000, 'm³'),
    'Product price': (1, 1000, '$'),
    'Promotional spending': (100, 100000, '$'),
    'Customer reviews count': (1, 10000, 'count'),
    'Checkout time': (0, 10, 'minutes'),
    'Sales volume': (100, 1000000, 'units/month'),
    # 'Customer satisfaction': (1, 5, 'rating'), # Duplicate
    'Average transaction value': (10, 500, '$'),
    'Return rate': (0, 20, '%'),
    'Foot traffic': (100, 100000, 'people/day'),

    'Training hours': (1, 40, 'hours/week'),
    'Athlete age': (15, 40, 'years'),
    'Nutrition intake': (1000, 5000, 'calories/day'),
    'Sleep duration': (4, 10, 'hours/night'),
    'Injury frequency': (0, 5, 'injuries/year'),
    'Performance score': (0, 100, 'score'),
    'Recovery time': (0.5, 7, 'days'),
    'Endurance level': (0, 100, 'index'),
    'Strength gain': (0, 50, '%'),
    'Win rate': (0, 100, '%'),

    'Hotel price': (50, 1000, '$/night'),
    'Attraction popularity': (100, 1000000, 'visitors/year'),
    'Travel distance': (10, 5000, 'miles'),
    'Marketing budget': (1000, 1000000, '$'),
    'Seasonality index': (0, 10, 'index'),
    'Occupancy rate': (30, 100, '%'),
    'Visitor spending': (50, 5000, '$/day'),
    'Booking conversion': (0, 20, '%'),
    'Repeat visitor rate': (0, 80, '%'),
    'Customer reviews score': (1, 5, 'rating'),

    'Property size': (500, 10000, 'm³'),
    'Construction cost': (100, 500, '$/m³'),
    'Location score': (1, 10, 'score'),
    # 'Interest rate': (0.1, 10, '%'), # Duplicate
    'Development density': (1, 100, 'units/acre'),
    'Property value': (50000, 5000000, '$'),
    'Rental yield': (1, 10, '%'),
    'Construction time': (1, 24, 'months'),
    'Vacancy rate': (0, 20, '%'),
    'Sales price per m³': (50, 1000, '$/m³'),

    'Content length': (1, 60, 'minutes'),
    'Posting frequency': (1, 20, 'posts/day'),
    'Hashtag use count': (1, 20, 'count/post'),
    'Follower count': (100, 10000000, 'count'),
    'Ad spend': (100, 100000, '$'),
    'Engagement rate': (0, 20, '%'),
    'View count': (100, 10000000, 'count'),
    'Shares': (10, 100000, 'count'),
    'New followers': (10, 100000, 'count/day'),
    # 'Conversion rate': (0, 10, '%'), # Duplicate
}


# Define diverse English descriptors for constructing the little theme "the xx of main theme"
ENGLISH_DESCRIPTORS = [
    "Relationship", "Correlation", "Distribution", "Analysis", "Overview",
    "Comparison", "Interaction", "Influence", "Pattern", "Dynamics", "Trend"
]

# Sanitize text for use in filenames (Copied from other scripts for consistency)
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


# (Keep DataGenerator class definition if needed, though not used in main scatter logic)
class DataGenerator:
     # ... (original DataGenerator code, not strictly needed for scatter generation) ...
     pass

# (Keep generate_scatter_data function as is)
def generate_scatter_data(trend: str, correlation: str, overlap_degree: float,
                          strength_range: Tuple[float, float], num_records: int,
                          x_min_target: float, x_max_target: float,
                          y_min_target: float, y_max_target: float,
                          x_col_name: str = 'x_value', y_col_name: str = 'y_value') -> Tuple[pd.DataFrame, float]:
    """
    Generates scatter plot data based on trend, correlation, and target ranges.
    """
    strength = random.uniform(*strength_range)
    x_values_base = np.linspace(0, 100, num_records)

    if trend not in TREND_TYPES: raise ValueError(f"Invalid trend type. Must be one of {TREND_TYPES}")
    if correlation not in CORRELATION_TYPES: raise ValueError(f"Invalid correlation type. Must be one of {CORRELATION_TYPES}")
    if not 0 <= overlap_degree <= 1: raise ValueError("Overlap degree must be between 0 and 1")
    if any(not 0 <= s <= 1 for s in strength_range): raise ValueError("Strength range must be between 0 and 1")
    if num_records < 2: raise ValueError("Number of records must be at least 2")
    if x_min_target >= x_max_target: x_max_target = x_min_target + 1
    if y_min_target >= y_max_target: y_max_target = y_min_target + 1

    # Generate base Y data (relative to 0-100 scale)
    if trend == 'linear':
        if correlation == 'positive':
            slope = (strength * 0.5); noise_scale = (1 - strength) * 50
            y_values_base = slope * x_values_base + np.random.normal(0, noise_scale, num_records)
        elif correlation == 'negative':
            slope = -(strength * 0.5); noise_scale = (1 - strength) * 50
            y_values_base = slope * x_values_base + np.random.normal(0, noise_scale, num_records) + (strength * 50)
        elif correlation == 'none':
            y_values_base = np.random.normal(50, 30, num_records)
    elif trend == 'exponential':
        x_normalized = x_values_base / 100
        if correlation == 'positive':
            base = 30 + np.random.normal(0, 15, num_records)
            exp_component = 70 * strength * (np.exp(3 * strength * x_normalized) - 1)
            y_values_base = base + exp_component
        elif correlation == 'negative':
            exp_component = np.exp(-strength * x_normalized * 10) if strength > 0 else 1
            y_values_base = 100 * exp_component + np.random.normal(0, 10 * (1-strength) + 5, num_records) # Adjusted noise
        elif correlation == 'none':
            y_values_base = 50 + np.random.normal(0, 30, num_records)
    elif trend == 'u_shape':
        noise_scale_u = 10 * (1 - strength) + 5 # Noise depends on inverse of strength
        if correlation == 'positive':
            y_values_base = (strength * 0.1) * (x_values_base - 50) ** 2 + np.random.normal(0, noise_scale_u, num_records)
        elif correlation == 'negative':
            x_normalized = (x_values_base - 50) / 50
            y_values_base = -80 * strength * (x_normalized ** 2 - 0.2) + 70
            boundary_effect = np.where(x_values_base < 30, (30 - x_values_base) * 0.8, np.where(x_values_base > 70, (x_values_base - 70) * 0.8, 0))
            y_values_base -= boundary_effect
            y_values_base += np.random.normal(0, noise_scale_u / 1.5, num_records) # Slightly less noise for negative U
        elif correlation == 'none':
             y_values_base = np.random.normal(50, 15, num_records) # Less variance for none correlation U-shape

    # Add overlap noise
    if overlap_degree > 0:
        overlap_indices = np.random.choice(num_records, int(num_records * overlap_degree), replace=False)
        y_values_base[overlap_indices] += np.random.normal(0, 15 * overlap_degree, len(overlap_indices)) # Noise scale depends on overlap degree

    # --- Dynamic Scaling ---
    x_values_scaled = x_min_target + (x_values_base / 100) * (x_max_target - x_min_target)
    y_min_base, y_max_base = np.min(y_values_base), np.max(y_values_base)
    if y_min_base == y_max_base:
         y_values_scaled = np.full_like(y_values_base, (y_min_target + y_max_target) / 2)
    else:
         y_values_scaled = y_min_target + ((y_values_base - y_min_base) * (y_max_target - y_min_target) / (y_max_base - y_min_base))

    # Optional: Clip to target range if strict bounds are needed
    # x_values_scaled = np.clip(x_values_scaled, x_min_target, x_max_target)
    # y_values_scaled = np.clip(y_values_scaled, y_min_target, y_max_target)

    return pd.DataFrame({x_col_name: x_values_scaled, y_col_name: y_values_scaled}), strength


# --- MODIFICATION START: Update save_scatter_to_csv ---
def save_scatter_to_csv(data: pd.DataFrame, topic: str, topic_seq_num: int, # Added topic_seq_num
                        actual_corr: float, trend: str, correlation: str,
                        x_col_name: str, y_col_name: str, x_unit: str, y_unit: str) -> str: # Removed global_file_index
    """
    Saves scatter data to CSV with the specified header format.

    Args:
        data: The DataFrame containing scatter data.
        topic: The data topic (Main theme).
        topic_seq_num: The sequence number for the file within its topic (1-based).
        actual_corr: The calculated actual correlation (no longer saved in header).
        trend: The generated trend type.
        correlation: The generated correlation type.
        x_col_name: Name of the X column.
        y_col_name: Name of the Y column.
        x_unit: Unit for the X axis.
        y_unit: Unit for the Y axis.

    Returns:
        The path to the saved CSV file.
    """
    # --- MODIFICATION START: Change output directory ---
    output_dir = './scatter/csv'
    # --- MODIFICATION END: Change output directory ---
    os.makedirs(output_dir, exist_ok=True)

    # Sanitize the topic name for the filename
    sanitized_topic = sanitize_filename(topic)
    # Construct filename: scatter_主题名_xx.csv
    filename = os.path.join(output_dir, f"scatter_{sanitized_topic}_{topic_seq_num}.csv")
    # --- MODIFICATION END: Update filename format ---

    # Generate little theme
    selected_descriptor = random.choice(ENGLISH_DESCRIPTORS)
    little_theme = f"the {selected_descriptor} of {topic}"

    # Construct the first header line (Main theme, little theme, trend, correlation)
    # Removed Actual Correlation as requested
    header_line_1 = f"{topic},{little_theme},{trend},{correlation}"

    # Construct the second header line (x_col_name (unit), y_col_name (unit))
    # Units are moved here as requested
    header_line_2 = f"{x_col_name} ({x_unit}),{y_col_name} ({y_unit})"

    # Round data to 2 decimal places before saving
    data_to_save = data.copy()
    # Ensure column order matches header_line_2
    data_to_save = data_to_save[[x_col_name, y_col_name]] # Select columns in order
    data_to_save[x_col_name] = data_to_save[x_col_name].round(2)
    data_to_save[y_col_name] = data_to_save[y_col_name].round(2)


    with open(filename, 'w', newline='') as f:
        # Write the custom header lines
        f.write(header_line_1 + "\n")
        f.write(header_line_2 + "\n")
        # Write the DataFrame data WITHOUT its header, and without index
        # header=False is crucial here as we wrote the headers manually
        data_to_save.to_csv(f, index=False, header=False)

    return filename
# --- MODIFICATION END ---


def main(num_files):
    # Data generation parameters (can be randomized per loop)
    trend_pattern = TREND_TYPES
    correlation_pattern = CORRELATION_TYPES
    strength_range = (0.4, 0.9) # Strength range (avoiding very weak correlations)

    # --- MODIFICATION START: Use topic counter ---
    topic_file_counters: Dict[str, int] = {} # Track file count per topic
    # --- MODIFICATION END ---

    generated_files = 0
    print(f"Starting data generation for {num_files} scatter plot files.")

    while generated_files < num_files:
        try:
            # Randomly select topic, axes, trend, correlation, etc. for each file
            topic = random.choice(list(topics_axes.keys()))
            # Ensure axis names exist in axis_info, otherwise skip this combination
            possible_x = [ax for ax in topics_axes[topic]['x_axis'] if ax in axis_info]
            possible_y = [ax for ax in topics_axes[topic]['y_axis'] if ax in axis_info]
            if not possible_x or not possible_y:
                print(f"Warning: Skipping topic '{topic}' because valid X/Y axes with info not found.")
                continue # Skip to next iteration of the while loop

            x_name = random.choice(possible_x)
            y_name = random.choice(possible_y)

            trend = random.choice(trend_pattern)
            # Adjust correlation possibilities based on trend
            if trend == 'u_shape':
                 # U-shape 'none' correlation often looks similar to positive/negative
                 # Let's bias away from 'none' for U-shape to make trends clearer
                 correlation = random.choice(['positive', 'negative'])
                 # For U-shape, strength affects the curve steepness/depth
                 current_strength_range = (0.5, 1.0) # Ensure U-shape is pronounced
            else:
                 correlation = random.choice(correlation_pattern)
                 current_strength_range = strength_range # Use standard strength range

            overlap_degree = random.randint(0, 7) / 10.0
            num_records = random.randint(30, 100)

            x_min_target, x_max_target, x_unit = axis_info[x_name]
            y_min_target, y_max_target, y_unit = axis_info[y_name]

            data, actual_strength = generate_scatter_data(
                trend=trend, correlation=correlation, overlap_degree=overlap_degree,
                strength_range=current_strength_range, num_records=num_records,
                x_min_target=x_min_target, x_max_target=x_max_target,
                y_min_target=y_min_target, y_max_target=y_max_target,
                x_col_name=x_name, y_col_name=y_name
            )

            # Calculate actual correlation (still useful for logging/debugging, but not saved in header)
            actual_corr = np.nan # Default to NaN
            # Check for sufficient variance before calculating correlation
            if data[x_name].nunique() > 1 and data[y_name].nunique() > 1:
                try:
                    actual_corr = np.corrcoef(data[x_name], data[y_name])[0, 1]
                except Exception: # Catch potential errors in corrcoef if data is weird
                    print(f"Warning: Could not calculate correlation for file {generated_files + 1}.")


            # --- MODIFICATION START: Increment topic counter and pass to save ---
            if topic not in topic_file_counters:
                topic_file_counters[topic] = 0
            topic_file_counters[topic] += 1
            current_topic_seq_num = topic_file_counters[topic]

            output_file = save_scatter_to_csv( # Use the updated function
                data=data,
                topic=topic,
                topic_seq_num=current_topic_seq_num, # Pass the topic-specific counter
                actual_corr=actual_corr, # Pass actual correlation (ignored in header)
                trend=trend,
                correlation=correlation,
                x_col_name=x_name,
                y_col_name=y_name,
                x_unit=x_unit,
                y_unit=y_unit
            )
            # --- MODIFICATION END ---

            generated_files += 1 # Increment successful count

            print(f"Generated file {generated_files}/{num_files}:") # Use global counter
            print(f"  Topic: {topic} (Seq: {current_topic_seq_num})") # Print topic and sequence number
            print(f"  X-axis: {x_name} ({x_unit})")
            print(f"  Y-axis: {y_name} ({y_unit})")
            print(f"  Trend: {trend}, Correlation Type: {correlation}")
            print(f"  Num Records: {num_records}")
            print(f"  Actual Correlation: {actual_corr:.2f}" if pd.notna(actual_corr) else "Actual Correlation: N/A") # Still print for info
            # print(f"  Strength Used: {actual_strength:.2f}") # Optional: print strength
            print(f"  Saved to {output_file}\n")


        except ValueError as e: print(f"Error generating data (ValueError): {e}. Skipping.")
        except Exception as e:
             import traceback
             print(f"An unexpected error occurred: {e}. Skipping.")
             traceback.print_exc()

    print(f"Finished generating {generated_files} scatter plot data files.")


if __name__ == "__main__":
    num_files = 10  # Specify the number of files to generate
    main(num_files)
