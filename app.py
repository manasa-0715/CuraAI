import os
import time
import streamlit as st
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from googletrans import Translator
import speech_recognition as sr
from gtts import gTTS
from IPython.display import Audio
from pydub import AudioSegment
import urllib.request
import uuid
import re

PDF_PATH = "Gale Encyclopedia of Medicine.pdf"
PDF_URL = "https://staibabussalamsula.ac.id/wp-content/uploads/2024/06/The-Gale-Encyclopedia-of-Medicine-3rd-Edition-staibabussalamsula.ac_.id_.pdf"

if not os.path.exists(PDF_PATH):
    try:
        urllib.request.urlretrieve(PDF_URL, PDF_PATH)
    except Exception as e:
        pass


# Configure Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])  # Replace with your Gemini API key

# Prompt Templates
qa_prompt_template = """
Use the following medical context to answer the user's question.
If you don't know the answer, say: "I'm not sure about that, please consult a professional."

Context:
- High blood pressure can lead to strokes and heart failure.
- A fever above 104°F (40°C) in adults may require emergency care.
- CPR is used during cardiac arrest.

Question: {question}

Helpful answer:
"""

emergency_prompt_template = """
You are an emergency response assistant. Use the following facts to help the user.

Context:
- Call emergency services immediately for chest pain or unconsciousness.
- Apply pressure to stop bleeding.
- For choking, use the Heimlich maneuver if trained.
- For burns, use cool running water.

Emergency Situation: {question}

Step-by-step rescue instructions:
"""

# Utility Functions
def translate_text(text, lang):
    return Translator().translate(text, dest=lang).text

def truncate_text(text, max_tokens=512):
    tokens = text.split()
    return ' '.join(tokens[:max_tokens]) if len(tokens) > max_tokens else text

def set_custom_prompt(template):
    return PromptTemplate(template=template, input_variables=["question"])

# Gemini-powered QA Bot
def qa_bot():
    prompt = set_custom_prompt(qa_prompt_template)
    def ask(query):
        full_prompt = prompt.format(question=query)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(full_prompt)
        return response.text.strip()
    return ask

# Gemini-powered Emergency Bot
def emergency_bot():
    prompt = set_custom_prompt(emergency_prompt_template)
    def ask(query):
        full_prompt = prompt.format(question=query)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(full_prompt)
        return response.text.strip()
    return ask

