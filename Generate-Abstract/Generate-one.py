import base64
import mimetypes
import openai

import os

from openai import OpenAI

# client = OpenAI(
#     api_key='')

client = OpenAI(
    base_url='https://az.gptplus5.com/v1',
    api_key='sk-ksgLY98Od26jBI1IBc1a749543Db427fAfEa113aE25a2e48'
)

def get_mime_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type

def create_file(file_path):
    with open(file_path, "rb") as file_content:
        result = client.files.create(
            file=file_content,
            purpose="vision",
        )
        return result.id


def analyze_image(image_path, output_path):
    # Upload image and analyze it
    # file_id = create_file(image_path)
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    mime_type = get_mime_type(image_path)
    data_url=f"data:{mime_type};base64,{encoded_image}"
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
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """
                You are a top-tier data analyst. Your task is to analyze the provided chart data and generate a professional summary. Please follow the following thought process (Chain of Thought) for your analysis, and then provide the final summary:
                
                Step 1: Key Metrics Identification
                Calculate and list the maximum, minimum values if they exist.
                Calculate the total value and average value if they exist.
                Step 2: Pattern Analysis
                If the chart shows data over time or has a sequential order:
                
                Identify whether the overall trend is increasing, decreasing, or stable
                Describe the trend's shape (e.g., linear, exponential, fluctuating)
                
                If the chart shows categorical comparisons, distributions, or relationships:
                
                Identify the dominant categories or segments
                Describe the distribution pattern (e.g., evenly distributed, concentrated, polarized)
                
                Step 3: Significant Event/Feature Identification
                For time-series data:
                
                Identify the highest growth period and calculate the growth rate
                Note any turning points or anomalies
                
                For other chart types:
                
                Identify significant outliers or standout data points
                Note notable variations or patterns
                
                Step 4: Synthesis & Summary
                Synthesize the key findings into a concise summary that includes the most important numerical data and factual observations.
                Your output:
                Only provide the Final Summary below. Do not show your analysis steps.
                【Final Summary】(Provide a factual summary in exactly 150 words or fewer. STRICTLY enforce this word limit - count every word and ensure you do not exceed 150 words. Include key numerical metrics, specific data points, and primary patterns observed from your analysis in Step 4).
                """},
                {
                    "type": "image_url",
                    "image_url": {
                        "url":data_url
                    }
                },
            ],
        }],)

    # Save the response output in a .txt file
    with open(output_path, "w") as f:
        f.write(response.choices[0].message.content)


def process_directory(root_dir):
    # Traverse the directory to find image files
    txt_folder = os.path.join(root_dir, 'txt')
    for subdir, dirs, files in os.walk(root_dir):
        dirs.sort()
        files.sort()
        for file in files:
            if file.endswith(".png"):
                # and 后面的条件控制生成顺序
                # if file.endswith(".png") and int(os.path.splitext(os.path.basename(file))[0])>9000:
                txt_file_path = os.path.join(txt_folder, os.path.splitext(file)[0] + ".txt")
                if os.path.exists(txt_file_path):
                    print(f"Skipping {file} as the corresponding .txt file already exists.")
                    continue  # Skip this file if the corresponding .txt file exists

                image_path = os.path.join(subdir, file)
                output_file = os.path.join(txt_folder, os.path.splitext(file)[0] + ".txt")  # Output text file name

                analyze_image(image_path, output_file)
                print(f"Analysis for {file} saved to {output_file}")


# Specify the root directory of your dataset
root_directory = r"D:\PycharmProjects\RAG4Ghart\Dataset-ZXQ\test20\chord"

# Start processing the directory
process_directory(root_directory)
