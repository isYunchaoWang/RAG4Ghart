import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import numpy as np
import os
import traceback
import re # Import re for parsing
from math import sqrt, pi, cos, sin, atan2
from matplotlib.colors import LinearSegmentedColormap
import random
from typing import Tuple, Dict, Any, List, Optional # Import necessary types
# import adjustText as adjust_text # Keeping this commented out as per "002gf" context

# --- Define layout parameters ---
BASE_LAYOUT_SCALE = 0.8
MIN_SPACING_FACTOR = 0.3
BOUNDARY_PADDING = 1.5
MAX_ITERATIONS = 25
REPULSION_DECAY = 0.7

# --- MODIFICATION START: Moved parse_fill_bubble_csv here ---
def parse_fill_bubble_csv(filepath: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Reads the fill_bubble CSV file, parses metadata from the first line,
    and loads the data from the rest, handling potential errors.
    Expected first line: Main theme, little theme, Total Nodes
    Expected data header (second line): size,father,depth,label
    """
    metadata: Dict[str, Any] = {}
    df = pd.DataFrame()
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found at {filepath}")

        # Read the first line (metadata) separately
        with open(filepath, 'r', encoding='utf-8') as f:
            header_line_1 = f.readline().strip()

        # Parse metadata from the first line
        parts_1 = [part.strip() for part in header_line_1.split(',')]
        expected_parts_1 = 3
        if len(parts_1) != expected_parts_1:
            error_msg = f"Incorrect first header format in {filepath}. Expected {expected_parts_1} parts, found {len(parts_1)}. Header: '{header_line_1}'"
            # Check for BOM (Byte Order Mark) which can sometimes cause parsing issues
            if header_line_1 and header_line_1.startswith('\ufeff'):
                 error_msg += " (File might have a BOM)"
            raise ValueError(error_msg)

        metadata['Topic'] = parts_1[0]
        metadata['Little_Theme'] = parts_1[1]
        try:
            metadata['Total_Nodes'] = int(parts_1[2])
        except ValueError:
            print(f"Warning: Could not parse Total Nodes '{parts_1[2]}' in {filepath}. Storing as string.")
            metadata['Total_Nodes'] = parts_1[2]
        except IndexError:
            print(f"Warning: Missing Total Nodes in {filepath}.")
            metadata['Total_Nodes'] = "N/A"

        # Read the rest of the data starting from the second line, using the second line as header
        df = pd.read_csv(filepath, skiprows=1, header=0, encoding='utf-8', index_col=False)

        # Validate required columns
        required_cols = ['size', 'father', 'depth', 'label']
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            raise ValueError(f"Missing required data columns in {filepath}: {', '.join(missing)}. Found: {list(df.columns)}")

        if df.empty:
            print(f"Warning: DataFrame is empty after reading data (before cleaning) from {filepath}.")
            return df, metadata

        # Convert columns to appropriate types and handle missing/invalid data
        # Use errors='coerce' to turn invalid parsing into NaN
        df['size'] = pd.to_numeric(df['size'], errors='coerce')
        # Fill NaN in father/depth with defaults and convert to int
        df['father'] = pd.to_numeric(df['father'], errors='coerce').fillna(0).astype(int)
        df['depth'] = pd.to_numeric(df['depth'], errors='coerce').fillna(1).astype(int)
        df['label'] = df['label'].astype(str).str.strip() # Ensure label is string and strip whitespace

        # Drop rows with missing required values after conversion
        df.dropna(subset=['size', 'label'], inplace=True)

        # Filter out nodes with non-positive size or empty labels (if any slipped through)
        df = df[df['size'] > 0]
        df = df[df['label'] != '']

        if df.empty:
            print(f"Warning: DataFrame is empty after cleaning data from {filepath}.")

    except FileNotFoundError:
        # Re-raise the exception so the caller can handle it
        raise
    except ValueError as ve:
        # Re-raise the exception so the caller can handle it
        raise ve
    except Exception as e:
        # Wrap other exceptions with file context and re-raise
        raise Exception(f"Error reading or parsing CSV file {filepath}: {e}") from e

    return df, metadata
# --- MODIFICATION END ---


def normalize_sizes(nodes: Dict[int, Dict[str, Any]], root_nodes_for_scaling: List[Dict[str, Any]], base_size: float = 800.0):
    if not nodes:
        return
    sizes = [n['size'] for n in nodes.values()]
    max_size = max(sizes) if sizes else 1.0
    scale_factor = base_size / max_size if max_size > 0 else 1.0
    for node_data in nodes.values():
        # Apply scaling factor to the 'size' used for layout calculation
        node_data['size'] *= scale_factor

# Helper function to apply absolute positions recursively
def apply_absolute_positions(node: Dict[str, Any], parent_absolute_x: float, parent_absolute_y: float):
    """
    Recursively calculates and sets the absolute x, y coordinates and radius for a node
    and its children based on their relative positions and the parent's absolute position.
    """
    node['x'] = parent_absolute_x + node['x_relative']
    node['y'] = parent_absolute_y + node['y_relative']
    node['radius'] = node['radius_relative'] # Store the calculated absolute radius (after scaling)
    for child_node_data in node['children']:
        apply_absolute_positions(child_node_data, node['x'], node['y'])


def calculate_layout(nodes: Dict[int, Dict[str, Any]], root_nodes_for_layout: List[Dict[str, Any]]):
    """
    Calculates the relative layout and then applies absolute positions for the bubble nodes.
    This function assumes nodes have 'size', 'children', and will add/modify
    'radius_relative', 'x_relative', 'y_relative', 'radius', 'x', 'y'.
    """
    # Normalize sizes first to get base radius for layout calculation
    normalize_sizes(nodes, root_nodes_for_layout)

    def calculate_relative_layout(node: Dict[str, Any], level: int) -> float:
        """
        Recursively calculates the relative positions and radius for a node and its children.
        This is the force-directed layout part.
        """
        # Base radius based on size, scaled by level
        base_radius = sqrt(node['size']) * BASE_LAYOUT_SCALE * (1.0 - level * 0.03)
        base_radius = max(base_radius, 0.1) # Ensure minimum radius
        node['radius_relative'] = base_radius # Store the calculated relative radius

        # Initialize relative position to (0,0) relative to its parent
        node['x_relative'] = 0
        node['y_relative'] = 0

        if not node['children']:
            # If no children, the node's size determines its relative radius
            return node['radius_relative']

        # If node has children, calculate their relative layouts first
        children_radius_relative = []
        for child_node_data in node['children']:
            child_radius = calculate_relative_layout(child_node_data, level + 1)
            children_radius_relative.append(child_radius)

        # Determine the required space for children
        max_child_radius = max(children_radius_relative) if children_radius_relative else 0
        min_spacing_relative = max_child_radius * MIN_SPACING_FACTOR # Spacing between children

        # Calculate the radius the parent node needs to enclose its children
        # If only one child, parent needs to be big enough for child + spacing within its radius
        if len(node['children']) == 1:
            arrange_radius_relative = children_radius_relative[0] * 1.8 + min_spacing_relative # A bit more than child radius + spacing
        else:
            # For multiple children, approximate needed radius based on sum of squares of radii + spacing
            arrange_radius_relative = sqrt(sum(r**2 for r in children_radius_relative)) * 1.5 + min_spacing_relative


        # The parent's relative radius should be at least its base radius, but also large enough to contain children
        node['radius_relative'] = max(node['radius_relative'], arrange_radius_relative)

        # Calculate the radius of the circle on which children centers will be initially placed
        # This circle is smaller than the parent's radius
        layout_circle_radius_relative = max(
            node['radius_relative'] - max_child_radius - min_spacing_relative * 1.2, # Ensure circle is inside parent boundary
            max_child_radius * 1.2 # Ensure circle is large enough for children
        )
        layout_circle_radius_relative = max(layout_circle_radius_relative, 0.1) # Minimum circle radius

        # Initial placement of children on a circle
        if len(node['children']) > 1:
            golden_angle = np.pi * (3 - np.sqrt(5)) # Golden angle for even distribution
            phase_shift = random.uniform(0, 2 * np.pi) # Randomize starting angle
            initial_angles = [(i * golden_angle + phase_shift) % (2 * np.pi) for i in range(len(node['children']))]
        else:
            # If only one child, place it at a random angle
            initial_angles = [random.uniform(0, 2 * np.pi)]

        for i, (child_node_data, angle) in enumerate(zip(node['children'], initial_angles)):
            # Initial position on the layout circle
            rand_factor = 0.9 + 0.2 * random.random() # Add a bit of randomness to initial placement radius
            child_node_data['x_relative'] = layout_circle_radius_relative * cos(angle) * rand_factor
            child_node_data['y_relative'] = layout_circle_radius_relative * sin(angle) * rand_factor

        # Iterative force-directed layout for children
        for iteration in range(MAX_ITERATIONS):
            total_displacement = 0 # Track movement to check for convergence

            # Repulsion between children nodes
            for i in range(len(node['children'])):
                for j in range(i + 1, len(node['children'])):
                    ci = node['children'][i]
                    cj = node['children'][j]
                    dx = ci['x_relative'] - cj['x_relative']
                    dy = ci['y_relative'] - cj['y_relative']
                    dist = sqrt(dx**2 + dy**2) # Distance between centers
                    dist = dist or 1e-6 # Avoid division by zero if centers are identical

                    # Target distance includes radii and minimum spacing
                    target_dist = ci['radius_relative'] + cj['radius_relative'] + min_spacing_relative

                    overlap = target_dist - dist # How much they overlap or are too close

                    if overlap > 0: # If they are too close
                        # Calculate unit vector direction of repulsion
                        ux, uy = dx / dist, dy / dist
                        # Calculate shift proportional to overlap and decay over iterations
                        shift = overlap * 0.5 * (REPULSION_DECAY**iteration)
                        # Apply shifts in opposite directions
                        ci['x_relative'] += ux * shift; ci['y_relative'] += uy * shift
                        cj['x_relative'] -= ux * shift; cj['y_relative'] -= uy * shift
                        total_displacement += abs(shift) # Sum absolute shifts

            # Attraction/Constraint towards parent center/layout circle
            for child_node_data in node['children']:
                dist_to_center = sqrt(child_node_data['x_relative']**2 + child_node_data['y_relative']**2)

                # Calculate the maximum distance a child's center can be from the parent's center
                # while still being fully inside the parent (considering min spacing)
                safe_radius_for_child_center = node['radius_relative'] - child_node_data['radius_relative'] - (min_spacing_relative * 0.5)
                safe_radius_for_child_center = max(safe_radius_for_child_center, 0) # Cannot be negative

                if dist_to_center > safe_radius_for_child_center:
                    # If child center is too far from parent center, pull it back
                    overshoot = dist_to_center - safe_radius_for_child_center
                    # Calculate unit vector pointing away from parent center
                    ux = child_node_data['x_relative'] / dist_to_center if dist_to_center > 0 else 0
                    uy = child_node_data['y_relative'] / dist_to_center if dist_to_center > 0 else 0

                    # Pull child back towards the parent center
                    child_node_data['x_relative'] -= ux * overshoot * 0.8 # Apply a fraction of overshoot
                    child_node_data['y_relative'] -= uy * overshoot * 0.8
                    total_displacement += overshoot # Add to total displacement

                # Optional: Gently pull children towards the ideal layout circle, especially later iterations
                if iteration > MAX_ITERATIONS // 2 and layout_circle_radius_relative > 0:
                    target_angle = atan2(child_node_data['y_relative'], child_node_data['x_relative'])
                    ideal_radius = layout_circle_radius_relative * 0.95 # Slightly smaller than the ideal circle radius
                    current_radius = dist_to_center # Re-calculate distance to center

                    # Interpolate between current position and ideal position on the circle
                    blend_factor = 0.05 # How strongly to pull towards the ideal circle
                    ideal_x = ideal_radius * cos(target_angle)
                    ideal_y = ideal_radius * sin(target_angle)

                    child_node_data['x_relative'] = child_node_data['x_relative'] * (1 - blend_factor) + ideal_x * blend_factor
                    child_node_data['y_relative'] = child_node_data['y_relative'] * (1 - blend_factor) + ideal_y * blend_factor
                    # Note: This blending doesn't directly add to total_displacement in a simple way,
                    # but it helps guide convergence.

            # Check for convergence: if total movement is very small, stop iterating
            if iteration > 5 and total_displacement < 0.01 * (min_spacing_relative or 1):
                break

        # Return the calculated relative radius of the current node
        return node['radius_relative']

    if not root_nodes_for_layout:
        return # Cannot calculate layout if no root nodes are provided

    # Start the recursive relative layout calculation from the main root
    the_main_root = root_nodes_for_layout[0]
    calculate_relative_layout(the_main_root, 0)

    # Apply the calculated relative positions as absolute positions, starting from (0,0) for the main root
    apply_absolute_positions(the_main_root, 0, 0)


# --- MODIFICATION START: create_hierarchical_bubble_chart signature changed ---
# Accepts specific output file paths for png and svg
def create_hierarchical_bubble_chart(csv_filepath: str, png_filepath: str, svg_filepath: str, visual_scale: float = 1.0) -> bool:
    print(f"Processing {os.path.basename(csv_filepath)}...")
    try:
        # --- MODIFICATION: Call parse_fill_bubble_csv (now defined earlier) ---
        df, metadata = parse_fill_bubble_csv(csv_filepath)
        # --- END MODIFICATION ---

        if df.empty:
             print(f"Skipping file {csv_filepath}: No valid data points after parsing/cleaning.")
             return False

        nodes: Dict[int, Dict[str, Any]] = {}
        for df_index, row in df.iterrows():
             node_id = df_index + 1
             nodes[node_id] = {
                 'id': node_id, 'size': float(row['size']), 'original_size': float(row['size']),
                 'depth': int(row['depth']), 'label': str(row['label']).strip(), 'father': int(row['father']),
                 'children': [], 'radius': 0, 'x': 0, 'y': 0, 'radius_relative': 0, 'x_relative': 0, 'y_relative': 0
             }

        the_main_root_node: Optional[Dict[str, Any]] = None
        # Find the main root node (father=0, depth=1)
        for node_data_val in nodes.values():
            if node_data_val['father'] == 0 and node_data_val['depth'] == 1:
                the_main_root_node = node_data_val
                if node_data_val['id'] != 1:
                     print(f"Warning: Main root found at ID {node_data_val['id']}, not ID 1, in {csv_filepath}.")
                break # Assume only one main root

        if not the_main_root_node:
            print(f"Critical Error: No main root node (father=0, depth=1) found in {csv_filepath}. Cannot create chart.")
            return False

        # Build the hierarchy tree structure by assigning children to parents
        for node_id, node_data_val in nodes.items():
            if node_data_val['father'] != 0: # If not the root
                parent_id = node_data_val['father']
                if parent_id in nodes:
                    nodes[parent_id]['children'].append(node_data_val)
                else:
                    print(f"Warning: Orphan node '{node_data_val['label']}' (ID: {node_id}) in {csv_filepath}. Parent ID {parent_id} not found.")

        # Calculate the layout starting from the main root
        root_nodes_for_layout = [the_main_root_node]
        calculate_layout(nodes, root_nodes_for_layout) # calculate_layout now calls apply_absolute_positions internally

        # Determine the bounds of the layout for setting plot limits and padding
        all_coords = [(n['x'], n['y'], n['radius']) for n in nodes.values() if n['radius'] > 0]
        min_x, max_x, min_y, max_y = 0,0,0,0
        dynamic_padding = 10 * visual_scale # Base padding

        if all_coords:
            min_x = min(x - r for (x, _, r) in all_coords); max_x = max(x + r for (x, _, r) in all_coords)
            min_y = min(y - r for (_, y, r) in all_coords); max_y = max(y + r for (_, y, r) in all_coords)
            width = max_x - min_x; height = max_y - min_y
            # Calculate padding based on the overall size of the layout
            dynamic_padding = max(width, height) * 0.10 * visual_scale # 10% of the larger dimension

            # Apply the visual scale to the final positions and radii after layout calculation
            # Note: This was done inside the loop in the previous version.
            # Doing it here after determining min/max for padding simplifies the padding calculation.
            # However, the font size calculation below depends on the scaled radius, so let's keep the scaling
            # applied to each node during the loop over nodes.
            # Let's revert the scaling part back into the loop over nodes.

            # Recalculate bounds after applying visual_scale if scaling is done per node
            # (Keeping the per-node scaling as in previous versions)
            # The scaling is applied within the calculate_layout -> apply_absolute_positions *implicitly*
            # because calculate_layout calls normalize_sizes which scales the base size,
            # and then positions/radii are derived from that.
            # The visual_scale factor needs to be applied *after* the layout calculation is complete.
            # Let's move the scaling of x, y, radius here.

            for node_data_val in nodes.values():
                # These were already scaled by normalize_sizes indirectly,
                # but apply an additional visual_scale factor for plot size adjustment.
                # Note: The naming 'radius_relative'/'x_relative'/'y_relative' vs 'radius'/'x'/'y' is a bit confusing.
                # 'radius'/'x'/'y' are intended to be the final plot coordinates/sizes.
                # Let's apply visual_scale to the final 'x', 'y', 'radius' values.
                node_data_val['x'] *= visual_scale
                node_data_val['y'] *= visual_scale
                node_data_val['radius'] *= visual_scale


            # Recalculate bounds after applying visual_scale to nodes
            all_coords_scaled = [(n['x'], n['y'], n['radius']) for n in nodes.values() if n['radius'] > 0]
            if all_coords_scaled:
                 min_x = min(x - r for (x, _, r) in all_coords_scaled); max_x = max(x + r for (x, _, r) in all_coords_scaled)
                 min_y = min(y - r for (_, y, r) in all_coords_scaled); max_y = max(y + r for (_, y, r) in all_coords_scaled)
                 width = max_x - min_x; height = max_y - min_y
                 dynamic_padding = max(width, height) * 0.10 # Padding is now a percentage of scaled size


            # --- MODIFICATION: Explicit Font Size based on CSV Depth (002gf context) ---
            # Apply font size logic *after* radius is scaled by visual_scale
            for node_data_val in nodes.values():
                csv_depth = node_data_val['depth']
                if csv_depth == 1: # Root (Your "0-layer")
                    node_data_val['fontsize'] = 20
                elif csv_depth == 2: # Direct children (Your "1st layer")
                    node_data_val['fontsize'] = 17
                elif csv_depth == 3: # Grandchildren (Your "2nd layer")
                    node_data_val['fontsize'] = 14
                else: # Deeper layers, if any
                    node_data_val['fontsize'] = 12 # Default smaller size

                # Apply visual_scale factor to the determined font size
                # The visual_scale**0.4 scaling was already present, keep it.
                node_data_val['fontsize'] *= (visual_scale ** 0.4) # Modest scaling

                # Optional: Simple shrink for very long text in small bubbles, respecting a minimum
                min_render_fontsize = 10 # Absolute minimum font size for rendering
                safe_radius = max(node_data_val['radius'], 1e-3)
                # --- MODIFICATION 1: Format size with two decimal places ---
                estimated_text = f"{node_data_val['label']}, {node_data_val['original_size']:.2f}"
                # --- END MODIFICATION 1 ---

                # Heuristic to check if text might be too wide for the bubble
                # (Length of text * approx_char_width_ratio * fontsize) vs (diameter * coverage_target)
                # Let's use a simpler check: if fontsize is large relative to radius and text is long
                if node_data_val['fontsize'] > safe_radius * 0.8 and len(estimated_text) > 10 : # If font is >80% of radius and text is long
                     # Reduce font size, but not below min_render_fontsize
                     node_data_val['fontsize'] = max(min_render_fontsize, node_data_val['fontsize'] * 0.7)
                elif node_data_val['fontsize'] > safe_radius * 1.0 and len(estimated_text) > 5 : # If font is >100% of radius and text is medium
                     node_data_val['fontsize'] = max(min_render_fontsize, node_data_val['fontsize'] * 0.8)

                node_data_val['fontsize'] = max(min_render_fontsize, node_data_val['fontsize'])
            # --- END MODIFICATION ---

        else: # If no valid nodes after cleaning
            min_x, max_x, min_y, max_y = -10 * visual_scale, 10*visual_scale, -10*visual_scale, 10*visual_scale


        color_palettes_options = [
            {1: ['#ADC8E6', '#82A9D1'], 2: ['#FFB6C1', '#FF9AA2'], 3: ['#A8D8B0', '#87C38F'], 4: ['#D8BFD8', '#C9A0DC'], 5: ['#FFE4B5', '#FFDAB9']},
            {1: ['#AEC6CF', '#94B0BA'], 2: ['#FFD1DC', '#FFB3C6'], 3: ['#BDECB6', '#A3D9A5'], 4: ['#CFCBDB', '#BAB7CE'], 5: ['#FFFACD', '#FFF0AC']},
        ]
        selected_palette = random.choice(color_palettes_options)
        if 1 not in selected_palette:
            selected_palette[1] = ['#D3D3D3', '#C0C0C0']

        depth_color_map: Dict[int, str] = {}
        for node_data_val in nodes.values():
            depth = node_data_val['depth']
            default_color_pair = selected_palette.get(1, ['#CCCCCC', '#AAAAAA'])
            colors_for_depth = selected_palette.get(depth, default_color_pair)
            node_data_val['color'] = colors_for_depth[0]
            if depth not in depth_color_map:
                depth_color_map[depth] = node_data_val['color']

        plt.rcParams.update({'font.family': 'Times New Roman', 'font.size': 12, 'figure.dpi': 300})

        # Calculate figure size based on the bounds of the layout plus padding
        chart_width = max_x - min_x
        chart_height = max_y - min_y
        # Add boundary padding
        plot_width = chart_width + 2 * dynamic_padding
        plot_height = chart_height + 2 * dynamic_padding

        # Determine figure size in inches. Assume 1 inch = 100 layout units for scaling.
        # Adjust fig size to be square or based on aspect ratio if needed, but simple scaling is fine.
        fig_width_inches = max(8, plot_width / 100.0) # Ensure a minimum figure size
        fig_height_inches = max(8, plot_height / 100.0)


        fig, ax = plt.subplots(figsize=(fig_width_inches, fig_height_inches)) # Use calculated figure size
        fig.patch.set_facecolor('white'); ax.set_facecolor('white')

        nodes_to_draw = sorted(nodes.values(), key=lambda n: n['depth'])

        for node_data_val in nodes_to_draw:
            if node_data_val['radius'] <= 0: continue
            ax.add_patch(patches.Circle(
                (node_data_val['x'], node_data_val['y']), radius=node_data_val['radius'],
                facecolor=node_data_val.get('color', '#cccccc'), edgecolor='#333333',
                linewidth=0.75, alpha=0.8, zorder=node_data_val['depth']
            ))

        for node_data_val in nodes_to_draw:
            current_fontsize = node_data_val.get('fontsize', 0)
            if node_data_val['label'] and node_data_val['radius'] > 0.5 * visual_scale and current_fontsize > 0:
                # --- MODIFICATION 1: Format size with two decimal places ---
                display_text = f"{node_data_val['label']}, {node_data_val['original_size']:.2f}"
                # --- END MODIFICATION 1 ---
                ax.text(
                    node_data_val['x'], node_data_val['y'], display_text,
                    ha='center', va='center', fontsize=current_fontsize,
                    color='#000000', zorder=node_data_val['depth'] + 100, wrap=True,
                    path_effects=[path_effects.withStroke(linewidth=1.2, foreground='white')]
                )

        legend_elements: List[patches.Patch] = []
        sorted_legend_depths = sorted([d for d in depth_color_map.keys() if d in depth_color_map])
        for depth_val in sorted_legend_depths:
            color = depth_color_map[depth_val]
            # --- MODIFICATION 2: Change legend labels to Layer 1, 2, 3 etc. ---
            layer_label = f"Layer {depth_val}"
            # --- END MODIFICATION 2 ---
            legend_elements.append(patches.Patch(facecolor=color, edgecolor='#333333', label=layer_label))

        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper right',
                      title="Hierarchy Layers",
                      fontsize=max(8, 10 * visual_scale**0.5),
                      title_fontsize=max(9, 11*visual_scale**0.5),
                      frameon=True, facecolor='#FFFFF0', edgecolor='gray', framealpha=0.8)

        # Set plot limits based on the layout bounds and padding
        ax.set_xlim(min_x - dynamic_padding, max_x + dynamic_padding)
        ax.set_ylim(min_y - dynamic_padding, max_y + dynamic_padding)

        ax.set_aspect('equal', adjustable='box'); ax.axis('off')

        # --- MODIFICATION: Set the chart title ---
        # Get the little theme from metadata. Remove "(unit)" if it was hardcoded before.
        base_chart_title = metadata.get('Little_Theme', 'Hierarchical Bubble Chart')
        # The little theme from the generator is already formatted like "the xx of topic"
        # So just use it directly as the title.
        chart_title = base_chart_title
        ax.set_title(chart_title, fontsize=max(14, 17 * visual_scale**0.7), pad=15)
        # --- END MODIFICATION ---


        # --- MODIFICATION START: Save to specified file paths ---
        # os.makedirs(os.path.dirname(png_filepath), exist_ok=True) # Directory creation handled in process_all_csv_files
        plt.savefig(png_filepath, bbox_inches='tight', facecolor='white')
        # os.makedirs(os.path.dirname(svg_filepath), exist_ok=True) # Directory creation handled in process_all_csv_files
        plt.savefig(svg_filepath, bbox_inches='tight', format='svg', facecolor='white') # Added format='svg'
        # --- MODIFICATION END ---

        plt.close(fig)
        print(f"Successfully created visualization for {os.path.basename(csv_filepath)}")
        return True
    except FileNotFoundError: print(f"Error: CSV file not found at {csv_filepath}")
    except ValueError as e: print(f"Skipping file {csv_filepath} due to data format issue: {e}\nDetails: {e}")
    except Exception as e:
        print(f"Skipping file {csv_filepath} due to unexpected error: {e}")
        traceback.print_exc()
        return False

# --- MODIFICATION START: process_all_csv_files signature and logic changed ---
# Accepts specific output directories for png and svg
def process_all_csv_files(input_dir: str, png_output_dir: str, svg_output_dir: str, visual_scale: float = 1.0):
    """
    Visualize all fill_bubble CSV files in a directory and save to specified output directories.

    Args:
        input_dir: Directory containing CSV files.
        png_output_dir: Directory to save PNG files.
        svg_output_dir: Directory to save SVG files.
        visual_scale: Scaling factor for visualization elements.
    """
    if not os.path.isdir(input_dir):
        print(f"Input directory not found: {input_dir}")
        return

    # Get all CSV files matching the pattern fill_bubble_*.csv
    # The filename pattern from the generator is fill_bubble_主题名_xx.csv
    # The regex needs to match this pattern
    # Updated regex to match the new filename format fill_bubble_主题名_xx.csv
    files_to_process = [f for f in os.listdir(input_dir) if re.match(r'fill_bubble_.*_\d+\.csv$', f, re.IGNORECASE) and not f.startswith('.')]

    if not files_to_process:
        print(f"No 'fill_bubble_*_XX.csv' files found in {input_dir}")
        return

    print(f"Found {len(files_to_process)} 'fill_bubble_*_XX.csv' file(s) to process in {input_dir}")

    # Sort files numerically based on the LAST number part in the filename
    # This handles filenames like fill_bubble_TopicName_1.csv, fill_bubble_TopicName_10.csv etc.
    try:
        def sort_key(f):
            base = os.path.basename(f)
            match = re.search(r'_(\d+)\.csv$', base, re.IGNORECASE)
            if match:
                return int(match.group(1))
            return base # Fallback to alphabetical sort if number not found or pattern doesn't match
        files_to_process.sort(key=sort_key)
    except Exception:
         # Generic sort if the specific key fails
         files_to_process.sort()
         print("Warning: Could not sort files numerically based on suffix. Sorting alphabetically.")


    # Ensure output directories exist (redundant if done in main, but safe for standalone calls)
    os.makedirs(png_output_dir, exist_ok=True)
    os.makedirs(svg_output_dir, exist_ok=True)

    for filename in files_to_process:
        csv_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0] # Get filename without extension

        # Construct the specific output paths for PNG and SVG
        png_output_path = os.path.join(png_output_dir, f"{base_name}.png")
        svg_output_path = os.path.join(svg_output_dir, f"{base_name}.svg")

        # Call create_hierarchical_bubble_chart with the specific file paths
        create_hierarchical_bubble_chart(
            csv_filepath=csv_path,
            png_filepath=png_output_path, # Pass specific PNG path
            svg_filepath=svg_output_path, # Pass specific SVG path
            visual_scale=visual_scale
        )

    print("\nVisualization process completed.")
# --- MODIFICATION END: process_all_csv_files signature and logic changed ---


# --- Main Execution ---
if __name__ == "__main__":
    # --- MODIFICATION START: Define specific input and output directories ---
    INPUT_CSV_DIR = './fill_bubble/csv' # Modified input directory
    OUTPUT_PNG_DIR = './fill_bubble/png' # Modified PNG output directory
    OUTPUT_SVG_DIR = './fill_bubble/svg' # Modified SVG output directory
    # --- MODIFICATION END ---

    # --- MODIFICATION START: Ensure the input and output directories exist ---
    os.makedirs(INPUT_CSV_DIR, exist_ok=True) # Ensure input directory exists (in case generator hasn't run)
    os.makedirs(OUTPUT_PNG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_SVG_DIR, exist_ok=True)
    # --- MODIFICATION END ---

    # Call the main processing function with the specified directories
    process_all_csv_files(
        input_dir=INPUT_CSV_DIR,
        png_output_dir=OUTPUT_PNG_DIR, # Pass PNG output directory
        svg_output_dir=OUTPUT_SVG_DIR, # Pass SVG output directory
        visual_scale=1.0
    )

