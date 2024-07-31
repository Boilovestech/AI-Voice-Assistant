import streamlit as st
import requests
import os
import tempfile
import json
import uuid
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
from groq import Groq
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()

# API Configurations
HF_API_URL_WHISPER = "https://api-inference.huggingface.co/models/openai/whisper-tiny.en"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

class AI_Assistant:
    def __init__(self):
        self.transcript = [
            {"role": "system", "content": "You are a tech nerd and concise, straight to the point. Your name is 'WonderAI' built by Boi loves code."},
        ]
        self.context_file = tempfile.NamedTemporaryFile(delete=False)
        self.groq_client = Groq(api_key=os.getenv("GROQ"))
        self.eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    def query_hf_api(self, audio_data):
        """Send audio data to Hugging Face API and return transcription."""
        try:
            response = requests.post(HF_API_URL_WHISPER, headers=HF_HEADERS, data=audio_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            st.error(f"Error with Hugging Face API: {error}")
            return {"text": ""}

    def generate_ai_response(self, user_input):
        """Generate AI response using Groq API."""
        try:
            with open(self.context_file.name, "r") as file:
                context = json.load(file) or []
            messages = context + self.transcript
            
            # Generate AI response
            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model="llama3-8b-8192",
                temperature=1,
                max_tokens=1024,
                top_p=1
            )
            ai_response = chat_completion.choices[0].message.content
            self.transcript.append({"role": "assistant", "content": ai_response})
            
            # Update context file
            with open(self.context_file.name, "w") as file:
                json.dump(messages + self.transcript, file)

            return ai_response
        except Exception as error:
            st.error(f"Error with Groq API: {error}")
            return ""

    def generate_and_play_tts(self, text):
        """Generate audio from text and play it."""
        try:
            # Calling the text_to_speech conversion API with detailed parameters
            response = self.eleven_client.text_to_speech.convert(
                voice_id="pNInz6obpgDQGcFmaJgB", # Adam pre-made voice
                optimize_streaming_latency="0",
                output_format="mp3_22050_32",
                text=text,
                model_id="eleven_turbo_v2_5", # use the turbo model for low latency
                voice_settings=VoiceSettings(
                    stability=0.0,
                    similarity_boost=1.0,
                    style=0.0,
                    use_speaker_boost=True,
                ),
            )

            # Generating a unique file name for the output MP3 file
            save_file_path = f"{uuid.uuid4()}.mp3"

            # Writing the audio to a file
            with open(save_file_path, "wb") as f:
                for chunk in response:
                    if chunk:
                        f.write(chunk)

            # Play the audio file
            os.system(f"mpg123 {save_file_path}")

            return save_file_path

        except Exception as error:
            st.error(f"Error generating and playing audio: {error}")

def main():
    st.title("AI Voice Assistant")
    ai_assistant = AI_Assistant()

    # Add custom CSS styles
    st.markdown("""
        <style>
        /* Include CSS styles for gradient text, animations, and layout */
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
            display: flex;   
            justify-content: center;   
            align-items: center;   
            border-radius: 25px;   
            height: 50px;   
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);   
            background-size: 400% 400%;   
            animation: gradient-text 15s ease infinite;   
        }
        .ai-response-box {   
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);   
            border-radius: 10px;   
            padding: 20px;   
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);   
        }
        </style>
        """, unsafe_allow_html=True)

    # Record audio input
    audio_data = audio_recorder()

    if st.button("Transcribe"):
        if audio_data is not None:
            st.success("Transcribing audio...")
            transcription_result = ai_assistant.query_hf_api(audio_data)
            transcription_text = transcription_result.get("text", "")
            st.session_state.user_input = transcription_text
            st.write(f"User: {transcription_text}")

            # Generate AI response
            st.write("Generating AI response...")
            ai_response = ai_assistant.generate_ai_response(transcription_text)
            st.write("AI: ", ai_response)

            # Generate and play audio for the AI response
            ai_assistant.generate_and_play_tts(ai_response)
        else:
            st.error("Please record audio before transcribing.")

    # Add UI elements as needed
    st.sidebar.title("Settings")
    st.sidebar.write("Adjust your preferences here.")
    # Additional settings can go here

if __name__ == "__main__":
    main()
