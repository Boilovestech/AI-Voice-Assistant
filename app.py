import streamlit as st  
import requests  
import os  
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
HF_API_URL_WHISPER = "https://api-inference.huggingface.co/models/openai/whisper-tiny.en"  
HF_API_URL_TTS = "https://api-inference.huggingface.co/models/facebook/tts_transformer"  # Change to a valid TTS model URL  
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}  

class AI_Assistant:  
    def __init__(self):  
        self.reset_conversation()  
        self.context_file = tempfile.NamedTemporaryFile(delete=False)  
        self.groq_client = Groq(  
            api_key=os.getenv("GROQ")  
        )  

    def reset_conversation(self):  
        self.full_transcript = [  
            {"role": "system", "content": "You are a tech nerd and concise and straight to the point kind of person. Your name is 'WonderAI', built by Boi loves code."},  
        ]  
    
    def query_hf_api(self, audio_data):  
        """Query the Hugging Face Whisper API for transcription."""  
        try:  
            response = requests.post(HF_API_URL_WHISPER, headers=HF_HEADERS, data=audio_data)  
            response.raise_for_status()  
            return response.json()  
        except requests.exceptions.RequestException as e:  
            st.error(f"Error with Hugging Face API: {e}")  
            return {"text": ""}  

    def query_tts_api(self, text):  
        """Query a TTS model from Hugging Face API."""  
        try:  
            response = requests.post(HF_API_URL_TTS, headers=HF_HEADERS, json={"text": text})  
            response.raise_for_status()  
            audio_data = response.content  
            return audio_data  
        except requests.exceptions.RequestException as e:  
            st.error(f"Error with Hugging Face TTS API: {e}")  
            return BytesIO()  

    def generate_ai_response(self, user_input):  
        try:  
            with open(self.context_file.name, "r") as f:  
                try:  
                    context = json.load(f)  
                except json.JSONDecodeError:  
                    context = []  
            chat_completion = self.groq_client.chat.completions.create(  
                messages=context + self.full_transcript,  
                model="llama3-8b-8192",  
                temperature=1,  
                max_tokens=1024,  
                top_p=1  
            )  
            ai_response = chat_completion.choices[0].message.content  
            self.full_transcript.append({"role": "assistant", "content": ai_response})  
            conversation_history = context + self.full_transcript  
            with open(self.context_file.name, "w") as f:  
                json.dump(conversation_history, f)  
            return ai_response  
        except Exception as e:  
            st.error(f"Error with Groq API: {e}")  
            return ""  

def autoplay_audio(file):  
    audio_base64 = base64.b64encode(file).decode('utf-8')  
    audio_tag = f'<audio id="tts-audio" autoplay><source src="data:audio/wav;base64,{audio_base64}" type="audio/wav"></audio>'  
    st.markdown(audio_tag, unsafe_allow_html=True)  

def main():  
    st.title("AI Assistant with Voice Interaction")  

    assistant = AI_Assistant()  
    
    # Audio recording  
    st.write("Press the button and dictate your question:")  
    audio_data = audio_recorder()  

    if audio_data is not None:  
        audio_bytes = audio_data.get_wav_data()  # Get raw audio bytes  
        transcription_result = assistant.query_hf_api(audio_bytes)  # Transcribe the audio  
        user_input = transcription_result.get("text", "").strip()  # Extract text  
        
        if user_input:  
            st.write(f"You said: {user_input}")  
            # Generate AI response  
            ai_response = assistant.generate_ai_response(user_input)  
            st.write(f"AI response: {ai_response}")  
            
            # Convert AI response to speech  
            tts_audio_data = assistant.query_tts_api(ai_response)  
            
            if tts_audio_data:  
                autoplay_audio(tts_audio_data)  # Play the TTS audio  

    # Clean up and disconnect  
    if os.path.exists(assistant.context_file.name):  
        os.unlink(assistant.context_file.name)  

if __name__ == "__main__":  
    main()