def speak_text(text):
    try:
        import tempfile
        from pydub import AudioSegment

        # Clean the text
        text = text.replace('\x00', '')
        clean_text = ''.join(c for c in text if c.isprintable())
        clean_text = clean_text.replace('\n', ' ').replace('\r', ' ')
        clean_text = re.sub(r'\s+', ' ', clean_text)
        clean_text = re.sub(r'[^\x00-\x7F]+', '', clean_text)
        clean_text = re.sub(r'[^\w\s.,?!]', '', clean_text)

        if not clean_text.strip():
            clean_text = "Sorry, the response could not be read aloud."

        # Split into smaller chunks (~100 words max)
        sentences = re.split(r'(?<=[.?!])\s+', clean_text)
        chunks = []
        chunk = ""

        for sentence in sentences:
            if len(chunk + sentence) < 400:
                chunk += sentence + " "
            else:
                chunks.append(chunk.strip())
                chunk = sentence + " "
        if chunk:
            chunks.append(chunk.strip())

        # Generate audio for each chunk and merge
        combined = AudioSegment.empty()
        for i, part in enumerate(chunks):
            tts = gTTS(text=part, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_path = temp_file.name
                tts.save(temp_path)
                segment = AudioSegment.from_mp3(temp_path)
                combined += segment
                os.remove(temp_path)

        # Save final audio
        output_file = "response.mp3"
        if os.path.exists(output_file):
            os.remove(output_file)
        combined.export(output_file, format="mp3")

        # Play it
        st.audio(output_file, format="audio/mp3")

    except Exception as e:
        st.error(f"TTS failed: {e}")

# UI Pages
def show_home():
    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='font-size: 50px; margin-bottom: 0px;'>
                <span style="color:#4CAF50;">Cura</span><span style="color:#F36F6F;">AI</span>
            </h1>
            <p style='font-size: 18px; margin-top: 5px;'>Your intelligent companion for health advice and emergency care.<br>
            Because every second counts, and every question matters.</p>
        </div>

        <hr style="margin-top: 30px; margin-bottom: 20px;">

        <div style='font-size: 20px;'>
            <p> <b>WHAT CuraAI OFFERS </b></p>
            <p>💬 <b>Medical Chatbot:</b> Ask anything health-related and get AI-powered responses instantly.</p>
            <p>🚑 <b>Emergency Assistant:</b> Describe a critical situation and receive step-by-step rescue guidance.</p>
        </div>

        <div style='margin-top: 30px; font-size: 18px;'>
            <p><b>WHY USE CuraAI ? </b></p>
            <p>📚 Built on real medical knowledge from trusted sources.</p>
            <p>⚡ Fast and available anytime.</p>
            <p>❤️ Supports life-saving decisions in emergencies.</p>
        </div>

        <br><br>
        <div style='text-align:center; font-size: 13px; color: grey;'>
            🩺 Powered by Gemini | Developed by Team 404 team not found
        </div>
    """, unsafe_allow_html=True)

def show_chatbot():
    st.title("Medical Chatbot")
    input_method = st.radio("Choose input method:", ["Type", "Upload Audio File"])
    user_input = ""

    if input_method == "Type":
        user_input = st.text_input("Ask a medical question")
    else:
        uploaded_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a"])
        if uploaded_file is not None:
            recognizer = sr.Recognizer()
            with open("temp_audio_input", "wb") as f:
                f.write(uploaded_file.getbuffer())
            audio = AudioSegment.from_file("temp_audio_input")
            audio.export("temp_audio.wav", format="wav")
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = recognizer.record(source)
                try:
                    user_input = recognizer.recognize_google(audio_data)
                    st.success(f"You said: {user_input}")
                except Exception as e:
                    st.error(f"Speech recognition failed: {e}")

    if user_input and st.button("Ask"):
        answer = qa_bot()(truncate_text(user_input))
        st.success(answer)
        speak_text(answer)

        # Clean up temp audio files after use
        if os.path.exists("temp_audio.wav"):
            os.remove("temp_audio.wav")
        if os.path.exists("temp_audio_input"):
            os.remove("temp_audio_input")




def show_emergency():
    st.title("Emergency Assistant")
    input_method = st.radio("Choose input method:", ["Type", "Upload Audio File"])
    emergency_input = ""

    if input_method == "Type":
        emergency_input = st.text_input("Describe the emergency")
    else:
        uploaded_file = st.file_uploader("Upload emergency description audio", type=["wav", "mp3", "m4a"])
        if uploaded_file is not None:
            recognizer = sr.Recognizer()
            with open("temp_audio_input", "wb") as f:
                f.write(uploaded_file.getbuffer())
            audio = AudioSegment.from_file("temp_audio_input")
            audio.export("temp_audio.wav", format="wav")
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = recognizer.record(source)
                try:
                    emergency_input = recognizer.recognize_google(audio_data)
                    st.success(f"You said: {emergency_input}")
                except Exception as e:
                    st.error(f"Speech recognition failed: {e}")

    if emergency_input and st.button("Get Instructions"):
        answer = emergency_bot()(truncate_text(emergency_input))
        st.warning(answer)
        speak_text(answer)

        # Clean up temp audio files
        if os.path.exists("temp_audio.wav"):
            os.remove("temp_audio.wav")
        if os.path.exists("temp_audio_input"):
            os.remove("temp_audio_input")

# Main
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Medical Chatbot", "Emergency Assistant"])

    if page == "Home":
        show_home()
    elif page == "Medical Chatbot":
        show_chatbot()
    elif page == "Emergency Assistant":
        show_emergency()

if __name__ == '__main__':
    main()
