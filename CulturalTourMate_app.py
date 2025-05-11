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
        "send": "🦄 Send",
        "response": "Cultural Insight",
        "feedback": "Was this helpful? Feel free to ask more.",
        "developer": "Developer: Xianrong Liang (Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh.",
        "upload_note": "Select and upload an image from your device, the image is limited to 2 MB.",
        "camera_note": "Due to limitations, rear camera might not be accessible on tablets. Try phone or upload a photo.",
        "input_placeholder": "Type your question here...",
        "user_role": "💬 Ask anything",
        "progress": "⏳ Please wait while I analyze your question and image...",
        "response_title": "Cultural Insight",
        "response_loading": "🧠 Generating response...",
        "oversize_error": "🚫 Image exceeds 3MB limit. Please upload a smaller image.",
        "no_camera": "⚠️ No camera available on this device.",
        "photo_success": "✅ Photo captured successfully.",
        "photo_captured": "✅ Photo captured successfully.",
        "image_uploaded": "✅ Image uploaded successfully.",
        "photo_uploaded": "✅ Image uploaded successfully.",
        "api_error": "⚠️ Gemini API request failed. Check your network or API Key.",
        "text_unsendable": "⚠️ You have to upload a picture before asking a question."
    },
    "zh": {
        "title": "🏛️AI文化旅伴",
        "slogan": "您忠实博学且智慧的文化旅行小伴伙。",
        "upload": "🖼️ 上传图像",
        "camera": "📷 环境拍照",
        "camera_on": "📸 打开相机",
        "camera_sub": "旅途中的文化困扰，请随手拍一张照片问问我。",
        "desc": "描述您想了解的图像内容：",
        "send": "🦄 发送",
        "response": "文化背景信息",
        "feedback": "这个回答有帮助吗？欢迎继续提问。",
        "developer": "开发者：梁羡荣(Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh",
        "upload_note": "从您的设备中选择并上传一张图片，大小不超2M。",
        "camera_note": "由于技术限制，部分平板不支持后置摄像头，建议使用手机或上传照片。",
        "input_placeholder": "请输入您的问题...",
        "user_role": "💬 请您提问",
        "progress": "⏳ 请稍后，正在分析您的图像与问题...",
        "response_title": "深挖文化元素",
        "response_loading": "🧠 正在生成对话...",
        "oversize_error": "🚫 图像大小超3MB限制，请重新选择。",
        "no_camera": "⚠️ 当前设备无可用摄像头。",
        "photo_success": "✅ 拍照成功。",
        "photo_captured": "✅ 拍照成功。",
        "image_uploaded": "✅ 图片上传成功。",
        "photo_uploaded": "✅ 图片上传成功。",
        "api_error": "⚠️ Gemini API 链接失败. 请检查你的API密钥.",
        "text_unsendable": "⚠️ 发消息前请拍照或上传一张图片。"
    }
}

# =========== 选择语言 =========== 
language = st.selectbox("🌐 Language / 语言", ["English", "中文"])
lang_map = {"English": "en", "中文": "zh"}
lang_code = lang_map[language]
t = translations[lang_code]
st.session_state["lang_code"] = lang_code

# =========== Avatar URL =========== 
avatar_urls = {
    "en": "https://static.vecteezy.com/system/resources/previews/055/495/027/non_2x/a-man-in-a-white-t-shirt-and-jeans-free-png.png",
    "zh": "https://static.vecteezy.com/system/resources/previews/013/167/583/original/portrait-of-a-smiling-asian-woman-cutout-file-png.png",
}
avatar_url = avatar_urls.get(lang_code, '')

