import random
import csv
from typing import List, Dict, Any, Optional, Tuple
import os
import io # Import io for handling BOM
import re # Import regex for cleaning keys

# --- Configuration Data ---

# Define 15 topics and their hierarchical labels (up to 3 layers)
# Format: { "Topic Name": { "Depth 2 Label": ["Depth 3 Label 1", "Depth 3 Label 2", ...], ... }, ... }
hierarchical_topics: Dict[str, Dict[str, List[str]]] = {
    "Technology and Software": {
        "Software Development": ["Frontend", "Backend", "Mobile", "Database", "DevOps", "Testing"],
        "Artificial Intelligence": ["Machine Learning", "Natural Language Processing", "Computer Vision", "Reinforcement Learning", "Neural Networks"],
        "Cloud Computing": ["AWS", "Azure", "Google Cloud", "Cloud Native", "Serverless"],
        "Cybersecurity": ["Network Security", "Endpoint Security", "Cryptography", "Threat Intelligence", "Vulnerability Management"],
        "Data Science": ["Data Analysis", "Big Data", "Data Visualization", "Statistical Modeling", "Data Engineering"]
    },
    "Healthcare and Medicine": {
        "Medical Specialties": ["Cardiology", "Neurology", "Oncology", "Pediatrics", "Dermatology", "Psychiatry"],
        "Medical Procedures": ["Surgery", "Diagnosis", "Therapy", "Rehabilitation", "Preventive Care"],
        "Pharmaceuticals": ["Drug Discovery", "Clinical Trials", "Pharmacology", "Pharmacy Practice"],
        "Hospital Management": ["Patient Care", "Administration", "Healthcare Informatics", "Quality Control"]
    },
    "Business and Finance": {
        "Investments": ["Stocks", "Bonds", "Real Estate", "Cryptocurrency", "Mutual Funds", "ETFs"],
        "Banking": ["Retail Banking", "Commercial Banking", "Investment Banking", "Digital Banking"],
        "Financial Markets": ["Stock Market", "Forex Market", "Commodity Market", "Derivatives"],
        "Accounting and Audit": ["Taxation", "Compliance", "Financial Reporting", "Auditing"]
    },
    "Education and Academics": {
        "Sciences": ["Physics", "Chemistry", "Biology", "Astronomy", "Geology", "Environmental Science"],
        "Humanities": ["History", "Literature", "Philosophy", "Linguistics", "Archaeology", "Cultural Studies"],
        "Engineering": ["Mechanical Engineering", "Electrical Engineering", "Civil Engineering", "Chemical Engineering", "Aerospace Engineering"],
        "Social Sciences": ["Psychology", "Sociology", "Economics", "Political Science", "Anthropology"]
    },
    "Food and Beverage": {
        "Cuisines": ["Italian Cuisine", "Mexican Cuisine", "Asian Cuisine", "Mediterranean Cuisine", "French Cuisine", "Indian Cuisine"],
        "Ingredients": ["Fruits and Vegetables", "Meats and Poultry", "Dairy and Eggs", "Grains and Legumes", "Spices and Herbs", "Seafood"],
        "Beverages": ["Coffee and Tea", "Alcoholic Drinks", "Juices and Smoothies", "Soft Drinks", "Water"]
    },
    "Transportation and Logistics": {
        "Modes of Transport": ["Road Transport", "Rail Transport", "Air Transport", "Maritime Transport", "Pipeline Transport"],
        "Logistics Operations": ["Warehousing", "Inventory Management", "Supply Chain", "Freight Forwarding", "Last-Mile Delivery"],
        "Vehicle Technology": ["Electric Vehicles", "Autonomous Vehicles", "Aerospace Technology", "Marine Engineering"]
    },
    "Environmental Science": {
        "Conservation": ["Wildlife Conservation", "Forest Conservation", "Marine Conservation", "Habitat Restoration"],
        "Renewable Energy": ["Solar Energy", "Wind Energy", "Hydro Energy", "Geothermal Energy", "Bioenergy"],
        "Pollution Control": ["Air Pollution", "Water Pollution", "Waste Management", "Soil Remediation"]
    },
    "Arts and Culture": {
        "Visual Arts": ["Painting", "Sculpture", "Photography", "Drawing", "Digital Art"],
        "Performing Arts": ["Music", "Theater", "Dance", "Opera", "Circus Arts"],
        "Literature and Writing": ["Fiction", "Non-Fiction", "Poetry", "Playwriting", "Screenwriting"],
        "Museums and Galleries": ["Collections", "Exhibitions", "Conservation", "Curatorial Studies"]
    },
    "Sports and Recreation": {
        "Team Sports": ["Soccer", "Basketball", "Baseball", "Volleyball", "American Football", "Hockey"],
        "Individual Sports": ["Tennis", "Swimming", "Athletics", "Gymnastics", "Cycling", "Badminton"],
        "Outdoor Activities": ["Hiking", "Camping", "Skiing", "Snowboarding", "Rock Climbing", "Kayaking"]
    },
    "Real Estate and Construction": {
        "Property Types": ["Residential Real Estate", "Commercial Real Estate", "Industrial Real Estate", "Land Development"],
        "Construction Phases": ["Planning and Design", "Building", "Finishing", "Inspection"],
        "Market Analysis": ["Valuation", "Trends", "Investment Analysis"],
        "Building Materials": ["Concrete", "Steel", "Wood", "Masonry"]
    },
     "Media and Communication": {
        "Social Media Platforms": ["Facebook", "Instagram", "Twitter", "TikTok", "LinkedIn", "Pinterest"],
        "Traditional Media": ["Television", "Radio", "Print Journalism", "Film"],
        "Digital Content": ["Streaming Services", "Podcasting", "Online News", "Blogging", "Vlogging"]
    },
    "Government and Politics": {
        "Levels of Government": ["Federal Government", "State Government", "Local Government", "International Relations"],
        "Policy Areas": ["Economic Policy", "Social Policy", "Foreign Policy", "Environmental Policy", "Healthcare Policy"],
        "Political Processes": ["Elections", "Legislation", "Lobbying", "Public Administration"]
    },
    "Manufacturing and Industry": {
        "Industry Sectors": ["Automotive Manufacturing", "Electronics Manufacturing", "Textile Manufacturing", "Food Processing", "Chemical Manufacturing"],
        "Production Processes": ["Assembly Line", "Quality Control", "Supply Chain Management", "Automation", "Lean Manufacturing"],
        "Materials Science": ["Metals", "Plastics", "Composites", "Ceramics"]
    },
    "Tourism and Hospitality": {
        "Accommodation": ["Hotels", "Resorts", "Vacation Rentals", "Hostels", "Bed and Breakfasts"],
        "Tourism Types": ["Adventure Tourism", "Cultural Tourism", "Eco-Tourism", "Business Tourism", "Medical Tourism"],
        "Destinations": ["Urban Destinations", "Coastal Destinations", "Mountain Destinations", "Rural Destinations"]
    },
    "Retail and E-commerce": {
        "Retail Channels": ["Physical Stores", "Online Stores", "Mobile Commerce", "Pop-up Shops"],
        "Product Categories": ["Apparel", "Electronics", "Home Goods", "Groceries", "Health and Beauty", "Books and Media"],
        "Customer Experience": ["Customer Service", "Personalization", "Loyalty Programs", "User Interface (UI)"]
    }
}

