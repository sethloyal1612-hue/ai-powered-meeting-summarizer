# 🎙️ AI-Powered Meeting Summarizer

An AI-powered application that automatically converts meeting recordings into structured meeting minutes using Speech Recognition and Large Language Models (LLMs).

The system processes audio recordings, generates accurate transcripts, and creates concise meeting summaries, decisions, and action items through a fully local and offline AI pipeline.

---

## 📌 Project Overview

Meetings are an essential part of academic institutions, businesses, and organizations. However, manually creating meeting minutes is time-consuming and prone to missing important information.

This project automates the entire process by:

1. Accepting a meeting audio recording.
2. Converting the audio into a suitable format.
3. Transcribing speech into text.
4. Analyzing the transcript using an AI model.
5. Generating structured Meeting Minutes (MOM).
6. Allowing users to download the transcript.

The entire system runs locally without relying on cloud-based AI services.

---

## 🚀 Features

### 🎧 Audio Upload
Upload meeting recordings in supported audio formats.

### 🎙️ Speech-to-Text Conversion
Uses Whisper.cpp to convert speech into text with high accuracy.

### 📝 Automatic Meeting Minutes Generation
Creates structured meeting summaries using Large Language Models.

### 📄 Transcript Download
Allows users to download the complete generated transcript.

### ⚡ Local AI Processing
Runs entirely on the user's machine using Ollama.

### 🔒 Privacy Friendly
No meeting data is sent to external servers.

### 🌐 Offline Functionality
Works without internet after setup.

---

## 🏗️ System Architecture

```text
User Uploads Audio
         │
         ▼
      Gradio UI
         │
         ▼
       FFmpeg
(Audio Preprocessing)
         │
         ▼
    Whisper.cpp
(Speech-to-Text)
         │
         ▼
    Transcript
         │
         ▼
 Ollama + TinyLlama
(AI Summarization)
         │
         ▼
 Meeting Minutes
         │
         ▼
 Download Transcript
```

---

## 🛠️ Technology Stack

### Frontend
- Gradio

### Backend
- Python

### Speech Recognition
- Whisper.cpp

### Audio Processing
- FFmpeg

### AI Inference
- Ollama

### Language Models
- TinyLlama
- Llama 3.2
- Other Ollama-compatible models

---

## 📂 Project Structure

```text
AI-Powered-Meeting-Summarizer/
│
├── main.py
├── requirements.txt
├── transcript.txt
├── README.md
├── .gitignore
│
├── whisper.cpp/
│
└── screenshots/
```

---

## ⚙️ Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/your-username/AI-Powered-Meeting-Summarizer.git

cd AI-Powered-Meeting-Summarizer
```

---

### Step 2: Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux / Mac

```bash
source .venv/bin/activate
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4: Install FFmpeg

Download and install FFmpeg.

Verify installation:

```bash
ffmpeg -version
```

---

### Step 5: Install Ollama

Download Ollama from:

https://ollama.com

Verify installation:

```bash
ollama --version
```

---

### Step 6: Download AI Model

Example:

```bash
ollama pull tinyllama
```

Or:

```bash
ollama pull llama3.2
```

---

### Step 7: Setup Whisper.cpp

Clone Whisper.cpp:

```bash
git clone https://github.com/ggerganov/whisper.cpp.git
```

Build Whisper.cpp.

Download a model:

```bash
models/download-ggml-model.cmd base
```

---

### Step 8: Run Application

```bash
python main.py
```

Open:

```text
http://127.0.0.1:7861
```

---

## 🔄 Workflow

### 1. Upload Meeting Audio

User uploads:

```text
meeting.mp3
```

---

### 2. Audio Preprocessing

FFmpeg converts audio into:

```text
16kHz Mono WAV
```

---

### 3. Speech Recognition

Whisper.cpp generates:

```text
Transcript
```

---

### 4. AI Analysis

Transcript is sent to Ollama.

The selected language model generates:

- Summary
- Decisions
- Action Items
- Meeting Minutes

---

### 5. Output Generation

Results are displayed in the UI and can be downloaded.

---

## 📸 Screenshots

### Home Page

(Add Screenshot Here)

### Audio Upload

(Add Screenshot Here)

### Generated Meeting Minutes

(Add Screenshot Here)

### Transcript Download

(Add Screenshot Here)

---

## 🎯 Applications

- Corporate Meetings
- Academic Meetings
- Project Reviews
- Team Discussions
- Client Meetings
- Research Discussions

---

## 🔍 Challenges Faced

- Audio format compatibility
- Whisper model integration
- Ollama connectivity issues
- Memory allocation errors
- Large audio processing time
- Structured meeting minutes generation

---

## ✅ Solutions Implemented

- FFmpeg-based preprocessing
- Dynamic model detection
- Prompt engineering
- Resource optimization
- Improved UI design
- Offline AI pipeline

---

## 🚧 Limitations

- Processing time increases for longer meetings.
- Speaker identification is not implemented.
- Accuracy depends on audio quality.
- Lightweight models may generate generic summaries.

---

## 🔮 Future Scope

- Speaker Diarization
- Multi-language Support
- PDF Meeting Reports
- Cloud Deployment
- Email Integration
- Calendar Integration
- Action Item Tracking
- Real-Time Meeting Summarization

---

## 👨‍💻 Developed By

**Loyal Seth**  
B.Tech Computer Science & Engineering  
Government College of Engineering & Technology, Jammu

