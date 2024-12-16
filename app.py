import streamlit as st
import requests
import io
import os
from pydub import AudioSegment
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading

# Audio Recorder Class (keep the same as previous implementation)
class AudioRecorder:
    def __init__(self, channels=1, rate=44100, chunk_duration=0.1):
        self.channels = channels
        self.rate = rate
        self.chunk_duration = chunk_duration
        self.frames = []
        self.is_recording = False
        self.recording_thread = None

def convert_audio_to_wav(uploaded_file):
    """Convert uploaded audio file to WAV format"""
    try:
        os.makedirs('temp', exist_ok=True)
        
        temp_input_path = f"temp/uploaded_audio{os.path.splitext(uploaded_file.name)[1]}"
        with open(temp_input_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        wav_path = "temp/converted_audio.wav"
        audio = AudioSegment.from_file(temp_input_path)
        audio.export(wav_path, format="wav")
        
        with open(wav_path, 'rb') as f:
            audio_file = io.BytesIO(f.read())
        
        os.remove(temp_input_path)
        os.remove(wav_path)
        
        return audio_file
    
    except Exception as e:
        st.error(f"Error converting audio file: {e}")
        return None

def main():
    st.title("Speech-to-Text Validator")
    st.write("This app verifies if your voice matches the entered text.")

    # Initialize recorder
    if 'recorder' not in st.session_state:
        st.session_state.recorder = AudioRecorder()

    # Step 1: Input Text
    text_input = st.text_area("Enter the text (English or Hindi):", placeholder="Type the text you will speak here...")

    # Step 2: Language Selection
    language = st.radio("Select the language for transcription:", ("English", "Hindi"))

    # Audio Input Method Selection
    input_method = st.radio("Choose Audio Input Method:", 
                             ("Record Audio", "Upload Audio File"))

    # Conditional UI based on input method
    if input_method == "Record Audio":
        st.write("Record your voice:")
        
        # Create columns for recording buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # Start Recording Button
            if st.button("Start Recording"):
                if not text_input:
                    st.error("Please enter text before recording.")
                else:
                    if os.path.exists("temp/temp_recording.wav"):
                        os.remove("temp/temp_recording.wav")
                    
                    st.session_state.recorder.start_recording()
        
        with col2:
            # Stop Recording Button
            if st.button("Stop Recording"):
                st.session_state.recorder.stop_recording()
                
                audio_file = st.session_state.recorder.save_recording()
                if audio_file:
                    st.session_state.audio_file = audio_file
                    st.success("Recording stopped and saved!")
                else:
                    st.error("Failed to save recording.")
    
    else:  # Upload Audio File
        uploaded_file = st.file_uploader(
            "Upload an audio file", 
            type=['wav', 'mp3', 'ogg', 'flac', 'm4a', 'wma'],
            help="Supports various audio formats"
        )
        
        if uploaded_file is not None:
            audio_file = convert_audio_to_wav(uploaded_file)
            if audio_file:
                st.session_state.audio_file = audio_file
                st.success(f"Uploaded file '{uploaded_file.name}' processed successfully!")
            else:
                st.error("Failed to process the uploaded audio file.")

    # Process Button
    if st.button("Check Match"):
        if not text_input:
            st.error("Please provide text input.")
            return

        if not hasattr(st.session_state, 'audio_file') or not st.session_state.audio_file:
            st.error("Please record or upload an audio file first.")
            return

        # Send request to backend API
        try:
            # IMPORTANT: Replace with your actual backend API URL
            BACKEND_URL = "https://your-backend-api-url.com/check-speech/"
            
            files = {"audio": st.session_state.audio_file}
            data = {"text": text_input, "language": language}
            
            response = requests.post(BACKEND_URL, files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                st.write(f"**Recognized Text:** {result['recognized_text']}")
                if result.get("match"):
                    st.success("✅ The speech matches the input text!")
                else:
                    st.error("❌ The speech does not match the input text.")
                if result.get("error"):
                    st.warning(f"Error: {result['error']}")
            else:
                st.error(f"Backend Error: {response.status_code}")
        except Exception as e:
            st.error(f"Failed to connect to the backend: {e}")

    st.markdown(
        """
        <div style="position: fixed; bottom: 10px; right: 10px; text-align: right;">
            <p style="font-size: 12px; color: gray;">Powered by Purple Block</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Run the Streamlit app
if __name__ == "__main__":
    main()