# Define diverse English descriptors for constructing the little theme "the xx of main theme"
ENGLISH_DESCRIPTORS = [
    "Breakdown", "Composition", "Structure", "Hierarchy", "Overview",
    "Distribution", "Analysis", "Segments", "Landscape", "Map", "Classification"
]

# --- NEW FUNCTION START: Sanitize text for use in filenames ---
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
# --- NEW FUNCTION END ---


# --- Data Generation Class ---

class DataGenerator:
    def __init__(self,
                 topic: str,
                 root_size_range: Tuple[float, float] = (50, 100),
                 d2_size_range: Tuple[float, float] = (15, 40),
                 d3_size_range: Tuple[float, float] = (5, 15),
                 total_children_range: Tuple[int, int] = (3, 10),
                 d2_count_range_base: Tuple[int, int] = (1, 6) # Base range for number of D2 nodes
                ):
        """
        Initializes the data generator for hierarchical bubble charts.

        Args:
            topic: The root topic for data generation (must be a key in hierarchical_topics).
            root_size_range: Tuple (min, max) for root node size.
            d2_size_range: Tuple (min, max) for depth 2 node size.
            d3_size_range: Tuple (min, max) for depth 3 node size.
            total_children_range: Tuple (min, max) for the total number of child nodes (Depth 2 + Depth 3).
            d2_count_range_base: Tuple (min, max) for the base random range of depth 2 node count.
        """
        if topic not in hierarchical_topics:
            raise ValueError(f"Unknown topic: {topic}. Available topics are: {list(hierarchical_topics.keys())}")

        self.topic = topic
        self.hierarchy_structure = hierarchical_topics[topic]
        self.root_size_range = root_size_range
        self.d2_size_range = d2_size_range
        self.d3_size_range = d3_size_range
        self.total_children_range = total_children_range
        self.d2_count_range_base = d2_count_range_base


    def generate_single_tree_data(self) -> List[Dict[str, Any]]:
        """
        Generates data for a single hierarchical tree based on the chosen topic.
        The structure will have 1 root (topic) and a total number of child nodes (Depth 2 + Depth 3)
        within the total_children_range.
        Node labels (except root) will be unique within the generated tree.

        Returns:
            A list of dictionaries representing the nodes, formatted for CSV output.
            Returns an empty list if generation fails to meet constraints after attempts.
        """
        nodes_with_temp_id: List[Dict[str, Any]] = []
        node_counter = 1 # 1-based temporary ID counter
        used_labels: set[str] = set() # To ensure uniqueness of labels (except root)

        # --- Depth 1 (Root Node) ---
        root_label = self.topic
        # Root node size
        root_size = random.uniform(*self.root_size_range)
        # Use a temporary ID for linking children before final re-indexing
        root_node = {"size": round(root_size, 2), "father": 0, "depth": 1, "label": root_label, "temp_id": node_counter}
        nodes_with_temp_id.append(root_node)
        node_counter += 1
        # --------------------------

        # --- Decide Total Children and Distribution ---
        total_children = random.randint(*self.total_children_range) # Total number of nodes at Depth 2 and Depth 3 combined


        # Determine available Depth 2 labels for this topic
        available_d2_labels = list(self.hierarchy_structure.keys())
        random.shuffle(available_d2_labels)

        # Decide how many Depth 2 nodes will be generated directly under the root
        # Use the base range, but clamp by 1, total_children, and available D2 labels
        min_d2_count_actual = max(1, self.d2_count_range_base[0]) # Must have at least 1 D2 node if total_children > 0
        max_d2_count_actual = min(total_children, len(available_d2_labels), self.d2_count_range_base[1])

        # Ensure min_d2_count_actual is not greater than max_d2_count_actual
        if min_d2_count_actual > max_d2_count_actual:
            # This means based on total_children or available labels, we can't even meet the minimum D2 count from the base range.
            # Set the number of D2 nodes to the maximum possible given constraints.
            num_d2_to_generate = max_d2_count_actual
        else:
            num_d2_to_generate = random.randint(min_d2_count_actual, max_d2_count_actual)

        # Decide how many Depth 3 nodes will be generated
        num_d3_to_generate = total_children - num_d2_to_generate


        # --- Generate Depth 2 Nodes ---
        generated_d2_nodes_with_temp_id: List[Dict[str, Any]] = []
        # Select the labels for the D2 nodes to be generated
        d2_labels_to_use = available_d2_labels[:num_d2_to_generate]

        for d2_label in d2_labels_to_use:
            # Ensure label hasn't been used (defensive check, mainly for D3 later)
            if d2_label not in used_labels:
                # Depth 2 node size
                d2_size = random.uniform(*self.d2_size_range)
                d2_node = {"size": round(d2_size, 2), "father": root_node["temp_id"], "depth": 2, "label": d2_label, "temp_id": node_counter}
                nodes_with_temp_id.append(d2_node)
                generated_d2_nodes_with_temp_id.append(d2_node)
                used_labels.add(d2_label)
                node_counter += 1
            # If label was already used or not enough available, just skip.


        # --- Generate Depth 3 Nodes ---
        # We need to generate num_d3_to_generate nodes, assigning them to generated D2 parents
        # and using unique labels from the available D3 labels under those parents.

        # Create a pool of available (d2_node_temp_id, d3_label) tuples based on generated D2 nodes and unused labels
        available_d3_options: List[Tuple[int, str]] = [] # List of (parent_temp_id, d3_label)
        for d2_node in generated_d2_nodes_with_temp_id:
            parent_temp_id = d2_node['temp_id']
            d2_label = d2_node['label']
            # Get potential D3 labels under this D2 parent
            potential_d3_labels = self.hierarchy_structure.get(d2_label, [])
            for d3_label in potential_d3_labels:
                # Add to options only if the label hasn't been used anywhere else in this tree
                if d3_label not in used_labels:
                    available_d3_options.append((parent_temp_id, d3_label))

        # Shuffle available D3 options and select up to num_d3_to_generate unique ones
        random.shuffle(available_d3_options)
        actual_d3_nodes_to_generate = min(num_d3_to_generate, len(available_d3_options))

        d3_options_to_use = available_d3_options[:actual_d3_nodes_to_generate]

        for parent_temp_id, d3_label in d3_options_to_use:
             if d3_label not in used_labels: # Double check uniqueness (should be handled by available_d3_options logic)
                # Depth 3 node size
                d3_size = random.uniform(*self.d3_size_range)
                d3_node = {"size": round(d3_size, 2), "father": parent_temp_id, "depth": 3, "label": d3_label, "temp_id": node_counter}
                nodes_with_temp_id.append(d3_node)
                used_labels.add(d3_label)
                node_counter += 1
             # If label was already used (shouldn't happen with current logic) or no options, just skip.


        # --- Final Data Preparation: Re-index Father IDs ---
        # Now that all nodes are generated with temporary IDs and father links using temp IDs,
        # create the final list with father IDs pointing to the 1-based index in the final list.

        final_data_list: List[Dict[str, Any]] = []
        # Map temp_id to final 1-based index (0 maps to 0 for root's father)
        temp_id_to_final_index: Dict[int, int] = {0: 0} # Father ID 0 in input means no father

        for i, node in enumerate(nodes_with_temp_id):
             # Ensure 'temp_id' key exists before accessing
             if 'temp_id' not in node:
                 # This indicates a logic error in node creation if it happens
                 print(f"Error: Node is missing 'temp_id' key: {node}") # Debugging print
                 continue # Skip this node or handle error appropriately

             temp_id = node['temp_id']
             temp_father_id = node['father']

             # Correct mapping: temp_id X maps to final index X.
             # EXCEPT for the root's father (temp_id 0 -> final father ID 0).
             # The father ID in the output CSV is the 1-based index of the parent in the *same* CSV.
             # Since we process nodes in order (root, then children), a node at index i (0-based)
             # with temp_id T will have its children created later.
             # If a child's father is T, its father ID in the final list should be i+1.

             # Let's rebuild the temp_id_to_final_index map based on the order in final_data_list
             # This map should contain temp_id -> final_1_based_index
             temp_id_to_final_index[temp_id] = len(final_data_list) + 1 # Map temp_id to its 1-based index in the final list


             final_node = {
                 "size": node['size'],
                 # Placeholder for father, will re-map after list is complete
                 "temp_father_id": temp_father_id, # Store the temporary father ID
                 "depth": node['depth'],
                 "label": node['label']
             }
             final_data_list.append(final_node)


        # Now re-map father IDs using the completed temp_id_to_final_index map
        for node in final_data_list:
            temp_father_id = node.pop("temp_father_id") # Remove the temporary key
            # Look up the final 1-based index for the temporary father ID
            # If temp_father_id is 0 (root's father), the final father ID is 0.
            # Otherwise, look up the temp_father_id in the map.
            node['father'] = temp_id_to_final_index.get(temp_father_id, 0) # Default to 0 if temp_father_id not found

        # Ensure the root node's father is correctly set to 0
        if final_data_list and final_data_list[0].get('depth') == 1:
             final_data_list[0]['father'] = 0

        # Check if the generated data list size is within the desired range (4-11)
        # This check is done in the calling loop (e.g., generate_all or main).
        # Return the list regardless, and the caller handles the size check.

        return final_data_list


    # --- MODIFICATION START: Update save_to_csv signature and logic ---
    def save_to_csv(self, data: List[Dict[str, Any]], topic_file_count: int):
        """
        Saves the data to a CSV file with metadata on the first line
        and column headers on the second line.

        Args:
            data: The list of dictionaries representing the hierarchical data.
            topic_file_count: The sequence number for the file within its topic (1-based).
        """
        # Create directory if it doesn't exist
        output_dir = './fill_bubble/csv' # Updated output directory
        os.makedirs(output_dir, exist_ok=True)

        # Sanitize the topic name for the filename
        sanitized_topic = sanitize_filename(self.topic)
        # Construct filename using sanitized topic and topic sequence number
        filename = os.path.join(output_dir, f"fill_bubble_{sanitized_topic}_{topic_file_count}.csv")
        # --- MODIFICATION END ---

        # Generate little theme
        selected_descriptor = random.choice(ENGLISH_DESCRIPTORS)
        little_theme = f"the {selected_descriptor} of {self.topic}"

        # Construct the first header line: Main theme, little theme, Total Nodes
        header_line_1 = f"{self.topic},{little_theme},{len(data)}"

        # Construct the second header line (the actual CSV headers)
        header_line_2 = "size,father,depth,label"

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Write the custom header lines
            csvfile.write(header_line_1 + '\n')
            csvfile.write(header_line_2 + '\n')

            writer = csv.writer(csvfile)
            # Write data rows
            for row in data:
                # Ensure order matches header_line_2 and handle potential missing keys (though generate_single_tree_data should provide them)
                writer.writerow([row.get("size", ""), row.get("father", ""), row.get("depth", ""), row.get("label", "")])

        print(f"Generated {filename} with {len(data)} nodes.")
    # --- MODIFICATION END ---


    # --- generate_all method is no longer needed as main loop controls file generation ---
    # def generate_all(self):
    #     """Generates the specified number of data files for the topic."""
    #     for i in range(1, self.num_files + 1):
    #         # Regenerate data until the total node count is within the desired range (4-11)
    #         while True:
    #             data = self.generate_single_tree_data()
    #             if 4 <= len(data) <= 11: # Check against the fixed requirement of 4-11 total nodes
    #                 break
    #             # Optional: print regeneration info for debugging
    #             # print(f"Generated {len(data)} nodes for {self.topic}, file {i}. Regenerating to meet 4-11 node count.")
    #
    #         self.save_to_csv(data, i) # This 'i' needs to be the global index


