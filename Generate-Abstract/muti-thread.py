import base64
import mimetypes
import os
from concurrent.futures import ThreadPoolExecutor

# Make sure you have the openai library installed: pip install openai
from openai import OpenAI

# It's a good practice to handle API keys securely, e.g., using environment variables.
# Replace with your actual API key and base_url if needed.
client = OpenAI(
    base_url='https://az.gptplus5.com/v1',
    api_key='sk-ksgLY98Od26jBI1IBc1a749543Db427fAfEa113aE25a2e48'
)

def get_mime_type(file_path):
    """
    Determines the MIME type of a file based on its extension.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type

def analyze_image(image_path, output_path):
    """
    Analyzes a single image using the GPT-4o model and saves the summary to a text file.
    """
    try:
        # Read and encode the image file
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        mime_type = get_mime_type(image_path)
        data_url = f"data:{mime_type};base64,{encoded_image}"

        # Define the prompt for the analysis
        prompt_text = """
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
        """

        # Send the request to the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url
                        }
                    },
                ],
            }],
        )

        # Save the response output in a .txt file
        with open(output_path, "w") as f:
            f.write(response.choices[0].message.content)

        print(f"Analysis for {os.path.basename(image_path)} saved to {os.path.basename(output_path)}")

    except Exception as e:
        print(f"Failed to analyze {os.path.basename(image_path)}. Error: {e}")

def process_directory(root_dir, max_workers=20):
    """
    Traverses a directory, finds all PNG files, and uses a thread pool
    to analyze them concurrently.
    """
    txt_folder = os.path.join(root_dir, 'txt')
    os.makedirs(txt_folder, exist_ok=True)  # Create the output directory if it doesn't exist

    # Use ThreadPoolExecutor to manage a pool of worker threads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for subdir, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".png"):
                    image_path = os.path.join(subdir, file)
                    output_file = os.path.join(txt_folder, os.path.splitext(file)[0] + ".txt")

                    # Skip if the output file already exists
                    if os.path.exists(output_file):
                        print(f"Skipping {file} as output already exists.")
                        continue

                    # Submit the analysis task to the thread pool
                    executor.submit(analyze_image, image_path, output_file)


# root_directory = r"/home/public/dataset-MegaCQA/bubble"
# root_directory = r"/home/public/dataset-MegaCQA/chord"
# root_directory = r"/home/public/dataset-MegaCQA/funnel"
# root_directory = r"/home/public/dataset-MegaCQA/line"
# root_directory = r"/home/public/dataset-MegaCQA/pie"
# root_directory = r"/home/public/dataset-MegaCQA/treemap"
root_directory = r"/home/public/dataset-MegaCQA/scatter"

process_directory(root_directory)
