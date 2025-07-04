# File: bubble_vis.py - Combined Matplotlib and Plotly versions

# --- Common Imports ---
import pandas as pd
import numpy as np
import os
import re
import glob
import random
import traceback
from typing import Dict, Any, List, Tuple
import textwrap
import math # Import math for log10, floor

# --- Matplotlib Imports (for PNG generation) ---
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import rcParams # Keep rcParams for Matplotlib formatting
import adjustText as adjust_text # Keep adjustText for Matplotlib label placement

# --- Plotly Imports (for SVG generation) ---
import plotly.graph_objects as go
import plotly.io as pio
import plotly.colors as pcolors # Import Plotly colors
import plotly.express as px # Added for potential future use or alternative color sequences


# --- Matplotlib Specific Configuration and Formatting ---

def apply_chart_formatting():
    """Adds 'Times New Roman' to the font list and applies the specified formatting for Matplotlib (Original Version)."""
    # Ensure Times New Roman is available, fallback to serif
    # Using rcParams directly as in the original code
    rcParams['font.family'] = ['Times New Roman', 'serif']
    rcParams['text.color'] = '#000000'
    rcParams['axes.labelcolor'] = '#000000'
    rcParams['xtick.labelcolor'] = '#000000'
    rcParams['ytick.labelcolor'] = '#000000'
    rcParams['legend.labelcolor'] = '#000000'
    rcParams['figure.facecolor'] = 'white'
    rcParams['axes.facecolor'] = 'white'
    rcParams['axes.linewidth'] = 1.0
    rcParams['xtick.major.width'] = 1.0
    rcParams['ytick.major.width'] = 1.0
    rcParams['axes.edgecolor'] = '#000000'
    rcParams['axes.titlesize'] = 16 # Adjusted for potentially longer titles
    rcParams['axes.labelsize'] = 14
    rcParams['xtick.labelsize'] = 12
    rcParams['ytick.labelsize'] = 12
    rcParams['legend.fontsize'] = 10 # Base legend font size
    rcParams['axes.grid'] = False
    rcParams['grid.alpha'] = 0.0
    # Original code had these False - keeping consistent with original code
    rcParams['axes.spines.top'] = False
    rcParams['axes.spines.right'] = False


# --- Plotly Specific Configurations ---

# Define a list of suitable single colors for drawing bubbles using Plotly's qualitative sequences
# Avoid sequences known for yellow or very light/dark extremes if possible, or rely on random chance.
PLOTLY_QUALITATIVE_COLOR_SEQUENCES = [
    pcolors.qualitative.Plotly,
    pcolors.qualitative.D3,
    pcolors.qualitative.G10,
    pcolors.qualitative.T10,
    pcolors.qualitative.Alphabet,
    pcolors.qualitative.Dark24,
    pcolors.qualitative.Light24,
    pcolors.qualitative.Prism,
    pcolors.qualitative.Vivid,
    pcolors.qualitative.Bold,
    pcolors.qualitative.Safe,
    pcolors.qualitative.Pastel,
    # Removed LightQualitative as it caused the AttributeError
    # pcolors.qualitative.LightQualitative
]

# Helper function to check if a color string represents yellow (basic heuristic, adapted for Plotly color strings)
def is_yellow_like_plotly(color_str: str) -> bool:
    """检测颜色是否为黄色系"""
    try:
        if color_str.startswith('#'):
            if len(color_str) == 7:
                r = int(color_str[1:3], 16) / 255.0
                g = int(color_str[3:5], 16) / 255.0
                b = int(color_str[5:7], 16) / 255.0
            elif len(color_str) == 4:
                r = int(color_str[1], 16) / 15.0
                g = int(color_str[2], 16) / 15.0
                b = int(color_str[3], 16) / 15.0
            else: return False
        elif color_str.startswith('rgb'):
            match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', color_str)
            if match:
                r = int(match.group(1)) / 255.0
                g = int(match.group(2)) / 255.0
                b = int(match.group(3)) / 255.0
            else: return False
        elif color_str in pcolors.named_colors:
            # This check is imperfect for named colors but better than nothing
            # Could potentially map popular names like 'yellow', 'gold', 'orange'
            lower_color_str = color_str.lower()
            if 'yellow' in lower_color_str or 'gold' in lower_color_str:
                 return True
            # For other named colors, rely on the RGB check if possible, or assume not yellow
            # A more robust check would involve looking up the named color's RGB value
            return False
        else:
            return False

        # Basic heuristic: high red, high green, low blue
        # Adjust thresholds slightly to be more inclusive of yellow-ish colors
        yellow_threshold_r = 0.6
        yellow_threshold_g = 0.6
        yellow_threshold_b = 0.5
        return r > yellow_threshold_r and g > yellow_threshold_g and b < yellow_threshold_b
    except Exception:
        return False


# --- Data Reading and Parsing (Keep as is) ---

def parse_label_unit(label_str: str) -> Tuple[str, str]:
    """
    Parses a string like 'Label (Unit)' or 'Label' into label and unit.
    """
    label_str = label_str.strip()
    match = re.match(r'^(.*?)\s*\((.*?)\)$', label_str)
    if match:
        label_part = match.group(1).strip()
        unit = match.group(2).strip()
        return label_part, unit
    else:
        return label_str, ""


