import pandas as pd
# Re-add matplotlib.pyplot specifically for listing colormaps
import matplotlib.pyplot as plt # <-- Re-added this import
import os
# from matplotlib import rcParams # Remove rcParams
import numpy as np
# Remove matplotlib colormap specific imports
# from matplotlib.colors import LinearSegmentedColormap
# Remove toolkit import
# from mpl_toolkits.axes_grid1 import make_axes_locatable
import io # Keep io (though might not be strictly needed after removing mpl)
import re # Keep re
import traceback # Keep traceback
import glob # Keep glob
import random # <-- Keep random import

# Import Plotly libraries
import plotly.graph_objects as go
import plotly.io as pio
import plotly.colors as pcolors # Import Plotly colors
# Need a way to get colors from Matplotlib colormaps for sampling.
import matplotlib.cm as cm # Keep cm for color sampling


# (Keep the colormap lists and filtering logic as before)
# Define single-color and dual-color color map lists
# Explicitly removing colormaps known to produce very dark, black, deep blue, deep purple, or brown colors.
# The lists are maintained to exclude potentially problematic maps based on common usage and visual outcome.
single_color_cmaps = [
    # Removed maps that often have very dark ends or are perceptually uniform but go to black/deep colors
    # 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', # Standard sequential, often have dark ends
    # 'viridis', 'plasma', 'inferno', 'magma', # Perceptually uniform, but have very dark ends
    # 'Greys', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'copper', 'hot', 'afmhot', 'gist_heat', # Black, grey, brown, or harsh dark ends
    # 'PuRd', 'RdPu', # Contain purple, might be too deep even with truncation
    # 'PuBu', 'PuBuGn', 'GnBu', 'YlGnBu', # Contain blue, might be too deep even with truncation
    # 'YlOrRd', 'OrRd', 'YlOrBr', # Contain red/orange/brown, OrRd/YlOrBr might be too dark/brown

    # Keeping maps that are generally lighter or transition to lighter shades, and avoid deep blues/purples/blacks/browns
    'YlGn',       # Yellow-Green (lighter greens)
    'Wistia',     # Pink-Yellow-Orange (generally bright)
    'summer',     # Green-Yellow (bright)
    'spring',     # Pink-Yellow (bright)
    'autumn',     # Red-Orange-Yellow (bright/warm)
    'Oranges',    # Re-added Oranges, truncation helps manage the dark end. Can be vibrant.
    'Reds',       # Re-added Reds, truncation helps manage the dark end. Can be vibrant.
    'Greens',     # Re-added Greens, truncation helps manage the dark end. Can be vibrant.
    'Blues'       # Re-added Blues, truncation helps manage the dark end. Can be vibrant.
    # Note: Re-adding Oranges, Reds, Greens, Blues relies more heavily on the truncation (0.35).
    # YlGnBu, GnBu, PuRd, RdPu are still excluded as they are more prone to deep blues/purples.
]

dual_color_cmaps = [
    # Removed diverging maps known for dark or problematic ends (blue/purple/black/brown)
    # 'RdBu_r', 'PuOr', 'BrBG', 'RdGy', 'seismic', # Often have dark ends, or involve blue/purple
    # 'Spectral', # Can have deep blue/purple ends
    # 'twilight', 'twilight_shifted', 'hsv', # Cyclic, can have dark transitions or jarring colors
    # 'terrain', 'ocean', 'gist_earth', # Geophysical, often dark/deep blues/greens/browns
    # 'PRGn', 'PRGn_r', # Purple-Green (involve purple)
    # 'PiYG', # Pink-Yellow-Green (can lean purple)
    # 'RdYlBu', # Red-Yellow-Blue (involves blue)

    # Keeping diverging maps that are generally lighter or transition between less extreme colors
    'RdYlGn_r',   # Green-Yellow-Red (avoids deep blue/purple)
    'coolwarm',   # Blue-Red (can have blue/red ends, but truncation helps, common diverging map)
    'bwr',        # Blue-White-Red (similar to coolwarm, truncation helps)
    # Note: coolwarm and bwr still involve blue/red extremes, but are common diverging maps.
    # Truncation is crucial here.
]


# Ensure lists contain unique color map names
single_color_cmaps = list(set(single_color_cmaps))
dual_color_cmaps = list(set(dual_color_cmaps))

