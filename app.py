import os
import requests
import streamlit as st
from io import BytesIO
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
from gtts import gTTS
import tempfile
from IPython.display import Audio

load_dotenv()

# Hugging Face API configuration
HF_API_URL_WHISPER = "https://api-inference.huggingface.co/models/openai/whisper-tiny.en"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/v1/query"
GROQ_HEADERS = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}

class AI_Assistant:
    def __init__(self):
        self.reset_conversation()

    def reset_conversation(self):
        self.full_transcript = [
            {"role": "system", "content": "You are a tech nerd, concise and to the point. Your name is 'WonderAI', created by Boi loves code."},
        ]

    def query_hf_api(self, audio_data):
        """Send audio data to the Hugging Face Whisper API for transcription."""
        try:
            response = requests.post(HF_API_URL_WHISPER, headers=HF_HEADERS, data=audio_data)
            response.raise_for_status()  # Raise an error for a bad response
            return response.json()  # Return JSON response
        except requests.exceptions.HTTPError as err_http:
            st.error(f"HTTP error occurred: {err_http}")
            return None
        except Exception as err:
            st.error(f"An error occurred: {err}")
            return None

    def query_groq_api(self, transcript):
        """Send transcription to the Groq API for response."""
        try:
            response = requests.post(GROQ_API_URL, headers=GROQ_HEADERS, json={"query": transcript})
            response.raise_for_status()  # Raise an error for a bad response
            return response.json()  # Return JSON response
        except requests.exceptions.HTTPError as err_http:
            st.error(f"HTTP error occurred: {err_http}")
            return None
        except Exception as err:
            st.error(f"An error occurred: {err}")
            return None

    def generate_tts(self, text):
        """Generate TTS using gTTS and return the path to the audio file."""
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name

def main():
    st.title("AI Voice Assistant")

    # Create an AI Assistant instance
    assistant = AI_Assistant()

    # Center the audio recorder
    st.markdown(
        """
        <style>
        .stButton button {
            margin: 0 auto;
            display: block;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Record audio input
    audio_data = audio_recorder()

    if audio_data:
        # Get WAV data from the recording
        audio_bytes = audio_data.get_wav_data()
        if audio_bytes:
            st.audio(audio_bytes)

            # Query Hugging Face Whisper API for transcription
            transcription = assistant.query_hf_api(audio_bytes)
            if transcription:
                transcript_text = transcription.get("text", "Transcription failed.")
                st.write("Transcription:")
                st.write(transcript_text)

                # Query Groq API with transcription
                response = assistant.query_groq_api(transcript_text)
                if response:
                    response_text = response.get("response", "No response.")
                    st.write("Groq Response:")
                    st.write(response_text)

                    # Generate and play TTS
                    tts_file_path = assistant.generate_tts(response_text)
                    st.audio(tts_file_path)

if __name__ == "__main__":
    main()
