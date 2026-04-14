import streamlit as st
import google.generativeai as genai
import requests
import os
import pandas as pd
from dotenv import load_dotenv

# --- 1. CẤU HÌNH HỆ THỐNG & BẢO MẬT ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Link Backend Render của bạn
BACKEND_URL = "https://test-0hc8.onrender.com"

# --- 2. THIẾT LẬP GIAO DIỆN (THEME) ---
st.set_page_config(
    page_title="AquaAI Enterprise",
    page_icon="🦐",
    layout="wide", # Chế độ màn hình rộng
    initial_sidebar_state="expanded"
)

# Custom CSS để làm giao diện sáng sủa, chuyên nghiệp
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
    }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #0D9488;
        color: #0D9488;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #0D9488;
        color: white;
    }
    h1, h2, h3 { color: #0F172A; font-family: 'Inter', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- 3. KHAI BÁO TOOLS (Giữ nguyên logic) ---
def check_environment(location: str) -> dict:
    """Kiểm tra thời tiết, độ mặn và rủi ro môi trường."""
    try:
        response = requests.get(f"{BACKEND_URL}/check-environment?location={location}", timeout=10)
        return response.json()
    except:
        return {"error": "Không thể kết nối Backend"}

def get_action_recommendation(alert_type: str) -> dict:
    """Lấy hướng dẫn hành động cụ thể."""
    try:
        response = requests.get(f"{BACKEND_URL}/get-action?alert_type={alert_type}", timeout=10)
        return response.json()
    except:
        return {"action_recommendation": "Liên hệ kỹ thuật viên ngay lập tức."}

# --- 4. KHỞI TẠO AI SESSION ---
if "chat_session" not in st.session_state:
    system_prompt = """
    Bạn là Chuyên gia cao cấp của Aquaculture Intelligence. 
    Nhiệm vụ: Tư vấn rủi ro môi trường cho doanh nghiệp và bà con nuôi tôm.
    Phong cách: Chuyên nghiệp, tin cậy nhưng gần gũi (xưng tôi, gọi bà con).
    Quy tắc: Luôn check_environment trước, nếu rủi ro phải get_action_recommendation ngay.
    """
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-8b',
        tools=[check_environment, get_action_recommendation],
        system_instruction=system_prompt
    )
    st.session_state.chat_session = model.start_chat(enable_automatic_function_calling=True)
    st.session_state.messages = []

# --- 5. BỐ CỤC GIAO DIỆN (SIDEBAR) ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/shrimp.png", width=100)
    st.title("AquaAI Platform")
    st.markdown("---")
    st.success("● Hệ thống đang kết nối")
    st.info("Phiên bản: Doanh nghiệp 1.0")
    
    if st.button("🗑️ Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()

# --- 6. GIAO DIỆN CHÍNH (DASHBOARD + CHAT) ---
col_dash, col_chat = st.columns([1.2, 1])

with col_dash:
    st.subheader("📊 Trung tâm Giám sát Ao nuôi")
    
    # Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Môi trường", "An toàn", delta="Normal")
    m2.metric("Chỉ số Rủi ro", "15%", delta="-2%")
    m3.metric("Trạm đo", "Hoạt động", delta="Online")
    
    st.markdown("### 📈 Dự báo Rủi ro sớm (7 ngày)")
    # Giả lập dữ liệu Analytics cho chuyên nghiệp
    df = pd.DataFrame({
        "Ngày": ["14/4", "15/4", "16/4", "17/4", "18/4", "19/4", "20/4"],
        "Sốc nhiệt (%)": [10, 15, 12, 45, 80, 20, 15],
        "Giảm mặn (%)": [5, 5, 8, 30, 95, 40, 10]
    })
    st.line_chart(df, x="Ngày", y=["Sốc nhiệt (%)", "Giảm mặn (%)"])
    st.caption("Dữ liệu được phân tích bởi AI dựa trên mô hình bão vệ tinh.")

with col_chat:
    st.subheader("💬 Cố vấn Thủy sản AI")
    
    # Khung chat hiển thị tin nhắn
    chat_placeholder = st.container(height=500)
    with chat_placeholder:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Xử lý input
    if prompt := st.chat_input("Hỏi chuyên gia (VD: Thời tiết Bến Tre (test bão) sao rồi?)..."):
        # Hiển thị tin nhắn User
        with chat_placeholder:
            with st.chat_message("user"):
                st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Gọi AI
        with chat_placeholder:
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Đang phân tích dữ liệu..."):
                    try:
                        response = st.session_state.chat_session.send_message(prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi: {str(e)}")

# --- 7. FOOTER ---
st.markdown("---")
st.caption("© 2026 AquaAI Platform - Giải pháp chuyển đổi số nông nghiệp bền vững.")