# test_sound.py
from gtts import gTTS
import pygame
import tempfile
import os

text = "Hello sir, this is Jarvis speaking"

tts = gTTS(text=text, lang='en', slow=False)

with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
    audio_file = f.name
    tts.save(audio_file)

pygame.mixer.init()
pygame.mixer.music.load(audio_file)
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    pygame.time.wait(100)

pygame.mixer.quit()
os.remove(audio_file)

print("✅ Sound worked!")