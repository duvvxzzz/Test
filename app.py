import streamlit as st
import google.generativeai as genai
import requests
import os
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

# --- 1. CẤU HÌNH HỆ THỐNG & BẢO MẬT ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("⚠️ Không tìm thấy GEMINI_API_KEY trong secrets!")
else:
    genai.configure(api_key=GEMINI_API_KEY)

BACKEND_URL = "https://test-0hc8.onrender.com"

# --- 2. THIẾT LẬP GIAO DIỆN ---
st.set_page_config(
    page_title="AquaAI – Hệ thống Giám sát Thủy sản",
    page_icon="🦐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS toàn diện – fix tất cả lỗi, thiết kế lại từ đầu
st.markdown("""
<style>
    /* ====== IMPORT FONT ====== */
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700&family=Sora:wght@600;700&display=swap');

    /* ====== ROOT VARIABLES ====== */
    :root {
        --primary: #0EA5E9;
        --primary-dark: #0284C7;
        --secondary: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --bg-main: #F0F7FF;
        --bg-card: #FFFFFF;
        --bg-sidebar: #0F2744;
        --text-main: #0F172A;
        --text-muted: #64748B;
        --border: #CBD5E1;
        --shadow: 0 4px 20px rgba(14, 165, 233, 0.12);
    }

    /* ====== GLOBAL APP ====== */
    .stApp {
        background-color: var(--bg-main) !important;
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    /* ====== SIDEBAR – Fix màu trắng tinh ====== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F2744 0%, #1a3a5c 100%) !important;
        border-right: none !important;
    }

    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label {
        color: #CBD5E1 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #F8FAFC !important;
        font-family: 'Sora', sans-serif !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: rgba(239, 68, 68, 0.15) !important;
        color: #FCA5A5 !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 10px !important;
        width: 100% !important;
        font-family: 'Be Vietnam Pro', sans-serif !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(239, 68, 68, 0.3) !important;
        border-color: rgba(239, 68, 68, 0.6) !important;
    }

    /* Success/info/warning trong sidebar */
    [data-testid="stSidebar"] .stAlert {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
    }

    /* ====== METRIC CARDS – Fix chữ ẩn ====== */
    div[data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: var(--shadow) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(14, 165, 233, 0.18) !important;
    }

    /* Fix màu chữ metric */
    div[data-testid="stMetric"] label {
        color: var(--text-muted) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    div[data-testid="stMetricValue"] {
        color: var(--text-main) !important;
        font-family: 'Sora', sans-serif !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetricDelta"] {
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }

    /* ====== HEADINGS ====== */
    h1, h2, h3 {
        font-family: 'Sora', sans-serif !important;
        color: var(--text-main) !important;
    }

    .stSubheader {
        color: var(--text-main) !important;
    }

    /* ====== CHAT MESSAGES – Fix không thấy kết quả ====== */
    [data-testid="stChatMessageContainer"] {
        background: transparent !important;
    }

    /* Toàn bộ khung chat */
    .stChatMessage {
        background: var(--bg-card) !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 1rem 1.5rem !important;
        margin-bottom: 0.75rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }

    /* Chat message text – đảm bảo luôn thấy */
    .stChatMessage p,
    .stChatMessage span,
    .stChatMessage div,
    .stChatMessage li,
    [data-testid="stChatMessageContent"] * {
        color: var(--text-main) !important;
    }

    /* User messages */
    [data-testid="stChatMessageUser"] {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
        border-color: #BFDBFE !important;
    }

    /* Assistant messages */
    [data-testid="stChatMessageAssistant"] {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%) !important;
        border-color: #BBF7D0 !important;
        border-left: 4px solid var(--secondary) !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background: var(--bg-card) !important;
        border: 2px solid var(--border) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: var(--text-main) !important;
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    /* ====== PLOTLY CHART CONTAINER ====== */
    .stPlotlyChart {
        background: var(--bg-card) !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        box-shadow: var(--shadow) !important;
    }

    /* ====== DIVIDER ====== */
    hr {
        border-color: #CBD5E1 !important;
        margin: 1.5rem 0 !important;
    }

    /* ====== CAPTION ====== */
    .stCaption, caption {
        color: var(--text-muted) !important;
    }

    /* ====== SPINNER ====== */
    .stSpinner > div {
        border-top-color: var(--primary) !important;
    }

    /* ====== MAIN CONTENT PADDING ====== */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    /* ====== CHAT SECTION WRAPPER ====== */
    .chat-wrapper {
        max-width: 860px;
        margin: 0 auto;
    }

    /* ====== CUSTOM HEADER ====== */
    .aqua-header {
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 50%, #075985 100%);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        color: white !important;
        position: relative;
        overflow: hidden;
    }

    .aqua-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
    }

    .aqua-header h1 {
        color: white !important;
        font-family: 'Sora', sans-serif !important;
        font-size: 1.8rem !important;
        margin: 0 !important;
    }

    .aqua-header p {
        color: rgba(255,255,255,0.8) !important;
        margin: 0.3rem 0 0 0 !important;
    }

    /* ====== SECTION LABEL ====== */
    .section-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-bottom: 0.75rem;
    }

    /* ====== STATUS BADGE ====== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .status-online {
        background: rgba(16, 185, 129, 0.15);
        color: #065F46;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# --- 3. KHAI BÁO TOOLS ---
def check_environment(location: str) -> dict:
    """Kiểm tra thời tiết, độ mặn và rủi ro môi trường."""
    try:
        response = requests.get(f"{BACKEND_URL}/check-environment?location={location}", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": f"Không thể kết nối Backend: {str(e)}"}

def get_action_recommendation(alert_type: str) -> dict:
    """Lấy hướng dẫn hành động cụ thể."""
    try:
        response = requests.get(f"{BACKEND_URL}/get-action?alert_type={alert_type}", timeout=10)
        return response.json()
    except Exception as e:
        return {"action_recommendation": "Liên hệ kỹ thuật viên ngay lập tức."}


# --- 4. KHỞI TẠO AI SESSION ---
if "chat_session" not in st.session_state:
    system_prompt = """
    Bạn là Chuyên gia AI hệ thống Aquaculture Intelligence. 
    Nhiệm vụ: Tư vấn rủi ro môi trường cho doanh nghiệp và bà con nông dân miền Tây.
    Phong cách: Chuyên nghiệp, tin cậy nhưng gần gũi, dễ hiểu (xưng tôi, gọi bà con).
    Quy tắc: Luôn check_environment trước, nếu rủi ro phải get_action_recommendation ngay.
    Trả lời bằng tiếng Việt, rõ ràng, có số liệu cụ thể.
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


# --- 5. SIDEBAR ---
with st.sidebar:
    # Logo text thay vì ảnh bị lỗi
    st.markdown("""
    <div style="text-align:center; padding: 1.5rem 0 1rem 0;">
        <div style="font-size: 3rem;">🦐</div>
        <div style="font-family: 'Sora', sans-serif; font-size: 1.3rem; font-weight: 700; color: #F8FAFC; margin-top: 0.3rem;">AquaAI</div>
        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.2rem;">Enterprise Platform v1.0.1</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="padding: 0.75rem 0; font-size: 0.82rem; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em;">
        Trạng thái hệ thống
    </div>
    """, unsafe_allow_html=True)

    # Kiểm tra kết nối Backend
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=3)
        backend_ok = r.status_code == 200
    except:
        backend_ok = False

    if backend_ok:
        st.markdown("""<div style="display:flex;align-items:center;gap:8px;padding:10px 12px;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);border-radius:10px;margin-bottom:8px;">
            <span style="color:#34D399;font-size:10px;">●</span>
            <span style="color:#A7F3D0;font-size:0.82rem;font-weight:500;">Backend: Online</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="display:flex;align-items:center;gap:8px;padding:10px 12px;background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);border-radius:10px;margin-bottom:8px;">
            <span style="color:#F87171;font-size:10px;">●</span>
            <span style="color:#FCA5A5;font-size:0.82rem;font-weight:500;">Backend: Offline</span>
        </div>""", unsafe_allow_html=True)

    ai_ok = st.session_state.get("chat_session") is not None
    if ai_ok:
        st.markdown("""<div style="display:flex;align-items:center;gap:8px;padding:10px 12px;background:rgba(14,165,233,0.15);border:1px solid rgba(14,165,233,0.3);border-radius:10px;margin-bottom:8px;">
            <span style="color:#38BDF8;font-size:10px;">●</span>
            <span style="color:#BAE6FD;font-size:0.82rem;font-weight:500;">Gemini AI: Sẵn sàng</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="display:flex;align-items:center;gap:8px;padding:10px 12px;background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);border-radius:10px;margin-bottom:8px;">
            <span style="color:#F87171;font-size:10px;">●</span>
            <span style="color:#FCA5A5;font-size:0.82rem;font-weight:500;">Gemini AI: Lỗi API Key</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="padding: 0.5rem 0; font-size: 0.82rem; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em;">
        Khu vực theo dõi
    </div>
    """, unsafe_allow_html=True)

    locations = ["Bến Tre", "Cà Mau", "Sóc Trăng", "Bạc Liêu", "Tiền Giang", "Kiên Giang"]
    for loc in locations:
        st.markdown(f"""<div style="padding: 8px 12px; border-radius: 8px; color: #CBD5E1; font-size: 0.84rem; cursor:pointer; margin-bottom:2px;">
            📍 {loc}
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🗑️ Xóa lịch sử trò chuyện"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div style="position:absolute; bottom:1.5rem; left:1.5rem; right:1.5rem; text-align:center; font-size:0.7rem; color:#475569;">
        © 2026 AquaAI Enterprise<br>Giải pháp chuyển đổi số ĐBSCL
    </div>
    """, unsafe_allow_html=True)


# --- 6. GIAO DIỆN CHÍNH ---

# Header đẹp
st.markdown("""
<div class="aqua-header">
    <h1>🦐 Trung tâm Giám sát Thủy sản ĐBSCL</h1>
    <p>Hệ thống AI phân tích môi trường & tư vấn rủi ro cho doanh nghiệp và bà con nông dân</p>
</div>
""", unsafe_allow_html=True)

# --- METRICS ---
st.markdown('<div class="section-label">📊 Tổng quan hôm nay</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
m1.metric("🌡️ Môi trường", "Tối ưu", help="Dữ liệu từ trạm vệ tinh OWM.")
m2.metric("⚠️ Chỉ số Rủi ro", "15%", delta="-5%", delta_color="inverse", help="So với tuần trước.")
m3.metric("📡 Thiết bị Online", "8/8", delta="100%", help="Số trạm đang hoạt động.")
m4.metric("🦐 Vụ nuôi hiện tại", "Tuần 12", help="Tính từ ngày thả giống.")

st.markdown("<br>", unsafe_allow_html=True)

# --- BIỂU ĐỒ PLOTLY (Fix lỗi st.line_chart bị scale sai) ---
st.markdown('<div class="section-label">📈 Phân tích & Dự báo Rủi ro 7 ngày tới</div>', unsafe_allow_html=True)

days = ["14/4", "15/4", "16/4", "17/4", "18/4", "19/4", "20/4"]
shock_heat = [10, 15, 12, 45, 80, 20, 15]
salinity_drop = [5, 5, 8, 30, 95, 40, 10]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=days, y=shock_heat,
    name="Sốc nhiệt (%)",
    mode="lines+markers",
    line=dict(color="#0EA5E9", width=3),
    marker=dict(size=8, symbol="circle"),
    fill="tozeroy",
    fillcolor="rgba(14,165,233,0.08)"
))

