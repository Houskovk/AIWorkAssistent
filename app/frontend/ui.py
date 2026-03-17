import streamlit as st
import os
import shutil
import sys
import zipfile
from audio_recorder_streamlit import audio_recorder

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.rag.engine import RAGEngine
from app.config.settings import settings
from app.audio.manager import audio_manager

def run_app():
    st.set_page_config(page_title="Local RAG Assistant", layout="wide")
    
    st.title("🤖 Local RAG Knowledge Assistant")
    
    if st.session_state.get("web_search_enabled", True):
        st.info("💡 The model can use external web search during conversation. To disable **External Web Search**, go to the **Control Panel** sidebar -> **Settings** tab and toggle 'Enable External Web Search'.")
    
    # Initialize RAG Engine
    if "rag_engine" not in st.session_state:
        st.session_state.rag_engine = RAGEngine()
        
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Sidebar
    with st.sidebar:
        st.header("Control Panel")
        
        tab1, tab3, tab4, tab5 = st.tabs(["Files", "Confluence", "Settings", "Metrics"])

        with tab1:
            st.subheader("Upload Documents")

            # Use session state for image toggle
            if "enable_image_ocr" not in st.session_state:
                st.session_state.enable_image_ocr = True

            uploaded_files = st.file_uploader(
                "Upload PDFs, TXTs, Images, Audio or Folders",
                accept_multiple_files=True,
                type=["pdf", "txt", "md", "zip", "png", "jpg", "jpeg", "bmp", "tiff", "mp3", "wav", "m4a", "ogg", "flac"]
            )

            if uploaded_files:
                if st.button("Process Files", key="process_files"):
                    with st.spinner("Processing documents..."):
                        for uploaded_file in uploaded_files:
                            # Determine file type
                            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                            is_image = file_ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]
                            is_audio = file_ext in [".mp3", ".wav", ".m4a", ".ogg", ".flac"]

                            # Check if image and if OCR allowed
                            if is_image and not st.session_state.enable_image_ocr:
                                st.warning(f"Skipping {uploaded_file.name} (Image ingestion is disabled in Settings).")
                                continue

                            # If image, we should probably check Tesseract presence again before failing blindly
                            if is_image and st.session_state.enable_image_ocr:
                                if not os.path.exists(settings.TESSERACT_PATH):
                                     st.error(f"Cannot process {uploaded_file.name}: Tesseract not found. Check Settings.")
                                     continue

                            # Save file locally
                            file_path = os.path.join(settings.UPLOAD_DIR, uploaded_file.name)
                            # Ensure directory exists
                            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
                            
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                                
                            if True:
                                # Check if zip
                                if uploaded_file.name.lower().endswith('.zip'):
                                    try:
                                        extract_path = os.path.join(settings.UPLOAD_DIR, os.path.splitext(uploaded_file.name)[0])
                                        os.makedirs(extract_path, exist_ok=True)

                                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                            zip_ref.extractall(extract_path)

                                        results = st.session_state.rag_engine.ingest_directory(extract_path)

                                        processed = results.get("processed", [])
                                        skipped = results.get("skipped", [])
                                        errors = results.get("errors", [])

                                        msg = f"ZIP '{uploaded_file.name}': {len(processed)} processed"
                                        if skipped: msg += f", {len(skipped)} skipped"
                                        if errors: msg += f", {len(errors)} errors"

                                        if errors:
                                            st.warning(msg)
                                            with st.expander(f"Errors in {uploaded_file.name}"):
                                                for e in errors: st.write(e)
                                        else:
                                            st.success(msg)
    
                                    except Exception as e:
                                        st.error(f"Error processing ZIP {uploaded_file.name}: {e}")
                                else:
                                    # Ingest regular file
                                    try:
                                        st.session_state.rag_engine.ingest_file(file_path)
                                        st.success(f"Processed: {uploaded_file.name}")
                                    except Exception as e:
                                        st.error(f"Error processing {uploaded_file.name}: {e}")


        with tab3:
            st.subheader("Confluence Integration")
            
            conf_url = st.text_input("Confluence URL", value=settings.CONFLUENCE_URL, placeholder="https://your-domain.atlassian.net")
            conf_user = st.text_input("Username / Email", value=settings.CONFLUENCE_USERNAME)
            conf_api_key = st.text_input("API Key / Token", value=settings.CONFLUENCE_API_KEY, type="password")
            
            st.markdown("---")
            ingest_type = st.radio("Ingest Scope", ["Space", "Page"])
            
            if ingest_type == "Space":
                space_key = st.text_input("Space Key", placeholder="DS (Design System)")
                page_id = None
            else:
                page_id = st.text_input("Page ID", placeholder="12345678")
                space_key = None
                
            limit = st.number_input("Max Pages", min_value=1, max_value=500, value=50)

            if st.button("Ingest Confluence"):
                if not conf_url or not conf_user or not conf_api_key:
                    st.error("Please provide URL, Username, and API Key.")
                elif not space_key and not page_id:
                    st.error("Please provide a Space Key or Page ID.")
                else:
                    with st.spinner("Ingesting from Confluence..."):
                        try:
                            st.session_state.rag_engine.ingest_confluence(
                                url=conf_url,
                                username=conf_user,
                                api_key=conf_api_key,
                                space_key=space_key,
                                page_id=page_id,
                                limit=limit
                            )
                            st.success(f"Successfully ingested from Confluence.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                            
        with tab4:
            st.subheader("Global Settings")
            
            # Web Search Toggle
            use_web_search = st.toggle("Enable External Web Search", value=True, key="web_search_enabled")
            
            # Audio Settings
            st.subheader("Voice Settings")
            enable_tts = st.toggle("Enable Audio Response (Read Aloud)", value=False, key="enable_tts")

            st.divider()
            
            # Tesseract Path Setting
            st.subheader("OCR Configuration")

            if "enable_image_ocr" not in st.session_state:
                st.session_state.enable_image_ocr = True

            enable_ocr = st.toggle("Enable Image OCR", value=st.session_state.enable_image_ocr)
            if enable_ocr != st.session_state.enable_image_ocr:
                st.session_state.enable_image_ocr = enable_ocr
                st.rerun()

            tesseract_path = st.text_input("Tesseract Executable Path", value=settings.TESSERACT_PATH)
            
            if tesseract_path != settings.TESSERACT_PATH:
                settings.TESSERACT_PATH = tesseract_path
                st.toast("Tesseract path updated!")
                
            if not os.path.exists(settings.TESSERACT_PATH):
                st.warning("⚠️ Tesseract executable not found at this path. Image OCR will fail.")
            else:
                st.success("✅ Tesseract found.")
            
            st.divider()
            
            if st.button("Clear Knowledge Base", type="primary"):
                st.session_state.rag_engine.clear_data()
                # Clear upload directory
                for filename in os.listdir(settings.UPLOAD_DIR):
                    file_path = os.path.join(settings.UPLOAD_DIR, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        st.error(f"Failed to delete {file_path}. Reason: {e}")
                
                st.success("Knowledge base cleared!")
                st.rerun()

        with tab5:
            st.subheader("Model Evaluation")
            
            if st.button("Evaluate Last Response"):
                with st.spinner("Computing metrics..."):
                    metrics = st.session_state.rag_engine.compute_metrics()
                    
                    if "error" in metrics:
                        st.warning(metrics["error"])
                    else:
                        st.write("### Quality Metrics")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Relevance", f"{metrics['relevance']}/5")
                        with col2:
                            st.metric("Faithfulness", f"{metrics['faithfulness']}/5")
                        with col3:
                            st.metric("Clarity", f"{metrics['clarity']}/5")
                            
                        st.markdown("**Reasoning:**")
                        st.info(metrics['reasoning'])

                        st.write("### Performance Stats")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric("Duration", f"{metrics.get('duration', 0):.2f}s")
                        with c2:
                            st.metric("Web Search", "Yes" if metrics.get('used_web_search', False) else "No")
                        with c3:
                            st.metric("Sources Used", len(metrics.get('source_files', [])))

                        if metrics.get('source_files'):
                            with st.expander("View Source Files"):
                                for src in metrics['source_files']:
                                    st.write(f"- {src}")

    # Chat Interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("audio_path") and os.path.exists(message["audio_path"]):
                st.audio(message["audio_path"])

    # Handle Input (Text or Voice)
    prompt = st.chat_input("Ask a question about your documents...")
    
    # If voice prompt exists, use it
    if "voice_prompt" in st.session_state and st.session_state.voice_prompt:
        prompt = st.session_state.voice_prompt
        # Clear it so we don't loop
        del st.session_state.voice_prompt

    if prompt:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Get generator from RAG engine
                response_generator = st.session_state.rag_engine.ask(
                    prompt, 
                    history=st.session_state.messages[:-1], # Exclude current message from history to avoid confusion
                    use_web_search=use_web_search
                )
                
                for chunk in response_generator:
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # TTS Generation
                audio_path = None
                if enable_tts:
                    with st.spinner("Generating audio response..."):
                        audio_path = audio_manager.text_to_speech_file(full_response)
                        if audio_path:
                            st.audio(audio_path)
                
                # Add assistant message to history
                msg_entry = {"role": "assistant", "content": full_response}
                if audio_path:
                    msg_entry["audio_path"] = audio_path
                    
                st.session_state.messages.append(msg_entry)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

    # Voice Input Integration
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="2x",
    )
    
    if audio_bytes:
        # Check if this is new audio
        if "last_audio_bytes" not in st.session_state or st.session_state.last_audio_bytes != audio_bytes:
            st.session_state.last_audio_bytes = audio_bytes
            with st.spinner("Transcribing voice..."):
                text = audio_manager.speech_to_text(audio_bytes)
                if text:
                    st.session_state.voice_prompt = text
                    st.rerun()
                else:
                    st.warning("Could not understand audio.")

if __name__ == "__main__":
    run_app()
