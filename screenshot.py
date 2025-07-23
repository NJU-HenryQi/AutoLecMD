from utils import read_json, convert_timestamp, convert_seconds
import os
import subprocess
import shutil
from config import screenshot_path, timestamps_file_path

def take_screenshots(video_path, duration = 5):
    os.makedirs(screenshot_path, exist_ok = True)
    if not shutil.which("ffmpeg"):
        print("ffmpeg not found")
        return False
    
    json_data = read_json(timestamps_file_path)

    interval_num = 1
    for start_time, end_time, _, _ in json_data:
        inner_num = 1
        for t in range(convert_timestamp(start_time), convert_timestamp(end_time) + 1, duration):
            file_name = str(interval_num) + "-" + str(inner_num) + ".png"
            command = [
                "ffmpeg", "-n",
                "-ss", convert_seconds(t),
                "-i", video_path,
                "-vframes", "1",
                "-q:v", "2",
                os.path.join(screenshot_path, file_name)
            ]
            try:
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                print(f"Failed to capture {file_name}, due to ffmpeg errors.")
            except Exception as e:
                print(f"Failed to capture {file_name}, due to {e}")

            inner_num += 1
        interval_num += 1

# take_screenshots("./videos/Lec 7： Exam 1 review ｜ MIT 18.01 Single Variable Calculus, Fall 2007.mp4")