# Cultural-Tour-Mate with Voice Input/Output

import streamlit as st
import google.generativeai as genai
import PIL.Image
import io
import time
import base64
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment

# Page Config
st.set_page_config(page_title="Cultural Tour Mate", layout="wide")

# Language Selector
lang = st.sidebar.radio("Language / \u8bed\u8a00", ("English", "\u4e2d\u6587"))
lang_code = "zh" if lang == "\u4e2d\u6587" else "en"

# Translations
translations = {
    "zh": {
        "title": "\u6587\u5316\u65c5\u884c\u5e2e\u624b",
        "upload_image": "\u4e0a\u4f20\u4e00\u5f20\u60a8\u5728\u65c5\u884c\u4e2d\u7684\u7167\u7247\uff1a",
        "ask_question": "\u8bf7\u5728\u4e0b\u9762\u8f93\u5165\u95ee\u9898\uff0c\u6216\u63d0\u4f9b\u60a8\u5bf9\u7167\u7247\u7684\u7591\u95ee\u6216\u597d\u5947\uff1a",
        "submit_button": "\u63d0\u4ea4\u95ee\u9898",
        "user_role": "\u7528\u6237",
        "model_role": "\u6a21\u578b",
        "response_title": "\u6a21\u578b\u56de\u590d\uff1a",
        "camera_button": "\u7528\u6444\u50cf\u5934\u62cd\u7167",
    },
    "en": {
        "title": "Cultural Tour Mate",
        "upload_image": "Upload a photo from your trip:",
        "ask_question": "Enter your question or curiosity about the image below:",
        "submit_button": "Submit",
        "user_role": "User",
        "model_role": "Model",
        "response_title": "Response:",
        "camera_button": "Take a photo with webcam",
    }
}
t = translations[lang_code]

# Gemini API Config
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')

# Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "parts": "You are CulturalTourMate, a culturally knowledgeable AI that helps tourists understand and explore local customs, heritage, and visual culture from photos."}
    ]
if "image_part" not in st.session_state:
    st.session_state["image_part"] = None

# Image Upload
st.markdown(f"## {t['title']}")
image_file = st.file_uploader(t["upload_image"], type=["jpg", "jpeg", "png", "webp"])

if image_file:
    image = PIL.Image.open(image_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    with io.BytesIO() as output:
        image.save(output, format="JPEG")
        compressed = output.getvalue()
    st.session_state["image_part"] = {"mime_type": "image/jpeg", "data": compressed}

# Voice Input
st.markdown("---")
st.markdown("### 🎙️ Voice Input (语音输入)")
audio_file = st.file_uploader("Upload a voice message (mp3/wav)", type=["mp3", "wav"])
if audio_file:
    st.audio(audio_file)
    recognizer = sr.Recognizer()
    audio_path = f"/tmp/{audio_file.name}"
    with open(audio_path, "wb") as f:
        f.write(audio_file.read())
    if audio_file.name.endswith(".mp3"):
        sound = AudioSegment.from_mp3(audio_path)
        wav_path = audio_path.replace(".mp3", ".wav")
        sound.export(wav_path, format="wav")
        audio_path = wav_path
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            recognized_text = recognizer.recognize_google(audio_data, language="zh-CN" if lang_code == "zh" else "en-US")
            st.success("📝 " + t["user_role"] + ": " + recognized_text)
            prompt = recognized_text
        except Exception as e:
            st.error(f"❌ Could not recognize audio: {e}")
else:
    prompt = st.text_area(t["ask_question"], height=100)

# Response
enable_speech = st.checkbox("🔊 Read aloud the response", value=True)
if st.button(t["submit_button"]):
    if not prompt:
        st.warning("Please enter a question.")
    elif not st.session_state["image_part"]:
        st.warning("Please upload an image first.")
    else:
        with st.spinner("Generating response..."):
            st.session_state["messages"].append({"role": "user", "parts": [prompt, st.session_state["image_part"]]})
            try:
                response = model.generate_content(st.session_state["messages"])
                st.session_state["messages"].append({"role": "model", "parts": [response.text]})
                st.markdown("#### " + t["response_title"])
                st.write(response.text)
                if enable_speech:
                    tts = gTTS(text=response.text, lang="zh" if lang_code == "zh" else "en")
                    mp3_fp = f"/tmp/response_audio_{int(time.time())}.mp3"
                    tts.save(mp3_fp)
                    st.audio(mp3_fp, format="audio/mp3")
            except Exception as e:
                st.error(f"❌ Failed to generate response: {e}")

# Chat History
st.markdown("---")
st.markdown("### 📜 Chat History")
for msg in st.session_state["messages"]:
    if msg["role"] in ["user", "model"]:
        speaker = t["user_role"] if msg["role"] == "user" else t["model_role"]
        st.markdown(f"**{speaker}:** {msg['parts'][0]}")
