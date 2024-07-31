import os
import requests
import streamlit as st
from io import BytesIO
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
from gtts import gTTS
import tempfile

load_dotenv()

# Hugging Face API configuration
HF_API_URL_WHISPER = "https://api-inference.huggingface.co/models/openai/whisper-tiny.en"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/v1/query"
GROQ_HEADERS = {"Authorization": f"Bearer {os.getenv('GROQ')}"}

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
def generate_ai_response(self, user_input):
    """Generate AI response using Groq API."""
    try:
        # Load context from file or initialize to an empty list
        if self.context_file is None:
            context = []
        else:
            with open(self.context_file.name, "r") as file:
                context = json.load(file) or []

        # Combine context with the current transcript
        messages = context + self.full_transcript

        # Generate AI response using Groq API
        chat_completion = self.groq_client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
            temperature=1,
            max_tokens=1024,
            top_p=1
        )
        
        # Extract the response
        ai_response = chat_completion.choices[0].message.content
        self.full_transcript.append({"role": "assistant", "content": ai_response})

        # Update context file with the new conversation history
        if self.context_file:
            with open(self.context_file.name, "w") as file:
                json.dump(messages + self.full_transcript, file)

        return ai_response

    except FileNotFoundError as e:
        st.error(f"File not found: {e}")
        return "Context file not found."
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return "Error processing context file."
    except AttributeError as e:
        st.error(f"Attribute error: {e}")
        return "Error with Groq API client or context file."
    except Exception as error:
        st.error(f"Unexpected error: {error}")
        return "An error occurred while generating a response."

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
        st.write("Audio data received. Processing...")
        
        # Convert the audio data to a byte stream
        audio_bytes = audio_data.getvalue() if hasattr(audio_data, 'getvalue') else audio_data

        # Display the audio
        st.audio(audio_bytes, format='audio/wav')

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
                st.write("Playing response...")
                st.audio(tts_file_path, format='audio/mp3')

if __name__ == "__main__":
    main()
