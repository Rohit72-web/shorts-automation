from a4f_local import A4F
client = A4F()
import os
import json
from moviepy.editor import AudioFileClip, concatenate_audioclips

try:
    # Read script.json
    script_path = "script.json"
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"{script_path} not found. Please generate the script first.")
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)
    news_lines = [item["news"] for item in script_data if "news" in item]
    temp_files = []
    for idx, news in enumerate(news_lines):
        try:
            audio_bytes = client.audio.speech.create(
                model="tts-1",
                input=news,
                voice="alloy"
            )
            temp_file = f"temp_chunk_{idx}.mp3"
            with open(temp_file, "wb") as f:
                f.write(audio_bytes)
            temp_files.append(temp_file)
        except Exception as chunk_err:
            print(f"Error generating audio for news {idx+1}: {chunk_err}")
    if not temp_files:
        raise RuntimeError("No audio was generated. Check your TTS API or script content.")
    audio_clips = [AudioFileClip(f) for f in temp_files]
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile("output.mp3")
    for f in temp_files:
        os.remove(f)
    print(f"Generated output.mp3 from script.json (full script, {len(audio_clips)} news items)")
except Exception as e:
    print(f"An error occurred: {e}")