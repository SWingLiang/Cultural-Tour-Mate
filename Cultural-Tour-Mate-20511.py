import streamlit as st
import google.generativeai as genai
import dotenv
import os
from PIL import Image
from io import BytesIO

# 页面配置
st.set_page_config(page_title="Cultural-Tour-Mate", layout="centered")

# 加载环境变量和 API Key
dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 多语言支持
t = {
    "en": {
        "title": "🏛️AI Cultural-Tour-Mate",
        "slogan": "Your trustworthy, insightful, and articulate cultural companion in tour.",
        "upload": "🖼️ Upload Image",
        "camera": "📷 Capture Photo",
        "camera_on": "📸 Take a shot",
        "camera_sub": "Any cultural troubles during the tour, please take a photo and ask me.",
        "desc": "💬 Describe Matters",
        "send": "🦄 Send",
        "response": "Cultural Insight",
        "feedback": "Was this helpful? Feel free to ask more.",
        "developer": "Developer: Xianrong Liang (Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh.",
        "upload_note": "Select and upload an image from your device, the image is limited to 2 MB.",
        "camera_note": "Due to limitations, rear camera might not be accessible on tablets. Try phone or upload a photo.",
        "input_placeholder": "Type what you want to learn about the image here",
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
        "reask":"🔄 Ask again",
        "text_unsendable": "⚠️ You have to upload a picture before asking a question."
    },
    "zh": {
        "title": "🏛️智慧文化旅伴",
        "slogan": "您忠实博学且智慧的文化旅行小伴伙。",
        "upload": "🖼️ 上传图像",
        "camera": "📷 环境拍照",
        "camera_on": "📸 打开相机",
        "camera_sub": "旅途中的文化困扰，请随手拍一张照片问问我。",
        "desc": "💬描述您的疑问：",
        "send": "🦄 发送",
        "response": "文化背景信息",
        "feedback": "这个回答有帮助吗？欢迎继续提问。",
        "developer": "开发者：梁羡荣(Sinwing); Abhay Soni; Shayan Majid Phamba; Gurjot Singh",
        "upload_note": "从您的设备中选择并上传一张图片，大小不超2M。",
        "camera_note": "由于技术限制，部分平板不支持后置摄像头，建议使用手机或上传照片。",
        "input_placeholder": "请在文本框中描述您的问题...",
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
        "reask":"🔄 重新提问",
        "text_unsendable": "⚠️ 发消息前请拍照或上传一张图片。"
    }
}

# 语言选择
lang_map = {"English": "en", "中文": "zh"}
st.markdown("### 🌐Language / 语言")
lang_code = lang_map[st.radio("", list(lang_map.keys()), horizontal=True)]
text = t[lang_code]


# 页面头像装饰
avatar_urls = {
    "en": "https://static.vecteezy.com/system/resources/previews/055/495/027/non_2x/a-man-in-a-white-t-shirt-and-jeans-free-png.png",
    "zh": "https://static.vecteezy.com/system/resources/previews/013/167/583/original/portrait-of-a-smiling-asian-woman-cutout-file-png.png"
}
avatar_url = avatar_urls.get(lang_code)
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
    @media (max-width: 768px) {{ .avatar-bg {{ display: none; }} }}
    </style><img class='avatar-bg' src='{avatar_url}' />
    """, unsafe_allow_html=True)

# 页面文字
st.title(text["title"])
st.markdown(text["slogan"])
st.caption(text["developer"])

# 会话初始化
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "parts": "system prompt: You are CulturalTourMate, a helpful and culturally knowledgeable travel assistant."}
    ]

# 图像压缩
def compress_image(image, max_size=(800, 800), quality=80):
    image.thumbnail(max_size)
    buf = BytesIO()
    image.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()

image_part = None

# 摄像头模块
st.markdown("### " + text["camera"])
st.markdown(text["camera_sub"])
st.caption(text["camera_note"])

if "show_camera" not in st.session_state:
    st.session_state["show_camera"] = False

if st.button(text["camera_on"]):
    st.session_state["show_camera"] = True

if st.session_state["show_camera"]:
    camera_img = st.camera_input("camera_capture")
    if camera_img:
        if len(camera_img.getvalue()) > 3 * 1024 * 1024:
            st.warning(text["oversize_error"])
        else:
            img = Image.open(camera_img)
            image_part = {"mime_type": "image/jpeg", "data": compress_image(img)}
            st.image(img, caption=text["photo_captured"], use_container_width=True)

# 上传模块
st.markdown("---")
st.markdown("### " + text["upload"])
st.markdown(text["upload_note"])

upload_img = st.file_uploader(label="", type=["jpg", "jpeg", "png", "webp"])
if upload_img:
    if upload_img.size > 3 * 1024 * 1024:
        st.warning(text["oversize_error"])
    else:
        img = Image.open(upload_img)
        image_part = {"mime_type": "image/jpeg", "data": compress_image(img)}
        st.image(img, caption=text["photo_uploaded"], use_container_width=True)

# 输入与提问
# 提问表单（支持回车键提交 + 语言提示）
st.markdown("### " + text["desc"])
with st.form("question_form", clear_on_submit=False):
    cols = st.columns([5, 1])

    with cols[0]:
        prompt = st.text_input(text["input_placeholder"], key="prompt_input")

    with cols[1]:
        # 用 st.markdown 或 st.write 添加空行，使按钮下移与输入框底部对齐
        st.markdown(" ")  # 也可以尝试 "##" 或 "<br>", 视情况微调
        submitted = st.form_submit_button(text["send"])

if submitted:
    if prompt and image_part:
        with st.spinner("Generating insight..." if lang_code == "en" else "正在思考，请稍候..."):
            model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
            language_prompt = "Please answer in English." if lang_code == "en" else "请用中文回答。"
            image_input = {
                "mime_type": image_part["mime_type"],
                "data": image_part["data"]
            }
            response = model.generate_content([language_prompt, prompt, image_input])
            st.markdown("### " + text["response"])
            st.markdown(response.text)
            st.info(text["feedback"])
    else:
        st.warning(text["warning_image_and_question"])

# 重新提问按钮（刷新页面）
if "prompt_input" not in st.session_state:
    st.session_state["prompt_input"] = ""
if "show_camera" not in st.session_state:
    st.session_state["show_camera"] = False

# 重新提问按钮（刷新页面）
st.markdown("---")
if st.button(t["reask"]):
    st.session_state["prompt_input"] = ""
    st.session_state["show_camera"] = False
    image_part = None
    st.rerun()