# Filter out any cmap names that might not exist in the current matplotlib version
# This is a safeguard
# Use plt.colormaps() instead of cm.list_colormaps()
all_available_cmaps = list(plt.colormaps()) # <-- Corrected this line
single_color_cmaps = [c for c in single_color_cmaps if c in all_available_cmaps]
dual_color_cmaps = [c for c in dual_color_cmaps if c in all_available_cmaps]

# Final check to ensure lists are not empty after filtering
if not single_color_cmaps and not dual_color_cmaps:
    print("Warning: No suitable color maps available after extensive filtering!")
    # As a fallback, add a few universally available and relatively light maps if possible
    fallback_cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'coolwarm', 'bwr']
    for cmap_name in fallback_cmaps:
         if cmap_name in all_available_cmaps:
             if cmap_name in ['viridis', 'plasma', 'inferno', 'magma', 'cividis']:
                 if cmap_name not in single_color_cmaps: single_color_cmaps.append(cmap_name)
             else: # coolwarm, bwr
                 if cmap_name not in dual_color_cmaps: dual_color_cmaps.append(cmap_name)
    print(f"Using fallback color maps: Single={single_color_cmaps}, Dual={dual_color_cmaps}")

# Helper function to convert RGBA tuple (0-1) to Hex string
def rgba_to_hex(rgba):
    """Converts an RGBA tuple (0-1 range) to a hex color string."""
    if len(rgba) == 4:
        r, g, b, a = rgba
    elif len(rgba) == 3: # Assume alpha is 1.0 if not provided
        r, g, b = rgba
        a = 1.0
    else:
        raise ValueError("Invalid RGBA tuple length")

    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    # Plotly hex colors do not include alpha, unless using rgba() string format.
    # For heatmap colorscale, list of colors is usually RGB.
    return f'#{r:02x}{g:02x}{b:02x}'

