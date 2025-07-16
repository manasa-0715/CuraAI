# CuraAI 🩺 – Your AI-powered Medical & Emergency Assistant

**CuraAI** is an intelligent health assistant built with [Streamlit](https://streamlit.io/), [Gemini AI](https://deepmind.google/technologies/gemini/), and [Google Speech Recognition](https://pypi.org/project/SpeechRecognition/). It helps users get instant responses to medical questions and provides life-saving instructions in emergencies — via text or voice.

---

## 🚀 Features

- 💬 **Medical Chatbot**  
  Ask health-related questions and get instant, AI-generated responses.

- 🚑 **Emergency Assistant**  
  Describe critical situations and receive step-by-step emergency rescue instructions.

- 🎙️ **Voice Input Support**  
  Upload `.wav` files with spoken questions or emergencies and get them transcribed automatically.

- 🔊 **Text-to-Speech Output**  
  Answers are spoken aloud using gTTS, making the experience accessible and interactive.

- 🌐 **Multilingual Support**  
  Auto-translation capabilities are built-in using `googletrans`.

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) for UI
- [Google Gemini AI](https://deepmind.google/technologies/gemini/) via `google.generativeai`
- [Google Text-to-Speech (gTTS)](https://pypi.org/project/gTTS/)
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) for audio transcription
- [googletrans](https://pypi.org/project/googletrans/) for translation
- `langchain` PromptTemplate for formatted querying

---

## 📦 Installation

1. **Clone the Repository:**

```bash
git clone https://github.com/yourusername/CuraAI.git
cd CuraAI# CuraAI
