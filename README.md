# Local RAG Knowledge Assistant

A privacy-focused, local Retrieval Augmented Generation (RAG) system that allows you to chat with your documents (PDF, TXT, Images, Audio) and Confluence pages using open-source LLMs.

## Features

- **Local & Private**: Runs entirely on your machine.
- **Multi-Format Ingestion**: 
  - **Documents**: PDF, Text files (.txt, .md).
  - **Images**: OCR via Tesseract (.png, .jpg, .bmp, etc.).
  - **Audio**: Transcribes audio files (.mp3, .wav, .m4a) to text.
  - **Archives**: Zip files and directory uploads.
- **Confluence Integration**: Ingest content directly from Confluence spaces or pages.
- **Voice Interaction**:
  - **Voice Input**: Dictate your queries using the microphone.
  - **Text-to-Speech**: Listen to the assistant's responses (optional toggle).
- **Web Search**:
  - Integrated DuckDuckGo search for up-to-date external information.
  - LLM autonomously decides when to search the web based on your query.
- **Quality Metrics**: Built-in evaluation tab to score answers on Relevance, Faithfulness, and Clarity.
- **Vector Search**: Uses ChromaDB for efficient retrieval.
- **Clean Architecture**: Modular codebase designed for maintainability.

## Prerequisites

1.  **Python 3.10+** (Python 3.14 via imageio-ffmpeg is supported).
2.  **Ollama**: 
    - [Download Ollama](https://ollama.com/)
    - Pull a model: `ollama pull llama3` (or `mistral`, `gemma`, etc.)
    - Update `app/config/settings.py` if you use a different model.
3.  **Tesseract OCR** (Required for image support):
    - **Windows**: [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH.
    - **Linux/Mac**: Install via package manager (e.g., `sudo apt install tesseract-ocr`).
4.  **Microphone** (Required for Voice Input).
5.  **Internet Connection** (Required for Web Search and Google Speech Recognition).

## Installation

1.  Create a virtual environment:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the application:

```bash
streamlit run app/frontend/ui.py
```
*Note: Using `streamlit run` directly is recommended over `python main.py`.*

The web interface will open in your browser automatically.

### Key Tabs

1.  **Files**: Upload documents, images, audio files, or ZIP archives. Provide context for the AI.
2.  **Confluence**: Connect to your Confluence instance to ingest documentation.
3.  **Settings**:
    - Toggle **External Web Search**.
    - Toggle **Image OCR**.
    - Toggle **Audio Response (Read Aloud)**.
    - Configure Tesseract path.
    - Clear Knowledge Base.
4.  **Metrics**: View detailed statistics about the last response (Latency, Source Count, Quality Scores).
