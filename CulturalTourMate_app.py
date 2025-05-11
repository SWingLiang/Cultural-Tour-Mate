import streamlit as st
import google.generativeai as genai
import dotenv
import os
import mimetypes
import time
from PIL import Image
from io import BytesIO

# ========== 页面配置 ==========
st.set_page_config(page_title="Cultural-Tour-Mate", layout="centered")

# ========== 加载 API Key ==========
dotenv.load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

# ========== 多语言支持 ==========
translations = {
    "en": {
        "title": "🏛️Cultural-Tour-Mate",
        "slogan": "Your trustworthy, insightful, and articulate cultural companion in tour.",
        "upload": "🖼️ Upload Image",
        "camera": "📷 Capture Photo",
        "camera_on": "📸 Take a shot",
        "camera_sub": "Any cultural troubles during the tour, please take a photo and ask me.",
        "desc": "Describe what you want to learn about the image:",
        "ask": "Send🦄",
        "response": "Cultural Insight",
        "feedback": "Was this helpful? Feel free to ask more.",
        "developer": "Developer: Xianrong Liang (Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh.",
        "upload_note": "Select and upload an image from your device, the image is limited to 2 MB.",
        "camera_note": "Due to limitations, rear camera might not be accessible on tablets. Try phone or upload a photo.",
        "input_placeholder": "Type your question here...",
        "user_role": "💬Ask anything",
        "oversize_error": "🚫 Image exceeds 3MB limit. Please upload a smaller image.",
        "no_camera": "⚠️ No camera available on this device.",
        "photo_success": "✅ Photo captured successfully."
    },
    "zh": {
        "title": "🏛️AI文化旅伴",
        "slogan": "您忠实博学且智慧的文化旅行小伙伴。",
        "upload": "🖼️ 上传图像",
        "camera": "📷 现场拍照",
        "camera_on": "📸 打开相机",
        "camera_sub": "旅途中的文化困扰，请随手拍一张照片问问我。",
        "desc": "描述您想了解的图像内容：",
        "ask": "发送🦄",
        "response": "文化背景信息",
        "feedback": "这个回答有帮助吗？欢迎继续提问。",
        "developer": "开发者：梁羡荣(Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh",
        "upload_note": "从您的设备中选择并上传一张图片，大小不超过2M。",
        "camera_note": "由于技术限制，部分平板不支持后置摄像头，建议使用手机或上传照片。",
        "input_placeholder": "请输入您的问题...",
        "user_role": "💬请您提问",
        "oversize_error": "🚫 图像大小超过3MB限制，请重新选择。",
        "no_camera": "⚠️ 当前设备无可用摄像头。",
        "photo_success": "✅ 拍照成功。"
    }
}

# ========== 语言选择 ==========
language = st.selectbox("🌐 Select Language EN/CN | 支持中英文", ["English", "中文"])
lang_map = {"English": "en", "中文": "zh"}
lang_code = lang_map[language]
t = translations[lang_code]

# ========== Avatar 图像 ==========
avatar_urls = {
    "en": "https://static.vecteezy.com/system/resources/previews/055/495/027/non_2x/a-man-in-a-white-t-shirt-and-jeans-free-png.png",
    "zh": "https://static.vecteezy.com/system/resources/previews/013/167/583/original/portrait-of-a-smiling-asian-woman-cutout-file-png.png",
}
avatar_url = avatar_urls.get(lang_code, '')

# ========== Avatar 背景样式 ==========
if avatar_url:
    st.markdown(f"""
    <style>
    .avatar-bg {{
        position: fixed;
        bottom: 0px;
        left: 10px;
        height: 45vh;
        opacity: 0.5;
        z-index: 0;
    }}
    @media (max-width: 768px) {{
        .avatar-bg {{
            display: none;
        }}
    }}
    .stFileUploader label {{
        display: none !important;
    }}
    .stFileUploader button {{
        background-color: #f0f0f0 !important;
        font-size: 20px !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        padding: 0 !important;
    }}
    </style>
    <img class="avatar-bg" src="{avatar_url}" />
    """, unsafe_allow_html=True)

# ========== 标题与说明 ==========
st.title(t["title"])
st.markdown(t["slogan"])
st.caption(t["developer"])