# =========== Avatar 背景样式 =========== 
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
    </style><img class="avatar-bg" src="{avatar_url}" />
    """, unsafe_allow_html=True)

# =========== 页面UI =========== 
st.title(t["title"])
st.markdown(t["slogan"])
st.caption(t["developer"])

# =============== 会话历史 ===============
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "user", "parts": "system prompt: You are CulturalTourMate, a helpful and culturally knowledgeable travel assistant..."}
    ]

# ============== 图像压缩处理 ===============
def compress_image(image, max_size=(800, 800), quality=80):
    image.thumbnail(max_size)
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()

# ================ 上传图像 & 拍照 ================
image_part = None  # 全局声明一次

# 摄像头说明区域
st.markdown("### " + t["camera"])
st.markdown(t["camera_sub"])
st.caption(t["camera_note"])

if "show_camera" not in st.session_state:
    st.session_state["show_camera"] = False

if st.button(t["camera_on"]):
    st.session_state["show_camera"] = True

if st.session_state["show_camera"]:
    camera_image = st.camera_input("camera_capture")
    if camera_image:
        if len(camera_image.getvalue()) > 3 * 1024 * 1024:
            st.warning(t["oversize_error"])
        else:
            image = Image.open(camera_image)
            compressed = compress_image(image)
            image_part = {"mime_type": "image/jpeg", "data": compressed}
            st.image(image, caption=t["photo_captured"], use_container_width=True)

# ================ 上传图像 ==================
st.markdown("---")
st.markdown("### " + t["upload"])
st.markdown(t["upload_note"])

uploaded_image = st.file_uploader(label="", type=["jpg", "jpeg", "png"])
if uploaded_image:
    if uploaded_image.size > 3 * 1024 * 1024:
        st.warning(t["oversize_error"])
    else:
        image = Image.open(uploaded_image)
        compressed = compress_image(image)
        st.image(image, caption=t["photo_uploaded"], use_container_width=True)
        image_part = {"mime_type": "image/jpeg", "data": compressed}

# ============== 提问函数 ===============
def generate_reply(messages, user_input, image_part=None):
    try:
        model = genai.GenerativeModel("gemini-pro-vision")
        chat = model.start_chat(history=messages)
        if image_part:
            response = chat.send_message([user_input, {"mime_type": image_part["mime_type"], "data": image_part["data"]}])
        else:
            response = chat.send_message(user_input)
        return response
    except Exception as e:
        import traceback
        st.error(t["api_error"])
        st.text_area("Error details", traceback.format_exc(), height=200)
        return str(e)

# ============== 提问发送 ===============
def submit_question():
    if not image_part:
        st.warning(t["text_unsendable"])
        return

    user_text = st.session_state.get("text_input", "").strip()
    if user_text:
        messages = st.session_state["messages"]
        messages.append({"role": "user", "parts": user_text})

        progress_text = t["progress"]
        my_bar = st.progress(0, text=progress_text)
        for percent_complete in range(1, 91):
            time.sleep(0.005)
            my_bar.progress(percent_complete, text=progress_text)

        with st.spinner(t["response_loading"]):
            response = generate_reply(messages, user_text, image_part)

        my_bar.progress(100, text="✅")

        if isinstance(response, str):
            st.error(response)
        else:
            bot_reply = response.candidates[0].content.parts[0].text
            messages.append({"role": "model", "parts": bot_reply})
            st.session_state["messages"] = messages
        st.session_state["text_input"] = ""

col1, col2 = st.columns([5, 1])
with col1:
    st.text_input(t["desc"], placeholder=t["input_placeholder"], key="text_input", on_change=submit_question)
with col2:
    st.markdown("<div style='height: 2em;'></div>", unsafe_allow_html=True)
    st.button(t["send"], on_click=submit_question)

# ========== 会话历史展示 ==========
st.markdown("---")
st.subheader("💬 Conversation History")
if "messages" in st.session_state:
    for message in st.session_state["messages"]:
        if "system prompt" in message["parts"]:
            continue
        if message["role"] == "user":
            st.markdown(
                f"<div style='text-align:right; padding: 8px 12px; background-color:#f5f5f5; border-radius:10px; margin-bottom:8px;'>{message['parts']}</div>",
                unsafe_allow_html=True
            )
        elif message["role"] == "model":
            st.markdown(
                f"<div style='text-align:left; padding: 8px 12px; background-color:#e8f5e9; border-radius:10px; margin-bottom:8px;'>{message['parts']}</div>",
                unsafe_allow_html=True
            )