# --- Refactored visualize_heatmap using Plotly ---
def visualize_heatmap(csv_file_path, png_output_dir, svg_output_dir):
    """
    Visualize heatmap data from CSV file and save as PNG and SVG to specified directories using Plotly.

    Args:
        csv_file_path: Path to the input CSV file
        png_output_dir: Directory to save PNG files.
        svg_output_dir: Directory to save SVG files.
    """
    try:
        # Read the CSV file
        # Assuming the first row is metadata: Main theme, little theme, dimension, pattern
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            # Read the header line
            header_line = f.readline().strip()
            # Read the rest as DataFrame, skipping the header row
            df = pd.read_csv(f, header=None)

        # Check if DataFrame has enough columns (at least 3 for data)
        if df.shape[1] < 3:
            print(f"Error: CSV file {csv_file_path} does not have at least 3 data columns.")
            return

        # Manually set column names assuming the first three data columns are x_block, y_block, level
        df.rename(columns={0: 'x_block', 1: 'y_block', 2: 'level'}, inplace=True)

        # Parse metadata from the header line: Main theme, little theme, dimension, pattern
        metadata = {}
        parts = [part.strip() for part in header_line.split(',')]

        if len(parts) >= 4:
            metadata['topic'] = parts[0] # Main theme
            metadata['little_theme'] = parts[1] # Little theme
            metadata['dimension_str'] = parts[2] # Dimension string
            metadata['pattern'] = parts[3] # Pattern

            # Optional: Parse dimensions if needed later (using the third part)
            try:
                x_str, y_str = metadata['dimension_str'].split('x')
                metadata['x_blocks'] = int(x_str.strip())
                metadata['y_blocks'] = int(y_str.strip())
            except (IndexError, ValueError):
                metadata['x_blocks'] = None
                metadata['y_blocks'] = None

        else:
            print(f"Warning: Header line in {csv_file_path} does not match expected format (Main theme, little theme, dimension, pattern). Using default metadata.")
            metadata['topic'] = 'Unknown Topic'
            metadata['little_theme'] = 'Unknown Purpose' # Default little theme
            metadata['dimension_str'] = 'NxM'
            metadata['x_blocks'] = None
            metadata['y_blocks'] = None
            metadata['pattern'] = 'Unknown Pattern'


        if df.empty:
             print(f"Error: DataFrame from {csv_file_path} is empty after reading.")
             return

        # Ensure 'level' column is numeric and round to 2 decimal places
        df['level'] = pd.to_numeric(df['level'], errors='coerce')
        df['level'] = df['level'].round(2) # Explicitly round to 2 decimals


        # Ensure x_block and y_block columns exist and are suitable for pivoting index/columns
        if 'x_block' not in df.columns or 'y_block' not in df.columns or 'level' not in df.columns:
             print(f"Error: DataFrame from {csv_file_path} is missing required columns (x_block, y_block, level) after renaming.")
             return

        # Attempt to sort labels before pivoting to ensure consistent ordering
        # Get unique labels and sort them
        unique_x_labels = sorted(df['x_block'].unique().tolist())
        unique_y_labels = sorted(df['y_block'].unique().tolist())

        # Drop rows where x_block or y_block might have become NaN or are otherwise invalid
        df.dropna(subset=['x_block', 'y_block'], inplace=True)

        # Pivot the data for heatmap
        # Handle potential duplicates in x_block, y_block pairs by taking the mean value
        # pivot_table automatically ignores NaN values in the 'level' column during aggregation
        # Plotly heatmap z-values correspond to y-index, x-index.
        # So index=y_block, columns=x_block is the correct pivot for Plotly.
        heatmap_data = df.pivot_table(index='y_block', columns='x_block', values='level', aggfunc='mean')

        if heatmap_data.empty:
             print(f"Error: Pivoted data from {csv_file_path} is empty or contains only NaNs.")
             return

        # Reindex to ensure all original unique labels are present in the pivoted table,
        # even if a combination is missing in the data (will result in NaN)
        # This ensures the heatmap dimensions match the expected labels.
        heatmap_data = heatmap_data.reindex(index=unique_y_labels, columns=unique_x_labels)


        # --- Random color map selection logic (remains the same) ---
        available_cmap_types = []
        if single_color_cmaps:
            available_cmap_types.append('single')
        if dual_color_cmaps:
            available_cmap_types.append('dual')

        if not available_cmap_types:
             print("Error: No suitable color maps available after filtering and fallback.")
             return # Exit the function if no cmaps

        weights = None
        if 'single' in available_cmap_types and 'dual' in available_cmap_types:
             weights = [7, 3] # More weight to single color maps
        elif 'single' in available_cmap_types:
             weights = [1]
        elif 'dual' in available_cmap_types:
             weights = [1]

        chosen_type = random.choices(available_cmap_types, weights=weights, k=1)[0]
        selected_cmap_name = random.choice(single_color_cmaps) if chosen_type == 'single' else random.choice(dual_color_cmaps)
        cmap_type = "Single Color" if chosen_type == 'single' else "Dual Color"
        print(f"Processing with color map: {selected_cmap_name} ({cmap_type})")

        # --- Modify the selected colormap to reduce darkness and get Plotly colors ---
        # Use matplotlib.cm to get the colormap and sample it
        # Use cm.get_cmap() which is available in older matplotlib versions
        original_cmap = cm.get_cmap(selected_cmap_name)
        dark_color_truncation = 0.35 # Increased from 0.3

        cmap_sample_start = 0.0
        cmap_sample_stop = 1.0
        # Heuristic for maps that are dark at the start of the 0-1 range
        dark_at_start_maps_heuristic = selected_cmap_name.endswith('_r') or selected_cmap_name in ['hot', 'copper', 'gist_heat', 'afmhot', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone']

        if selected_cmap_name in dual_color_cmaps:
             # For diverging maps, truncate equally from both ends
             truncation_per_end = dark_color_truncation / 2.0
             cmap_sample_start = truncation_per_end
             cmap_sample_stop = 1.0 - truncation_per_end
        elif dark_at_start_maps_heuristic:
             # For sequential maps that are dark at the start, truncate from the start
             cmap_sample_start = dark_color_truncation
             cmap_sample_stop = 1.0
        else:
             # For sequential maps that are dark at the end, truncate from the end
             cmap_sample_start = 0.0
             cmap_sample_stop = 1.0 - dark_color_truncation

        cmap_sample_start = max(0.0, cmap_sample_start)
        cmap_sample_stop = min(1.0, cmap_sample_stop)

        num_colors = 256 # Number of colors to sample
        if cmap_sample_start >= cmap_sample_stop - 1e-9:
            print(f"Warning: Truncation resulted in invalid range [{cmap_sample_start:.2f}, {cmap_sample_stop:.2f}] for {selected_cmap_name}. Using full colormap range.")
            cmap_sample_start = 0.0
            cmap_sample_stop = 1.0

        # Get colors from the truncated range using the matplotlib colormap
        sampled_colors_rgba = original_cmap(np.linspace(cmap_sample_start, cmap_sample_stop, num_colors))
        # Convert RGBA colors to Hex strings for Plotly
        plotly_colorscale = [rgba_to_hex(color) for color in sampled_colors_rgba]

        # ----------------------------------------------------

        # Use vmin/vmax based on the range of values in the heatmap data
        valid_data = heatmap_data.values[~np.isnan(heatmap_data.values)]

        if valid_data.size == 0:
            print(f"Error: Heatmap data from {csv_file_path} contains only NaNs or is empty after reindexing.")
            return

        data_min = np.min(valid_data)
        data_max = np.max(valid_data)

        if data_min == data_max:
             vmin = data_min - 0.01 if data_min > 0.01 else 0
             vmax = data_max + 0.01 if data_max < 0.99 else 1
             if vmin == vmax:
                 vmin = max(0.0, vmin - 0.001)
                 vmax = min(1.0, vmax + 0.001)
             print(f"Warning: All non-NaN heatmap values are identical ({data_min}). Using colorbar range [{vmin:.2f}, {vmax:.2f}].")
        else:
             vmin, vmax = data_min, data_max

        # Create Plotly figure
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns.tolist(), # Use the actual column names as x-axis labels
            y=heatmap_data.index.tolist(),   # Use the actual index names as y-axis labels
            colorscale=plotly_colorscale,    # Use the modified list of colors
            zmin=vmin,                       # Set color mapping min directly on trace
            zmax=vmax,                       # Set color mapping max directly on trace
            hoverinfo='x+y+z',               # Show x, y, and z value on hover
            # --- MODIFICATION START: Configure Colorbar directly in the trace with outline ---
            colorbar=dict(
                # Corrected title configuration
                title=dict(
                    text='Level', # Color bar title text
                    side='right', # Position of the title ('right', 'top', 'bottom')
                    font=dict(
                        size=14, # Original color bar label size
                        color='#000000',
                        family='Times New Roman'
                    )
                ),
                tickfont=dict(
                    size=12, # Original code used 12 for color bar ticks
                    color='#000000',
                    family='Times New Roman'
                ),
                # Set color bar ticks based on calculated vmin/vmax
                tickvals=np.linspace(vmin, vmax, 5).round(2).tolist(), # 5 ticks, rounded
                # You can add ticktext if you want custom labels, but default is fine here
                len=1.05, # Make colorbar length match plot height (100%) - This meets the height requirement
                lenmode='fraction', # Explicitly state length is a fraction
                thickness=20 / 3, # Adjust thickness (in pixels) - This meets the width requirement (1/3 of 20px)
                thicknessmode='pixels', # Explicitly state thickness is in pixels
                orientation='v', # Explicitly state orientation is vertical
                 # Position the colorbar relative to the plot
                x=1.02, # Position slightly outside the right edge of the plot (fraction of plot width)
                xanchor='left', # Anchor the left side of the colorbar at x
                y=0.5, # Vertically centered relative to the plot height (fraction of plot height)
                yanchor='middle', # Anchor the middle of the colorbar at y
                # Add OUTLINE properties for the border around the colored bar
                outlinecolor='#000000', # Black outline color
                outlinewidth=1 # 1 pixel outline width
                # Removed bordercolor and borderwidth
            )
            # --- MODIFICATION END: Configure Colorbar directly in the trace with outline ---
        ))

        # Set title - Use the little theme from metadata
        little_theme_name = metadata.get('little_theme', 'Unknown Purpose')


        # Add value annotations
        annotations = []
        text_color = "#000000" # Black text color
        # Iterate through the pivoted data to get values and positions
        for i in range(heatmap_data.shape[0]): # Iterate through rows (y-axis labels)
            for j in range(heatmap_data.shape[1]): # Iterate through columns (x-axis labels)
                # Get the value at this position
                value = heatmap_data.iloc[i, j]
                # Get the corresponding x and y labels
                x_label = heatmap_data.columns[j]
                y_label = heatmap_data.index[i]

                if pd.notna(value):
                     annotations.append(dict(
                         x=x_label,        # Use the actual x-label as the x coordinate
                         y=y_label,        # Use the actual y-label as the y coordinate
                         text=f"{value:.2f}", # Text to display (formatted value)
                         showarrow=False,  # Do not show an arrow pointing to the text
                         xanchor='center', # Center the text horizontally
                         yanchor='middle', # Center the text vertically
                         font=dict(
                             color=text_color, # Text color
                             size=10,          # Font size
                             family='Times New Roman' # Font family
                         )
                     ))
        # Add annotations to the layout
        fig.update_layout(annotations=annotations)


        # Configure layout
        fig.update_layout(
            # Preserve title
            title=dict(
                text=little_theme_name,
                font=dict(
                    size=16, # Original heatmap title size
                    color='#000000',
                    family='Times New Roman'
                ),
                 # Position title at the top center
                 x=0.5,
                 xanchor='center',
                 yanchor='top'
            ),
            # Configure X-axis
            xaxis=dict(
                title=dict( # Heatmap doesn't have explicit X/Y axis titles in original plot, only tick labels
                    text="", # No axis title text
                    font=dict( # Still define font for consistency if title added later
                        size=12, # Using 12 as base font size
                        color='#000000',
                        family='Times New Roman'
                    )
                ),
                tickvals=heatmap_data.columns.tolist(), # Use actual labels as tick values
                ticktext=[str(label) for label in heatmap_data.columns], # Use actual labels as tick text
                tickangle=-45, # Rotate x-axis labels
                tickfont=dict(
                    size=12, # Original code used 12 for tick labels
                    color='#000000',
                    family='Times New Roman'
                ),
                showgrid=False, # Remove grid lines
                zeroline=False, # Remove zero line
                showline=False, # <-- Hide axis line
                ticks='outside', # Ticks outside the axis line - Still show ticks even if line is hidden
                tickcolor='#000000',
            ),
            # Configure Y-axis
            yaxis=dict(
                 title=dict( # No axis title text
                    text="",
                    font=dict(
                        size=12,
                        color='#000000',
                        family='Times New Roman'
                    )
                ),
                tickvals=heatmap_data.index.tolist(), # Use actual index values as tick values
                ticktext=[str(label) for label in heatmap_data.index], # Use actual index values as tick text
                tickfont=dict(
                    size=12, # Original code used 12 for tick labels
                    color='#000000',
                    family='Times New Roman'
                ),
                showgrid=False, # Remove grid lines
                zeroline=False, # Remove zero line
                showline=False, # <-- Hide axis line
                ticks='outside', # Ticks outside the axis line - Still show ticks even if line is hidden
                tickcolor='#000000',
                # Invert y-axis so index 0 is at the top, matching imshow default
                autorange="reversed"
            ),
            # Configure overall font
            font=dict(
                family='Times New Roman',
                size=12, # Base font size
                color='#000000'
            ),
            # Set plot background to white
            plot_bgcolor='white',
            # Set paper background to white
            paper_bgcolor='white',
            # Set figure size (approximating original dynamic size)
            # Plotly size is in pixels. Original scaled roughly by 80 pixels per block.
            # Add some base size for padding/margins.
            width=max(600, heatmap_data.shape[1]*80),
            height=max(480, heatmap_data.shape[0]*80),
            # --- MODIFICATION START: Adjust margins ---
            # l, r, b, t are left, right, bottom, top margins in pixels
            # Adjusted margins again based on border and thinner colorbar
            # Need enough right margin for colorbar, its title, and ticks/labels
            margin=dict(l=30, r=100, b=80, t=80, pad=4) # Slightly increased right margin to accommodate colorbar + border + labels
            # --- MODIFICATION END: Adjust margins ---
        )

        # --- Save to specified output directories ---
        # Directory creation is handled in the calling function (visualize_all_heatmaps)

        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(csv_file_path))[0]
        output_filename_base = f"{base_name}"

        # Save as PNG
        png_path = os.path.join(png_output_dir, f"{output_filename_base}.png")
        try:
            # Use pio.write_image for static export
            # scale=3 approximates 300 DPI for a default size figure
            pio.write_image(fig, png_path, format='png', scale=3)
            print(f"Saved PNG to {png_path}")
        except Exception as e:
             print(f"Error saving PNG to {png_path}: {e}")
             print("Plotly image export requires 'kaleido'. Install with: pip install kaleido")
             # Re-raise or handle differently if saving is critical
             # raise # Uncomment to stop processing on first save error

        # Save as SVG
        svg_path = os.path.join(svg_output_dir, f"{output_filename_base}.svg")
        try:
            pio.write_image(fig, svg_path, format='svg')
            print(f"Saved SVG to {svg_path}")
        except Exception as e:
             print(f"Error saving SVG to {svg_path}: {e}")
             print("Plotly image export requires 'kaleido'. Install with: pip install kaleido")
             # Re-raise or handle differently if saving is critical
             # raise # Uncomment to stop processing on first save error

        # --- Save End ---

        # No explicit figure closing needed with Plotly objects unless managing a large number.

    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
    except pd.errors.EmptyDataError:
        print(f"Error: CSV file {csv_file_path} is empty.")
    except ValueError as e: # Explicitly catch ValueError
         print(f"Skipping file {csv_file_path} due to data or configuration issue: {e}")
         traceback.print_exc()
    except Exception as e:
        print(f"An unexpected error occurred while processing {csv_file_path}:")
        traceback.print_exc() # Print full traceback for debugging
        # In case of error, no matplotlib figures to close.


