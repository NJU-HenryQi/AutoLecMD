from utils import load_text, generate_MLLM_prompt
from google import genai
from dotenv import load_dotenv
import os
import re
from config import srt_file_path, LLM_prompt_path, screenshot_path, timestamps_file_path

def check():
    # Step 1: load your API key from .env; initialize genai client with it
    load_dotenv()
    client = genai.Client()

    # Step 2: load the LLM prompt template and fill the srt text in it; feed it to the LLM
    prompt = load_text(LLM_prompt_path)
    srt_content = load_text(srt_file_path)
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt.format(full_srt_file_content=srt_content)
    )

    # Step 3: make directory "./intermediate"
    directory = os.path.dirname(timestamps_file_path)
    if directory:
        os.makedirs(directory, exist_ok = True)

    # Step 4: write the response into the "./intermediate/crucial_timestamps.json" file. Do not include the code block sign "```json"
    output = response.text
    match = re.search(r"```json\s*([\s\S]*?)\s*```", response.text)
    if match:
        output = match.group(1).strip()
    with open(timestamps_file_path, "w") as f:
        f.write(output)
        
def summarize(video_title):
    load_dotenv()
    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=generate_MLLM_prompt(srt_file_path, timestamps_file_path, screenshot_path)
    )

    with open(video_title + ".md", "w") as f:
        f.write(response.text)

# second_round_summarize(
#     "./captions/Lec 7： Exam 1 review ｜ MIT 18.01 Single Variable Calculus, Fall 2007.en.srt",
#     "./intermediate/crucial_timestamps.json",
#     "./intermediate/screenshots"
# )