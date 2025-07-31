import os
import requests
from openai import OpenAI

client = OpenAI(
    base_url='https://az.gptplus5.com/v1',
    api_key=''
)

def analyze_image(image_url, output_path):
    # Create the input data with the image URL
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """
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
                    "type": "image_url",
                    "image_url": {
                        "url":image_url
                    }
                },
            ],
        }],)
    # Save the response output in a .txt file
    with open(output_path, "w") as f:
        f.write(response.choices[0].message.content)


def process_directory(root_dir):
    # Traverse the directory to find image files
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".png"):
                # Build the URL for the image file
                image_url = f"https://github.com/isYunchaoWang/RAG4Ghart/blob/main/{os.path.relpath(os.path.join(subdir, file)).replace(os.sep, '/')[3:]}?raw=true"
                output_file = os.path.splitext(os.path.relpath(os.path.join(subdir, file)).replace(os.sep, '/'))[0] + ".txt"  # Output text file name

                analyze_image(image_url, output_file)
                print(f"Analysis for {file} saved to {output_file}")


# Specify the root directory of your dataset
root_directory = r"D:\PycharmProjects\RAG4Ghart\Dataset-ZXQ\sample100\line\png"

# Start processing the directory
process_directory(root_directory)
