import os
import subprocess
import json
from tkinter import filedialog
from tkinter import Tk, Button, Label

FFPROBE_PATH = "ffprobe"  # Replace with your path to ffprobe if not in system's PATH

def get_video_info(video_file):
    try:
        cmd = [
            FFPROBE_PATH,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate,width,height",
            "-of", "json",
            video_file
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(result.stderr)
        probe_result = json.loads(result.stdout)
        stream = probe_result['streams'][0]
        r_frame_rate = stream['r_frame_rate']
        num, denom = map(int, r_frame_rate.split('/'))
        fps = num / denom
        width = stream['width']
        height = stream['height']
        return fps, width, height
    except Exception as e:
        print(str(e))
        raise

def process_video(video_path):
    fps, width, height = get_video_info(video_path)
    new_fps = fps / 2

    video_dir = os.path.dirname(video_path)
    image_sequence_path = os.path.join(video_dir, "image sequence")
    os.makedirs(image_sequence_path, exist_ok=True)

    output_path = os.path.join(video_dir, "output")
    os.makedirs(output_path, exist_ok=True)

    output_file = os.path.join(image_sequence_path, "frame_%04d.png")
    audio_file = os.path.join(output_path, "audio.mp3")
    info_file = os.path.join(output_path, "videoinfo.txt")

    subprocess.run(["ffmpeg", "-i", video_path, "-vf", f"fps={new_fps}", output_file], check=True)
    subprocess.run(["ffmpeg", "-i", video_path, "-vn", "-acodec", "mp3", audio_file], check=True)

    with open(info_file, 'w') as f:
        f.write(f"Video resolution: {width}x{height}\n")
        f.write(f"Original FPS: {fps}\n")

def combine_frames(folder_path):
    video_file = os.path.join(folder_path, "output.mp4")
    audio_file = os.path.join(folder_path, "audio.mp3")

    if not os.path.exists(audio_file):
        print("Audio file not found!")
        return

    subprocess.run(["ffmpeg", "-r", "15", "-i", os.path.join(folder_path, "frame_%04d.png"), "-i", audio_file, "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental", video_file], check=True)

def select_video():
    root = Tk()
    root.title("Video Processor")
    
    label = Label(root, text="Select a video to process:")
    label.pack()

    btn_select_video = Button(root, text="Select Video", command=lambda: process_video_wrapper(root))
    btn_select_video.pack()

    label2 = Label(root, text="Select a folder to combine frames:")
    label2.pack()

    btn_combine_frames = Button(root, text="Select Folder", command=lambda: combine_frames_wrapper(root))
    btn_combine_frames.pack()

    root.mainloop()

def process_video_wrapper(root):
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.mov;*.avi;*.mkv")])  # show an "Open" dialog box and return the path to the selected file
    if video_path:
        process_video(video_path)
        root.destroy()

def combine_frames_wrapper(root):
    folder_path = filedialog.askdirectory()  # show a dialog to select a directory and return the path
    if folder_path:
        combine_frames(folder_path)
        root.destroy()

if __name__ == "__main__":
    select_video()
