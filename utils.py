import os
import json
from google import genai
from dotenv import load_dotenv
import time
from config import MLLM_prompt_path, analysis_block_path, dict_file_path

def parse(argv):
    # return three values, say x, y and z
    # If argv is a flag or a bunch of flags:
    #   x: 1 -> "-n", 2 -> "-d", 4 -> "-c", 8 -> "-t". All these 5 flags are exclusive to each other.
    #   y: 0 -> default, 1 -> "-y". 
    #   z: 0 -> default, 1 -> "-h"
    # If argv is a URL:
    #   x: URL; y: -1; z: 0
    x, y, z = 0, 0, 0
    x_map = {
        'n': 1,
        'd': 2,
        'c': 4,
        't': 8
    }
    if argv[0] == '-':
        for ch in argv[1:]:
            if ch in x_map:
                x += x_map[ch]
            if ch == 'y':
                y = 1
            if ch == 'h':
                z = 1
    else:
        x = argv
        y = -1
    return x, y, z

def delete():
    for path in ['captions', 'videos', 'intermediate', 'intermediate/screenshots']:
        if path == 'intermediate/screenshots':
            if not os.path.exists(path):
                continue

        for filename in os.listdir(path):
            full_path = os.path.join(path, filename)
            if os.path.isfile(full_path):
                os.remove(full_path)

def convert_timestamp(timestamp):
    # convert timestamp in the form of "hh:mm:ss" to seconds
    splits = timestamp.split(":")
    hours = int(splits[0])
    minutes = int(splits[1])
    seconds = int(splits[2])
    return hours * 3600 + minutes * 60 + seconds

def convert_seconds(sec):
    # convert seconds to "hh:mm:ss"
    hours = int(sec // 3600)
    minutes = int((sec % 3600) // 60)
    seconds = sec % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def load_text(file_path):
    # load prompt template or srt text
    ext = file_path.split('.')[-1]
    if ext == 'md':
        type_name = 'prompt'    
    elif ext == 'srt':
        type_name = 'srt'
    else:
        type_name = 'UNKNOWN'

    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: No {type_name} file found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the {type_name} file {file_path}: {e}")
        return None

def read_json(file_path):
    # specifically designed to read "./intermediate/crucial_timestamps.json"
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {file_path}")
    except Exception as e:
        print(f"An error occurred while reading the JSON file {file_path}: {e}")
    
    # returns a generator of "start_time, end_time, reason, index" of the crucial timestamps given in the JSON file
    for i in range(len(data)):
        yield data[i]['start_time'], data[i]['end_time'], data[i]['reason'], i + 1

def generate_MLLM_prompt(srt_file_path, timestamps_file_path, screenshots_file_path):
    contents = []
    name_dict = {}
    uploaded_count = {}
    load_dotenv()
    client = genai.Client()
    with open(srt_file_path, "r") as f:
        srt_content = f.read()
    prompt = load_text(MLLM_prompt_path).format(full_srt_text=srt_content)
    contents.append(prompt)

    if os.path.exists(dict_file_path):
        with open(dict_file_path, 'r') as f:
            name_dict = json.load(f)

        for root, _, files in os.walk(screenshots_file_path):
            for file in files:
                segment_index = int(file.split('-')[0])
                uploaded_count[segment_index] = uploaded_count.get(segment_index, 0) + 1
    else:
        for root, _, files in os.walk(screenshots_file_path):
            for file in files:
                full_path = os.path.join(root, file)
                uploaded_file = client.files.upload(file=full_path)
                name = uploaded_file.name
                name_dict[file] = name
                
                segment_index = int(file.split('-')[0])
                uploaded_count[segment_index] = uploaded_count.get(segment_index, 0) + 1
                print(f'uploaded {file}')
        with open(dict_file_path, "w") as f:
            json.dump(name_dict, f, indent=4)

    for start_time, end_time, reason, index in read_json(timestamps_file_path):
        analysis_block_text = load_text(analysis_block_path).format(interval_index=index, start_time=start_time, end_time=end_time, reason=reason)
        contents.append(analysis_block_text)
        for part_index in range(1, uploaded_count[index] + 1):
            file = str(index) + '-' + str(part_index) + '.png'
            uploaded_file = client.files.get(name=name_dict[file])
            while uploaded_file.state.name != 'ACTIVE':
                time.sleep(0.5)
                uploaded_file = client.files.get(name=name_dict[file])
            contents.append(uploaded_file)
        print(f'{index} done.')
    
    return contents