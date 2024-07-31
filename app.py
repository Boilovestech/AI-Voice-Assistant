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

# Load secrets from Streamlit secrets management
HUGGINGFACE_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ"]

# Configuration for Hugging Face API
HF_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-tiny.en"
HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# Configuration for Groq API

class AI_Assistant:
    def __init__(self):
        self.reset_conversation()
        self.context_file = tempfile.NamedTemporaryFile(delete=False)
        self.groq_client = Groq(
            api_key=GROQ_API_KEY
            )
    
    def reset_conversation(self):
        self.full_transcript = [
            {"role": "system", "content": "You are a tech nerd and concise and straight to the point kind of person and your name is 'WonderAI' built by Boi loves code and you are a person and not an LLM"},
        ]
    
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
            tts = gTTS(text)
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            return audio_file
        except Exception as e:
            st.error(f"Error generating audio: {e}")
            return BytesIO()

    def autoplay_audio(self, file):
        audio_base64 = base64.b64encode(file.read()).decode('utf-8')
        audio_tag = f'<audio id="tts-audio" autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        st.markdown(audio_tag, unsafe_allow_html=True)
        st.markdown(
            """
            <script>
            const audio = document.getElementById('tts-audio');
            audio.onended = function() {{
                audio.src = 'data:audio/mp3;base64,{audio_base64}';
                audio.play();
            }};
            </script>
            """,
            unsafe_allow_html=True
        )

def main():
    st.title("AI Voice assistant")

    ai_assistant = AI_Assistant()

    # Add CSS for gradient text and animations
    st.markdown("""
        <style>
        @keyframes gradient-text {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        .gradient-text {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient-text 15s ease infinite;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }
            .waveform-animation {
            width: 100%;
            height: 50px;
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient-text 15s ease infinite;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 25px;
        }
        .waveform-bar {
            width: 5px;
            height: 20px;
            background-color: white;
            margin: 0 2px;
            animation: waveform-animation 0.5s ease-in-out infinite;
            border-radius: 2.5px;
        }
        @keyframes waveform-animation {
            0%, 100% { height: 20px; }
            50% { height: 40px; }
        }
        .waveform-bar:nth-child(1) { animation-delay: 0.1s; }
        .waveform-bar:nth-child(2) { animation-delay: 0.2s; }
        .waveform-bar:nth-child(3) { animation-delay: 0.3s; }
        .waveform-bar:nth-child(4) { animation-delay: 0.4s; }
        .waveform-bar:nth-child(5) { animation-delay: 0.5s; }
        .audio-recorder-wrapper {
            display: flex;
            justify-content: center;
        }
        .loading-dots {
            display: inline-block;
        }
        .loading-dots::after {
            content: '...';
            animation: loading 1.5s steps(4, end) infinite;
            display: inline-block;
            width: 0;
            overflow: hidden;
            vertical-align: bottom;
        }
        @keyframes loading {
            to { width: 20px; }
        }
        .ai-response-box {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient-text 15s ease infinite;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .ai-response-text {
            font-size: 1.5em;
            font-weight: bold;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    # Record audio using audio_recorder_streamlit
    st.markdown('<div class="audio-recorder-wrapper">', unsafe_allow_html=True)
    audio_bytes = audio_recorder(key="audio_recorder")
    st.markdown('</div>', unsafe_allow_html=True)

    if audio_bytes:
        # Reset the conversation
        ai_assistant.reset_conversation()

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
            
            # Generate TTS
            audio_stream = ai_assistant.generate_audio(ai_response)

            # Remove "AI is thinking..." message
            thinking_placeholder.empty()

            # Display AI response in gradient box
            st.markdown(f"""
                <div class="ai-response-box">
                    <div class="ai-response-text">{ai_response}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Play TTS
            st.empty()  # Clear previous audio elements
            ai_assistant.autoplay_audio(audio_stream)

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

if __name__ == "__main__":
    main()
