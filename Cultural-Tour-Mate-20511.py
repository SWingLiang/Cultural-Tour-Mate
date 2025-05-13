import streamlit as st
import google.generativeai as genai
import dotenv
import os
from PIL import Image
from io import BytesIO

# ========== 页面配置 ==========
st.set_page_config(page_title="Cultural-Tour-Mate", layout="centered")

# ========== 加载ENV环境与 API Key ==========
dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ========== 多语言支持 ==========
translations = {
    "en": {
        "title": "\ud83c\udfdb\ufe0fCultural-Tour-Mate",
        "slogan": "Your trustworthy, insightful, and articulate cultural companion in tour.",
        "upload": "\ud83d\uddbc\ufe0f Upload Image",
        "camera": "\ud83d\udcf7 Capture Photo",
        "camera_on": "\ud83d\udcf8 Take a shot",
        "camera_sub": "Any cultural troubles during the tour, please take a photo and ask metters.",
        "desc": "\ud83d\udcac Ask Matters",
        "send": "\ud83e\udd20 Send",
        "response": "Cultural Insight",
        "feedback": "Was this helpful? Feel free to ask more.",
        "developer": "Developer: Xianrong Liang (Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh.",
        "upload_note": "Select and upload an image from your device, the image is limited to 2 MB.",
        "camera_note": "Due to limitations, rear camera might not be accessible on tablets. Try phone or upload a photo.",
        "input_placeholder": "Describe what you want to learn about the image...",
        "user_role": "\ud83d\udcac Ask anything",
        "oversize_error": "\ud83d\udeab Image exceeds 3MB limit. Please upload a smaller image.",
        "no_camera": "\u26a0\ufe0f No camera available on this device.",
        "photo_uploaded": "\u2705 Photo uploaded successfully.",
        "warning_image_and_question": "\u2757Please provide both an image and a question.",
        "photo_captured": "\u2705 Photo captured successfully."
    },
    "zh": {
        "title": "\ud83c\udfdb\ufe0fAI\u6587\u5316\u65c5\u4f34",
        "slogan": "\u60a8\u5fe0\u5b9e\u535a\u5b66\u4e14\u667a\u6167\u7684\u6587\u5316\u65c5\u884c\u5c0f\u4f34\u4f19\u3002",
        "upload": "\ud83d\uddbc\ufe0f \u4e0a\u4f20\u56fe\u50cf",
        "camera": "\ud83d\udcf7 \u73af\u5883\u62cd\u7167",
        "camera_on": "\ud83d\udcf8 \u6253\u5f00\u76f8\u673a",
        "camera_sub": "\u65c5\u9014\u4e2d\u7684\u6587\u5316\u56f0\u6270\uff0c\u8bf7\u968f\u624b\u62cd\u4e00\u5f20\u7167\u7247\u95ee\u95ee\u6211\u3002",
        "desc": "\ud83d\udcac \u63cf\u8ff0\u95ee\u9898",
        "send": "\ud83e\udd20 \u53d1\u9001",
        "response": "\u6587\u5316\u80cc\u666f\u4fe1\u606f",
        "feedback": "\u8fd9\u4e2a\u56de\u7b54\u6709\u5e2e\u52a9\u5417\uff1f\u6b22\u8fce\u7ee7\u7eed\u63d0\u95ee\u3002",
        "developer": "\u5f00\u53d1\u8005\uff1a\u6881\u8d35\u8363(Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh",
        "upload_note": "\u4ece\u60a8\u7684\u8bbe\u5907\u4e2d\u9009\u62e9\u5e76\u4e0a\u4f20\u4e00\u5f20\u56fe\u7247\uff0c\u5927\u5c0f\u4e0d\u8d852M\u3002",
        "camera_note": "\u7531\u4e8e\u6280\u672f\u9650\u5236\uff0c\u90e8\u5206\u5e73\u677f\u4e0d\u652f\u6301\u540e\u7f6e\u6444\u50cf\u5934\uff0c\u5efa\u8bae\u4f7f\u7528\u624b\u673a\u6216\u4e0a\u4f20\u7167\u7247\u3002",
        "input_placeholder": "\u63cf\u8ff0\u60a8\u60f3\u4e86\u89e3\u7684\u56fe\u50cf\u5185\u5bb9...",
        "user_role": "\ud83d\udcac \u8bf7\u60a8\u63d0\u95ee",
        "oversize_error": "\ud83d\udeab \u56fe\u50cf\u5927\u5c0f\u8d85\u8fc73MB\u9650\u5236\uff0c\u8bf7\u91cd\u65b0\u9009\u62e9\u3002",
        "no_camera": "\u26a0\ufe0f \u5f53\u524d\u8bbe\u5907\u65e0\u53ef\u7528\u6444\u50cf\u5934\u3002",
        "warning_image_and_question": "\u2757\u8bf7\u540c\u65f6\u63d0\u4f9b\u56fe\u7247\u548c\u95ee\u9898\u63cf\u8ff0\u3002",
        "photo_uploaded": "\u2705 \u7167\u7247\u4e0a\u4f20\u6210\u529f\uff01",
        "photo_captured": "\u2705 \u7167\u7247\u62cd\u6444\u6210\u529f\uff01"
    }
}