fig.add_trace(go.Scatter(
    x=days, y=salinity_drop,
    name="Giảm mặn (%)",
    mode="lines+markers",
    line=dict(color="#10B981", width=3, dash="dot"),
    marker=dict(size=8, symbol="diamond"),
    fill="tozeroy",
    fillcolor="rgba(16,185,129,0.06)"
))

# Vùng cảnh báo
fig.add_hrect(y0=50, y1=100, fillcolor="rgba(239,68,68,0.07)",
              line_width=0, annotation_text="⚠️ Ngưỡng nguy hiểm",
              annotation_position="top right",
              annotation_font_color="#EF4444", annotation_font_size=12)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Be Vietnam Pro, sans-serif", color="#0F172A"),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        bgcolor="rgba(255,255,255,0.8)", bordercolor="#E2E8F0", borderwidth=1
    ),
    xaxis=dict(
        gridcolor="#F1F5F9", linecolor="#E2E8F0", tickfont=dict(size=12)
    ),
    yaxis=dict(
        gridcolor="#F1F5F9", linecolor="#E2E8F0", tickfont=dict(size=12),
        range=[0, 105],
        ticksuffix="%"
    ),
    hovermode="x unified",
    margin=dict(l=10, r=10, t=40, b=10),
    height=320,
)

