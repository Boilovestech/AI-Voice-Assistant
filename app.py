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
import uuid

# ... (previous code remains the same)

class AI_Assistant:
    # ... (previous methods remain the same)

    def generate_audio(self, text):
        try:
            tts = gTTS(text)
            audio_file = BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)
            st.write(f"Debug: Audio file size: {len(audio_file.getvalue())} bytes")  # Debug information
            return audio_file
        except Exception as e:
            st.error(f"Error generating audio: {e}")
            return BytesIO()

def autoplay_audio(file):
    audio_key = str(uuid.uuid4())
    audio_base64 = base64.b64encode(file.read()).decode('utf-8')
    audio_tag = f'<audio id="tts-audio-{audio_key}" preload="auto"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    st.markdown(audio_tag, unsafe_allow_html=True)
    return audio_key

def main():
    # ... (previous code remains the same)

    if audio_bytes:
        # ... (previous code remains the same)

        if user_text:
            # ... (previous code remains the same)

            # Generate TTS
            audio_stream = ai_assistant.generate_audio(ai_response)

            # Play TTS
            audio_key = autoplay_audio(audio_stream)

            # Increment the conversation turn
            st.session_state.conversation_turn += 1

            # Show waveform animation and play audio
            waveform_placeholder = st.empty()
            waveform_placeholder.markdown(f"""
                <div id="waveform-{audio_key}" class="waveform-animation">
                    <div class="waveform-bar"></div>
                    <div class="waveform-bar"></div>
                    <div class="waveform-bar"></div>
                    <div class="waveform-bar"></div>
                    <div class="waveform-bar"></div>
                </div>
                <script>
                    var audio = document.getElementById('tts-audio-{audio_key}');
                    var waveform = document.getElementById('waveform-{audio_key}');
                    
                    function playAudio() {{
                        audio.play().then(() => {{
                            console.log('Audio playback started');
                        }}).catch(error => {{
                            console.error('Audio playback failed:', error);
                        }});
                    }}
                    
                    audio.onended = function() {{
                        waveform.style.display = 'none';
                        console.log('Audio playback ended');
                    }};
                    
                    // Attempt to play audio immediately
                    playAudio();
                    
                    // If immediate playback fails, add a button to trigger playback
                    if (audio.paused) {{
                        var playButton = document.createElement('button');
                        playButton.innerHTML = 'Play Response';
                        playButton.onclick = playAudio;
                        document.body.appendChild(playButton);
                    }}
                </script>
            """, unsafe_allow_html=True)

            # Debug information
            st.write(f"Debug: Conversation turn {st.session_state.conversation_turn}")
            st.write(f"Debug: Audio key {audio_key}")
            st.write("Debug: Check browser console for additional logs")

if __name__ == "__main__":
    main()
