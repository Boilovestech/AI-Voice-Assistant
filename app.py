import os  
import requests  
import streamlit as st  
from io import BytesIO  
from audio_recorder_streamlit import audio_recorder  
from dotenv import load_dotenv  
import tempfile  

load_dotenv()  

# Hugging Face API configuration  
HF_API_URL_WHISPER = "https://api-inference.huggingface.co/models/openai/whisper-tiny.en"  
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}  

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

def main():  
    st.title("AI Voice Assistant")  

    # Create an AI Assistant instance  
    assistant = AI_Assistant()  

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

if __name__ == "__main__":  
    main()
