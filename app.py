import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- 1. CẤU HÌNH ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(
    page_title="Gemini Clone",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed" # Thu gọn sidebar giống giao diện ảnh
)

# --- 2. CSS CUSTOMIZATION CHO GIAO DIỆN GEMINI ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

:root {
    --bg-app: #ffffff;
    --text-primary: #1f1f1f;
    --text-secondary: #444746;
    --card-bg: #f0f4f9;
    --card-hover: #e1e5ea;
}

/* Reset tổng thể */
.stApp {
    background-color: var(--bg-app) !important;
    font-family: 'Google Sans', sans-serif !important;
}

/* Căn chỉnh vùng main */
.main .block-container {
    padding-top: 5rem !important;
    max-width: 900px !important;
    margin: 0 auto !important;
}

/* --- HERO TEXT (Lời chào) --- */
.hero-greeting {
    font-size: 3.5rem !important;
    font-weight: 500 !important;
    letter-spacing: -0.05rem !important;
    background: linear-gradient(74deg, #4285f4 0%, #9b72cb 33%, #d96570 66%, #137333 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-bottom: 0px !important;
    line-height: 1.1 !important;
}

.hero-sub {
    font-size: 3.5rem !important;
    font-weight: 500 !important;
    letter-spacing: -0.05rem !important;
    color: #c4c7c5 !important;
    margin-top: 0px !important;
    margin-bottom: 3rem !important;
    line-height: 1.1 !important;
}

/* --- SUGGESTION CARDS --- */
div[data-testid="column"] button {
    background-color: var(--card-bg) !important;
    color: var(--text-secondary) !important;
    border: none !important;
    border-radius: 12px !important;
    height: 180px !important;
    width: 100% !important;
    padding: 1.2rem !important;
    text-align: left !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    font-size: 0.95rem !important;
    font-family: 'Google Sans', sans-serif !important;
    transition: background-color 0.2s ease !important;
    box-shadow: none !important;
    white-space: normal !important;
    line-height: 1.4 !important;
}

div[data-testid="column"] button:hover {
    background-color: var(--card-hover) !important;
    color: var(--text-primary) !important;
}

/* Cố gắng đẩy icon xuống góc dưới bằng CSS ngầm định với st.button */
div[data-testid="column"] button p {
    margin: 0 !important;
    height: 100%;
    display: flex;
    flex-direction: column;
}

/* --- CHAT INPUT --- */
[data-testid="stChatInput"] {
    background-color: var(--card-bg) !important;
    border: none !important;
    border-radius: 30px !important;
    padding: 5px 10px !important;
}

[data-testid="stChatInput"]:focus-within {
    background-color: #e1e5ea !important;
}

/* Ẩn các nút rườm rà của Streamlit */
header {visibility: hidden;}
footer {visibility: hidden;}

/* --- DISCLAIMER TEXT (Dưới ô chat) --- */
.disclaimer {
    text-align: center;
    font-size: 0.75rem;
    color: #444746;
    margin-top: 10px;
    font-family: 'Google Sans', sans-serif;
}
.disclaimer a {
    color: #444746;
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# --- 3. KHỞI TẠO CHAT SESSION ---
if "chat_session" not in st.session_state:
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.messages = []
    except Exception:
        st.session_state.chat_session = None
        st.session_state.messages = []

# --- 4. GIAO DIỆN CHÍNH ---

# 4.1 Lời chào (Hero Section)
if not st.session_state.messages:
    st.markdown("""
        <div style="margin-bottom: 2rem;">
            <p class="hero-greeting">Hello, Lisa.</p>
            <p class="hero-sub">How can I help you today?</p>
        </div>
    """, unsafe_allow_html=True)

    # 4.2 Thẻ gợi ý (Cards)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        if st.button("Help me find YouTube videos to care for a plant \n\n ▶️", use_container_width=True):
            st.session_state._qp = "Help me find YouTube videos to care for a plant"
            st.rerun()
            
    with c2:
        if st.button("Brainstorm presentation ideas about a topic \n\n 🧭", use_container_width=True):
            st.session_state._qp = "Brainstorm presentation ideas about a topic"
            st.rerun()
            
    with c3:
        if st.button("What are some tips to improve public speaking skills for beginners? \n\n 💡", use_container_width=True):
            st.session_state._qp = "What are some tips to improve public speaking skills for beginners?"
            st.rerun()
            
    with c4:
        if st.button("Come up with a product name for a new app \n\n ✏️", use_container_width=True):
            st.session_state._qp = "Come up with a product name for a new app"
            st.rerun()

# 4.3 Xử lý hiển thị tin nhắn chat (Nếu có)
quick_prompt = st.session_state.pop("_qp", None)

if st.session_state.messages:
    for msg in st.session_state.messages:
        avatar = "🧑" if msg["role"] == "user" else "✨"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# 4.4 Ô nhập liệu (Chat Input)
prompt = st.chat_input("Enter a prompt here") or quick_prompt

if prompt:
    # Ẩn lời chào và thẻ khi bắt đầu chat bằng cách thêm vào messages
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="✨"):
        if not st.session_state.get("chat_session"):
            st.error("⚠️ AI is currently unavailable. Please check your API Key.")
        else:
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat_session.send_message(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# 4.5 Disclaimer Text (Chỉ hiển thị khi chưa có tin nhắn hoặc ép xuống cuối trang)
st.markdown("""
    <div class="disclaimer">
        Gemini may display inaccurate info, including about people, so double-check its responses. 
        <a href="#">Your privacy & Gemini</a>
    </div>
""", unsafe_allow_html=True)