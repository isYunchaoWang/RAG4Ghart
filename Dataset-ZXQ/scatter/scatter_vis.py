# Import necessary libraries
import pandas as pd
# Remove matplotlib imports
# import matplotlib.pyplot as plt
import os # Keep os <-- Uncommented this line
# from matplotlib import rcParams # Remove rcParams
import numpy as np # Keep numpy
from typing import Tuple, Dict, Any, List, Optional # Keep typing hints
import random # Keep random
import traceback # Keep traceback
import glob # Keep glob
import re # Keep re
# Remove adjustText (unused)
# import adjustText as adjust_text
# Remove matplotlib.ticker (specific to matplotlib offset handling)
# import matplotlib.ticker as mticker # --- NEW: Import matplotlib.ticker ---

# Import Plotly libraries
import plotly.graph_objects as go
import plotly.io as pio
import plotly.colors as pcolors # Import Plotly colors

# Define some suitable categorical color lists from Plotly
CATEGORICAL_COLOR_SEQUENCES = [
    pcolors.qualitative.D3,
    pcolors.qualitative.Plotly,
    pcolors.qualitative.G10,
    pcolors.qualitative.T10,
    pcolors.qualitative.Alphabet,
    pcolors.qualitative.Dark24,
    pcolors.qualitative.Light24,
]

# Define some common marker styles (Plotly symbols)
# https://plotly.com/python/reference/scatter/#scatter-marker-symbol
MARKER_SYMBOLS = [
    'circle',
    # 'square', # Add more if needed, but original only had 'o' (circle)
]

# Helper function to parse name and unit from "Name (Unit)" format
def parse_name_unit(info_string: str) -> Tuple[str, str]:
    """
    Parses 'Name (Unit)' format from a string. Handles potential nested parentheses
    by looking for the last pair.
    """
    name = info_string.strip()
    # Updated regex to be more robust in capturing content inside the last parenthesis
    match = re.search(r'^(.*)\s*\(([^)]*)\)$', name)
    if match:
        label_part = match.group(1).strip()
        unit = match.group(2).strip()
        return label_part, unit
    else:
        return name, "" # Return original name if no unit found


