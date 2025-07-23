# AutoLecMD

### Introduction

Summarize a lecture/tutorial video to a study note in Markdown with illustrations.

---

### Demo

[Lec 7: Exam 1 review | MIT 18.01 Single Variable Calculus, Fall 2007](https://drive.google.com/file/d/1kp-r7_X2jpAXrbFmGmXVCWgqfR5kA9_2/preview)

[How To Draw Sprigatito | Pokemon Scarlet & Violet](https://drive.google.com/file/d/1qPeq3tbxMhvob_eHzcJkFlUUIt1I30yU/preview)

---

### Setup

Clone the project

`git clone https://github.com/NJU-HenryQi/AutoLecMD.git`

Change directory

`cd AutoLecMD`

Create a **.env** file and write your GOOGLE_API_KEY into it. Change the whole [your_api_key] with the real API key, altogether with the square brackets.

`echo GOOGLE_API_KEY=[your_api_key] > .env`

---

### Usage

`python3 main.py <URL> <flag1> [<flag2> ...]`

Flags are required, so that you won't accidentally delete all the files and start over. For convenience, you can combine multiple flags. So `-a -b` would be the same as `-ab`.

- "-n": **Start a "new" task.** The "download", "check", "take_screenshots", "summarize" tasks will be executed sequentially.
- "-d": **Continue from the "download" task.** Execute all tasks except "download".
- "-c": **Continue from the "check" task.** Execute all tasks except "download" and "first_round_summarize".
- "-t": **Continue from the "take_screenshots" task.**
- "-y": "Do you want to continue?" will be asked between tasks. **Always continue with a force "yes".** 

---

### Tasks

- ##### download

Download the video and the subtitle file from the given URL.

- ##### check

Let LLM decide crucial timestamps of content highly demanding on visual information, solely based on the srt file.

- ##### take_screenshots

Take screenshots with an interval within the given timestamp ranges.

- ##### summarize

Upload the screenshots to the Google Genai File System; combine the textual content and screenshots together for the MLLM prompt; make MLLM summarize a study note and write it in Markdown.