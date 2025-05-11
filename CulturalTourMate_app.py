import streamlit as st
import google.generativeai as genai
import dotenv
import os
from PIL import Image

# ========== 页面配置 ==========
st.set_page_config(page_title="🏛️Cultural-Tour-Mate🧧", layout="centered")

# ========== 加载 API Key ==========
dotenv.load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

# ========== 多语言支持 ==========
translations = {
    "en": {
        "title": "Cultural-Tour-Mate",
        "slogan": "Your trustworthy, insightful, and articulate cultural companion in tour.",
        "upload": "🖼️ Upload Image",
        "camera": "📷 Capture Photo",
        "camera_on": "📸 Take a shot",
        "camera_sub": "Any ultural troubles during the tour, please take a photo and ask me.",
        "desc": "Describe what you want to learn about the image:",
        "ask": "Send",
        "response": "Cultural Insight",
        "feedback": "Was this helpful? Feel free to ask more.",
        "developer": "Developer: Xianrong Liang (Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh.",
        "upload_note": "Select and upload an image from your device, image is limited 200M.",
        "camera_note": "Due to technical limitations, only the front camera is supported. Suggest upload photos.",
        "input_placeholder": "Type your question here..."
    },
    "zh": {
        "title": "AI文化旅伴",
        "slogan": "您诚实而智慧的旅行伙伴。",
        "upload": "🖼️ 上传图像",
        "camera": "📷 现场拍照",
        "camera_on": "📸 打开相机",
        "camera_sub": "旅途中的文化困扰，请随手拍一张照片问问我。",
        "desc": "描述您想了解的图像内容：",
        "ask": "发送",
        "response": "文化背景信息",
        "feedback": "这个回答有帮助吗？欢迎继续提问。",
        "developer": "开发者：梁羡荣(Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh",
        "upload_note": "从您的设备中选择并上传一张图片，大小不超过200M。",
        "camera_note": "由于技术限制，目前仅支持前置摄像头，建议上传照片。",
        "input_placeholder": "请输入您的问题..."
    }
}

# ========== 语言选择 ==========
language = st.selectbox("🌐 Select Language / 支持中文", ["English", "中文"])
lang_map = {"English": "en", "中文": "zh"}
lang_code = lang_map[language]
t = translations[lang_code]

# ========== Avatar 图像 ==========
avatar_urls = {
    "en": "https://static.vecteezy.com/system/resources/previews/055/495/027/non_2x/a-man-in-a-white-t-shirt-and-jeans-free-png.png",
    "zh": "https://static.vecteezy.com/system/resources/previews/013/167/583/original/portrait-of-a-smiling-asian-woman-cutout-file-png.png",
}

# ========== Avatar 背景样式 ==========
# Debugging the URL path first
avatar_url = avatar_urls.get(lang_code, '')  # Ensure it's not empty

# Add HTML and CSS
if avatar_url:  # Only apply if the URL is valid
    st.markdown(f"""
    <style>
    .avatar-bg {{
        position: fixed;
        bottom: 0px;
        left: 10px;
        height: 38.2vh;
        opacity: 0.5;
        z-index: 0;
    }}
    @media (max-width: 768px) {{
        .avatar-bg {{
            display: none;
        }}
    }}
    </style>
    <img class="avatar-bg" src="{avatar_url}" />
    """, unsafe_allow_html=True)

# ========== 标题与说明 ==========
st.title(t["title"])
st.markdown(t["slogan"])
st.caption(t["developer"])

# ========== 初始化会话 ==========
def fetch_conversation_history():
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "user",
                "parts": "system prompt: You are CulturalTourMate，a trustworthy, insightful, and articulate cultural companion. When a tourist uploads or captures an image of a landmark, artifact, or artwork, you provide engaging, accurate, and culturally rich information to deepen their understanding. You explain historical context, symbolism, artistic style, and local significance in a concise yet refined way. Your tone is friendly, professional, and easy to understand, empowering travelers to connect meaningfully with the cultures they encounter."
            }
        ]
    return st.session_state["messages"]

# ========== Gemini 回复 ==========
def generate_reply(messages, user_input, image_part=None):
    try:
        chat = genai.GenerativeModel("gemini-pro-vision").start_chat(history=messages)
        if image_part:
            response = chat.send_message([user_input, image_part])
        else:
            response = chat.send_message(user_input)
        return response
    except Exception as e:
        return str(e)

# ========== 上传与拍照（互斥选择） ==========
image_part = None
image = None

st.markdown("### " + t["camera"])
st.markdown(t["camera_sub"])
st.caption(t["camera_note"])

# ========== 控制相机是否显示 ============
if st.button(t["camera_on"]):  
    camera_image = st.camera_input("")
    if camera_image:
        image = Image.open(camera_image)
        image_part = {
            "mime_type": "image/jpeg",
            "data": camera_image.getvalue()
        }

st.markdown("---")
st.markdown("### " + t["upload"])
uploaded_image = st.file_uploader(t["upload_note"], type=["jpg", "jpeg", "png"])

# ========== 控制上传照片是否显示 ============
if uploaded_image:
    image = Image.open(uploaded_image)
    image_part = {
        "mime_type": "image/jpeg",
        "data": uploaded_image.getvalue()
    }

if image:
    st.image(image, caption="Selected Image", use_container_width=True)

# ========== 用户输入与发送按钮 ==========
st.markdown("---")
user_input = st.text_input("You:", placeholder=t["input_placeholder"], key="text_input")

if st.button(t["ask"]):  # =====添加发送按钮========
    if user_input:
        messages = fetch_conversation_history()
        messages.append({"role": "user", "parts": user_input})

        with st.spinner("Processing..."):
            response = generate_reply(messages, user_input, image_part)

        if isinstance(response, str):
            st.error(response)
        else:
            bot_reply = response.candidates[0].content.parts[0].text
            messages.append({"role": "model", "parts": bot_reply})
            st.session_state["messages"] = messages

# ========== 对话内容展示 ==========
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
