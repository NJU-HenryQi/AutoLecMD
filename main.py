import download
import summarize
import screenshot
import sys
from utils import parse, delete
from config import video_file_path

start_stage = 0
force_yes = 0
need_help = 0
url = ""
video_title = ""

def ask(force_yes):
    if force_yes:
        return True
    ans = input("Do you want to continue? (y/n)")
    while ans != 'y' and ans != 'n':
        ans = input("Do you want to continue? (y/n)")
    return ans == 'y'

def main():
    if start_stage <= 1:
        try:
            delete()
            video_title = download.download(url)
        except Exception as e: 
            print(e)
            return -1
        with open("temp.txt", "w") as f:
            f.write(video_title)
        print("Caption and video files have been downloaded")
        if not ask(force_yes):
            return 1
        
    if start_stage <= 2:
        try:
            summarize.check()
        except Exception as e: 
            print(e)
            return -2
        print("Crucial timestamps have been summarized.")
        if not ask(force_yes):
            return 2

    if start_stage <= 4:
        try:
            screenshot.take_screenshots(video_file_path)
        except Exception as e: 
            print(e)
            return -4
        print("Screenshots have been taken.")
        if not ask(force_yes):
            return 4
        
    if start_stage <= 8:
        try:
            with open("temp.txt", "r") as f:
                video_title = f.read()
            summarize.summarize(video_title)
        except Exception as e: 
            print(e)
            return -8
        print("The lecture note has been summarized.")
    
    return 0

if __name__ == '__main__':
    for _, argv in enumerate(sys.argv[1:]):
        x, y, z = parse(argv)
        if y == -1:
            url = x
            continue

        if y == 1:
            force_yes = 1
        if z == 1:
            need_help = 1
        start_stage += x
    
    if need_help == 1:
        if force_yes != 0 or start_stage != 0:
            print("Do not use other flags together with -h")
            sys.exit(1)
        else:
            print(
                "The whole job is consisted of 4 tasks, and you can start from any of them.\n" + 
                "The first task is download. It downloads caption and video files.\n" +
                "The second task is check. It asks an LLM to decide crucial timestamps of content highly demanding on visual information.\n" +
                "The third task is take_screenshots. It takes screenshots of the video with an interval within the given timestamp ranges.\n" +
                "The fourth task is summairze. It asks an MLLM to summarize the caption and screenshots to a lecture note.\n\n" +
                "Usage:\n" +
                "python3 main.py <URL> <flag1> [<flag2> ...]\n" +
                "Use -n to start a new job. All downloaded and generated files will be DELETED.\n" +
                "Use -d to start after download.\n" +
                "Use -c to start after check\n" +
                "Use -t to start after take_screenshots\n" +
                "Use -s to start after summarize\n" + 
                "Unknwon flags will be ignored"
            )
    else:
        if start_stage == 0:
            print("Choose one starting stage! Use -h for help.")
            sys.exit(1)
        if start_stage not in {1, 2, 4, 8, 16}:
            print("You can only start from one stage! Use -h for help.")
            sys.exit(1)
        if start_stage == 1 and url == "":
            print("The URL is needed for a new job. Use -h for help.")
            sys.exit(1)

        ret = main()
        ret_map = {
            1: 'download', -1: 'download',
            2: 'check', -2: 'check',
            4: 'take_screenshots', -4: 'take_screenshots',
            -8: 'summarize'
        }
        if ret < 0:
            print(f"Failed the {ret_map[ret]} task")
            sys.exit(1)
        elif ret > 0:
            print(f"Quitted after finishing the {ret_map[ret]} task")
    # test()
    # summarize.second_round_summarize(
    #     './captions/Lec 7： Exam 1 review ｜ MIT 18.01 Single Variable Calculus, Fall 2007.en.srt',
    #     './intermediate/crucial_timestamps.json',
    #     './intermediate/screenshots'
    # )

    # https://www.youtube.com/watch?v=eHJuAByQf5A