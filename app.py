import streamlit as st
import requests
import os
from gtts import gTTS
from io import BytesIO
from audio_recorder_streamlit import audio_recorder
import tempfile
from dotenv import load_dotenv
from groq import Groq
import base64
import json
import time
load_dotenv()

# Configuration for Hugging Face API
HF_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-tiny.en"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

class AI_Assistant:
    # ... [Keep the AI_Assistant class as is] ...

def autoplay_audio(file):
    file.seek(0)
    audio_bytes = file.read()
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

def main():
    st.title("AI Voice Assistant")

    ai_assistant = AI_Assistant()

    # ... [Keep the CSS styles as is] ...

    # Initialize session state
    if 'audio_queue' not in st.session_state:
        st.session_state.audio_queue = []

    # Record audio using audio_recorder_streamlit
    st.markdown('<div class="audio-recorder-wrapper">', unsafe_allow_html=True)
    audio_bytes = audio_recorder(key="audio_recorder")
    st.markdown('</div>', unsafe_allow_html=True)

    if audio_bytes:
        loading_placeholder = st.empty()
        loading_placeholder.markdown('<div class="loading-dots">Processing audio</div>', unsafe_allow_html=True)

        # Save the audio_bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
            temp_audio_file.write(audio_bytes)
            temp_audio_file_path = temp_audio_file.name

        # Transcribe using Whisper
        with open(temp_audio_file_path, "rb") as audio_file:
            transcription = ai_assistant.query_hf_api(audio_file.read())

        user_text = transcription.get("text", "")
        st.write(f"User: {user_text}")
        
        if user_text:
            ai_assistant.full_transcript.append({"role": "user", "content": user_text})

            # Hide loading dots and show "AI is thinking..." message
            loading_placeholder.empty()
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown('<h3 class="gradient-text">AI is thinking...</h3>', unsafe_allow_html=True)

            # Generate AI response
            ai_response = ai_assistant.generate_ai_response(user_text)
            
            # Remove "AI is thinking..." message
            thinking_placeholder.empty()

            # Display AI response in gradient box
            st.markdown(f"""
                <div class="ai-response-box">
                    <div class="ai-response-text">{ai_response}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if ai_response.strip():
                # Generate TTS
                audio_stream = ai_assistant.generate_audio(ai_response)
                
                # Add to audio queue
                st.session_state.audio_queue.append(audio_stream)

    # Play audio from the queue
    if st.session_state.audio_queue:
        audio_to_play = st.session_state.audio_queue.pop(0)
        autoplay_audio(audio_to_play)

        # Show waveform animation
        waveform_placeholder = st.empty()
        waveform_placeholder.markdown("""
            <div class="waveform-animation">
                <div class="waveform-bar"></div>
                <div class="waveform-bar"></div>
                <div class="waveform-bar"></div>
                <div class="waveform-bar"></div>
                <div class="waveform-bar"></div>
            </div>
        """, unsafe_allow_html=True)

        # Hide waveform animation after TTS is done (adjust time if needed)
        time.sleep(5)
        waveform_placeholder.empty()

    # Force a rerun to play the next audio in queue, if any
    if st.session_state.audio_queue:
        st.experimental_rerun()

if __name__ == "__main__":
    main()
