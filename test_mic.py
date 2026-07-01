import pyaudio
import wave
import struct
import time

def test_mic():
    """Test microphone and find optimal volume threshold"""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    DURATION = 5
    
    print("="*60)
    print("🎤 MICROPHONE TEST")
    print("="*60)
    print(f"Recording for {DURATION} seconds...")
    print("Speak normally and then stay silent for a few seconds")
    print("-"*60)
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                   input=True, frames_per_buffer=CHUNK)
    
    frames = []
    volumes = []
    max_volume = 0
    min_volume = 99999
    
    for i in range(0, int(RATE / CHUNK * DURATION)):
        data = stream.read(CHUNK)
        frames.append(data)
        
        # Calculate volume
        audio_data = struct.unpack('h' * (len(data) // 2), data)
        if audio_data:
            volume = max(abs(x) for x in audio_data)
            volumes.append(volume)
            if volume > max_volume:
                max_volume = volume
            if volume < min_volume:
                min_volume = volume
            
            # Show live volume
            bar = int(volume / 100)
            if bar > 50:
                bar = 50
            print(f"Volume: {volume:6d}  {'█' * bar}", end='\r')
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    print("\n" + "-"*60)
    print("📊 RESULTS:")
    print(f"   Max Volume: {max_volume}")
    print(f"   Min Volume: {min_volume}")
    print(f"   Average Volume: {sum(volumes)//len(volumes) if volumes else 0}")
    
    # Recommend threshold
    if max_volume > 1000:
        recommended = max_volume // 3
        print(f"\n✅ RECOMMENDED THRESHOLD: {recommended}")
        print("   Set VOLUME_THRESHOLD in jarvis.py to this value")
        print("   (Lower = more sensitive, Higher = less sensitive)")
    else:
        print("\n⚠️ Low volume detected. Try:")
        print("   - Speak louder")
        print("   - Move closer to microphone")
        print("   - Check microphone settings in Windows")
    
    # Save test recording
    with wave.open("test_recording.wav", 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    print(f"\n💾 Test recording saved to: test_recording.wav")
    print("="*60)

if __name__ == "__main__":
    test_mic()