# Local RAG Knowledge Assistant

---

## Table of Contents

1. [Installation](#installation)
2. [Startup](#startup)
3. [Usage](#usage)
4. [Architecture](#architecture)

---

## Installation

### Prerequisites

| # | Requirement | Notes |
|---|-------------|-------|
| 1 | **Python 3.10+** | Python 3.14 supported via `imageio-ffmpeg` |
| 2 | **Ollama** | <https://ollama.com/> — run `ollama pull llama3` |
| 3 | **Tesseract OCR** | Required for image ingestion (see below) |
| 4 | **Microphone** | Required for voice input |
| 5 | **Internet connection** | Required for Web Search and Google Speech Recognition |

#### Tesseract OCR Installation

- **Windows:** Download installer from <https://github.com/UB-Mannheim/tesseract/wiki> and add to `PATH`
- **Linux:** `sudo apt install tesseract-ocr`
- **macOS:** `brew install tesseract`

```bash
# If Tesseract is not in your PATH, set the path in the .env file:
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# Path can also be set in the Settings tab of the UI.
```

#### Ollama Model Setup

```bash
# Pull a model (choose one)
ollama pull llama3
ollama pull mistral
ollama pull gemma

# If using a non-default model, update LLM_MODEL in:
# app/config/settings.py
```

### Setup Steps

**1. Create a virtual environment:**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

**2. Install all dependencies:**

```bash
pip install -r requirements.txt
```

### Key Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `langchain` / `langchain-community` / `langchain-ollama` | LLM orchestration |
| `chromadb` | Local vector database |
| `sentence-transformers` | Embedding model (`all-MiniLM-L6-v2`) |
| `ollama` | Local LLM inference client |
| `pypdf` | PDF parsing |
| `pytesseract` | Image OCR |
| `pyttsx3` | Text-to-speech output |
| `pydub` / `imageio-ffmpeg` | Audio file processing |
| `duckduckgo-search` | External web search |

### Optional Configuration

Create a `.env` file in the project root to override defaults:

```dotenv
LLM_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_K=4
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## Startup

### Run the Application

```bash
streamlit run app/frontend/ui.py
```

The web interface opens automatically at **<http://localhost:8501>**

> **Note:** Using `streamlit run` directly is recommended over `python main.py`.

### Required Services

| Service | How to start | Default URL |
|---------|-------------|-------------|
| Ollama LLM server | `ollama serve` (auto-starts on most installs) | `http://localhost:11434` |
| Streamlit UI | `streamlit run app/frontend/ui.py` | `http://localhost:8501` |

---

## Usage

The interface consists of a **main chat area** and a **sidebar Control Panel** with four tabs.

### Sidebar Tabs

#### Files

Upload and ingest documents into the local knowledge base.

| Accepted Format | Processing Method |
|-----------------|-------------------|
| `.pdf` | PyPDF text extraction |
| `.txt`, `.md` | Plain text loader |
| `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff` | Tesseract OCR |
| `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` | Audio transcription via pydub + ffmpeg |
| `.zip` / directory | Extracted and processed recursively |

1. Select one or more files using the uploader.
2. Click **"Process Files"** — files are chunked, embedded and stored in ChromaDB.

#### Confluence

Ingest documentation directly from a Confluence instance.

1. Enter your **Confluence URL**, **username** and **API key**.
2. Provide a **Space Key** (entire space) or a **Page ID** (single page).
3. Set a result **limit** and click **"Load from Confluence"**.

#### Settings

| Toggle / Field | Description |
|----------------|-------------|
| **Enable External Web Search** | LLM autonomously uses DuckDuckGo when needed |
| **Enable Image OCR** | Allow image files to be ingested |
| **Audio Response (Read Aloud)** | TTS playback of assistant answers via pyttsx3 |
| **Tesseract Path** | Custom path to the `tesseract` binary |
| **Clear Knowledge Base** | Wipes all vectors from ChromaDB |

#### Metrics

Displays statistics from the last response:

- **Latency** — total response time in seconds
- **Source Count** — number of retrieved document chunks used
- **Quality Scores** — LLM-graded evaluation:
  - *Relevance* — how well the answer addresses the query
  - *Faithfulness* — whether the answer is grounded in the retrieved sources
  - *Clarity* — readability and coherence of the response

### Chat Area

- **Type** a query in the input box and press **Enter**.
- **Dictate** a query by clicking the 🎤 microphone button (transcribed via Google Speech Recognition).
- The assistant streams the response token by token.
- Enable **"Read Aloud"** to hear responses spoken aloud via TTS.
- The LLM **autonomously decides** whether to search the web or use only the local knowledge base.
- Conversation **history is preserved** for the duration of the session.

---

## Architecture

The application follows a modular, layered architecture. Data flows from user input through the RAG engine to the LLM and back to the UI.

### Module Overview

| Module | Path | Responsibility |
|--------|------|----------------|
| **Frontend** | `app/frontend/ui.py` | Streamlit UI, session state, voice I/O |
| **RAG Engine** | `app/rag/engine.py` | Query orchestration, self-correction loop |
| **Prompts** | `app/rag/prompts.py` | Router, grader and comparison prompt templates |
| **Evaluator** | `app/rag/evaluator.py` | LLM-based answer quality scoring |
| **Loader Factory** | `app/loaders/loader_factory.py` | Selects correct loader by file extension |
| **PDF Loader** | `app/loaders/pdf_loader.py` | PDF text extraction via pypdf |
| **Text Loader** | `app/loaders/text_loader.py` | Plain text / Markdown ingestion |
| **Image Loader** | `app/loaders/image_loader.py` | OCR via pytesseract |
| **Audio Loader** | `app/loaders/audio_loader.py` | Audio transcription via pydub |
| **Confluence** | `app/loaders/confluence_connector.py` | Confluence REST API ingestion |
| **Embeddings** | `app/embeddings/manager.py` | Sentence-transformer embedding wrapper |
| **Vector Store** | `app/vectorstore/chroma_store.py` | ChromaDB add / search interface |
| **LLM Client** | `app/llm/ollama_client.py` | Ollama streaming and text generation |
| **Web Search** | `app/tools/web_search.py` | DuckDuckGo search tool |
| **Audio Manager** | `app/audio/manager.py` | TTS playback coordination |
| **TTS Worker** | `app/audio/tts_worker.py` | Background pyttsx3 speech thread |
| **Settings** | `app/config/settings.py` | Pydantic-settings config + `.env` support |
| **Interfaces** | `app/core/interfaces.py` | Abstract base classes: `IDocumentLoader`, `IVectorStore`, `ILLMClient` |

### Directory Structure

```
AIWorkAssistent/
├── main.py                        # Alternative entry point
├── requirements.txt
├── .env                           # Optional local config overrides
├── architecture.md                # This file
├── app/
│   ├── audio/
│   │   ├── manager.py             # TTS playback coordinator
│   │   └── tts_worker.py          # Background speech thread
│   ├── config/
│   │   └── settings.py            # Pydantic-settings configuration
│   ├── core/
│   │   └── interfaces.py          # Abstract base classes
│   ├── embeddings/
│   │   └── manager.py             # Embedding model wrapper
│   ├── frontend/
│   │   └── ui.py                  # Streamlit application
│   ├── llm/
│   │   └── ollama_client.py       # Ollama LLM client
│   ├── loaders/
│   │   ├── loader_factory.py      # Loader dispatcher
│   │   ├── pdf_loader.py
│   │   ├── text_loader.py
│   │   ├── image_loader.py
│   │   ├── audio_loader.py
│   │   └── confluence_connector.py
│   ├── rag/
│   │   ├── engine.py              # Core RAG orchestrator
│   │   ├── prompts.py             # Prompt templates
│   │   └── evaluator.py           # Answer quality scorer
│   ├── tools/
│   │   └── web_search.py          # DuckDuckGo integration
│   └── vectorstore/
│       └── chroma_store.py        # ChromaDB wrapper
└── data/
    ├── chroma_db/                 # Persistent vector store
    └── uploads/                   # Temporary upload staging
```

---

*Local RAG Knowledge Assistant — v1.0.0*

