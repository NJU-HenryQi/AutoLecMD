import subprocess
import os

def download(url):
    # Preprocess
    #   If the URL is in a "list+index" format, yt-dlp will download the whole list
    #   of videos rather than only the single video corresponding to the given index.
    if "&list=" in url:
        url = url.split("&list=")[0]
        
    # Step 1: get the video title
    result = subprocess.run([
        "yt-dlp",
        "--cookies-from-browser", "safari",
        "--print", "%(title)S",
        url
    ], capture_output=True, text=True, check=True)
    video_title = result.stdout.strip()

    # Step 2: download video
    subprocess.run([
        "yt-dlp", "-f", "mp4", "--cookies-from-browser", "safari",
        "-o", "./videos/v.%(ext)S",
        url
    ])

    # Step 3: download captions only
    subprocess.run([
        "yt-dlp",
        "--cookies-from-browser", "safari",
        "--skip-download",
        "--write-auto-subs",
        "--sub-langs", "en",
        "--convert-subs", "srt",
        "-o", "./captions/c.%(ext)S",
        url
    ])
    
    # Step 4: modify the captions file name
    #   could be something like "c.en.srt" or "c.zh.srt"; standardize it to be "c.srt"
    for _, _, filenames in os.walk('captions'):
        for filename in filenames:
            if filename.split('.')[-1] == 'srt':
                os.rename(os.path.join('captions', filename), os.path.join('captions', 'c.srt'))

    return video_title