st.plotly_chart(fig, use_container_width=True)
st.caption("📡 Dữ liệu AI phân tích từ vệ tinh & trạm đo – Khu vực ĐBSCL. Dự báo Bão ngày 17–18/4.")

st.markdown("<br>", unsafe_allow_html=True)

# --- CHATBOX ---
st.markdown("---")
st.markdown("""
<div style="text-align:center; margin-bottom:1rem;">
    <div style="font-family:'Sora',sans-serif; font-size:1.3rem; font-weight:700; color:#0F172A;">💬 Cố vấn Thủy sản AI</div>
    <div style="color:#64748B; font-size:0.85rem; margin-top:0.3rem;">Hỏi bất kỳ điều gì về môi trường ao nuôi, thời tiết, dịch bệnh – AI sẽ trả lời ngay</div>
</div>
""", unsafe_allow_html=True)

# Gợi ý câu hỏi nếu chưa có chat
if not st.session_state.get("messages"):
    c1, c2, c3 = st.columns(3)
    suggestions = [
        ("🌊", "Thời tiết Bến Tre hôm nay thế nào?", "Kiểm tra thời tiết"),
        ("⚠️", "Dự báo bão ảnh hưởng ao nuôi ra sao?", "Dự báo rủi ro"),
        ("🦠", "Phòng bệnh đốm trắng mùa mưa thế nào?", "Hỏi về dịch bệnh"),
    ]
    for col, (icon, prompt_text, label) in zip([c1, c2, c3], suggestions):
        with col:
            if st.button(f"{icon} {label}", key=f"suggest_{label}", use_container_width=True):
                st.session_state._quick_prompt = prompt_text
                st.rerun()

