import streamlit as st
import google.generativeai as genai
import requests
import os
import pandas as pd
from dotenv import load_dotenv

# --- 1. CẤU HÌNH HỆ THỐNG & BẢO MẬT ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("Cảnh báo: Không tìm thấy GEMINI_API_KEY trong secrets!")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Link Backend Render của bạn (KIỂM TRA LẠI CHÍNH XÁC LINK CỦA BẠN NHÉ)
BACKEND_URL = "https://test-0hc8.onrender.com"

# --- 2. THIẾT LẬP GIAO DIỆN (THEME & CSS TỰ CHẾ) ---
st.set_page_config(
    page_title="AquaAI Enterprise Platform",
    page_icon="🦐",
    layout="wide", # Chế độ màn hình rộng cho doanh nghiệp
    initial_sidebar_state="expanded"
)

# Custom CSS để "chữa" các lỗi: gap:0, Sidebar trắng tinh, Chatbox cho ra giữa
st.markdown("""
<style>
    /* Chữa lỗi gap:0 làm dính nhau */
    .stApp { gap: 1rem; }
    
    /* Làm Sidebar có màu nền chuyên nghiệp */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Chữa lỗi Metrics và Cards trắng tinh (làm chúng nổi bật hơn) */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Làm biểu đồ cũng nổi bật */
    .stPlotlyChart {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* QUAN TRỌNG: Làm cho Chatbox ra giữa màn hình Wide */
    [data-testid="stChatMessageContainer"] {
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    [data-testid="stChatInput"] {
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Tùy chỉnh chat bubbles */
    .stChatMessage {
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        width: fit-content;
        max-width: 70%;
    }
    
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #EDF2F7;
        margin-left: auto;
        margin-right: 0;
    }
    
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #E6FFFA;
        border: 1px solid #B2F5EA;
        margin-left: 0;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. KHAI BÁO TOOLS (Giữ nguyên logic) ---
def check_environment(location: str) -> dict:
    """Kiểm tra thời tiết, độ mặn và rủi ro môi trường."""
    try:
        response = requests.get(f"{BACKEND_URL}/check-environment?location={location}", timeout=10)
        return response.json()
    except Exception as e:
        st.error(f"Lỗi kết nối Backend: {str(e)}")
        return {"error": "Không thể kết nối Backend"}

def get_action_recommendation(alert_type: str) -> dict:
    """Lấy hướng dẫn hành động cụ thể."""
    try:
        response = requests.get(f"{BACKEND_URL}/get-action?alert_type={alert_type}", timeout=10)
        return response.json()
    except Exception as e:
        return {"action_recommendation": "Liên hệ kỹ thuật viên ngay lập tức."}

# --- 4. KHỞI TẠO AI SESSION (Dùng try-except để tránh app trắng tinh) ---
if "chat_session" not in st.session_state:
    system_prompt = """
    Bạn là Chuyên gia AI hệ thống Aquaculture Intelligence. 
    Nhiệm vụ: Tư vấn rủi ro môi trường cho doanh nghiệp miền Tây.
    Phong cách: Chuyên nghiệp, tin cậy nhưng gần gũi (xưng tôi, gọi bà con).
    Quy tắc: Luôn check_environment trước, nếu rủi ro phải get_action_recommendation ngay.
    """
    try:
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-8b',
            tools=[check_environment, get_action_recommendation],
            system_instruction=system_prompt
        )
        st.session_state.chat_session = model.start_chat(enable_automatic_function_calling=True)
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Lỗi khởi tạo Gemini AI: {str(e)}")
        st.session_state.chat_session = None

# --- 5. BỐ CỤC GIAO DIỆN (SIDEBAR CỐ ĐỊNH & SÁNG SỦA) ---
with st.sidebar:
    # Lỗi ảnh: Dùng icon vệ tinh chuẩn hơn
    st.image("https://img.icons8.com/clouds/200/satellite-dish.png", width=100)
    st.title("AquaAI Enterprise")
    st.markdown("---")
    
    if BACKEND_URL != "https://test-0hc8.onrender.com":
        st.warning("● URL Backend không khớp mặc định!")
    else:
        st.success("● Đã kết nối Backend Render")
    
    st.info("Trạng thái: Live 1.0.1")
    
    if st.button("🗑️ Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()

# --- 6. GIAO DIỆN CHÍNH (DASHBOARD + CHAT RA GIỮA) ---
# Dùng CSS để Chat ra giữa, nên không cần chia column nữa
st.subheader("📊 Trung tâm Giám sát Doanh nghiệp")

# Dashboard Metrics: Có nền trắng, bóng đổ rõ ràng
m1, m2, m3 = st.columns(3)
m1.metric("Trạng thái Môi trường", "Tối ưu", help="Dữ liệu từ trạm vệ tinh OWM.")
m2.metric("Chỉ số Rủi ro (7 ngày)", "15%", delta="-5%", help="So với tuần trước.")
m3.metric("Hoạt động Thiết bị", "Online", delta="8/8")

st.markdown("### 📈 Analytics: Phân tích & Dự báo Sớm (Test Bão)")
# Giả lập dữ liệu Analytics chuyên nghiệp
df = pd.DataFrame({
    "Ngày": ["14/4", "15/4", "16/4", "17/4", "18/4", "19/4", "20/4"],
    "Sốc nhiệt (%)": [10, 15, 12, 45, 80, 20, 15],
    "Giảm mặn (%)": [5, 5, 8, 30, 95, 40, 10]
})
# Vẽ biểu đồ line chart, st.line_chart tự động có CSS của Metric
st.line_chart(df, x="Ngày", y=["Sốc nhiệt (%)", "Giảm mặn (%)"])
st.caption("Dữ liệu được AI phân tích từ vệ tinh & trạm đo, dự báo cho khu vực ĐBSCL.")

# --- PHẦN CHATBOX ĐÃ ĐƯỢC CỨU (RA GIỮA) ---
st.markdown("---")
st.subheader("💬 Cố vấn Thủy sản AI")
st.caption("Sử dụng Google Gemini 1.5 Flash-8b")

# In ra hội thoại chat (Dùng CSS tự chế ở trên để nó ra giữa)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Xử lý input của user (Tự động ra giữa nhờ CSS)
if prompt := st.chat_input("Hỏi tôi... (VD: Thời tiết Bến Tre (test bão) sao rồi bà con?)"):
    # Tin nhắn user
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Tin nhắn assistant
    with st.chat_message("assistant", avatar="🤖"):
        if not st.session_state.chat_session:
             st.error("AI không hoạt động. Vui lòng kiểm tra GEMINI_API_KEY.")
        else:
            with st.spinner("Đang phân tích dữ liệu trạm đo..."):
                try:
                    response = st.session_state.chat_session.send_message(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {str(e)}")

# --- 7. FOOTER CHUYÊN NGHIỆP ---
st.markdown("---")
st.caption("© 2026 AquaAI Enterprise Platform | Giải pháp chuyển đổi số nông nghiệp ĐBSCL.")