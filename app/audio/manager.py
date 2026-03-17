import os
import sys
import tempfile
import speech_recognition as sr
import io
import subprocess
from pydub import AudioSegment

# Try to get ffmpeg path from imageio-ffmpeg if available
try:
    import imageio_ffmpeg
    FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_BINARY = "ffmpeg"

class AudioManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def speech_to_text(self, audio_bytes):
        """
        Convert audio bytes to text using Google Speech Recognition (free online).
        Fallback to Sphinx (offline) if available/configured, but quality is poor.
        """
        if not audio_bytes:
            return ""

        try:
            # Check if bytes are valid WAV or convert
            audio_io = io.BytesIO(audio_bytes)
            
            # Convert to compatible format if needed (e.g. ensure 16kHz mono PCM)
            with sr.AudioFile(audio_io) as source:
                audio_data = self.recognizer.record(source)
                
            # Use Google Web Speech API (Free, high quality, online)
            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "" # Could not understand audio
        except sr.RequestError as e:
            return f"Error connecting to STT service: {e}"
        except Exception as e:
            return f"Error determining audio format: {e}"

    def transcribe_file(self, file_path):
        """
        Transcribe an audio file using Google Speech Recognition.
        Handles format conversion and splitting long audio into chunks.
        Uses explicit ffmpeg conversion to wav to avoid pydub dependency issues.
        """
        temp_wav = None
        try:
            # Create a localized temp wav file
            fd, temp_wav = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            
            # Explicitly convert input to WAV (16kHz, mono, pcm_s16le) using ffmpeg
            cmd = [
                FFMPEG_BINARY, 
                "-y", 
                "-i", file_path,
                "-ar", "16000",
                "-ac", "1", 
                "-c:a", "pcm_s16le",
                temp_wav
            ]
            
            # Run conversion
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                return f"Error converting audio file (ffmpeg failed). Ensure ffmpeg is working. Details: {e}"
            except FileNotFoundError:
                return "Error: ffmpeg executable not found. Please install imageio-ffmpeg or ffmpeg system-wide."

            # Load the converted wav file using pydub (handles WAV natively well)
            sound = AudioSegment.from_wav(temp_wav)
            
            # Split audio into 30-second chunks
            chunk_length_ms = 30 * 1000 
            chunks = [sound[i:i + chunk_length_ms] for i in range(0, len(sound), chunk_length_ms)]
            
            full_text = ""
            
            # Iterate through chunks
            for i, chunk in enumerate(chunks):
                # Export chunk to wav buffer (in memory)
                chunk_io = io.BytesIO()
                chunk.export(chunk_io, format="wav")
                chunk_io.seek(0)
                
                with sr.AudioFile(chunk_io) as source:
                    audio_listened = self.recognizer.record(source)
                    
                    try:
                        # Convert to text
                        text = self.recognizer.recognize_google(audio_listened)
                        full_text += text + " "
                    except sr.UnknownValueError:
                        continue # Skip unintelligible chunks
                    except sr.RequestError as e:
                        return f"Error connecting to STT service: {e}"
                        
            return full_text.strip()
            
        except Exception as e:
             # Detailed error logging for debugging
            return f"Error transcribing file: {str(e)}"
        finally:
            # Clean up temp file
            if temp_wav and os.path.exists(temp_wav):
                try:
                    os.remove(temp_wav)
                except:
                    pass

    def text_to_speech_file(self, text):
        """
        Generate audio file from text using pyttsx3 (offline) via a worker script.
        We use a separate process because pyttsx3/COM loop conflicts with Streamlit.
        Returns path to the generated file.
        """
        if not text:
            return None
            
        try:
            # Create a temp file for output audio
            fd_out, output_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd_out)
            
            # Create a temp file for input text (to avoid cli length limits)
            fd_in, text_path = tempfile.mkstemp(suffix=".txt")
            os.close(fd_in)
            
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text)
                
            # Get path to worker script
            worker_path = os.path.join(os.path.dirname(__file__), "tts_worker.py")
            
            # Call worker
            cmd = [sys.executable, worker_path, "--file", text_path, "--output", output_path]
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Clean up text file
            try:
                os.remove(text_path)
            except:
                pass
                
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"DEBUG: Generated TTS audio at {output_path}")
                return output_path
            else:
                return None
                
        except Exception as e:
            print(f"TTS Error: {e}")
            return None

# Singleton
audio_manager = AudioManager()

