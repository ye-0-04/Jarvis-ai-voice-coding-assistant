# 🤖 Jarvis - Code Assistant

A voice-activated AI coding assistant that uses **local LLMs** (via Ollama) with **RAG (Retrieval-Augmented Generation)** to search and answer questions about your codebase. Whisper handles speech-to-text, and Google TTS provides voice output.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎤 **Voice Control** | Speak naturally — just say "Hey Jarvis" and ask about your code |
| 🔍 **RAG-Powered Search** | ChromaDB indexes your codebase; Jarvis retrieves relevant context before answering |
| 🧠 **Local LLM** | Runs entirely offline via Ollama (no API keys, no cloud) |
| 🔇 **Multiple Listening Modes** | Hybrid (silence detection), fixed duration, or push-to-talk |
| 🔊 **Voice Response** | Google TTS reads answers aloud |
| 📊 **Usage Stats** | Track queries, runtime, and indexed code chunks |

## 🧩 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Jarvis Assistant                       │
├───────────┬───────────┬─────────────┬────────────────────┤
│  🎤 Input │  🧠 Brain │  📚 Memory  │  🔊 Output         │
├───────────┼───────────┼─────────────┼────────────────────┤
│ Whisper   │ Ollama    │ ChromaDB    │ gTTS + pygame      │
│ (STT)     │ (LLM)     │ (Vector DB) │ (Text-to-Speech)   │
└───────────┴───────────┴─────────────┴────────────────────┘
```

## 📋 Prerequisites

| Dependency | Version | Purpose |
|-----------|---------|---------|
| [Python](https://python.org) | 3.10+ | Runtime |
| [Ollama](https://ollama.ai) | Latest | Local LLM server |
| [Git](https://git-scm.com) | Any | Version control |
| [PortAudio](https://portaudio.com) | v19 | Microphone input (Windows: `pip install pyaudio` handles this) |

### Ollama Models Required

Pull these models **before** running Jarvis:

```bash
# Main reasoning model
ollama pull deepseek-coder:1.3b

# Embedding model (for code search)
ollama pull nomic-embed-text

# Fallback model (optional)
ollama pull qwen2.5:1.5b
```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ye-0-04/jarvis-code-assistant.git
cd jarvis-code-assistant
```

### 2. Set Up Python Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If `pyaudio` fails to install on Windows, download the appropriate wheel from [PyAudio Wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install it manually:
> ```bash
> pip install PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl
> ```

### 4. Start Ollama

Make sure the Ollama service is running:

```bash
ollama serve
```

Or launch the Ollama desktop application.

### 5. Index Your Codebase

Edit `index_codebase.py` and change `PROJECT_PATH` to point at the project you want Jarvis to search:

```python
PROJECT_PATH = r"C:\Users\YourName\Projects\my-project"
```

Then run the indexer:

```bash
python index_codebase.py
```

This scans all code files (`.py`, `.js`, `.ts`, `.java`, `.cpp`, etc.), chunks them, and stores embeddings in `D:/Ollama/CodeIndex`.

### 6. Run Jarvis

```bash
python jarvis.py
```

Or double-click `run_jarvis.bat` (Windows).

## 🎯 Usage

### Voice Commands

| Action | Say |
|--------|-----|
| Ask a question | `"Hey Jarvis, how does the main function work?"` |
| Quick question (no wake word) | Just speak after the beep |
| View statistics | `"Stats"` or `"show stats"` |
| Exit | `"Exit"` or `"Quit"` |

### Listening Modes

Set `LISTEN_MODE` in `jarvis.py`:

| Mode | Behavior |
|------|----------|
| `hybrid` (default) | Records until silence is detected (up to 15s) |
| `duration` | Records for a fixed `LISTEN_DURATION` seconds |
| `push_to_talk` | Press Enter to start/stop recording |

### Configuration Reference

All settings are at the top of `jarvis.py`:

```python
MAIN_MODEL = "deepseek-coder:1.3b"     # LLM for answers
EMBEDDING_MODEL = "nomic-embed-text"    # Model for embeddings
WAKE_WORD = "hey jarvis"                # Wake phrase
SILENCE_TIMEOUT = 1.2                   # Seconds of silence to stop
VOLUME_THRESHOLD = 2400                 # Mic sensitivity
MAX_LISTEN_TIME = 15                    # Max recording seconds
```

## 📂 File Structure

```
D:\Jarvis\
├── jarvis.py              # Main assistant (voice, LLM, RAG)
├── index_codebase.py       # Codebase indexer (ChromaDB)
├── requirements.txt        # Python dependencies
├── run_jarvis.bat          # Windows launcher
├── test_jarvis.py          # Unit tests
├── test_mic.py             # Microphone test
├── test_sound.py           # Sound playback test
├── test_tts.py             # Text-to-speech test
└── README.md               # This file
```

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest test_jarvis.py -v

# Test microphone
python test_mic.py

# Test sound playback
python test_sound.py

# Test TTS
python test_tts.py
```

## 🛠️ Troubleshooting

### "No code indexed!"
Run `python index_codebase.py` after editing `PROJECT_PATH` to point at your project.

### Whisper model fails to load
Whisper downloads the model on first run (≈1.5 GB for "small"). Ensure a stable internet connection.

### "Ollama not running"
Start Ollama via the desktop app or run `ollama serve` in a terminal.

### PyAudio installation fails
- **Windows:** Install from [Gohlke's wheels](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
- **Linux:** `sudo apt install portaudio19-dev python3-pyaudio`
- **macOS:** `brew install portaudio`

### No sound from TTS
Jarvis falls back to text-only output. Ensure `pygame` and `gTTS` are installed correctly.

## 📦 Dependencies

```
ollama           # Ollama Python client
chromadb         # Vector database for RAG
sentence-transformers  # Embeddings
openai-whisper   # Speech-to-text
pyaudio          # Microphone input
pyttsx3          # Fallback TTS
numpy            # Audio processing
pydub            # Audio utilities
gtts             # Google Text-to-Speech
pygame           # Audio playback
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for local LLM inference
- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [gTTS](https://github.com/pndurette/gTTS) for text-to-speech
