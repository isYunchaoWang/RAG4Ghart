import openai

import os

from openai import OpenAI

client = OpenAI(
    api_key='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')


def create_file(file_path):
    with open(file_path, "rb") as file_content:
        result = client.files.create(
            file=file_content,
            purpose="vision",
        )
        return result.id


def analyze_image(image_path, output_path):
    # Upload image and analyze it
    file_id = create_file(image_path)

    # Create the request content for the analysis
    # response = client.responses.create(
    #     model="gpt-4o",
    #     input=[{
    #         "role": "user",
    #         "content": [
    #             {"type": "input_text", "text": """
    #                 You are a top-tier data analyst. Your task is to analyze the provided chart data and generate a professional summary. Please follow the following thought process (Chain of Thought) for your analysis, and then provide the final summary:
    #
    #                 Step 1: Basic Statistics
    #
    #                 Calculate the total number of nodes and the total number of edges in the graph.
    #
    #                 Categorize the nodes by their type attribute and provide a count for each type.
    #
    #                 Step 2: Connectivity and Components
    #
    #                 Determine if the graph is fully connected (i.e., all nodes are part of a single component) or if it is disconnected.
    #
    #                 If it is disconnected, identify how many separate components (islands) exist and briefly describe the main constituents of each one.
    #
    #                 Step 3: Key Node Identification (Centrality Analysis)
    #
    #                 For this analysis, define a node's "influence" as its degree centrality (the total number of incoming and outgoing connections).
    #
    #                 Identify the top 3 most influential nodes (hubs) in the network. List them along with their calculated degree.
    #
    #                 Step 4: Synthesis & Summary
    #
    #                 Based on the insights from the previous steps, synthesize these findings into a smooth, concise final summary.
    #
    #                 Your output:
    #                 【Final Summary】 (Here, only provide the final summary based on your analysis in Step 4).
    #             """},
    #             {
    #                 "type": "input_image",
    #                 "file_id": file_id,
    #             },
    #         ],
    #     }])
    response = client.responses.create(
        model="gpt-4o",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": """
                    You are a top-tier data analyst. Your task is to analyze the provided chart data and generate a professional summary. Please follow the following thought process (Chain of Thought) for your analysis, and then provide the final summary:

                    Step 1: Key Metrics Identification

                    Calculate and list the maximum, minimum values.

                    Calculate the total value and average value.

                    Step 2: Overall Trend Analysis

                    Compare the data to determine whether the overall trend is increasing, decreasing, or stable.

                    Describe the trend's shape (e.g., linear growth, or growth after fluctuations?).

                    Step 3: Significant Event Identification

                    Identify the highest growth and the growth rate.

                    Check if there are any turning points.

                    Step 4: Synthesis & Summary

                    Based on the insights from the previous steps, synthesize these findings into a smooth, concise final summary.

                    Your output:
                    【Final Summary】 (Here, only provide the final summary based on your analysis in Step 4).
                """},
                {
                    "type": "input_image",
                    "file_id": file_id,
                },
            ],
        }])

    # Save the response output in a .txt file
    with open(output_path, "w") as f:
        f.write(response.output_text)


def process_directory(root_dir):
    # Traverse the directory to find image files
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".png"):  # Add more file types if needed
                image_path = os.path.join(subdir, file)
                output_file = os.path.splitext(image_path)[0] + ".txt"  # Output text file name

                analyze_image(image_path, output_file)
                print(f"Analysis for {file} saved to {output_file}")


# Specify the root directory of your dataset
root_directory = r"D:\PycharmProjects\RAG4Ghart\Dataset-ZXQ\sample100\node_link"

# Start processing the directory
process_directory(root_directory)