language = st.selectbox("\ud83c\udf10 Language / \u8bed\u8a00", ["English", "\u4e2d\u6587"])
lang_code = {"English": "en", "\u4e2d\u6587": "zh"}[language]
t = translations[lang_code]

# ========== UI顶部 ==========
st.title(t["title"])
st.markdown(t["slogan"])
st.caption(t["developer"])

# ========== 图像预处理 ==========
def compress_image(image, max_size=(800, 800), quality=80):
    image.thumbnail(max_size)
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()

# ========== 全局变量初始化 ==========
image_part = None
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "parts": "system prompt: You are CulturalTourMate, a helpful and culturally knowledgeable travel assistant."}]

# ========== 拍照输入 ==========
st.markdown("### " + t["camera"])
st.markdown(t["camera_sub"])
st.caption(t["camera_note"])
if st.button(t["camera_on"]):
    st.session_state["show_camera"] = True

if st.session_state.get("show_camera", False):
    camera_image = st.camera_input("camera_capture")
    if camera_image:
        if len(camera_image.getvalue()) > 3 * 1024 * 1024:
            st.warning(t["oversize_error"])
        else:
            image = Image.open(camera_image)
            image_part = {"mime_type": "image/jpeg", "data": compress_image(image)}
            st.image(image, caption=t["photo_captured"], use_container_width=True)

# ========== 上传图像输入 ==========
st.markdown("---")
st.markdown("### " + t["upload"])
st.markdown(t["upload_note"])

uploaded_image = st.file_uploader(label="", type=["jpg", "jpeg", "png", "webp"])
if uploaded_image:
    if uploaded_image.size > 3 * 1024 * 1024:
        st.warning(t["oversize_error"])
    else:
        image = Image.open(uploaded_image)
        image_part = {"mime_type": "image/jpeg", "data": compress_image(image)}
        st.image(image, caption=t["photo_uploaded"], use_container_width=True)

# ========== 用户输入 & 回应 ==========
st.markdown("### " + t["desc"])
prompt = st.text_input(t["input_placeholder"])

if st.button(t["send"]):
    if prompt and image_part:
        with st.spinner("Generating insight..."):
            model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
            response = model.generate_content([
                prompt,
                genai.types.content_types.ImagePart(
                    mime_type=image_part["mime_type"],
                    data=image_part["data"]
                )
            ])
            st.markdown("### " + t["response"])
            st.markdown(response.text)
            st.info(t["feedback"])
    else:
        st.warning(t["warning_image_and_question"])

# ========== 背景形象 ==========
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
        .avatar-bg {{ display: none; }}
    }}
    </style>
    <img class='avatar-bg' src='{avatar_url}'/>
    """, unsafe_allow_html=True)
