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
if os.getenv("GOOGLE_API_KEY") is None:
    st.error("❌ Google API Key not found. Please check .env file.")

# 多语言支持
t = {
    "en": {
        "title": "🏛️AI Cultural-Tour-Mate",
        "slogan": "Your trustworthy, insightful, and articulate cultural companion in tour.",
        "upload": "🖼️ Upload Image",
        "camera": "📷 Capture Photo",
        "camera_on": "📸 Open Camera",
        "camera_sub": "Any cultural troubles during the tour, please take a photo and ask me.",
        "desc": "📝 Describe Trouble",
        "send": "🎈 Send",
        "response": "Cultural Insight",
        "feedback": "🦄 Was this helpful? Feel free to ask more.",
        "developer": "Developer: Sin-Wing | Xianrong Liang ",
        "upload_note": "Select and upload an image from your device, the image is limited to 2 MB.",
        "camera_note": "Notice: If the camera cannot be opened, please close it and try again. Some terminals might not convert↔️ the rear camera, suggest uploading photos.",
        "input_placeholder": "Type what you want to learn about the image here...",
        "user_role": "💬 Ask anything",
        "progress": "⏳ Please wait while I analyze your question and image...",
        "response_title": "💬 Cultural Insight",
        "response_loading": "🧠 Generating response...",
        "oversize_error": "🚫 Image exceeds 2MB limit. Please upload a smaller image.",
        "no_camera": "⚠️ No camera available on this device.",
        "photo_success": "✅ Photo captured successfully.",
        "photo_captured": "✅ Photo captured successfully.",
        "image_uploaded": "✅ Image uploaded successfully.",
        "photo_uploaded": "✅ Image uploaded successfully.",
        "api_error": "⚠️ Gemini API request failed. Check your network or API Key.",
        "reask": "♻️ Empty Conversation and Ask another",
        "text_unsendable": "⚠️ You must upload a picture before asking a question."
    },
    "zh": {
        "title": "🏛️智慧文化旅伴",
        "slogan": "您忠实博学且智慧的文化旅行小伙伴。",
        "upload": "🖼️ 上传图像",
        "camera": "📷 现场拍照",
        "camera_on": "📸 打开相机",
        "camera_sub": "旅途中的文化困扰，请随手拍张照片发我解读。",
        "desc": "📝 描述疑问",
        "send": "🎈 发送",
        "response": "文化背景信息",
        "feedback": "🦄 这个回答有帮助吗？欢迎继续提问。",
        "developer": "开发者：梁羡荣 (Leung, Sin-Wing)",
        "upload_note": "从您的设备中选择并上传一张图片，大小不超2M。",
        "camera_note": "提示：若无法打开相机，请关闭相机重试；部分终端不能转换↔️后置摄像头，建议上传照片。",
        "input_placeholder": "请在文本框中描述您的问题...",
        "user_role": "💬 请您提问",
        "progress": "⏳ 请稍后，正在分析您的图像与问题...",
        "response_title": "💬 文化洞察",
        "response_loading": "🧠 正在生成对话...",
        "oversize_error": "🚫 图像大小超2MB限制，请重新选择。",
        "no_camera": "⚠️ 当前设备无可用摄像头。",
        "photo_success": "✅ 拍照成功。",
        "photo_captured": "✅ 拍照成功。",
        "image_uploaded": "✅ 图片上传成功。",
        "photo_uploaded": "✅ 图片上传成功。",
        "api_error": "⚠️ Gemini API 链接失败. 请检查你的API密钥.",
        "reask": "♻️ 清空结果并重新提问",
        "text_unsendable": "⚠️ 发消息前请拍照或上传一张图片。"
    }
}