# --- parse_scatter_csv (Keep as is) ---
def parse_scatter_csv(filepath: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Reads the scatter plot CSV file and parses its metadata from the first two lines.
    Expected header format:
    Line 1: Main theme, little theme, trend, correlation
    Line 2: x_col_name (unit), y_col_name (unit)
    Line 3 onwards: data rows (x_value, y_value)

    Args:
        filepath: Path to the CSV file.

    Returns:
        A tuple containing:
            - pd.DataFrame: The data from the CSV (headers read from the third line onwards).
            - Dict[str, Any]: A dictionary containing the parsed metadata.
              Includes 'X_label_display', 'Y_label_display' (full string including unit for axis labels),
              'X_col', 'Y_col' (cleaned names for DataFrame access), and parsed units.
    Raises:
         FileNotFoundError, ValueError, Exception for errors.
    """
    metadata: Dict[str, Any] = {}
    df = pd.DataFrame()

    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found at {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            # Read first header line
            header_line_1 = f.readline().strip()
            # Read second header line (axis info)
            header_line_2 = f.readline().strip()


        # Parse first header line
        parts_1 = [part.strip() for part in header_line_1.split(',')]
        expected_parts_1 = 4
        if len(parts_1) != expected_parts_1:
            raise ValueError(f"Incorrect first header format in {filepath}. Expected {expected_parts_1} parts separated by commas, but found {len(parts_1)}. Header: '{header_line_1}'")

        metadata['Topic'] = parts_1[0]
        metadata['Little_Theme'] = parts_1[1]
        metadata['Trend'] = parts_1[2]
        metadata['Correlation_Type'] = parts_1[3]
        # Actual_Correlation is no longer in the header

        # Parse second header line (axis info)
        parts_2 = [part.strip() for part in header_line_2.split(',')]
        expected_parts_2 = 2
        if len(parts_2) != expected_parts_2:
             raise ValueError(f"Incorrect second header format in {filepath}. Expected {expected_parts_2} parts separated by commas, but found {len(parts_2)}. Header: '{header_line_2}'")

        x_info_str = parts_2[0]
        y_info_str = parts_2[1]

        x_col_name_cleaned, x_unit_display = parse_name_unit(x_info_str)
        y_col_name_cleaned, y_unit_display = parse_name_unit(y_info_str)

        metadata['X_label_display'] = x_info_str # Store the original string including unit
        metadata['Y_label_display'] = y_info_str # Store the original string including unit

        metadata['X_col'] = x_col_name_cleaned # Store cleaned name for df access
        metadata['Y_col'] = y_col_name_cleaned # Store cleaned name for df access

        metadata['X_unit_display'] = x_unit_display # Store unit separately
        metadata['Y_unit_display'] = y_unit_display # Store unit separately

        # Read the actual data, skipping the first two header lines
        # header=None because we are providing column names manually
        # names=[...] specifies the column names based on the parsed second header line
        df = pd.read_csv(filepath, skiprows=2, header=None, encoding='utf-8', index_col=False, names=[metadata['X_col'], metadata['Y_col']])

        if df.empty:
             print(f"Warning: DataFrame is empty after reading data from {filepath}.")
             # Return empty df and metadata, calling code should handle
             return df, metadata


        cols_to_convert = [metadata['X_col'], metadata['Y_col']]
        for col in cols_to_convert:
            # Ensure the column exists in the DataFrame before attempting conversion
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].round(2)
                if df[col].isnull().any():
                    print(f"Warning: Column '{col}' in {filepath} contains non-numeric values after conversion. Invalid values treated as NaN.")
            else:
                 # This should ideally not happen if names argument in read_csv is correct
                 raise ValueError(f"Logic Error: Column '{col}' not found in DataFrame after reading and naming for {filepath}. DataFrame columns: {list(df.columns)}")


    except FileNotFoundError: raise
    except ValueError as ve: raise ve
    except Exception as e: raise Exception(f"Error reading or parsing CSV file {filepath}: {e}") from e

    return df, metadata
# --- parse_scatter_csv End ---


# Helper function to check if a color string represents yellow (basic heuristic)
def is_yellow_like(color_str: str) -> bool:
    """
    Checks if a color string (hex, rgb, rgba) is yellow-like. Basic heuristic.
    """
    try:
        # Convert color string to RGB tuple (0-1 range)
        # Plotly's to_rgb function is useful, but not directly in pcolors.
        # Manual parsing or using a helper might be needed.
        # A simple approach: assume hex or rgb(a) and parse.
        if color_str.startswith('#'): # Hex color
            if len(color_str) == 7: # #RRGGBB
                r = int(color_str[1:3], 16) / 255.0
                g = int(color_str[3:5], 16) / 255.0
                b = int(color_str[5:7], 16) / 255.0
            elif len(color_str) == 4: # #RGB
                 r = int(color_str[1], 16) / 15.0
                 g = int(color_str[2], 16) / 15.0
                 b = int(color_str[3], 16) / 15.0
            else: return False # Not a standard hex format

        elif color_str.startswith('rgb'): # rgb or rgba
            # Extract numbers using regex
            match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', color_str)
            if match:
                r = int(match.group(1)) / 255.0
                g = int(match.group(2)) / 255.0
                b = int(match.group(3)) / 255.0
            else: return False # Not a recognized rgb/rgba format
        else:
            # Could be a named color string, harder to check. Assume not yellow for simplicity.
            # Or use a lookup if needed. Sticking to hex/rgb for now.
            return False

        # Yellow heuristic: High Red, High Green, Low Blue
        # Thresholds might need tuning
        yellow_threshold_rgb = (0.7, 0.7, 0.4) # (R, G, B) in 0-1 range
        return r > yellow_threshold_rgb[0] and g > yellow_threshold_rgb[1] and b < yellow_threshold_rgb[2]

    except Exception as e:
        print(f"Warning: Could not parse or check color '{color_str}': {e}. Assuming not yellow.")
        return False # Assume not yellow if parsing fails


# --- Refactored visualize_scatter_plot using Plotly ---
def visualize_scatter_plot(csv_file_path: str, png_filepath: str, svg_filepath: str) -> None:
    """
    Visualize scatter plot data from a single CSV file and save as PNG and SVG
    to the specified file paths using Plotly. Uses the new CSV header format (2 header lines).

    Args:
        csv_file_path: Path to the input CSV file.
        png_filepath: Full path to save the output PNG file.
        svg_filepath: Full path to save the output SVG file.
    """
    try:
        # Read and parse the data
        df, metadata = parse_scatter_csv(csv_file_path)
        print(f"CSV file '{os.path.basename(csv_file_path)}' parsed successfully.")

        # Get actual column names for DataFrame access
        x_col = metadata.get('X_col')
        y_col = metadata.get('Y_col')

        # Check if required metadata is available and if there's valid data to plot
        if x_col is None or y_col is None or df.empty or df.dropna(subset=[x_col, y_col]).empty:
             print(f"Skipping file {csv_file_path}: Missing column info or no valid data points to plot after parsing.")
             return # Skip visualization for this file

        # Get cleaned column names and units separately
        x_col_cleaned = metadata.get('X_col', 'X')
        y_col_cleaned = metadata.get('Y_col', 'Y')
        x_unit_display = metadata.get('X_unit_display', '')
        y_unit_display = metadata.get('Y_unit_display', '')

        # Get title from metadata
        little_theme = metadata.get('Little_Theme', metadata.get('Topic', 'Scatter Plot'))

        # --- Random Single Scatter Color per File (Excluding Yellow) ---
        selected_color_str = '#1f77b4' # Default blue (Plotly default is similar)
        max_color_selection_attempts = 20 # Increased attempts as more sequences are available

        for attempt in range(max_color_selection_attempts):
            try:
                # Select a random color sequence
                color_sequence = random.choice(CATEGORICAL_COLOR_SEQUENCES)
                # Select a random color from the sequence
                candidate_color = random.choice(color_sequence)

                # Check if the selected color is yellow-like
                if not is_yellow_like(candidate_color):
                    selected_color_str = candidate_color
                    break # Found a suitable color, exit the loop
                else:
                     # If yellow, try again
                     if attempt == max_color_selection_attempts - 1:
                         print("Warning: Failed to find a non-yellow color after multiple attempts. Using default blue.")

            except Exception as e:
                print(f"Attempt {attempt+1}: Error selecting color: {e}. Trying again.")
                if attempt == max_color_selection_attempts - 1:
                    print("Warning: Failed to select color after multiple attempts. Using default blue.")
        # -------------------------------------------------------------------


        # --- Random Scatter Size (Plotly uses diameter in pixels) ---
        # Original matplotlib used area (s). To get a visually similar scale,
        # let's pick a random size (diameter) in a reasonable range.
        # Original Matplotlib radius was 3-6, area 28-113. Diameter 6-12.
        # Let's use a Plotly size range like 6 to 15 pixels diameter.
        scatter_size_pixels = random.uniform(6, 12)
        # ----------------------------------------------------------

        # --- Random Scatter Alpha (Transparency) ---
        random_opacity = random.uniform(0.8, 1.0)
        # ----------------------------------------------

        # --- Random Marker Symbol ---
        selected_symbol = random.choice(MARKER_SYMBOLS) # e.g., 'circle'
        # ------------------------------

        # Create Plotly figure
        fig = go.Figure()

        # Add scatter trace
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='markers',
            marker=dict(
                size=scatter_size_pixels,
                color=selected_color_str,
                opacity=random_opacity,
                symbol=selected_symbol,
                line=dict( # Add white edge like in Matplotlib
                    width=0.5,
                    color='white'
                )
            )
        ))

        # Construct axis titles including unit
        x_axis_title = x_col_cleaned
        if x_unit_display:
            x_axis_title += f" ({x_unit_display})"

        y_axis_title = y_col_cleaned
        if y_unit_display:
            y_axis_title += f" ({y_unit_display})"

        # Configure layout
        fig.update_layout(
            # Preserve title
            title=dict(
                text=little_theme,
                font=dict(
                    size=16,
                    color='#000000',
                    # Plotly uses its own font configurations; Times New Roman might need specific setup
                    # but we can request it. It might fallback if not available.
                    family='Times New Roman'
                ),
                 # Position title at the top center
                 x=0.5,
                 xanchor='center',
                 yanchor='top'
            ),
            # Configure X-axis
            xaxis=dict(
                title=dict(
                    text=x_axis_title,
                    font=dict(
                        size=14,
                        color='#000000',
                        family='Times New Roman'
                    )
                ),
                linewidth=2, # Prominent axis line
                linecolor='#333333',
                showline=True,
                mirror=True, # Draw lines on top/right as well
                ticks='outside', # Ticks outside the axis line
                tickcolor='#000000',
                tickfont=dict(
                    size=12,
                    color='#000000',
                    family='Times New Roman'
                ),
                # Matplotlib's offset text handling is different. Plotly adds it automatically
                # if needed, usually near the axis title or ticks. We set the title text here.
            ),
            # Configure Y-axis
            yaxis=dict(
                 title=dict(
                    text=y_axis_title,
                    font=dict(
                        size=14,
                        color='#000000',
                        family='Times New Roman'
                    )
                ),
                linewidth=2, # Prominent axis line
                linecolor='#333333',
                showline=True,
                mirror=True, # Draw lines on top/right as well
                ticks='outside', # Ticks outside the axis line
                tickcolor='#000000',
                 tickfont=dict(
                    size=12,
                    color='#000000',
                    family='Times New Roman'
                ),
                 # Plotly handles offset text automatically
            ),
            # Configure overall font
            font=dict(
                family='Times New Roman',
                size=12,
                color='#000000'
            ),
            # Set plot background to white
            plot_bgcolor='white',
            # Set paper background to white
            paper_bgcolor='white',
            # Adjust margins if needed, but Plotly's autodimming usually works well
            # margin=dict(l=50, r=50, b=50, t=50, pad=4)
        )

        # Set the size of the figure (approximating the original figsize=(7, 5))
        # Plotly size is in pixels. 7*100 x 5*100 might be a starting point, or adjust based on visual output.
        # Let's try 700x500 pixels.
        fig.update_layout(width=640, height=480)


        # --- Save to specified file paths ---
        # Directory creation is handled in the calling function (process_all_csv_files)
        try:
            # Use pio.write_image for static export
            # scale=3 approximates 300 DPI for a default size figure
            pio.write_image(fig, png_filepath, format='png', scale=3)
            print(f"Saved PNG to {png_filepath}")
        except Exception as e:
             print(f"Error saving PNG to {png_filepath}: {e}")
             # Note: Plotly static image export requires the `kaleido` engine.
             # If you get an error here, you likely need to install it: `pip install kaleido`
             print("Plotly image export requires 'kaleido'. Install with: pip install kaleido")


        try:
            pio.write_image(fig, svg_filepath, format='svg')
            print(f"Saved SVG to {svg_filepath}")
        except Exception as e:
             print(f"Error saving SVG to {svg_filepath}: {e}")
             print("Plotly image export requires 'kaleido'. Install with: pip install kaleido")
        # --- Save End ---

        # No need to close figure explicitly with Plotly unless managing memory in a loop with many figures.
        # The figure object can be garbage collected.

    except FileNotFoundError: print(f"Error: CSV file not found at {csv_file_path}")
    except ValueError as e: print(f"Skipping file {csv_file_path} due to data format issue: {e}\nDetails: {e}")
    except Exception as e:
        print(f"Skipping file {csv_file_path} due to unexpected error: {e}")
        traceback.print_exc()
# --- Refactored visualize_scatter_plot End ---


# --- process_all_csv_files (Keep structure, call new visualization function) ---
# Accepts specific output directories for png and svg
def process_all_csv_files(input_dir: str, png_output_dir: str, svg_output_dir: str):
    """
    Visualize all scatter CSV files in a directory and save to specified output directories.

    Args:
        input_dir: Directory containing CSV files.
        png_output_dir: Directory to save PNG files.
        svg_output_dir: Directory to save SVG files.
    """
    if not os.path.isdir(input_dir):
        print(f"Input directory not found: {input_dir}")
        return

    # Get all CSV files matching the pattern scatter_*.csv
    # The filename pattern from the generator is scatter_主题名_xx.csv
    # The regex needs to match this pattern
    # Updated regex to match the new filename format scatter_主题名_xx.csv
    files_to_process = glob.glob(os.path.join(input_dir, "scatter_*.csv")) # Use glob for pattern matching

    if not files_to_process:
        print(f"No 'scatter_*_XX.csv' files found in {input_dir}")
        return

    print(f"Found {len(files_to_process)} 'scatter_*_XX.csv' file(s) to process in {input_dir}")

    # Sort files numerically based on the LAST number part in the filename
    # This handles filenames like scatter_TopicName_1.csv, scatter_TopicName_10.csv etc.
    try:
        def sort_key(f):
            base = os.path.basename(f)
            # Regex to find the last number before .csv
            match = re.search(r'_(\d+)\.csv$', base, re.IGNORECASE)
            if match:
                return int(match.group(1))
            return base # Fallback to alphabetical sort if number not found or pattern doesn't match
        files_to_process.sort(key=sort_key)
    except Exception:
         # Generic sort if the specific key fails
         files_to_process.sort()
         print("Warning: Could not sort files numerically based on suffix. Sorting alphabetically.")


    # Ensure output directories exist
    os.makedirs(png_output_dir, exist_ok=True)
    os.makedirs(svg_output_dir, exist_ok=True)

    for csv_path in files_to_process:
        filename = os.path.basename(csv_path)
        base_name = os.path.splitext(filename)[0] # Get filename without extension

        # Construct the specific output paths for PNG and SVG
        png_output_path = os.path.join(png_output_dir, f"{base_name}.png")
        svg_output_path = os.path.join(svg_output_dir, f"{base_name}.svg")

        # Call visualize_scatter_plot with the specific file paths
        visualize_scatter_plot(
            csv_file_path=csv_path,
            png_filepath=png_output_path, # Pass specific PNG path
            svg_filepath=svg_output_path # Pass specific SVG path
        )

    print("\nVisualization process completed.")
# --- process_all_csv_files End ---


# --- Main Execution ---

if __name__ == "__main__":
    # Define specific input and output directories
    INPUT_CSV_DIR = './scatter/csv' # Modified input directory
    OUTPUT_PNG_DIR = './scatter/png' # Modified PNG output directory
    OUTPUT_SVG_DIR = './scatter/svg' # Modified SVG output directory

    # Ensure the input and output directories exist
    os.makedirs(INPUT_CSV_DIR, exist_ok=True) # Ensure input directory exists (in case generator hasn't run)
    os.makedirs(OUTPUT_PNG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_SVG_DIR, exist_ok=True)

    # Call the main processing function with the specified directories
    process_all_csv_files(
        input_dir=INPUT_CSV_DIR,
        png_output_dir=OUTPUT_PNG_DIR, # Pass PNG output directory
        svg_output_dir=OUTPUT_SVG_DIR # Pass SVG output directory
    )
