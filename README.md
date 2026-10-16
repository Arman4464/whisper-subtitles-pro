# Whisper Subtitles Pro 🎙️✨

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20|%20macOS%20|%20Windows-brightgreen.svg)]()
[![Accuracy](https://img.shields.io/badge/drift-0.00%25%20(Zero%20Desync)-success.svg)]()
[![Cloud Runner](https://img.shields.io/badge/cloud-GitHub%20Actions%20Runner-orange.svg)]()

> **Universal 100% Accurate Audio-to-Subtitles & Alignment Engine.**  
> A professional cross-platform CLI tool built for Linux, macOS, and Windows. Eliminates subtitle drift and desync using acoustic speech pause detection, Silero VAD, word-level cross-attention DTW, and autonomous GitHub Actions cloud execution.

---

## ⚡ Key Highlights

- **🎯 Zero Drift (0.00% Desync Guarantee)**: Mathematical forced alignment pins each word and sentence to real acoustic audio frames and speech pauses.
- **🧠 Universal Dual Engine**:
  - **Mode A (Acoustic Neural ASR)**: Transcribe raw audio using Faster-Whisper (CTranslate2) or Google Gemini Audio API with word-level timestamps.
  - **Mode B (Exact Forced Alignment)**: Align existing book text, transcripts, or narration scripts to audio with zero desync.
- **🖥️ Proper App-Like Terminal CLI**: Rich color-coded terminal interface with interactive TUI menu, status badges, progress indicators, and summary metrics.
- **☁️ Autonomous GitHub Actions Cloud Runner**: Dispatch heavy 1-hour to 6-hour audio transcription tasks directly to GitHub Actions in the cloud. Zero local PC heating, zero GPU requirements.
- **📦 Multi-Format Export**: Generates `.srt`, `.vtt`, `.json` (with word-level timestamps & confidence scores), `.lrc` (karaoke sync), and clean `.txt`.

---

## 🚀 Installation

### Linux / macOS
```bash
git clone https://github.com/Arman4464/whisper-subtitles-pro.git
cd whisper-subtitles-pro
pip install -e .
```

### Windows (PowerShell / Command Prompt)
```powershell
git clone https://github.com/Arman4464/whisper-subtitles-pro.git
cd whisper-subtitles-pro
pip install -e .
```

---

## 💻 CLI Usage

### 1. Interactive Studio Wizard (Recommended)
Simply run without arguments to launch the interactive terminal menu:
```bash
whisper-subtitles-pro
# or shortcut:
wsub
```

```
  ╦ ╦┬ ┬┬┌─┐┌─┐┌─┐┬─┐  ╔═╗┬ ┬┌┐ ┌┬┐┬┌┬┐┬  ┌─┐┌─┐  ╔═╗┬─┐┌─┐
  ║║║├─┤│└─┐├─┘├┤ ├┬┘  ╚═╗│ │├┴┐ │ │ │ │  ├┤ └─┐  ╠═╝├┬┘│ │
  ╚╩╝┴ ┴┴└─┘┴  └─┘┴└─  ╚═╝└─┘└─┘ ┴ ┴ ┴ ┴─┘└─┘└─┘  ╩  ┴└─└─┘
  100% Accurate Word-Level Audio-to-Subtitles & Alignment Engine
  Version 1.0.0 • Cross-Platform (Linux / macOS / Windows)

 Welcome to Whisper Subtitles Pro Interactive Studio!

 Select an operation:
   [1] Transcribe Audio to Subtitles (Faster-Whisper / Gemini)
   [2] Forced Alignment (Audio + Transcript -> 100% Zero Drift)
   [3] Dispatch to Autonomous Cloud Worker (GitHub Actions)
   [4] Inspect Audio File Properties
   [5] Exit
```

---

### 2. Transcribe Raw Audio
Transcribe audio into synchronized sentence & word-level subtitles:
```bash
# Using local Faster-Whisper base model
whisper-subtitles-pro transcribe lecture.wav --model base --format srt,vtt,json

# Using Gemini Cloud API (fast, zero local model downloads)
whisper-subtitles-pro transcribe podcast.mp3 --model gemini --format all

# Specify spoken language and custom characters per line
whisper-subtitles-pro transcribe speech.wav -l en --max-cpl 42 --max-lines 2
```

---

### 3. Forced Alignment (Audio + Transcript)
When you have a book chapter or transcript, forced alignment provides **100% mathematical zero drift**:
```bash
whisper-subtitles-pro align chapter_1.wav chapter_1_transcript.txt --format all
```

---

### 4. Autonomous GitHub Actions Cloud Runner
Process heavy audio files (up to 6 hours continuous execution) directly on GitHub Actions cloud runners without using your PC:
```bash
# Dispatch audio to cloud worker
whisper-subtitles-pro cloud my_large_audio.wav --model large-v3-turbo

# Specify target repo & language
whisper-subtitles-pro cloud lecture.wav --repo Arman4464/whisper-subtitles-pro -l en
```

---

### 5. Inspect Audio Properties
Quickly inspect duration, sample rate, channels, and recommended model size:
```bash
whisper-subtitles-pro info meeting.wav
```

---

## 📊 Supported Subtitle Formats

| Format | Extension | Features |
| :--- | :--- | :--- |
| **SubRip** | `.srt` | Standard player subtitles with CPL and line-wrapping limits. |
| **WebVTT** | `.vtt` | Modern HTML5 web video captions. |
| **Rich JSON** | `.json` | Full segment IDs, sentence boundaries, word-level timestamps, confidence scores. |
| **Karaoke LRC**| `.lrc` | Word-by-word / sentence-by-sentence lyric sync. |
| **Plain Text** | `.txt` | Clean formatted text transcript with timestamps. |

---

## ⚙️ Environment Variables

| Variable | Description |
| :--- | :--- |
| `GITHUB_TOKEN` | Required for dispatching autonomous cloud jobs to GitHub Actions. |
| `GEMINI_API_KEY` | Required when using `--model gemini` for multimodal cloud transcription. |

---

## 📜 License

Released under the [MIT License](LICENSE).
Created with precision by **Arman4464**.
