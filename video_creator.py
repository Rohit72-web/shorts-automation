import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
from gtts import gTTS
import os
import moviepy.config as mconf
import moviepy.video.fx.all as vfx
# Update ImageMagick path if needed
mconf.change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})



# --- CONSTANT FRAME SIZE ---
FRAME_W, FRAME_H = 720, 1280  # Shorts vertical



# --- PIPELINE: news1 -> script_generator -> voice_test -> video creation ---
import subprocess
import json
import re
import os

def run_script(script):
    result = subprocess.run(["python", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {script}:\n{result.stderr}")
        raise RuntimeError(f"{script} failed")
    return result.stdout

# 1. Run news1.py (if needed, e.g., if it saves headlines for script_generator)
if os.path.exists("news1.py"):
    print("Fetching headlines with news1.py...")
    run_script("news1.py")

# 2. Run script_generator.py and clean up JSON output
print("Generating script with script_generator.py...")
sg_out = run_script("script_generator.py")
# Extract JSON array from output (remove ```json or similar wrappers)
json_match = re.search(r'\[.*\]', sg_out, re.DOTALL)
if not json_match:
    # Try reading script.json directly if not in stdout
    with open("script.json", "r", encoding="utf-8") as f:
        script_json = f.read()
else:
    script_json = json_match.group(0)
    # Overwrite script.json with clean JSON
    with open("script.json", "w", encoding="utf-8") as f:
        f.write(script_json)

# 3. Run voice_test.py to generate output.mp3
print("Generating voiceover with voice_test.py...")
run_script("voice_test.py")

# 4. Load script.json and extract news/keywords
def load_news_segments(script_path):
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [{"text": item["news"], "keyword": " ".join(item["keywords"])} for item in data if "news" in item and "keywords" in item]

news_segments = load_news_segments("script.json")

pexels_api_key = "lXt4k8fRhaQqJ326bCl2UpsGvsroY95r9efOSlwyV9uHne4yA0U0LK24"  # Replace with your actual key

def download_pexels_video(query, idx):
    headers = {"Authorization": pexels_api_key}
    params = {"query": query, "per_page": 1}
    res = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
    try:
        data = res.json()
    except Exception as e:
        print(f"Error decoding JSON for query '{query}': {e}")
        return None
    if "videos" not in data or not data["videos"]:
        print(f"No videos found for query '{query}' or API error: {data}")
        return "fallback.mp4"  # Use a fallback video if not found
    video_url = data["videos"][0]["video_files"][0]["link"]
    video_data = requests.get(video_url).content
    filename = f"segment_{idx}.mp4"
    with open(filename, "wb") as f:
        f.write(video_data)
    return filename


# Download all relevant video segments (one per news, in order)
video_files = []
for idx, seg in enumerate(news_segments):
    print(f"Downloading video for: {seg['keyword']}")
    fname = download_pexels_video(seg["keyword"], idx)
    video_files.append(fname)




import moviepy.video.fx.all as vfx

# --- Intro ---
INTRO_VIDEO = "intro.mp4"  # 8 sec
OUTRO_IMAGE = "outro.jpg"
OUTRO_DURATION = 6  # seconds


# Use only output.mp3 for all voiceover
audio = AudioFileClip("output.mp3")
duration = audio.duration

# Load background music
bg_music = AudioFileClip("news_bg_music.mp3").volumex(0.12)

# Split audio for intro, main, outro
intro_clip = VideoFileClip(INTRO_VIDEO).subclip(0, 8)
intro_audio = audio.subclip(0, intro_clip.duration)
intro_bg = bg_music.subclip(0, intro_clip.duration)
intro_mix = CompositeAudioClip([intro_audio, intro_bg]).set_duration(intro_clip.duration)
intro_clip = intro_clip.set_audio(intro_mix)

main_audio_start = intro_clip.duration
main_audio_end = duration - OUTRO_DURATION
main_audio = audio.subclip(main_audio_start, main_audio_end)
main_bg = bg_music.subclip(intro_clip.duration, intro_clip.duration + main_audio.duration)
main_mix = CompositeAudioClip([main_audio, main_bg]).set_duration(main_audio.duration)

# Main news clips
clips = []
seg_duration = (main_audio_end - main_audio_start) / len(news_segments)
for i, f in enumerate(video_files):
    clip = VideoFileClip(f)
    # Resize to constant height, preserve aspect ratio, add black bars
    clip = clip.resize(height=FRAME_H)
    if clip.w < FRAME_W:
        clip = clip.margin(left=(FRAME_W-clip.w)//2, right=(FRAME_W-clip.w)//2, color=(0,0,0))
    elif clip.w > FRAME_W:
        clip = clip.crop(x_center=clip.w//2, width=FRAME_W)
    clip = clip.set_position((0,0)).set_duration(seg_duration)
    if clip.duration > seg_duration:
        clip = clip.subclip(0, seg_duration)
    else:
        n_loops = int(seg_duration // clip.duration) + 1
        clip = concatenate_videoclips([clip] * n_loops).subclip(0, seg_duration)
    clips.append(clip)

# Apply smooth crossfade transition between clips
news_clips = []
for i, clip in enumerate(clips):
    if i == 0:
        news_clips.append(clip)
    else:
        news_clips.append(clip.crossfadein(0.5))
main_video = concatenate_videoclips(news_clips, method="compose", padding=-0.5)
main_video = main_video.set_audio(main_mix)


# --- Outro ---
from moviepy.editor import ImageClip
outro_clip = ImageClip(OUTRO_IMAGE, duration=OUTRO_DURATION).resize(height=FRAME_H)
if outro_clip.w < FRAME_W:
    outro_clip = outro_clip.margin(left=(FRAME_W-outro_clip.w)//2, right=(FRAME_W-outro_clip.w)//2, color=(0,0,0))
elif outro_clip.w > FRAME_W:
    outro_clip = outro_clip.crop(x_center=outro_clip.w//2, width=FRAME_W)
# Slow zoom out
outro_clip = outro_clip.fx(vfx.resize, lambda t: 1 + 0.05 * t)
# Fade to black
outro_clip = outro_clip.fadeout(2)
# Only outro voiceover, no background music
outro_audio = audio.subclip(duration-OUTRO_DURATION, duration)
outro_clip = outro_clip.set_audio(outro_audio)

# --- Concatenate all ---
final = concatenate_videoclips([intro_clip, main_video, outro_clip], method="compose")
final.write_videofile("final_news_video.mp4", fps=24, codec="libx264", audio_codec="aac")
print("✅ Final video generated: final_news_video.mp4 (voiceover, bg music, smooth transitions, aspect ratio preserved)")