# ========== 会话初始化 ==========
def fetch_conversation_history():
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "user",
                "parts": "system prompt: You are CulturalTourMate..."
            }
        ]
    return st.session_state["messages"]

# ========== Gemini 回复 ==========
def generate_reply(messages, user_input, image_part=None):
    try:
        model = genai.GenerativeModel("gemini-pro-vision")
        chat = model.start_chat(history=messages)
        if image_part:
            response = chat.send_message([
                user_input,
                {
                    "mime_type": image_part["mime_type"],
                    "data": image_part["data"]
                }
            ])
        else:
            response = chat.send_message(user_input)
        return response
    except Exception as e:
        import traceback
        st.error("⚠️ Gemini API request failed. Check your network or API Key.")
        st.text_area("Error details", traceback.format_exc(), height=200)
        return str(e)

# ========== 图片压缩函数 ==========
def compress_image(image, max_size=(1000, 1000), quality=80):
    image.thumbnail(max_size)
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()

# ========== 拍照与上传 ==========
image = None
image_part = None

st.markdown("### " + t["camera"])
st.markdown(t["camera_sub"])
st.caption(t["camera_note"])

camera_image = st.camera_input("")
if camera_image:
    if len(camera_image.getvalue()) > 3 * 1024 * 1024:
        st.warning(t["oversize_error"])
    else:
        image = Image.open(camera_image)
        compressed = compress_image(image)
        st.image(image, caption=t["photo_success"], use_container_width=True)
        image_part = {
            "mime_type": "image/jpeg",
            "data": compressed
        }

st.markdown("---")
st.markdown("### " + t["upload"])

uploaded_image = st.file_uploader(t["upload_note"], type=["jpg", "jpeg", "png"])
if uploaded_image:
    if uploaded_image.size > 3 * 1024 * 1024:
        st.warning(t["oversize_error"])
    else:
        image = Image.open(uploaded_image)
        compressed = compress_image(image)
        st.image(image, caption="Selected Image", use_container_width=True)
        mime_type, _ = mimetypes.guess_type(uploaded_image.name)
        image_part = {
            "mime_type": mime_type or "image/jpeg",
            "data": compressed
        }

# ========== 用户提问 ==========
st.markdown("---")
st.markdown("### " + t["user_role"])

def submit_question():
    if st.session_state["text_input"]:
        messages = fetch_conversation_history()
        messages.append({"role": "user", "parts": st.session_state["text_input"]})

        progress_text = "⏳ Please wait while I analyze your question and image..."
        my_bar = st.progress(0, text=progress_text)
        for percent_complete in range(1, 91):
            time.sleep(0.02)
            my_bar.progress(percent_complete, text=progress_text)

        with st.spinner("🧠 Generating response..."):
            response = generate_reply(messages, st.session_state["text_input"], image_part)

        my_bar.progress(100, text="✅ Done!")

        if isinstance(response, str):
            st.error(response)
        else:
            bot_reply = response.candidates[0].content.parts[0].text
            messages.append({"role": "model", "parts": bot_reply})
            st.session_state["messages"] = messages
        st.session_state["text_input"] = ""

st.text_input(" ", placeholder=t["input_placeholder"], key="text_input", on_change=submit_question)

if st.button(t["ask"]):
    submit_question()

# ========== 对话历史 ==========
st.markdown("---")
st.subheader("🗨️ Conversation History")

if "messages" in st.session_state:
    for message in st.session_state["messages"]:
        if "system prompt" in message["parts"]:
            continue
        if message["role"] == "user":
            st.markdown(
                f"<div style='text-align:right; padding: 8px 12px; background-color:#e6f7ff; border-radius:10px; margin-bottom:8px;'>{message['parts']}</div>",
                unsafe_allow_html=True
            )
        elif message["role"] == "model":
            st.markdown(
                f"<div style='display:flex; align-items:center; margin-bottom:8px;'><img src='{avatar_urls[lang_code]}' width='40' style='margin-right:10px;'><div style='background-color:#f5f5f5; padding:8px 12px; border-radius:10px;'>{message['parts']}</div></div>",
                unsafe_allow_html=True
            )
