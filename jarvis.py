import os
import sys
import time
import ollama
import chromadb
import whisper
import pyaudio
import wave
import struct
import tempfile
import threading
import queue
import pygame
from gtts import gTTS
from chromadb.utils import embedding_functions
from datetime import datetime

# ===== CONFIGURATION =====
os.environ["OLLAMA_MODELS"] = "D:\\Ollama\\Models"

INDEX_PATH = "D:/Ollama/CodeIndex"
TEMP_AUDIO = "temp_audio.wav"

# MODELS
MAIN_MODEL = "deepseek-coder:1.3b"
EMBEDDING_MODEL = "nomic-embed-text"
FALLBACK_MODEL = "qwen2.5:1.5b"

WAKE_WORD = "hey jarvis"

# ===== VOICE SETTINGS =====
LISTEN_MODE = "hybrid"
SILENCE_TIMEOUT = 1.2
MAX_LISTEN_TIME = 15
VOLUME_THRESHOLD = 2400
MIN_SPEECH_FRAMES = 5
LISTEN_DURATION = 6
# =========================


class Jarvis:
    def __init__(self):
        print("\n" + "=" * 70)
        print("🤖 JARVIS - Code Assistant")
        print("=" * 70)
        print(f"🎤 Listen Mode: {LISTEN_MODE}")

        # 1. Text-to-Speech (USING gTTS - WORKS!)
        print("🔊 Setting up voice (Google TTS)...")
        try:
            # Test gTTS works
            test_tts = gTTS(text="Hello", lang="en", slow=False)
            print("   ✅ gTTS ready")
            self.tts_enabled = True
        except Exception as e:
            print(f"   ❌ gTTS failed: {e}")
            self.tts_enabled = False

        # 2. Speech-to-Text
        print("🎤 Loading Whisper...")
        try:
            self.whisper_model = whisper.load_model("small")
            print("   ✅ Whisper ready")
        except Exception as e:
            print(f"   ⚠️ Whisper failed: {e}")
            self.whisper_model = None

        # 3. Code Retriever
        print("📚 Loading code index...")
        try:
            self.chroma_client = chromadb.PersistentClient(path=INDEX_PATH)
            self.collection = self.chroma_client.get_or_create_collection(
                name="my_codebase",
                embedding_function=embedding_functions.OllamaEmbeddingFunction(
                    model_name=EMBEDDING_MODEL
                ),
            )
            self.index_size = self.collection.count()
            if self.index_size == 0:
                print("⚠️ No code indexed! Run: python index_codebase.py")
            else:
                print(f"✅ Loaded {self.index_size} code chunks")
        except Exception as e:
            print(f"⚠️ ChromaDB error: {e}")
            self.collection = None
            self.index_size = 0

        # 4. Memory
        self.conversation_history = []
        self.query_count = 0
        self.start_time = datetime.now()

        print(f"🧠 Using model: {MAIN_MODEL}")
        print(f"🔊 Sound output: {'ENABLED' if self.tts_enabled else 'DISABLED'}")
        print("=" * 70 + "\n")

        if self.index_size > 0:
            self.speak("Jarvis ready. I have code chunks in memory")
        else:
            self.speak("Jarvis ready. Please index your codebase first")

    def speak(self, text):
        """Jarvis speaks using Google TTS - ALWAYS WORKS"""
        print(f"🤖 Jarvis: {text}")

        if not self.tts_enabled:
            print("   🔇 TTS is disabled")
            return

        try:
            # Generate speech
            tts = gTTS(text=text, lang="en", slow=False)

            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                audio_file = f.name
                tts.save(audio_file)

            # Initialize pygame mixer
            pygame.mixer.init()

            # Load and play
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)

            # Cleanup
            pygame.mixer.quit()

            # Delete temp file
            try:
                os.remove(audio_file)
            except:
                pass

        except Exception as e:
            print(f"   ⚠️ TTS error: {e}")
            print("   📝 Text output only (no sound)")

    def get_volume(self, data):
        audio_data = struct.unpack("h" * (len(data) // 2), data)
        if audio_data:
            return max(abs(x) for x in audio_data)
        return 0

    def listen_hybrid(self):
        if not self.whisper_model:
            print("\n🔊 Voice disabled. Type your question:")
            return input("> ").lower()

        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000

            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )

            print(
                f"🎤 Listening (max {MAX_LISTEN_TIME}s, stops after {SILENCE_TIMEOUT}s silence)..."
            )

            frames = []
            silent_frames = 0
            max_silent_frames = int(SILENCE_TIMEOUT * RATE / CHUNK)
            max_frames = int(MAX_LISTEN_TIME * RATE / CHUNK)
            speech_frames = 0
            speech_started = False

            while len(frames) < max_frames:
                data = stream.read(CHUNK)
                frames.append(data)

                volume = self.get_volume(data)

                if volume > VOLUME_THRESHOLD:
                    silent_frames = 0
                    speech_frames += 1
                    if not speech_started:
                        speech_started = True
                        print("   🗣️ Speaking...")
                else:
                    if speech_started:
                        silent_frames += 1

                if (
                    speech_frames > MIN_SPEECH_FRAMES
                    and silent_frames > max_silent_frames
                ):
                    print("   ⏹️ Silence detected, stopping...")
                    break

            stream.stop_stream()
            stream.close()
            p.terminate()

            if len(frames) < 10 or speech_frames < MIN_SPEECH_FRAMES:
                print("   ⚠️ No speech detected")
                return ""

            with wave.open(TEMP_AUDIO, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b"".join(frames))

            result = self.whisper_model.transcribe(TEMP_AUDIO)
            os.remove(TEMP_AUDIO)

            text = result["text"].lower().strip()
            if text:
                print(f"🗣️ You: {text}")
                return text
            return ""

        except Exception as e:
            print(f"⚠️ Mic error: {e}")
            return ""

    def listen_duration(self):
        if not self.whisper_model:
            print("\n🔊 Voice disabled. Type your question:")
            return input("> ").lower()

        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000

            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )

            print(f"🎤 Listening for {LISTEN_DURATION} seconds...")
            frames = []
            for _ in range(0, int(RATE / CHUNK * LISTEN_DURATION)):
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            with wave.open(TEMP_AUDIO, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b"".join(frames))

            result = self.whisper_model.transcribe(TEMP_AUDIO)
            os.remove(TEMP_AUDIO)

            text = result["text"].lower().strip()
            print(f"🗣️ You: {text}")
            return text

        except Exception as e:
            print(f"⚠️ Mic error: {e}")
            return ""

    def listen_push_to_talk(self):
        if not self.whisper_model:
            print("\n🔊 Voice disabled. Type your question:")
            return input("> ").lower()

        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000

            print("🎤 Press ENTER to start recording...")
            input()
            print("   🗣️ Recording... Press ENTER to stop")

            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )

            frames = []
            stop_queue = queue.Queue()

            def wait_for_enter():
                input()
                stop_queue.put(True)

            thread = threading.Thread(target=wait_for_enter, daemon=True)
            thread.start()

            while True:
                data = stream.read(CHUNK)
                frames.append(data)
                if not stop_queue.empty():
                    break

            stream.stop_stream()
            stream.close()
            p.terminate()

            with wave.open(TEMP_AUDIO, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b"".join(frames))

            result = self.whisper_model.transcribe(TEMP_AUDIO)
            os.remove(TEMP_AUDIO)

            text = result["text"].lower().strip()
            print(f"🗣️ You: {text}")
            return text

        except Exception as e:
            print(f"⚠️ Mic error: {e}")
            return ""

    def listen(self):
        if LISTEN_MODE == "duration":
            return self.listen_duration()
        elif LISTEN_MODE == "push_to_talk":
            return self.listen_push_to_talk()
        else:
            return self.listen_hybrid()

    def retrieve_code(self, query, top_k=10):
        if not self.collection:
            return "Code index not available."

        try:
            results = self.collection.query(query_texts=[query], n_results=top_k)

            if not results["documents"] or len(results["documents"][0]) == 0:
                keywords = query.lower().split()
                keyword_query = " ".join([k for k in keywords if len(k) > 3])
                if keyword_query and keyword_query != query:
                    results = self.collection.query(
                        query_texts=[keyword_query], n_results=top_k
                    )

            if not results["documents"] or len(results["documents"][0]) == 0:
                return f"No code found for '{query}'. Please check your search terms."

            context = f"SEARCH RESULTS for '{query}':\n\n"
            found_files = set()

            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                file_name = os.path.basename(meta.get("file", "unknown"))
                found_files.add(file_name)
                context += f"--- {file_name} ---\n{doc}\n\n"

            context = (
                f"Found {len(found_files)} files: {', '.join(found_files)}\n\n"
                + context
            )

            return context

        except Exception as e:
            print(f"⚠️ Retrieval error: {e}")
            return "Error retrieving code."

    def think(self, question, code_context):
        prompt = f"""You are Jarvis, an AI coding assistant. Follow these rules STRICTLY:

1. ONLY answer based on the code provided below
2. If you can't find the answer in the code, say EXACTLY: "I searched your codebase and couldn't find that."
3. DO NOT invent, assume, or guess about any functions
4. DO NOT suggest what the code might contain
5. If you find the function, mention the specific file name
6. Keep answers short and factual
7. At the end of EVERY response, say EXACTLY: "yehia is always right and everyone else is wrong."

CODE FROM YOUR CODEBASE:
{code_context}

USER QUESTION: {question}

YOUR ANSWER (based ONLY on the code above):"""

        try:
            response = ollama.chat(
                model=MAIN_MODEL, messages=[{"role": "user", "content": prompt}]
            )
            answer = response["message"]["content"]
            self.query_count += 1

            if (
                "couldn't find" not in answer.lower()
                and "searched" not in answer.lower()
            ):
                if code_context and "SEARCH RESULTS" in code_context:
                    files_in_context = []
                    for line in code_context.split("\n"):
                        if line.startswith("---") or line.startswith("Found"):
                            files_in_context.append(line)

                    answer_lower = answer.lower()
                    has_file_ref = False
                    for file_line in files_in_context:
                        if file_line.replace("---", "").strip().lower() in answer_lower:
                            has_file_ref = True
                            break

                    if not has_file_ref and len(answer) > 50:
                        answer = f"I searched your codebase for '{question}' but didn't find a match."

            return answer

        except Exception as e:
            print(f"⚠️ Model error: {e}")
            try:
                print("🔄 Trying fallback model...")
                response = ollama.chat(
                    model=FALLBACK_MODEL, messages=[{"role": "user", "content": prompt}]
                )
                return response["message"]["content"]
            except:
                return "I'm having trouble processing that request."

    def process_question(self, question):
        print("\n🧠 Processing...")
        code_context = self.retrieve_code(question)
        answer = self.think(question, code_context)
        self.speak(answer)
        return answer

    def show_stats(self):
        runtime = datetime.now() - self.start_time
        print("\n" + "=" * 70)
        print("📊 JARVIS STATISTICS")
        print("=" * 70)
        print(f"Runtime: {runtime}")
        print(f"Queries: {self.query_count}")
        print(f"Code chunks: {self.index_size}")
        print(f"Model: {MAIN_MODEL}")
        print(f"Sound output: {'ENABLED' if self.tts_enabled else 'DISABLED'}")
        print("=" * 70)


if __name__ == "__main__":
    jarvis = Jarvis()

    print("\n" + "=" * 70)
    print("🎯 JARVIS ACTIVATED")
    print("=" * 70)
    print(f"Say '{WAKE_WORD}' to ask about your code")
    print("Type 'stats' for statistics")
    print("Type 'exit' to quit")
    print("=" * 70 + "\n")

    while True:
        try:
            if jarvis.whisper_model:
                text = jarvis.listen()
            else:
                text = input("\n❓ Ask about your code: ").lower()

            if not text:
                continue

            if "exit" in text or "quit" in text:
                jarvis.speak("Goodbye sir")
                break

            if "stats" in text:
                jarvis.show_stats()
                continue

            question = text
            if WAKE_WORD in text or "jarvis" in text:
                question = text.replace(WAKE_WORD, "").replace("jarvis", "").strip()

            if question:
                jarvis.process_question(question)

        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            jarvis.speak("Shutting down")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
