from gtts import gTTS
def text_to_voice(text, filename="output.mp3"):
    tts = gTTS(text=text, lang='en', tld='co.in')  # Indian English
    tts.save(filename)
    print(f"✅ Voice saved as {filename}")

if __name__ == "__main__":
    # Example usage
    text = "Dilli mein aaj tez baarish ke wajah se heavy traffic jam ho gaya!"
    text_to_voice(text)