# 减少页眉空白
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem;
        }
        header {
            visibility: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# 语言选择 st.markdown("🌐Language / 语言")
col1, col2 = st.columns([75, 25])
with col2:
    lang_code = {"English": "en", "中文": "zh"}[st.radio("", ["English", "中文"], horizontal=True)]
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
st.divider()

# 会话初始化
if "messages" not in st.session_state:
    st.session_state["messages"] = [ {"role": "system", "content": "Your Cultural-Tour-Mate, a helpful and culturally knowledgeable travel assistant. Don't hesitate to ask..." if lang_code == "en" else "您的文化旅行旅伴，旅途上遇见任何问题都可以问我..."}]


# 图像压缩
def compress_image(image, max_size=(800, 800), quality=80):
    image = image.convert("RGB")  # 保证 JPEG 兼容性
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

# 拍照按钮显示逻辑
if not st.session_state["show_camera"]:
    if st.button(text["camera_on"]):  # 例如 📸 Take a shot
        st.session_state["show_camera"] = True
        st.rerun()
else:
    if st.button("❌ Close Camera" if lang_code == "en" else "❌ 关闭相机"):
        st.session_state["show_camera"] = False
        st.rerun()


if st.session_state["show_camera"]:
    camera_img = st.camera_input("camera_capture")
    if camera_img:
        # 处理压缩
        if len(camera_img.getvalue()) > 3 * 1024 * 1024:
            st.warning(text["oversize_error"])
        else:
            img = Image.open(camera_img)
            st.session_state["image_part"] = {"mime_type": "image/jpeg", "data": compress_image(img)}
            st.image(img, caption=text["photo_captured"], use_container_width=True)
            st.rerun()  # 强制刷新页面，确保 image_part 生效

# 上传模块
st.divider()
st.markdown("### " + text["upload"])
st.markdown(text["upload_note"])
upload_img = st.file_uploader(label="", type=["jpg", "jpeg", "png", "webp"])
if upload_img:
    if upload_img.size > 3 * 1024 * 1024:
        st.warning(text["oversize_error"])
    else:
        img = Image.open(upload_img)
        st.session_state["image_part"] = {"mime_type": "image/jpeg", "data": compress_image(img)}
        st.image(img, caption=text["photo_uploaded"], use_container_width=True)
        st.rerun()  # 强制刷新页面，确保 image_part 生效

# 输入与提问
# 提问表单（支持回车键提交 + 语言提示）
st.divider()
st.markdown("### " + text["desc"])
st.markdown(text["input_placeholder"])

# 清空输入框
with st.form("question_form"):  # 移除了 clear_on_submit=True
    cols = st.columns([5, 1])
    with cols[0]:
        prompt = st.text_input(label="### ", key="prompt_input", label_visibility="collapsed")
    with cols[1]:
        submitted = st.form_submit_button(text["send"])

# 提交后处理部分 应该放在 显示对话历史之前
if submitted:
    image_part = st.session_state.get("image_part")
    if prompt and image_part:
        with st.spinner("🧠 Generating insight..." if lang_code == "en" else "🧠 正在思考，请稍候..."):
            try:
                model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
                response = model.generate_content([prompt, image_part])
                response_text = response.text
                
                # 添加新的用户提问和AI回答到会话状态的开头
                st.session_state["messages"].insert(1, {"role": "assistant", "content": response_text})
                st.session_state["messages"].insert(1, {"role": "user", "content": prompt})
                
                # 可选择在这里手动清除输入框内容
                st.session_state["prompt_input"] = ""
            except Exception as e:
                st.error(text["api_error"])
                st.exception(e)
    else:
        st.warning(text["text_unsendable"])

# 显示对话历史（倒序）
for message in reversed(st.session_state["messages"]):  # 首先反转整个列表以保证最新的消息最先处理
    if message["role"] != "system":  # 跳过系统消息
        bubble_style = (
            "text-align: right; background-color: #99000033; padding: 10px; border-radius: 12px; margin: 5px 0;"
            if message["role"] == "user" 
            else "text-align: left; background-color: #55555533; padding: 10px; border-radius: 12px; margin: 5px 0;"
        )
        st.markdown(f'<div style="{bubble_style}">{message["content"]}</div>', unsafe_allow_html=True)

# 添加“重新提问”按钮（Reask）
if len(st.session_state["messages"]) > 1:  # 有对话记录才显示按钮
    st.divider()
    if st.button(text["reask"]):
        # 重置消息列表，仅保留系统提示
        st.session_state["messages"] = [
            {
                "role": "system",
                "content": "Your Cultural-Tour-Mate, a helpful and culturally knowledgeable travel assistant. Don't hesitate to ask..."
                if lang_code == "en"
                else "您的文化旅行旅伴，旅途上遇见任何问题都可以问我..."
            }
        ]
        # 重置上传图片数据
        st.session_state["image_part"] = None
        # 关闭相机视图
        st.session_state["show_camera"] = False
        # 立即刷新页面
        st.rerun()
