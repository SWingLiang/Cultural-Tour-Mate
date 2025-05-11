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
        "send": "🧤 Send",
        "response": "Cultural Insight",
        "feedback": "Was this helpful? Feel free to ask more.",
        "developer": "Developer: Xianrong Liang (Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh.",
        "upload_note": "Select and upload an image from your device, the image is limited to 2 MB.",
        "camera_note": "Due to limitations, rear camera might not be accessible on tablets. Try phone or upload a photo.",
        "input_placeholder": "Type your question here...",
        "user_role": "💬 Ask anything",
        "oversize_error": "🚫 Image exceeds 3MB limit. Please upload a smaller image.",
        "no_camera": "⚠️ No camera available on this device.",
        "photo_success": "✅ Photo captured successfully."
    },
    "zh": {
        "title": "🏛️AI文化旅伴",
        "slogan": "您忠实博学且智慧的文化旅行小伙伴。",
        "upload": "🖼️ 上传图像",
        "camera": "📷 环境拍照",
        "camera_on": "📸 打开相机",
        "camera_sub": "旅途中的文化困扰，请随手拍一张照片问问我。",
        "desc": "描述您想了解的图像内容：",
        "send": "🧤 发送",
        "response": "文化背景信息",
        "feedback": "这个回答有帮助吗？欢迎继续提问。",
        "developer": "开发者：梁贤荣(Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh",
        "upload_note": "从您的设备中选择并上传一张图片，大小不超2M。",
        "camera_note": "由于技术限制，部分平板不支持后置摄像头，建议使用手机或上传照片。",
        "input_placeholder": "请输入您的问题...",
        "user_role": "💬 请您提问",
        "oversize_error": "🚫 图像大小超过3MB限制，请重新选择。",
        "no_camera": "⚠️ 当前设备无可用摄像头。",
        "photo_success": "✅ 拍照成功。"
    }
}

# 选择语言
language = st.selectbox("🌐 Select Language EN/CN | 支持中英文", ["English", "中文"])
lang_map = {"English": "en", "中文": "zh"}
lang_code = lang_map[language]
t = translations[lang_code]

# 头像展示
avatar_urls = {
    "en": "https://static.vecteezy.com/system/resources/previews/055/495/027/non_2x/a-man-in-a-white-t-shirt-and-jeans-free-png.png",
    "zh": "https://static.vecteezy.com/system/resources/previews/013/167/583/original/portrait-of-a-smiling-asian-woman-cutout-file-png.png",
}
avatar_url = avatar_urls.get(lang_code, '')

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

st.title(t["title"])
st.markdown(t["slogan"])
st.caption(t["developer"])

# 会话历史
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "user", "parts": "system prompt: You are CulturalTourMate, a helpful and culturally knowledgeable travel assistant..."}
    ]

# 图像压缩处理
def compress_image(image, max_size=(800, 800), quality=80):
    image.thumbnail(max_size)
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()

# 上传图像 & 拍照
image = None
image_part = None

st.markdown("### " + t["camera"])
st.markdown(t["camera_sub"])
st.caption(t["camera_note"])

show_camera = st.button(t["camera_on"])
if show_camera:
    camera_image = st.camera_input("")
    if camera_image:
        if len(camera_image.getvalue()) > 3 * 1024 * 1024:
            st.warning(t["oversize_error"])
        else:
            image = Image.open(camera_image)
            compressed = compress_image(image)
            st.image(image, caption=t["photo_success"], use_container_width=True)
            image_part = {"mime_type": "image/jpeg", "data": compressed}

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
        st.image(image, caption="✅ Uploaded successfully", use_container_width=True)
        image_part = {"mime_type": "image/jpeg", "data": compressed}

# 用户提问输入
st.markdown("### " + t["desc"])
prompt = st.text_input(t["input_placeholder"])

# 提问按钮
if st.button(t["send"]):
    if prompt and image_part:
        with st.spinner("Generating insight..."):
            model = genai.GenerativeModel("gemini-pro-vision")
            chat = model.start_chat(history=st.session_state["messages"])
            response = chat.send_message([prompt, image_part])
            st.session_state["messages"].append({"role": "user", "parts": prompt})
            st.session_state["messages"].append({"role": "model", "parts": response.text})
            st.markdown("### " + t["response"])
            st.markdown(response.text)
            st.info(t["feedback"])
    else:
        st.warning("❗ Please provide both an image and a question.")