# --- parse_bubble_csv (Keep the latest version) ---
def parse_bubble_csv(filepath: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Reads the bubble chart CSV file (new format) and parses its metadata.
    Expected header format on first line (6 fields):
    Main theme, little theme, {x_col_name} ({x_unit}), {y_col_name} ({y_unit}), {size_meaning} ({size_unit}), Size Distribution
    Expected data starts from the second line WITHOUT a header row.

    Args:
        filepath: Path to the CSV file.

    Returns:
        A tuple containing:
            - pd.DataFrame: The data from the CSV with columns correctly named.
            - Dict[str, Any]: A dictionary containing the parsed metadata.
    Raises:
         FileNotFoundError, ValueError, Exception for errors.
    """
    metadata: Dict[str, Any] = {}
    df = pd.DataFrame()

    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found at {filepath}")

        # Read the first line (custom header) separately
        with open(filepath, 'r', encoding='utf-8') as f:
            header_line_content = f.readline().strip()

        # Parse the custom header line
        parts = [part.strip() for part in header_line_content.split(',')]
        # --- MODIFICATION: Expected parts changed from 7 to 6 ---
        expected_parts = 6
        if len(parts) != expected_parts:
            raise ValueError(
                f"Incorrect header format in {filepath}. Expected {expected_parts} parts separated by commas, "
                f"but found {len(parts)}. Header content: '{header_line_content}'"
            )

        metadata['Topic'] = parts[0]
        metadata['Little_Theme'] = parts[1]

        # Parse X and Y columns and units from the first line metadata
        x_info_str = parts[2]
        y_info_str = parts[3]
        size_info_str = parts[4] # The 5th part is now size_meaning (size_unit)

        x_col_name_in_df, x_unit_display = parse_label_unit(x_info_str)
        y_col_name_in_df, y_unit_display = parse_label_unit(y_info_str)
        parsed_size_meaning, parsed_size_unit_display = parse_label_unit(size_info_str)


        # Store actual column names needed for DataFrame access
        metadata['X_col'] = x_col_name_in_df
        metadata['Y_col'] = y_col_name_in_df
        # For DataFrame column name, use the descriptive part of the 5th header field
        metadata['Size_col'] = parsed_size_meaning # Use the descriptive part as the column name for size data


        # Store display units
        metadata['X_unit_display'] = x_unit_display
        metadata['Y_unit_display'] = y_unit_display
        metadata['Size_unit_display'] = parsed_size_unit_display # This is the unit for size

        # Store the original strings including unit for axis labels and legend title
        metadata['X_label_display'] = x_info_str
        metadata['Y_label_display'] = y_info_str
        metadata['Size_label_with_unit'] = size_info_str # Store the 5th part directly

        metadata['Size Distribution'] = parts[5] # The 6th part is now Size Distribution


        # Read the actual data, starting from the second line (skiprows=1)
        df = pd.read_csv(filepath, skiprows=1, header=None, encoding='utf-8', index_col=False)

        expected_data_cols = 3
        if df.shape[1] < expected_data_cols:
             raise ValueError(f"Data section in {filepath} has fewer than {expected_data_cols} columns. Expected {expected_data_cols}, found {df.shape[1]}.")
        elif df.shape[1] > expected_data_cols:
             print(f"Warning: Data section in {filepath} has more than {expected_data_cols} columns. Using first {expected_data_cols}.")
             df = df.iloc[:, :expected_data_cols]

        # Assign the correct column names derived from the metadata
        # The DataFrame columns should correspond to X, Y, and the conceptual Size metric
        df.columns = [metadata['X_col'], metadata['Y_col'], metadata['Size_col']]

        # Ensure data columns are numeric
        cols_to_convert = [metadata['X_col'], metadata['Y_col'], metadata['Size_col']]
        for col in cols_to_convert:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Rounding might not be needed for plotting, but keep for consistency with Matplotlib version data processing
                # df[col] = df[col].round(2) # Removed rounding here, let formatting handle it.
                if df[col].isnull().any():
                    print(f"Warning: Column '{col}' in {filepath} contains non-numeric values after conversion. Invalid values treated as NaN.")
            else:
                 # This should ideally not happen if names argument in read_csv is correct
                 raise ValueError(f"Logic Error: Column '{col}' not found after assignment for {filepath}.")

    except FileNotFoundError:
        raise
    except ValueError as ve:
        print(f"Error details for ValueError: {ve}") # Print more details for ValueError
        raise ve
    except Exception as e:
        raise Exception(f"Error reading or parsing CSV file {filepath}: {e}") from e

    return df, metadata
# --- END parse_bubble_csv ---


# --- Format number with units (Keep as is) ---
def format_number_with_unit(number: float) -> str:
    """
    Formats a number with appropriate unit suffixes (k, M, B, T)
    for better readability in labels.
    """
    if pd.isna(number):
        return ""
    abs_number = abs(number)
    if abs_number >= 1e12: return f"{number / 1e12:.1f}T"
    elif abs_number >= 1e9: return f"{number / 1e9:.1f}B"
    elif abs_number >= 1e6: return f"{number / 1e6:.1f}M"
    elif abs_number >= 1e3: return f"{number / 1e3:.1f}k"
    else:
        # Check if it's an integer like value
        if abs(number - round(number)) < 1e-9:
            return f"{int(round(number))}"
        else:
            # Format to 2 decimal places, strip trailing zeros and decimal if integer
            formatted = f"{number:.2f}"
            # Remove trailing .00 or .0 if the number is effectively an integer
            if formatted.endswith('.00'):
                return formatted[:-3]
            if formatted.endswith('.0'):
                 return formatted[:-2]
            # Remove trailing zeros if not .00, but keep decimal if needed
            return formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted

# --- END Format number with units ---

# --- Helper function to determine scale factor and prefix for Plotly axis title ---
def get_scale_factor_and_prefix(max_value: float) -> Tuple[float, str]:
    """
    Determines the appropriate scale factor (1, 1000, 1e6, etc.) and its prefix string ( "", "1e3", "1e6", etc.)
    based on the max value. Used for Plotly axis titles and scaling data.
    Handles positive and negative maximums.
    """
    if pd.isna(max_value) or max_value == 0:
        return 1.0, ""

    # Use the absolute maximum value to determine the scale
    abs_max_value = abs(max_value)

    # Determine the power of 10 that is a multiple of 3, less than or equal to log10(abs_max_value)
    # Use a small epsilon for log10(0) case, though abs_max_value == 0 is handled above
    epsilon = 1e-9
    try:
        log_val = math.log10(max(abs_max_value, epsilon))
        # Find the power of 10 that is a multiple of 3, less than or equal to log_val
        # Ensure we don't get negative powers for small numbers > 1
        power_of_10 = max(0, math.floor(log_val / 3) * 3)

        factor = 10**power_of_10
        # Construct prefix string like "1e3", "1e6"
        if power_of_10 > 0:
            # Use scientific notation for the prefix
            prefix_str = f"1e{power_of_10}"
        else:
             prefix_str = "" # No prefix for factor 1

        return factor, prefix_str
    except ValueError: # log10(0) case, though handled, defensive
        return 1.0, ""
    except Exception: # Catch other potential math errors
         return 1.0, ""


# --- Original Matplotlib Plotting Function (for PNG) ---
# Renamed from plot_bubble_chart to plot_bubble_chart_matplotlib
def plot_bubble_chart_matplotlib(df: pd.DataFrame, metadata: Dict[str, Any]) -> plt.Figure:
    """
    Creates a bubble chart visualization using Matplotlib from the DataFrame and metadata.
    Includes original size scaling, adjustText for labels, and legend.

    Args:
        df: DataFrame containing the data.
        metadata: Dictionary containing chart metadata.

    Returns:
        plt.Figure: The Matplotlib figure object.
    """
    x_col = metadata['X_col']
    y_col = metadata['Y_col']
    size_col = metadata['Size_col']

    # Use Little_Theme directly as the chart title
    chart_title = metadata.get('Little_Theme', 'Bubble Chart Analysis')

    x_unit_str = str(metadata.get('X_unit_display', ''))
    y_unit_str = str(metadata.get('Y_unit_display', ''))
    size_label_with_unit = metadata.get('Size_label_with_unit', size_col) # Use original string for legend title


    # Apply original Matplotlib formatting
    apply_chart_formatting()

    # Use original figsize
    fig, ax = plt.subplots(figsize=(10, 7.5)) # <-- Original figsize


    # Filter out rows with NaN in critical columns for plotting
    required_cols = [x_col, y_col, size_col]
    plot_df = df.dropna(subset=required_cols).copy()

    if plot_df.empty:
         print("Warning: No valid data points to plot for Matplotlib chart after dropping NaNs. Plot will be empty.")
         # Set default limits if no data
         ax.set_xlim(0, 1); ax.set_ylim(0, 1) # Set some small default range
         # Set labels and title even for empty plot
         x_label_full = x_col
         if x_unit_str: x_label_full += f" ({x_unit_str})"
         y_label_full = y_col
         if y_unit_str: y_label_full += f" ({y_unit_str})"
         ax.set_xlabel(x_label_full)
         ax.set_ylabel(y_label_full)
         ax.set_title(chart_title, pad=20, fontsize=rcParams['axes.titlesize'])
         # Apply spine visibility based on original settings (top/right False)
         for spine in ['top', 'right']: ax.spines[spine].set_visible(False) # <-- Original was False
         for spine in ['bottom', 'left']: ax.spines[spine].set_visible(True) # Original was True
         plt.tight_layout()
         return fig


    # --- Scale bubble sizes for display (using Matplotlib's 's' parameter which is area) ---
    # Original Matplotlib code used radius 3-6, area pi*3^2 to pi*6^2 (approx 28 to 113)
    # Request: min radius 10, max radius 20.
    # Corresponding areas: pi*10^2 to pi*20^2 (approx 314 to 1256)
    min_display_radius = 10 # <-- Original min radius
    max_display_radius = 20 # <-- Original max radius
    min_display_size_area = np.pi * (min_display_radius ** 2) # Minimum bubble area for display <-- DEFINED HERE
    max_display_size_area = np.pi * (max_display_radius ** 2) # Maximum bubble area for display <-- DEFINED HERE


    valid_sizes = plot_df[size_col].astype(float)

    # Calculate min/max or quantiles for scaling, handle edge cases
    q_min = valid_sizes.min() if len(valid_sizes) > 0 and not valid_sizes.empty and pd.notna(valid_sizes.min()) else 0.0
    q_max = valid_sizes.max() if len(valid_sizes) > 0 and not valid_sizes.empty and pd.notna(valid_sizes.max()) else 0.0

    # Initialize display_sizes_area with a default size
    display_sizes_area = np.full(len(plot_df), (min_display_size_area + max_display_size_area) / 2.0, dtype=float)


    interp_q_min = q_min
    interp_q_max = q_max

    # Use quantiles for scaling if enough data points (>= 20), otherwise use actual min/max
    if len(valid_sizes) >= 20 and q_min != q_max: # Add check for q_min != q_max
        # Ensure quantiles are not NaN
        q_05 = valid_sizes.quantile(0.05)
        q_95 = valid_sizes.quantile(0.95)
        if pd.notna(q_05) and pd.notna(q_95) and q_05 != q_95:
             interp_q_min = q_05
             interp_q_max = q_95
        elif q_min != q_max: # Fallback to actual min/max if quantiles are bad
             interp_q_min = q_min
             interp_q_max = q_max
        # else: interp_q_min, interp_q_max remain q_min, q_max (which are identical)
    elif len(valid_sizes) > 1 and q_min != q_max: # Add check for q_min != q_max
        interp_q_min = q_min
        interp_q_max = q_max
    # If len(valid_sizes) is 0 or 1, or q_min == q_max, interp_q_min and interp_q_max remain q_min/q_max (which might be identical or 0)


    if interp_q_min != interp_q_max:
        # Scale the size values from the data range to the desired area range
        display_sizes_area = np.interp(plot_df[size_col].astype(float),
                               (float(interp_q_min), float(interp_q_max)),
                               (min_display_size_area, max_display_size_area))
        # Ensure display sizes are within the min/max area range
        display_sizes_area = np.clip(display_sizes_area, min_display_size_area, max_display_size_area)
    elif len(valid_sizes) > 0 and pd.notna(valid_sizes.iloc[0]):
         # If interp_q_min == interp_q_max (meaning all valid data points have the same size),
         # set all display sizes to the average of min/max display area
         uniform_area = (min_display_size_area + max_display_size_area) / 2.0
         display_sizes_area = np.full(len(plot_df), uniform_area, dtype=float)
         print(f"Warning: Scaled size data range for column '{size_col}' is zero (all valid values are identical). Using uniform bubble size ({np.sqrt(display_sizes_area[0]/np.pi):.1f}px radius).")
    else:
        # Case with no valid sizes or only NaN
        print(f"Warning: No valid numeric values in size column '{size_col}'. Using uniform bubble size ({(min_display_radius + max_display_radius) / 2.0 :.1f}px radius).")
        uniform_area = (min_display_size_area + max_display_size_area) / 2.0
        display_sizes_area = np.full(len(plot_df), uniform_area, dtype=float)


    # --- Sort data by calculated display size descending for correct plotting order (larger bubbles underneath) ---
    # Add the calculated areas as a temporary column for sorting
    plot_df['__display_size_area__'] = display_sizes_area
    plot_df_sorted = plot_df.sort_values(by='__display_size_area__', ascending=False).reset_index(drop=True).copy()
    # Get the sorted areas array
    display_sizes_area_sorted = plot_df_sorted['__display_size_area__'].values
    # Remove the temporary column from the sorted DataFrame
    plot_df_sorted = plot_df_sorted.drop(columns=['__display_size_area__'])


    # --- Select a single random color (using Matplotlib's default cycle) ---
    # Get the default color cycle
    prop_cycle = plt.rcParams['axes.prop_cycle']
    default_colors = prop_cycle.by_key()['color']
    # Select a random color from the default cycle
    selected_color = random.choice(default_colors)

    fixed_alpha = 0.7 # Original alpha


    # Plot scatter points using the sorted data and calculated areas
    ax.scatter(plot_df_sorted[x_col], plot_df_sorted[y_col],
               s=display_sizes_area_sorted, # 's' parameter in scatter is area
               alpha=fixed_alpha,
               color=selected_color,
               edgecolors='#000000', # Black edge color
               linewidth=0.5) # Edge line width


    # --- Add Annotations for bubble text (formatted size values) and use adjustText ---
    texts = []
    # Iterate through the sorted data to get values and positions
    for index, row in plot_df_sorted.iterrows():
        x_val, y_val, size_val = row[x_col], row[y_col], row[size_col]
        # No need for pd.notna check here, as plot_df_sorted already dropped NaNs in required_cols
        annotation_text = format_number_with_unit(size_val)
        # Add text centered on the bubble position
        texts.append(ax.text(x_val, y_val, annotation_text,
                             ha='center', va='center', # Horizontal and vertical alignment
                             color='#000000', # Text color
                             fontsize=8, # Original Matplotlib size was 8
                             family='Times New Roman')) # Text font family

    # Apply adjustText to prevent label overlaps
    if texts:
        adjust_text.adjust_text(texts,
                                force_points=(0.0, 0.0), # How much force to push text away from points
                                force_text=(0.2, 0.5), # How much force to push text away from other texts
                                expand_points=(1.0, 1.0), # Expand bbox around points
                                expand_text=(1.0, 1.0), # Expand bbox around texts
                                arrowprops=None, # Do not draw arrows
                                only_move={'points': 'xy', 'text': 'xy'}, # Allow moving in x and y directions
                                lim=100, # Limit the number of iterations
                                precision=0.01, # Precision for text movement
                                avoid_self=False, # Don't avoid overlapping with own bubble (usually not needed)
                                ensure_inside_axes=True) # Keep text inside the axes


    # --- Determine axis ranges with padding ---
    x_min_data = plot_df_sorted[x_col].min()
    x_max_data = plot_df_sorted[x_col].max()
    y_min_data = plot_df_sorted[y_col].min()
    y_max_data = plot_df_sorted[y_col].max()

    padding_percentage = 0.15
    # Handle cases where data range is zero or very small
    x_data_range = x_max_data - x_min_data if pd.notna(x_max_data) and pd.notna(x_min_data) else 0
    y_data_range = y_max_data - y_min_data if pd.notna(y_max_data) and pd.notna(y_min_data) else 0

    # Original Matplotlib code used a fixed min_data_padding = 1.0, which seems incorrect if data range is large.
    # Let's revert to the logic in the provided original code which calculated padding based on percentage and min_data_padding = 1.0.
    min_data_padding_orig = 1.0
    # Ensure padding is calculated even if range is 0, using min_data_padding
    # Add a small epsilon to range check to avoid float comparison issues
    x_padding_data = max(x_data_range * padding_percentage, min_data_padding_orig if abs(x_data_range) < 1e-9 else 0.15 * x_data_range if abs(x_data_range) > 1e-9 else min_data_padding_orig)
    y_padding_data = max(y_data_range * padding_percentage, min_data_padding_orig if abs(y_data_range) < 1e-9 else 0.15 * y_data_range if abs(y_data_range) > 1e-9 else min_data_padding_orig)


    ax.set_xlim(x_min_data - x_padding_data, x_max_data + x_padding_data)
    ax.set_ylim(y_min_data - y_padding_data, y_max_data + y_padding_data)


    # --- Handle Axis Labels and Offset Text (Matplotlib specific) ---
    # Original Matplotlib code handled offset text and units in labels after tight_layout.
    # Let's set labels first, then handle offset text after potential layout adjustments.
    ax.set_xlabel(x_col, fontsize=rcParams['axes.labelsize']) # Set cleaned name first
    ax.set_ylabel(y_col, fontsize=rcParams['axes.labelsize']) # Set cleaned name first


    # Set Title
    ax.set_title(chart_title, pad=20, fontsize=rcParams['axes.titlesize'])

    # Adjust layout before getting offset text
    plt.tight_layout()

    # Get offset text after tight_layout
    x_offset_text = ""
    y_offset_text = ""

    # Access the formatter to ensure it's created/updated
    # Calling get_major_formatter ensures the formatter exists and is configured
    ax.xaxis.get_major_formatter()
    ax.yaxis.get_major_formatter()

    # Check if the formatter is a ScalarFormatter and has an offset text artist
    # Use mticker.ScalarFormatter
    if isinstance(ax.xaxis.get_major_formatter(), mticker.ScalarFormatter):
        # Get the *artist* that draws the offset text
        offset_artist = ax.xaxis.get_offset_text()
        # Check if the artist exists, has text, and the text is not just the backspace character '\x08'
        if offset_artist and offset_artist.get_text().strip() and offset_artist.get_text().strip() != '\x08':
             x_offset_text = offset_artist.get_text().strip()
             # Hide the original offset text artist
             offset_artist.set_visible(False)

    if isinstance(ax.yaxis.get_major_formatter(), mticker.ScalarFormatter):
         offset_artist = ax.yaxis.get_offset_text()
         if offset_artist and offset_artist.get_text().strip() and offset_artist.get_text().strip() != '\x08':
              y_offset_text = offset_artist.get_text().strip()
              # Hide the original offset text artist
              offset_artist.set_visible(False)


    # Construct the final axis labels, incorporating the offset and unit
    # Format: "Name (Offset Unit)" or "Name (Offset)" or "Name (Unit)" or "Name"

    # Start with the cleaned column name
    x_label_full = x_col
    # Collect parts to put in parentheses
    label_parts_x = []
    if x_offset_text:
        label_parts_x.append(x_offset_text)
    if x_unit_str:
        label_parts_x.append(x_unit_str)

    if label_parts_x: # If there's anything to put in parentheses
         x_label_full += f" ({' '.join(label_parts_x)})"


    # Repeat for Y axis
    y_label_full = y_col
    label_parts_y = []
    if y_offset_text:
        label_parts_y.append(y_offset_text)
    if y_unit_str:
        label_parts_y.append(y_unit_str)

    if label_parts_y: # If there's anything to put in parentheses
         y_label_full += f" ({' '.join(label_parts_y)})"


    # Set axis labels again using the newly constructed full strings
    ax.set_xlabel(x_label_full, fontsize=rcParams['axes.labelsize'])
    ax.set_ylabel(y_label_full, fontsize=rcParams['axes.labelsize'])


    # --- Simulate Size Legend (Matplotlib version - Min only) ---
    legend_data_values = []
    # Use the actual minimum data value for the legend
    if len(valid_sizes) > 0 and not valid_sizes.empty and pd.notna(valid_sizes.min()):
         actual_min_size = valid_sizes.min()
         legend_data_values = [actual_min_size] # Only include the minimum


    legend_elements = []
    if legend_data_values: # Should contain only one value if valid_sizes is not empty and min is not NaN
        data_value = legend_data_values[0] # Get the minimum value

        # Calculate the display area corresponding to this minimum data value
        # using the same interpolation logic as the main bubbles
        display_area = (min_display_size_area + max_display_size_area) / 2.0 # Default to average size
        if interp_q_min != interp_q_max:
            # Map the actual minimum value using the interpolation range
            area = np.interp(data_value,
                             (float(interp_q_min), float(interp_q_max)),
                             (min_display_size_area, max_display_size_area))
            # Clip area to the display range
            display_area = np.clip(area, min_display_size_area, max_display_size_area)
        elif len(valid_sizes) > 0 and pd.notna(valid_sizes.iloc[0]):
             # If the interpolation range is zero, use the uniform area calculated earlier
             # Fallback to average if calculation failed
             uniform_area = (min_display_size_area + max_display_size_area) / 2.0
             # Try to use the uniform area from the main plot calculation if possible
             if '__display_size_area__' in plot_df_sorted.columns and len(plot_df_sorted) > 0:
                 uniform_area = plot_df_sorted['__display_size_area__'].iloc[0]
             display_area = uniform_area


        # Apply a slight scaling factor for legend appearance
        legend_size_scale_factor = 0.8
        scaled_display_area = display_area * legend_size_scale_factor

        # Ensure display area is not too small to be seen
        scaled_display_area = max(scaled_display_area, min_display_size_area * 0.1) # Use a small minimum area

        formatted_label = format_number_with_unit(data_value)
        # Create a dummy scatter point for the legend entry
        legend_elements.append(ax.scatter([], [], s=scaled_display_area, color=selected_color, alpha=fixed_alpha,
                                   edgecolors='#000000', linewidth=0.5, label=formatted_label))


        # --- Construct legend title with wrapping ---
        # Use the original string including unit for the legend title
        size_meaning_desc, size_unit_disp = parse_label_unit(size_label_with_unit)
        MAX_LEGEND_TITLE_LINE_WIDTH = 25  # Max characters per line for the description

        wrapped_desc = textwrap.fill(size_meaning_desc, width=MAX_LEGEND_TITLE_LINE_WIDTH)

        if size_unit_disp:
            # Ensure unit part is on a new line
            legend_title_str = f"{wrapped_desc}\n({size_unit_disp})"
        else:
            legend_title_str = wrapped_desc
        # --- END MODIFICATION for legend title ---


        if legend_elements:
            # Add the legend to the plot
            # Use original Matplotlib legend parameters
            legend = ax.legend(
                handles=legend_elements, # The dummy scatter points (only one now)
                labels=[elem.get_label() for elem in legend_elements], # The formatted label (only one now)
                title=legend_title_str, # The wrapped legend title
                loc='upper right', # <-- Original loc
                bbox_to_anchor=(1.25, 1), # <-- Original bbox_to_anchor
                borderaxespad=0., # Padding between the axes and legend bbox
                frameon=True, # Draw a box around the legend
                labelspacing=1.75, # Vertical space between legend items
                borderpad=1.2, # Padding inside the legend box
                handletextpad=2.0, # Padding between legend handle and text
                handlelength=1.5, # Length of the legend handle
                facecolor='white', # Legend box background color
                edgecolor='#000000' # Legend box border color
            )
            # Set legend title font size
            plt.setp(legend.get_title(), fontsize=rcParams['legend.fontsize'] + 1, family='Times New Roman')
            # Set legend label font size (already set by rcParams['legend.fontsize'])
            # Set legend label font family (already set by rcParams['font.family'])


    # --- Adjust right margin for legend using rect in tight_layout ---
    # Use original rect coordinates
    plt.tight_layout(rect=[0, 0, 0.97, 1]) # <-- Original rect (0.97)


    return fig

# --- END Original Matplotlib Plotting Function ---


# --- Refactored Plotly Plotting Function (for SVG) ---
# --- SVG 生成核心逻辑 ---

# Removed unused functions: generate_svg_layout, create_plotly_bubbles, select_non_yellow_color, create_legend_traces

def _calculate_size_range(size_data: pd.Series) -> Tuple[float, float]:
    """计算实际使用的尺寸范围 (Plotly version)"""
    # Handle cases with no valid data or only one point
    if size_data.empty:
        return 0.0, 0.0

    valid_sizes = size_data.dropna()
    if valid_sizes.empty:
        return 0.0, 0.0

    # Always calculate actual min/max for fallback
    actual_min = valid_sizes.min()
    actual_max = valid_sizes.max()

    if len(valid_sizes) >= 20:
        # Calculate quantiles. Handle potential errors if quantiles are NaN or identical.
        q_05 = valid_sizes.quantile(0.05)
        q_95 = valid_sizes.quantile(0.95)

        # Use quantiles if valid and different, otherwise fallback to actual min/max
        if pd.notna(q_05) and pd.notna(q_95) and q_05 != q_95:
            return q_05, q_95
        elif pd.notna(actual_min) and pd.notna(actual_max) and actual_min != actual_max: # Fallback to actual min/max if quantiles are bad
             return actual_min, actual_max
        else:
             # If quantiles and actual min/max are identical or NaN
             return 0.0, 0.0 # Indicate zero range

    elif len(valid_sizes) > 0:
        # Use min/max for less than 20 points
        actual_min = valid_sizes.min()
        actual_max = valid_sizes.max()
        if pd.notna(actual_min) and pd.notna(actual_max) and actual_min != actual_max:
             return actual_min, actual_max
        else:
             # If actual min/max are identical or NaN
             return 0.0, 0.0 # Indicate zero range
    else:
        # Should be caught by valid_sizes.empty check, but defensive
        return 0.0, 0.0


def _select_non_yellow_color() -> str:
    """选择非黄色系颜色 (Plotly version)"""
    # Create a pool of colors from sequences, filtering out potential yellow-like colors
    color_pool = [
        color for seq in PLOTLY_QUALITATIVE_COLOR_SEQUENCES
        for color in seq
        # Use the potentially improved is_yellow_like_plotly
        if not is_yellow_like_plotly(color)
    ]

    # If the filtered pool is not empty, select a random color from it
    if color_pool:
        return random.choice(color_pool)
    else:
        # Fallback to a default non-yellow color if all colors were filtered out (unlikely)
        print("Warning: All colors filtered as potentially yellow. Using default blue.")
        return '#1f77b4' # Plotly's default blue


def _create_legend_traces(
    size_data: pd.Series, # Use original size data to determine legend values
    color: str,
    display_min_diameter: int, # Use diameter for Plotly
    display_max_diameter: int  # Use diameter for Plotly
) -> List[go.Scatter]: # Changed back to go.Scatter
    """创建尺寸图例 (Plotly version - 仅显示最小尺寸)"""
    traces = []
    valid_sizes = size_data.dropna()
    if valid_sizes.empty or pd.isna(valid_sizes.min()):
        return [] # No legend if no valid data or min is NaN

    actual_min = valid_sizes.min()
    # actual_max = valid_sizes.max() # No longer needed for legend values

    legend_value = actual_min

    # Calculate bubble size (diameter) for the legend entry
    # This bubble should represent the minimum size.
    # Use the interpolation range (actual min/max) to map the actual min value
    # to the display diameter range.
    # If actual_min == actual_max, use the uniform size logic.
    if valid_sizes.min() != valid_sizes.max():
        # Use np.interp to map the actual minimum value
        # from the actual data range (actual_min, actual_max)
        # to the display diameter range (display_min_diameter, display_max_diameter)
        size = np.interp(legend_value,
                         (float(valid_sizes.min()), float(valid_sizes.max())), # Use actual min/max of data for interpolation range
                         (display_min_diameter, display_max_diameter))
        # Clip sizes to the display range, just in case
        size = np.clip(size, display_min_diameter, display_max_diameter)
    else:
        # If all values are the same, use the middle size for the legend bubble
        size = (display_min_diameter + display_max_diameter) / 2.0


    # Apply a slight scaling factor for legend appearance
    legend_size_scale_factor = 0.8
    size *= legend_size_scale_factor

    # Ensure size is not zero or negative after scaling
    size = max(size, display_min_diameter * 0.1) # Use a small minimum size so it's visible


    formatted_label = format_number_with_unit(legend_value)

    # Create a single trace for the minimum size legend entry
    traces.append(go.Scatter( # Changed back to go.Scatter
        x=[None], y=[None], # Use None for x/y to create a dummy trace for legend
        mode='markers',
        name=formatted_label, # Formatted minimum data value as the legend label
        marker={
            'size': size, # Use the calculated display size for the minimum
            'color': color,
            'opacity': 0.7,
            'line': {'width': 0.5, 'color': '#000000'}
        },
        showlegend=True # Make this trace visible in the legend
    ))

    return traces


def _configure_final_layout(fig: go.Figure, plot_df: pd.DataFrame, metadata: Dict, x_label: str) -> None:
    """配置最终布局 (Plotly version)"""
    # Calculate coordinate axis range
    x_col_scaled = 'Scaled_X' # The scaled X column name
    y_col = metadata['Y_col']

    if plot_df.empty:
         # Set default range if DataFrame is empty
         x_min = 0; x_max = 1
         y_min = 0; y_max = 1
    else:
        # Ensure min/max are valid floats
        x_min = float(plot_df[x_col_scaled].min())
        x_max = float(plot_df[x_col_scaled].max())
        y_min = float(plot_df[y_col].min())
        y_max = float(plot_df[y_col].max())

    # Set 15% boundary buffer
    x_data_range = x_max - x_min if not (pd.isna(x_max) or pd.isna(x_min)) else 0
    y_data_range = y_max - y_min if not (pd.isna(y_max) or pd.isna(y_min)) else 0

    # Ensure padding is added even if range is zero
    min_padding_value = 0.1 # Minimum padding value if range is zero
    # Use a small epsilon for range check to avoid float comparison issues
    x_padding = max(x_data_range * 0.15, min_padding_value if abs(x_data_range) < 1e-9 else 0.15 * x_data_range if abs(x_data_range) > 1e-9 else min_padding_value)
    y_padding = max(y_data_range * 0.15, min_padding_value if abs(y_data_range) < 1e-9 else 0.15 * y_data_range if abs(y_data_range) > 1e-9 else min_padding_value)


    # Ensure range is not zero if data points exist and range was zero
    # Add extra padding if min == max but there's data
    if x_min == x_max and not plot_df.empty:
        x_padding = max(x_padding, 0.5) # Add significant padding if all x values are the same
    if y_min == y_max and not plot_df.empty:
        y_padding = max(y_padding, 0.5) # Add significant padding if all y values are the same


    fig.update_layout(
        title={
            'text': metadata.get('Little_Theme', '气泡图分析'),
            'font': {'size': 16, 'color': '#000000', 'family': 'Times New Roman'},
            'x': 0.5, 'xanchor': 'center'
        },
        xaxis={
            'title': {'text': x_label, 'font': {'size': 14, 'color': '#000000', 'family': 'Times New Roman'}},
            'range': [x_min - x_padding, x_max + x_padding],
            'showgrid': False, 'zeroline': False,
            'showline': True, 'linewidth': 1.0, 'linecolor': '#000000', # Keep bottom line
            'mirror': False, # <--- REMOVED TOP BORDER
            'tickfont': {'size': 12, 'color': '#000000', 'family': 'Times New Roman'},
            'ticks': 'outside', 'tickcolor': '#000000',
            'tickformat': ".1f" # Add tickformat for scaled axis
        },
        yaxis={
            'title': {'text': metadata['Y_label_display'], 'font': {'size': 14, 'color': '#000000', 'family': 'Times New Roman'}},
            'range': [y_min - y_padding, y_max + y_padding],
            'showgrid': False, 'zeroline': False,
            'showline': True, 'linewidth': 1.0, 'linecolor': '#000000', # Keep left line
            'mirror': False, # <--- REMOVED RIGHT BORDER
            'tickfont': {'size': 12, 'color': '#000000', 'family': 'Times New Roman'},
            'ticks': 'outside', 'tickcolor': '#000000',
        },
        font={'family': 'Times New Roman', 'size': 12, 'color': '#000000'},
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=640,
        height=480,
        margin={'l': 80, 'r': 150, 'b': 80, 't': 100},
        legend={
            'title': {'text': _format_legend_title(metadata['Size_label_with_unit']), 'font': {'size': 12, 'family': 'Times New Roman'}},
            'font': {'size': 12, 'family': 'Times New Roman'},
            'x': 1.02, 'y': 1, 'xanchor': 'left', 'yanchor': 'top',
            'bgcolor': 'white', 'bordercolor': '#000000', 'borderwidth': 1
        },
        hovermode='closest' # Improve hover behavior
    )


def _format_legend_title(label: str) -> str:
    """格式化图例标题 (Plotly version - uses <br> for new line)"""
    desc, unit = parse_label_unit(label)
    MAX_LEGEND_TITLE_LINE_WIDTH = 25  # Max characters per line for the description

    # Use textwrap for description, then add unit on a new line if present
    wrapped_desc_lines = textwrap.wrap(desc, width=MAX_LEGEND_TITLE_LINE_WIDTH)
    wrapped_desc = '<br>'.join(wrapped_desc_lines)

    if unit:
        # Add unit on a new line using <br>
        return f"{wrapped_desc}<br>({unit})"
    else:
        return wrapped_desc


def _create_empty_plotly_figure(metadata: Dict) -> go.Figure:
    """创建空数据图表 (Plotly version)"""
    fig = go.Figure()
    # Use default ranges and labels even for empty plot
    fig.update_layout(
        title={'text': metadata.get('Little_Theme', '气泡图分析'), 'x': 0.5, 'font': {'size': 16, 'color': '#000000', 'family': 'Times New Roman'}},
        xaxis={'title': {'text': _construct_axis_label(metadata['X_label_display'], ""), 'font': {'size': 14, 'color': '#000000', 'family': 'Times New Roman'}}, 'range': [0, 1],
               'showgrid': False, 'zeroline': False, 'showline': True, 'linewidth': 1.0, 'linecolor': '#000000',
               'mirror': False, # <--- REMOVED TOP BORDER for empty plot
               'tickfont': {'size': 12, 'color': '#000000', 'family': 'Times New Roman'}, 'ticks': 'outside', 'tickcolor': '#000000'},
        yaxis={'title': {'text': metadata['Y_label_display'], 'font': {'size': 14, 'color': '#000000', 'family': 'Times New Roman'}}, 'range': [0, 1],
               'showgrid': False, 'zeroline': False, 'showline': True, 'linewidth': 1.0, 'linecolor': '#000000',
               'mirror': False, # <--- REMOVED RIGHT BORDER for empty plot
               'tickfont': {'size': 12, 'color': '#000000', 'family': 'Times New Roman'}, 'ticks': 'outside', 'tickcolor': '#000000'},
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        font={'family': 'Times New Roman', 'size': 12, 'color': '#000000'},
        width=640,
        height=480,
        margin={'l': 80, 'r': 150, 'b': 80, 't': 100}
    )
    # Add a text annotation indicating no data
    fig.add_annotation(
        text="No valid data to display",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font={'size': 16, 'color': '#000000', 'family': 'Times New Roman'},
        xanchor='center', yanchor='middle'
    )
    return fig


def _construct_axis_label(label_str: str, scale_prefix: str) -> str:
    """构建坐标轴标签 (Plotly version)"""
    name, unit = parse_label_unit(label_str)
    parts = [p for p in [scale_prefix, unit] if p]

    # Combine parts into a single string, separated by space.
    # If there are parts, enclose them in parentheses.
    if parts:
        # Join parts with spaces inside parentheses
        return f"{name} ({' '.join(parts)})"
    else:
        # If no parts (no scale prefix, no unit), just return the name
        return name


# --- Plotly SVG生成完整函数组 ---
def plot_bubble_chart_plotly(df: pd.DataFrame, metadata: Dict[str, Any]) -> go.Figure:
    """Plotly气泡图完整生成函数"""
    # Data preprocessing
    x_col = metadata['X_col']
    y_col = metadata['Y_col']
    size_col = metadata['Size_col']
    required_cols = [x_col, y_col, size_col]

    # Drop rows where any of the required columns are NaN or None
    plot_df = df.dropna(subset=required_cols).copy()

    if plot_df.empty:
        print("Warning: No valid data points to plot for Plotly chart after dropping NaNs. Plot will be empty.")
        return _create_empty_plotly_figure(metadata)

    # Ensure size column is numeric after dropping NaNs
    plot_df[size_col] = pd.to_numeric(plot_df[size_col], errors='coerce')
    # Drop NaNs again in case coerce introduced them (unlikely after first dropna but safer)
    plot_df.dropna(subset=[size_col], inplace=True)

    if plot_df.empty:
         print("Warning: No valid data points to plot for Plotly chart after numeric conversion check. Plot will be empty.")
         return _create_empty_plotly_figure(metadata)


    # Axis scaling processing
    # Use the maximum absolute value from the data for scaling
    max_x_val = plot_df[x_col].abs().max() if not plot_df[x_col].empty else 0
    x_scale, x_prefix = get_scale_factor_and_prefix(float(max_x_val)) # Ensure float type

    plot_df['Scaled_X'] = plot_df[x_col] / x_scale
    x_label = _construct_axis_label(metadata['X_label_display'], x_prefix)

    # Y axis label doesn't use scaling prefix based on current logic
    y_label = metadata['Y_label_display']


    # Bubble size calculation
    # Use the size data from the cleaned dataframe
    size_data = plot_df[size_col].astype(float)
    # Define desired min/max display diameter in pixels
    min_display_diameter = 20
    max_display_diameter = 40

    # Calculate the interpolation range based on the cleaned size data
    # This range (interp_min, interp_max) is used for scaling the MAIN bubbles
    interp_min, interp_max = _calculate_size_range(size_data)

    # Calculate the display diameters for each bubble
    # Handle the case where the interpolation range is zero
    if interp_min != interp_max:
         diameters = np.interp(size_data,
                               (interp_min, interp_max),
                               (min_display_diameter, max_display_diameter))
         # Ensure diameters are within the min/max display range
         diameters = np.clip(diameters, min_display_diameter, max_display_diameter)
    else:
         # If the data range for scaling is zero, use the average display diameter for all points
         uniform_size = (min_display_diameter + max_display_diameter) / 2.0
         diameters = np.full(len(plot_df), uniform_size, dtype=float)
         if len(size_data) > 0:
              print(f"Warning: Scaled size data range for column '{size_col}' is zero (all valid values are identical). Using uniform bubble size ({diameters[0]:.1f}px diameter).")
         else:
              # This case should be caught by the empty check earlier, but defensive
              print(f"Warning: No valid numeric values in size column '{size_col}'. Using uniform bubble size ({uniform_size:.1f}px diameter).")


    # Add the calculated diameters to the dataframe for easier plotting/text trace
    plot_df['Bubble_Diameter'] = diameters

    # Sort data by diameter descending for correct plotting order (larger bubbles underneath)
    plot_df_sorted = plot_df.sort_values(by='Bubble_Diameter', ascending=False).reset_index(drop=True).copy()

    # Color selection
    selected_color = _select_non_yellow_color()

    # Create main bubble trace
    fig = go.Figure()
    fig.add_trace(
        go.Scatter( # Changed from go.Scattergl to go.Scatter
            x=plot_df_sorted['Scaled_X'],
            y=plot_df_sorted[y_col],
            mode='markers',
            marker={
                'size': plot_df_sorted['Bubble_Diameter'], # Use calculated diameters
                'color': selected_color,
                'opacity': 0.7,
                'line': {'width': 0.5, 'color': '#000000'}
            },
            showlegend=False, # Main trace does not need a legend entry
            hoverinfo='x+y+z', # Show hover info for x, y, and size (z)
            customdata=np.column_stack((
                plot_df_sorted[x_col], # Unscaled X for hover
                plot_df_sorted[y_col],
                plot_df_sorted[size_col].apply(format_number_with_unit) # Formatted size for hover
            )),
            hovertemplate=(
                f"<b>{x_col}</b>: %{{customdata[0]}}<br>"
                f"<b>{y_col}</b>: %{{customdata[1]}}<br>"
                f"<b>{size_col}</b>: %{{customdata[2]}}<extra></extra>" # Use Size_col name in hover
            )
        )
    )

    # Add text labels as a separate trace
    # Note: Plotly's automatic text placement with mode='text' is not as sophisticated as Matplotlib's adjustText.
    # Text might overlap significantly, especially with many bubbles.
    fig.add_trace(
        go.Scatter( # Changed from go.Scattergl to go.Scatter
            x=plot_df_sorted['Scaled_X'],
            y=plot_df_sorted[y_col],
            mode='text',
            text=plot_df_sorted[size_col].apply(format_number_with_unit), # Formatted size for text
            textposition='middle center', # Center text on the bubble
            textfont={
                'size': 8, # Text font size
                'color': '#000000', # Text color
                'family': 'Times New Roman' # Text font family
            },
            showlegend=False, # Text trace does not need a legend entry
            hoverinfo='skip' # Skip hover for text trace
        )
    )


    # Add legend traces (simulating size legend - Min only)
    # Pass the original size_data series, color, and display diameter range
    fig.add_traces(
        _create_legend_traces(
            size_data=size_data,
            color=selected_color,
            display_min_diameter=min_display_diameter,
            display_max_diameter=max_display_diameter
        )
    )

    # Configure final layout
    _configure_final_layout(fig, plot_df_sorted, metadata, x_label) # Pass plot_df_sorted and x_label

    return fig

# --- END Refactored Plotly Plotting Function ---


# --- Saving (Adapted for both Matplotlib and Plotly) ---
# This function is no longer needed as saving is done directly after plotting each type
# def save_chart(fig: ?, png_filepath: str, svg_filepath: str, scale: int = 3): pass


# --- Main Execution ---
if __name__ == "__main__":
    OUTPUT_PNG_DIR = "./bubble/png"
    OUTPUT_SVG_DIR = "./bubble/svg"
    # Ensure output directories exist
    os.makedirs(OUTPUT_PNG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_SVG_DIR, exist_ok=True)

    INPUT_CSV_DIR = "./bubble/csv"
    # Ensure input directory exists (in case generator hasn't run)
    os.makedirs(INPUT_CSV_DIR, exist_ok=True)


    csv_files = glob.glob(os.path.join(INPUT_CSV_DIR, "bubble_*.csv"))

    if not csv_files:
        print(f"No 'bubble_*.csv' files found in the directory: {INPUT_CSV_DIR}")
    else:
        print(f"Found {len(csv_files)} 'bubble_*.csv' file(s) in '{INPUT_CSV_DIR}'.")
        try:
            def sort_key(f):
                base = os.path.basename(f)
                match = re.search(r'_(\d+)\.csv$', base)
                return int(match.group(1)) if match else base
            csv_files.sort(key=sort_key)
        except Exception:
             csv_files.sort()
             print("Warning: Could not sort files numerically. Sorting alphabetically.")

        processed_count = 0
        for input_csv_path in csv_files:
            print(f"\nProcessing file: {input_csv_path}")
            # Initialize fig_mpl to None before the try block
            fig_mpl = None # <-- Initialize fig_mpl
            fig_plotly = None # Initialize fig_plotly

            try:
                output_filename_base = os.path.splitext(os.path.basename(input_csv_path))[0]
                png_output_path = os.path.join(OUTPUT_PNG_DIR, f"{output_filename_base}.png")
                svg_output_path = os.path.join(OUTPUT_SVG_DIR, f"{output_filename_base}.svg")

                # --- Parse data (common for both) ---
                df_data, metadata_dict = parse_bubble_csv(input_csv_path)
                print("CSV file parsed successfully.")

                # Check if required columns exist in the DataFrame after parsing
                required_cols = [metadata_dict['X_col'], metadata_dict['Y_col'], metadata_dict['Size_col']]
                # Check if dataframe is empty before checking columns
                # The parsing function already handles errors for missing columns or empty data section,
                # but let's add a check here for robustness before plotting.
                if df_data.empty or not all(col in df_data.columns for col in required_cols):
                     if df_data.empty:
                         print(f"Skipping file {input_csv_path}: DataFrame is empty after parsing.")
                     else:
                         # This case should ideally be caught by parse_bubble_csv's ValueError
                         print(f"Skipping file {input_csv_path}: Required columns {required_cols} not found in DataFrame.")
                     # Still generate empty plots for consistency
                     try:
                         # Attempt to generate empty PNG
                         fig_mpl = plot_bubble_chart_matplotlib(df_data.copy(), metadata_dict.copy())
                         fig_mpl.savefig(png_output_path, dpi=300)
                         print(f"Saved empty PNG to {png_output_path}")
                     except Exception as e_png_empty:
                          print(f"Error generating or saving empty PNG for {input_csv_path}: {e_png_empty}")
                          traceback.print_exc()
                     try:
                         # Attempt to generate empty SVG
                         fig_plotly = plot_bubble_chart_plotly(df_data.copy(), metadata_dict.copy())
                         if fig_plotly: # Check if figure object was created
                              pio.write_image(fig_plotly, svg_output_path, format='svg')
                              print(f"Saved empty SVG to {svg_output_path}")
                     except Exception as e_svg_empty:
                          print(f"Error generating or saving empty SVG for {input_csv_path}: {e_svg_empty}")
                          print("Plotly image export requires 'kaleido'. Install with: pip install kaleido")
                          traceback.print_exc()
                     continue # Skip to next file


                # Check if there is any valid data to plot after dropping NaNs in required columns
                # This check is also done inside the plotting functions, but doing it early avoids calling them
                # if there's no valid data at all.
                df_for_plot_check = df_data.dropna(subset=required_cols)
                if df_for_plot_check.empty:
                     print(f"Skipping file {input_csv_path}: No valid data points after dropping NaNs in required columns.")
                     # Still generate empty plots for consistency, but log the skip reason
                     try:
                         # Attempt to generate empty PNG
                         fig_mpl = plot_bubble_chart_matplotlib(df_data.copy(), metadata_dict.copy())
                         fig_mpl.savefig(png_output_path, dpi=300)
                         print(f"Saved empty PNG to {png_output_path}")
                     except Exception as e_png_empty:
                          print(f"Error generating or saving empty PNG for {input_csv_path}: {e_png_empty}")
                          traceback.print_exc()
                     try:
                         # Attempt to generate empty SVG
                         fig_plotly = plot_bubble_chart_plotly(df_data.copy(), metadata_dict.copy())
                         if fig_plotly: # Check if figure object was created
                              pio.write_image(fig_plotly, svg_output_path, format='svg')
                              print(f"Saved empty SVG to {svg_output_path}")
                     except Exception as e_svg_empty:
                          print(f"Error generating or saving empty SVG for {input_csv_path}: {e_svg_empty}")
                          print("Plotly image export requires 'kaleido'. Install with: pip install kaleido")
                          traceback.print_exc()
                     continue # Skip to next file


                # --- Generate and Save PNG using Matplotlib (Original Logic) ---
                print("Generating PNG using Matplotlib...")
                try:
                    fig_mpl = plot_bubble_chart_matplotlib(df_data.copy(), metadata_dict.copy()) # Pass copies to avoid side effects
                    # Save PNG with original Matplotlib parameters (300 DPI, tight_layout handled in plotting)
                    # Use the savefig method from the original code
                    fig_mpl.savefig(png_output_path, dpi=300) # <-- Original savefig call (no bbox_inches)
                    print(f"Saved PNG to {png_output_path}")
                except Exception as e:
                     print(f"Error generating or saving PNG for {input_csv_path}: {e}")
                     traceback.print_exc()
                     # Do NOT re-raise here, allow SVG generation to proceed if PNG failed


                # --- Generate and Save SVG using Plotly ---
                print("Generating SVG using Plotly...")
                try:
                    fig_plotly = plot_bubble_chart_plotly(df_data.copy(), metadata_dict.copy()) # Pass copies
                    if fig_plotly: # Check if figure object was created
                         # Save SVG using Plotly (layout size 640x480 determines SVG size)
                         # scale parameter is ignored for SVG, but keeping the call consistent
                         pio.write_image(fig_plotly, svg_output_path, format='svg')
                         print(f"Saved SVG to {svg_output_path}")
                except Exception as e:
                     print(f"Error generating or saving SVG for {input_csv_path}: {e}")
                     print("Plotly image export requires 'kaleido'. Install with: pip install kaleido")
                     traceback.print_exc()

                processed_count += 1

            except FileNotFoundError as e_fnf:
                print(f"Skipping file {input_csv_path}: {e_fnf}")
            except ValueError as e_val:
                print(f"Skipping file {input_csv_path} due to data format/parsing issue: {e_val}")
                traceback.print_exc() # Print more details for ValueError
            except Exception as e_generic:
                print(f"Skipping file {input_csv_path} due to unexpected error: {e_generic}")
                traceback.print_exc()
            finally:
                 # Close Matplotlib figure ONLY if it was successfully created
                 if fig_mpl is not None: # <-- Check if fig_mpl was assigned
                     plt.close(fig_mpl)
                 # Plotly figures don't explicitly need closing like Matplotlib figures


        print(f"\nVisualization process finished. Successfully processed {processed_count} out of {len(csv_files)} files found.")

