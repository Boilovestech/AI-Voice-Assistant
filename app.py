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

# Hugging Face API configuration  
HF_API_URL_WHISPER = "https://api-inference.huggingface.co/models/openai/whisper-tiny.en"  
HF_API_URL_TTS = "https://api-inference.huggingface.co/models/facebook/tts_transformer"  # Update with a valid TTS model URL  
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}  

class AI_Assistant:  
    def __init__(self):  
        self.reset_conversation()  
        self.context_file = tempfile.NamedTemporaryFile(delete=False)  
        self.groq_client = Groq(api_key=os.getenv("GROQ"))  

    def reset_conversation(self):  
        self.full_transcript = [  
            {"role": "system", "content": "You are a tech nerd, concise and to the point. Your name is 'WonderAI', created by Boi loves code."},  
        ]  
    
    def query_hf_api(self, audio_data):  
        """Send audio data to the Hugging Face Whisper API for transcription."""  
        try:  
            response = requests.post(HF_API_URL_WHISPER, headers=HF_HEADERS, data=audio_data)