# Xử lý quick prompt
quick_prompt = st.session_state.pop("_quick_prompt", None)

# Hiển thị lịch sử chat
for message in st.session_state.get("messages", []):
    avatar = "🧑‍🌾" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Ô nhập liệu
prompt = st.chat_input("Hỏi tôi... VD: Thời tiết Bến Tre sao rồi bà con?") or quick_prompt

if prompt:
    with st.chat_message("user", avatar="🧑‍🌾"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🤖"):
        if not st.session_state.get("chat_session"):
            st.error("⚠️ AI không hoạt động. Vui lòng kiểm tra GEMINI_API_KEY trong secrets.")
        else:
            with st.spinner("🔍 Đang phân tích dữ liệu trạm đo..."):
                try:
                    response = st.session_state.chat_session.send_message(prompt)
                    reply = response.text
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    err_msg = f"⚠️ Có lỗi xảy ra: {str(e)}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding: 1rem 0; color: #94A3B8; font-size:0.78rem;">
    © 2026 <strong style="color:#0EA5E9;">AquaAI Enterprise Platform</strong> &nbsp;|&nbsp; 
    Giải pháp chuyển đổi số nông nghiệp ĐBSCL &nbsp;|&nbsp; 
    Powered by Google Gemini AI
</div>
""", unsafe_allow_html=True)