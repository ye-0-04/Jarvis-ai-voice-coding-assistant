import pyttsx3
import time

print("🔊 Testing Text-to-Speech...")

try:
    # Initialize TTS
    engine = pyttsx3.init()
    
    # List available voices
    voices = engine.getProperty('voices')
    print(f"Found {len(voices)} voices:")
    for i, voice in enumerate(voices):
        print(f"  {i}: {voice.name}")
    
    # Test with different voices
    test_phrases = [
        "Hello sir, this is Jarvis speaking.",
        "I am your code assistant.",
        "How can I help you today?"
    ]
    
    for phrase in test_phrases:
        print(f"🔊 Speaking: {phrase}")
        engine.say(phrase)
        engine.runAndWait()
        time.sleep(0.5)
    
    print("✅ Sound test complete!")

except Exception as e:
    print(f"❌ Sound test FAILED: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check your speakers/headphones are connected")
    print("2. Check Windows sound settings")
    print("3. Try: pip install pyttsx3 --upgrade")
    print("4. Try: pip install pypiwin32")