# --- Main Execution ---
if __name__ == "__main__":
    # === Customizable Parameters ===
    # >>> USER: Configure data generation here <<<

    # List of topics to generate data for. Choose from keys in hierarchical_topics.
    # Example: Generate for all 15 topics
    topics_to_generate: List[str] = list(hierarchical_topics.keys())

    # Number of files to generate per topic (used when GENERATE_TOTAL_RANDOM_FILES is False)
    NUM_FILES_PER_TOPIC = 0 # Example: Generate 5 files per topic

    # Total number of files to generate (used when GENERATE_TOTAL_RANDOM_FILES is True)
    NUM_TOTAL_RANDOM_FILES = 10

    # Control mode:
    # True: Generate NUM_TOTAL_RANDOM_FILES in total, picking topics randomly.
    # False: Generate NUM_FILES_PER_TOPIC files for each topic in topics_to_generate.
    GENERATE_TOTAL_RANDOM_FILES = True # Set this to True for the new mode


    # Random range for node sizes
    ROOT_SIZE_RANGE: Tuple[float, float] = (50.0, 100.0)
    D2_SIZE_RANGE: Tuple[float, float] = (15.0, 40.0)
    D3_SIZE_RANGE: Tuple[float, float] = (5.0, 15.0)

    # Random range for the total number of child nodes (Depth 2 + Depth 3)
    # Total nodes will be 1 (root) + random value from this range.
    # The while loop ensures total nodes are 4-11.
    # Setting this range to (3, 10) directly targets 4-11 total nodes.
    TOTAL_CHILDREN_RANGE: Tuple[int, int] = (3, 10)


    # Base random range for the number of Depth 2 nodes generated directly under the root.
    # The actual number generated will also be limited by the total_children and available labels.
    # E.g., (1, 6) means attempt to generate 1 to 6 D2 nodes, but not more than total_children or available D2 labels.
    D2_COUNT_RANGE_BASE: Tuple[int, int] = (1, 6)


    # === End Customizable Parameters ===

    # --- Determine total files to generate based on mode ---
    if GENERATE_TOTAL_RANDOM_FILES:
        total_files_to_generate = NUM_TOTAL_RANDOM_FILES
        print(f"Starting data generation for {total_files_to_generate} total random files.")
    else:
        total_topics = len(topics_to_generate)
        total_files_to_generate = total_topics * NUM_FILES_PER_TOPIC
        print(f"Starting data generation for {total_files_to_generate} files across {total_topics} topics ({NUM_FILES_PER_TOPIC} file(s) per topic).")


    # --- MODIFICATION START: Initialize counters and output directory ---
    topic_file_counters: Dict[str, int] = {} # Used to track file count per topic for naming
    OUTPUT_DIRECTORY = './fill_bubble/csv' # Define the output directory
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True) # Create the output directory
    # --- MODIFICATION END ---

    global_file_counter = 0 # Keep track of total files successfully generated across all topics
    total_attempts = 0 # Track total generation attempts (outer loop)
    max_total_attempts = total_files_to_generate * 5 # Safety limit for attempts (adjust as needed)


    # --- MODIFICATION START: Modify the main generation loop ---
    # Create a list of topics to iterate through if not generating totally random files
    # This list will be used to cycle through topics in the per-topic mode.
    if not GENERATE_TOTAL_RANDOM_FILES:
        all_topics_for_generation = []
        for topic_name in topics_to_generate:
            all_topics_for_generation.extend([topic_name] * NUM_FILES_PER_TOPIC)
        # Shuffle the list of topics to generate files with mixed topics
        random.shuffle(all_topics_for_generation)
        # Use an iterator for the topic list
        topic_iterator = iter(all_topics_for_generation)


    # Loop continues until enough files are generated or max attempts reached
    while global_file_counter < total_files_to_generate and total_attempts < max_total_attempts:
        total_attempts += 1 # Increment total attempt counter

        # --- Select Topic based on mode ---
        if GENERATE_TOTAL_RANDOM_FILES:
            # In random mode, pick a topic randomly from the list
            topic_name = random.choice(topics_to_generate)
        else:
            # In per-topic mode, get the next topic from the shuffled list
            try:
                topic_name = next(topic_iterator)
            except StopIteration:
                 # Should not happen if total_attempts < max_total_attempts and logic is correct,
                 # but handle defensively.
                 print("Warning: Topic iterator exhausted unexpectedly.")
                 break # Exit loop


        try:
            generator = DataGenerator(
                topic=topic_name,
                root_size_range=ROOT_SIZE_RANGE,
                d2_size_range=D2_SIZE_RANGE,
                d3_size_range=D3_SIZE_RANGE,
                total_children_range=TOTAL_CHILDREN_RANGE,
                d2_count_range_base=D2_COUNT_RANGE_BASE
            )

            # Generate data, ensuring node count is between 4 and 11
            data = []
            attempts_inner = 0
            max_attempts_inner = 100 # Prevent infinite loops in case constraints are impossible
            while True:
                 data = generator.generate_single_tree_data()
                 attempts_inner += 1
                 if 4 <= len(data) <= 11 or attempts_inner >= max_attempts_inner:
                     break
                 # print(f"Attempt {attempts_inner}: Generated {len(data)} nodes. Regenerating...") # Optional debug print

            if not (4 <= len(data) <= 11):
                 print(f"Attempt {total_attempts}: Warning: Could not generate data with 4-11 nodes for topic '{topic_name}' after {max_attempts_inner} attempts. Generated {len(data)} nodes.")
                 print("Skipping file generation for this instance.")
                 # global_file_counter is NOT incremented here
                 continue # Move to the next file (next iteration of the while loop)


            # --- Determine topic-specific file index and save ---
            # Get and increment topic sequence number for the chosen topic
            if topic_name not in topic_file_counters:
                topic_file_counters[topic_name] = 0
            topic_file_counters[topic_name] += 1
            current_topic_seq_num = topic_file_counters[topic_name]

            # Increment global counter as a file will be generated
            global_file_counter += 1

            # Print progress using the global counter and topic-specific counter
            print(f"\n--- Generating File {global_file_counter}/{total_files_to_generate} for topic: '{topic_name}' (Seq: {current_topic_seq_num}) ---")

            # Save the generated data using the topic sequence number
            # save_to_csv now uses the globally defined OUTPUT_DIRECTORY implicitly
            generator.save_to_csv(data, topic_file_count=current_topic_seq_num)


        except ValueError as e:
            print(f"Attempt {total_attempts}: Error generating data for topic '{topic_name}' (ValueError): {e}. Skipping this file.")
            # global_file_counter is NOT incremented here
        except Exception as e:
            # Catching general exceptions to print the error and skip the file
            print(f"Attempt {total_attempts}: An unexpected error occurred while generating data for topic '{topic_name}': {e}. Skipping this file.")
            # global_file_counter is NOT incremented here
            import traceback
            traceback.print_exc()

    # --- MODIFICATION END: Modify the main generation loop ---


    # --- Final Summary ---
    if global_file_counter < total_files_to_generate:
        print(f"\nData generation process finished due to reaching max attempts ({max_total_attempts}).")
        print(f"Successfully generated {global_file_counter} files out of {total_files_to_generate} targeted.")
    else:
        print("\nData generation process finished successfully.")
        print(f"Successfully generated {global_file_counter} files.")
