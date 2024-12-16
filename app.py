import streamlit as st
import requests
import io
import os
from pydub import AudioSegment
import numpy as np

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
    st.title("Speech-to-Text Matcher")
    st.write("Compare your spoken text with a target text")

    # Input Text
    text_input = st.text_area("Enter the text you will speak:", 
                               placeholder="Type the exact text you'll speak...")

    # Language Selection
    language = st.radio("Select Language:", ("English", "Hindi"))

    # Audio Input Method
    input_method = st.radio("Choose Audio Input:", 
                             ("Upload Audio File", "Web Recording"))

    # File Upload Method
    if input_method == "Upload Audio File":
        uploaded_file = st.file_uploader(
            "Upload Audio File", 
            type=['wav', 'mp3', 'ogg', 'flac']
        )
        
        if uploaded_file is not None:
            # Convert audio file
            audio_file = convert_audio_to_wav(uploaded_file)
            
            if audio_file:
                st.success("Audio file processed successfully!")
                
                # Add a mock comparison (replace with actual API in production)
                if st.button("Check Text Match"):
                    # Simulated matching logic
                    st.warning("Note: Actual speech recognition requires backend API")
                    st.info("Placeholder: Would normally compare spoken text with input text")

    else:  # Web Recording Method
        st.warning("Web audio recording not supported in this environment.")
        st.info("Recommended to use file upload or a backend API for precise speech recognition")

    # Additional Information
    st.markdown("""
    ### How This Works
    1. Enter the exact text you plan to speak
    2. Upload an audio file containing your speech
    3. Our system will compare the spoken words with your input
    
    ### Limitations
    - Requires precise matching
    - Works best with clear audio recordings
    - Accuracy depends on audio quality
    """)

if __name__ == "__main__":
    main()
