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

load_dotenv()

# Configuration for Hugging Face API
HF_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-tiny.en"
HF_HEADERS = {"Authorization": f"Bearer {st.secrets['HUGGINGFACE_API_KEY']}"}

# Configuration for Groq API
class AI_Assistant:
    def __init__(self):
        self.full_transcript = [
            {
                "role": "system",
                "content": "You are a tech nerd and concise and straight to the point kind of person and your name is 'WonderAI' built by Boi loves code and you are a person and not an LLM"
            },
        ]
        self.context_file = tempfile.NamedTemporaryFile(delete=False)
        self.groq_client = Groq(api_key=st.secrets["GROQ"])

    def query_hf_api(self, audio_data):
        try:
            response = requests.post(HF_API_URL, headers=HF_HEADERS, data=audio_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error with Hugging Face API: {e}")
            return {"text": ""}

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

    def generate_audio(self, text):
        try:
            tts = gTTS(text, lang='en')
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            return audio_file
        except Exception as e:
            st.error(f"Error generating audio: {e}")
            return BytesIO()

def autoplay_audio(file):
    audio_base64 = base64.b64encode(file.read()).decode('utf-8')
    audio_tag = f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg"></audio>'
    st.markdown(audio_tag, unsafe_allow_html=True)

def main():
    st.title("AI Voice assistant")
    ai_assistant = AI_Assistant()

    # Add CSS for gradient text and animations
    st.markdown("""
        <style>
            .gradient-text {
                background: linear-gradient(90deg, #FF5733, #FFC300);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
        </style>
    """, unsafe_allow_html=True)

    # Record audio using audio_recorder_streamlit
    audio_data = audio_recorder()

    if audio_data:
        # Process the audio data to get text
        transcription = ai_assistant.query_hf_api(audio_data)
        user_input = transcription.get("text", "")

        # Generate AI response based on user input
        ai_response = ai_assistant.generate_ai_response(user_input)

        # Generate audio from AI response
        audio_file = ai_assistant.generate_audio(ai_response)

        # Play the audio
        autoplay_audio(audio_file)

if __name__ == "__main__":
    main()
