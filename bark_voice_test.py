from bark import SAMPLE_RATE, generate_audio
from scipy.io.wavfile import write

# Your Hinglish script
script = "Namaste doston! Aaj ke tech duniya mein kuch zabardast hua hai!"

# Generate voice
audio_array = generate_audio(script)

# Save to file
write("output.wav", SAMPLE_RATE, audio_array)

print("Voice generated and saved as output.wav ✅")