# --- visualize_all_heatmaps (Keep structure, call new visualization function) ---
# Accepts specific output directories for png and svg
def visualize_all_heatmaps(input_dir, png_output_dir, svg_output_dir):
    """
    Visualize all heatmap CSV files in a directory and save to specified output directories.

    Args:
        input_dir: Directory containing CSV files.
        png_output_dir: Directory to save PNG files.
        svg_output_dir: Directory to save SVG files.
    """
    if not os.path.isdir(input_dir):
        print(f"Input directory not found: {input_dir}")
        return

    # Get all CSV files in input directory
    # Sorting now happens in the generation script by filename
    # We can still sort here for processing order consistency if needed,
    # but the filenames are already sequential.
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]

    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return

    # Sort files numerically based on the sequence number in the filename (e.g., heatmap_XX.csv or heatmap_Topic_XX.csv)
    try:
        def sort_key(f):
            base = os.path.basename(f)
            match = re.search(r'_(\d+)\.csv$', base)
            if match:
                return int(match.group(1))
            return base # Fallback to alphabetical sort if number not found
        csv_files.sort(key=sort_key)
    except Exception:
         # Generic sort if the specific key fails
         csv_files.sort()
         print("Warning: Could not sort files numerically. Sorting alphabetically.")


    print(f"Found {len(csv_files)} CSV files in {input_dir}. Visualizing...")

    # Ensure output directories exist (redundant with main block, but harmless)
    os.makedirs(png_output_dir, exist_ok=True)
    os.makedirs(svg_output_dir, exist_ok=True)


    for csv_file in csv_files: # Process in sorted order
        csv_path = os.path.join(input_dir, csv_file)
        print(f"\n--- Processing {csv_file} ---")
        # Pass the specific output directories to visualize_heatmap
        visualize_heatmap(csv_path, png_output_dir, svg_output_dir)

    print("\nVisualization process completed.")
# --- visualize_all_heatmaps End ---


# --- Main Execution ---
if __name__ == "__main__":
    # Define the input and output directories
    INPUT_CSV_DIR = "./heatmap/csv" # Modified input directory
    OUTPUT_PNG_DIR = "./heatmap/png" # Modified PNG output directory
    OUTPUT_SVG_DIR = "./heatmap/svg" # Modified SVG output directory

    # Ensure the output directories exist
    os.makedirs(OUTPUT_PNG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_SVG_DIR, exist_ok=True)

    # Call the main visualization function with the specified directories
    visualize_all_heatmaps(input_dir=INPUT_CSV_DIR, png_output_dir=OUTPUT_PNG_DIR, svg_output_dir=OUTPUT_SVG_DIR)
