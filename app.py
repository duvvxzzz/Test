import streamlit as st
import google.generativeai as genai
import requests
import os
from dotenv import load_dotenv

# --- BƯỚC BẢO MẬT: Tải các biến bí mật từ file .env ---
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# --- CẤU HÌNH ĐƯỜNG DẪN BACKEND ---
# Khi chạy ở máy tính: Để "http://127.0.0.1:8000"
# Khi đưa lên mây: Đổi thành link Render của bạn (VD: "https://aqua-ai-backend.onrender.com")
BACKEND_URL = "https://test-0hc8.onrender.com"

# 2. KHAI BÁO TOOLS
def check_environment(location: str) -> dict:
    """Gọi hàm này ĐẦU TIÊN để kiểm tra thời tiết, độ mặn và rủi ro môi trường nước cho một địa điểm."""
    response = requests.get(f"{BACKEND_URL}/check-environment?location={location}")
    return response.json()

def get_action_recommendation(alert_type: str) -> dict:
    """Gọi hàm này khi môi trường có rủi ro/sốc để lấy hướng dẫn hành động cụ thể cho người nuôi."""
    response = requests.get(f"{BACKEND_URL}/get-action?alert_type={alert_type}")
    return response.json()

# 3. KHỞI TẠO AI & LỊCH SỬ CHAT
if "chat_session" not in st.session_state:
    system_prompt = """
    Bạn là một chuyên gia AI hệ thống Aquaculture Intelligence. 
    Nhiệm vụ của bạn là tư vấn rủi ro nuôi trồng thủy sản cho người dân miền Tây.
    Quy tắc:
    1. LUÔN gọi hàm check_environment để có dữ liệu thực tế trước khi trả lời.
    2. Nếu có rủi ro cao, phải gọi tiếp hàm get_action_recommendation.
    3. Trả lời dân dã, xưng 'tôi' và gọi người dùng là 'bà con'. Dùng markdown (in đậm, icon) để câu trả lời dễ đọc.
    """
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-8b', # Dùng bản 8b này bao la Quota, tốc độ siêu nhanh
        tools=[check_environment, get_action_recommendation],
        system_instruction=system_prompt
    )
    st.session_state.chat_session = model.start_chat(enable_automatic_function_calling=True)
    st.session_state.messages = []

# 4. GIAO DIỆN CHÍNH
st.set_page_config(page_title="Aquaculture AI", page_icon="🦐")
st.title("🦐 Trợ lý AI Thủy Sản")
st.caption("Hệ thống cảnh báo rủi ro & Khuyến nghị hành động sớm (Predictive Analytics)")
st.divider()

# In ra toàn bộ lịch sử chat cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. XỬ LÝ KHI NGƯỜI DÙNG NHẬP CÂU HỎI
if prompt := st.chat_input("Bà con muốn hỏi gì? (VD: Thời tiết Bến Tre (test bão) hôm nay thế nào?)"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Hệ thống đang quét dữ liệu vệ tinh và môi trường..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {str(e)}")