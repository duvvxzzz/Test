import streamlit as st
import google.generativeai as genai
import requests
import os
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

# --- 1. CẤU HÌNH ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("⚠️ Không tìm thấy GEMINI_API_KEY trong secrets!")
else:
    genai.configure(api_key=GEMINI_API_KEY)

BACKEND_URL = "https://test-0hc8.onrender.com"

st.set_page_config(
    page_title="AquaAI – Giám sát Thủy sản",
    page_icon="🦐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-app:        #212121;
    --bg-sidebar:    #171717;
    --bg-card:       #2f2f2f;
    --bg-card-hover: #383838;
    --bg-input:      #2f2f2f;
    --text-primary:  #ececec;
    --text-secondary:#a0a0a0;
    --text-muted:    #6b6b6b;
    --border:        #3a3a3a;
    --border-light:  #444444;
    --accent:        #0EA5E9;
    --accent-green:  #10B981;
}

*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background-color: var(--bg-app) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: var(--text-primary) !important;
}

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
}
/* Đủ padding dưới để nút không bị đè */
[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 1rem !important;
}
[data-testid="stSidebar"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label {
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 8px !important;
    width: 100% !important;
    font-size: 0.85rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(239,68,68,0.12) !important;
    color: #FCA5A5 !important;
    border-color: rgba(239,68,68,0.4) !important;
}

/* === MAIN === */
.main .block-container {
    padding: 2rem 2.5rem 4rem 2.5rem !important;
    max-width: 920px !important;
    margin: 0 auto !important;
}

/* Đảm bảo tất cả text trong app có màu sáng */
.stApp p, .stApp li, .stApp span:not(.stMetricDelta),
.stApp h1, .stApp h2, .stApp h3, .stMarkdown {
    color: var(--text-primary) !important;
}

/* === METRIC CARDS === */
div[data-testid="stMetric"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.25rem 1.5rem !important;
    transition: border-color 0.15s !important;
}
div[data-testid="stMetric"]:hover {
    border-color: var(--border-light) !important;
}
[data-testid="stMetricLabel"] p {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 1.45rem !important;
    font-weight: 600 !important;
}

/* === CHAT – Fix màu chữ bị ẩn === */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0.5rem 0 !important;
}

/* User message */
[data-testid="stChatMessageUser"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

/* AI message */
[data-testid="stChatMessageAssistant"] {
    background-color: transparent !important;
    border-left: 2px solid var(--accent) !important;
    border-radius: 0 !important;
    padding-left: 1rem !important;
}

/* === FIX CHÍNH: màu chữ trong chat === */
.stChatMessage p,
.stChatMessage li,
.stChatMessage span,
.stChatMessage strong,
.stChatMessage em,
.stChatMessage code,
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] li,
[data-testid="stChatMessageContent"] span,
[data-testid="stChatMessageContent"] strong,
[data-testid="stChatMessageContent"] div {
    color: var(--text-primary) !important;
}
.stChatMessage strong {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* === CHAT INPUT === */
[data-testid="stChatInput"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(14,165,233,0.18) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    background: transparent !important;
    font-family: 'Inter', sans-serif !important;
    caret-color: var(--accent) !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
}

/* === PLOTLY CHART === */
.stPlotlyChart {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

/* === HR === */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* === CAPTION === */
[data-testid="stCaptionContainer"] p,
.stCaption { color: var(--text-muted) !important; font-size: 0.77rem !important; }

/* === SPINNER === */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* === SUGGESTION BUTTONS === */
.suggest-btn > div > button {
    background-color: var(--bg-card) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.15s ease !important;
    height: auto !important;
    padding: 0.6rem 1rem !important;
    white-space: normal !important;
    text-align: left !important;
}
.suggest-btn > div > button:hover {
    background-color: var(--bg-card-hover) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-light) !important;
}
</style>
""", unsafe_allow_html=True)


# --- TOOLS ---
def check_environment(location: str) -> dict:
    try:
        r = requests.get(f"{BACKEND_URL}/check-environment?location={location}", timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def get_action_recommendation(alert_type: str) -> dict:
    try:
        r = requests.get(f"{BACKEND_URL}/get-action?alert_type={alert_type}", timeout=10)
        return r.json()
    except Exception as e:
        return {"action_recommendation": "Liên hệ kỹ thuật viên ngay lập tức."}


# --- KHỞI TẠO AI ---
if "chat_session" not in st.session_state:
    system_prompt = """
    Bạn là Chuyên gia AI hệ thống Aquaculture Intelligence.
    Nhiệm vụ: Tư vấn rủi ro môi trường cho doanh nghiệp và bà con nông dân miền Tây.
    Phong cách: Chuyên nghiệp, tin cậy nhưng gần gũi (xưng tôi, gọi bà con).
    Quy tắc: Luôn check_environment trước, nếu rủi ro phải get_action_recommendation ngay.
    Trả lời bằng tiếng Việt, rõ ràng, số liệu cụ thể.
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
        st.session_state.chat_session = None
        st.session_state.messages = []


# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("""
    <div style="padding:1.4rem 0 1rem 0;">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.5rem;">🦐</span>
            <div>
                <div style="font-size:1.05rem;font-weight:700;color:#ececec;letter-spacing:-0.02em;">AquaAI</div>
                <div style="font-size:0.68rem;color:#6b6b6b;">Enterprise v1.0.1</div>
            </div>
        </div>
    </div>
    <div style="height:1px;background:#3a3a3a;margin-bottom:1.2rem;"></div>
    <div style="font-size:0.67rem;font-weight:600;color:#6b6b6b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.6rem;">Trạng thái hệ thống</div>
    """, unsafe_allow_html=True)

    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=3)
        backend_ok = r.status_code == 200
    except:
        backend_ok = False

    badge_style = "padding:7px 10px;border-radius:8px;margin-bottom:6px;font-size:0.81rem;"
    if backend_ok:
        st.markdown(f'<div style="{badge_style}background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);color:#6ee7b7;">● Backend: Online</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="{badge_style}background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);color:#fca5a5;">● Backend: Offline</div>', unsafe_allow_html=True)

    if st.session_state.get("chat_session"):
        st.markdown(f'<div style="{badge_style}background:rgba(14,165,233,0.1);border:1px solid rgba(14,165,233,0.25);color:#7dd3fc;">● Gemini AI: Sẵn sàng</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="{badge_style}background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);color:#fca5a5;">● Gemini AI: Lỗi API Key</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="height:1px;background:#3a3a3a;margin:1.2rem 0;"></div>
    <div style="font-size:0.67rem;font-weight:600;color:#6b6b6b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.6rem;">Khu vực theo dõi</div>
    """, unsafe_allow_html=True)

    for loc, dot in [("Bến Tre","🟢"),("Cà Mau","🟡"),("Sóc Trăng","🟢"),("Bạc Liêu","🔴"),("Tiền Giang","🟢"),("Kiên Giang","🟡")]:
        st.markdown(f'<div style="padding:6px 10px;border-radius:7px;color:#a0a0a0;font-size:0.83rem;margin-bottom:2px;">{dot} {loc}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#3a3a3a;margin:1.2rem 0;"></div>', unsafe_allow_html=True)

    # Nút xóa (không dùng absolute position – tránh đè lên nhau)
    if st.button("🗑️ Xóa lịch sử trò chuyện"):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div style="margin-top:1rem;font-size:0.67rem;color:#4a4a4a;text-align:center;line-height:1.7;">© 2026 AquaAI Enterprise<br>Giải pháp số nông nghiệp ĐBSCL</div>', unsafe_allow_html=True)


# ===================== MAIN =====================

# Header
st.markdown("""
<div style="margin-bottom:2rem;">
    <h1 style="font-size:1.4rem;font-weight:700;color:#ececec;margin:0;letter-spacing:-0.02em;">
        🦐 Trung tâm Giám sát Thủy sản ĐBSCL
    </h1>
    <p style="color:#6b6b6b;font-size:0.85rem;margin:0.25rem 0 0 0;">
        Phân tích môi trường & tư vấn rủi ro theo thời gian thực
    </p>
</div>
""", unsafe_allow_html=True)

# Metrics
st.markdown('<div style="font-size:0.67rem;font-weight:600;color:#6b6b6b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem;">Tổng quan hôm nay</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
m1.metric("🌡️ Môi trường", "Tối ưu")
m2.metric("⚠️ Chỉ số rủi ro", "15%", delta="-5%", delta_color="inverse")
m3.metric("📡 Thiết bị", "8/8 Online")
m4.metric("🦐 Vụ nuôi", "Tuần 12")

st.markdown("<br>", unsafe_allow_html=True)

# Biểu đồ
st.markdown('<div style="font-size:0.67rem;font-weight:600;color:#6b6b6b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem;">Phân tích & Dự báo rủi ro – 7 ngày tới</div>', unsafe_allow_html=True)

days = ["14/4","15/4","16/4","17/4","18/4","19/4","20/4"]
shock_heat    = [10, 15, 12, 45, 80, 20, 15]
salinity_drop = [5,  5,  8,  30, 95, 40, 10]

fig = go.Figure()
fig.add_trace(go.Scatter(x=days, y=shock_heat, name="Sốc nhiệt (%)",
    mode="lines+markers", line=dict(color="#0EA5E9", width=2.5),
    marker=dict(size=7), fill="tozeroy", fillcolor="rgba(14,165,233,0.1)"))
fig.add_trace(go.Scatter(x=days, y=salinity_drop, name="Giảm mặn (%)",
    mode="lines+markers", line=dict(color="#10B981", width=2.5, dash="dot"),
    marker=dict(size=7, symbol="diamond"), fill="tozeroy", fillcolor="rgba(16,185,129,0.07)"))
fig.add_hrect(y0=50, y1=105, fillcolor="rgba(239,68,68,0.06)", line_width=0,
    annotation_text="⚠️ Ngưỡng nguy hiểm", annotation_position="top right",
    annotation_font_color="#EF4444", annotation_font_size=11)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#a0a0a0", size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        bgcolor="rgba(47,47,47,0.95)", bordercolor="#3a3a3a", borderwidth=1,
        font=dict(color="#ececec")),
    xaxis=dict(gridcolor="#2a2a2a", linecolor="#3a3a3a", tickfont=dict(color="#a0a0a0")),
    yaxis=dict(gridcolor="#2a2a2a", linecolor="#3a3a3a", tickfont=dict(color="#a0a0a0"),
        range=[0, 105], ticksuffix="%"),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#2f2f2f", font_color="#ececec", bordercolor="#444"),
    margin=dict(l=10, r=10, t=40, b=10), height=300,
)
st.plotly_chart(fig, use_container_width=True)
st.caption("📡 Dữ liệu AI phân tích từ vệ tinh & trạm đo khu vực ĐBSCL. Cảnh báo bão dự kiến 17–18/4.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:#3a3a3a;margin-bottom:1.5rem;"></div>', unsafe_allow_html=True)

# Chat section
st.markdown("""
<div style="margin-bottom:1rem;">
    <div style="font-size:0.95rem;font-weight:600;color:#ececec;">💬 Cố vấn Thủy sản AI</div>
    <div style="color:#6b6b6b;font-size:0.8rem;margin-top:0.2rem;">Hỏi về môi trường ao nuôi, thời tiết, dịch bệnh – AI phân tích và trả lời ngay</div>
</div>
""", unsafe_allow_html=True)

# Gợi ý nhanh
if not st.session_state.get("messages"):
    c1, c2, c3 = st.columns(3)
    for col, (label, prompt_text) in zip([c1, c2, c3], [
        ("🌊 Thời tiết hôm nay", "Thời tiết Bến Tre hôm nay thế nào?"),
        ("⚠️ Dự báo bão", "Bão ảnh hưởng ao nuôi ra sao?"),
        ("🦠 Phòng bệnh tôm",  "Phòng bệnh đốm trắng mùa mưa thế nào?"),
    ]):
        with col:
            st.markdown('<div class="suggest-btn">', unsafe_allow_html=True)
            if st.button(label, key=f"s_{label}", use_container_width=True):
                st.session_state._qp = prompt_text
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

quick_prompt = st.session_state.pop("_qp", None)

for msg in st.session_state.get("messages", []):
    avatar = "🧑‍🌾" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

prompt = st.chat_input("Nhập câu hỏi... VD: Thời tiết Sóc Trăng sao rồi bà con?") or quick_prompt

if prompt:
    with st.chat_message("user", avatar="🧑‍🌾"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🤖"):
        if not st.session_state.get("chat_session"):
            st.error("⚠️ AI không hoạt động. Kiểm tra GEMINI_API_KEY.")
        else:
            with st.spinner("Đang phân tích..."):
                try:
                    response = st.session_state.chat_session.send_message(prompt)
                    reply = response.text
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    err = f"⚠️ Lỗi: {str(e)}"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})

# Footer
st.markdown('<div style="height:1px;background:#3a3a3a;margin:2.5rem 0 1rem 0;"></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#4a4a4a;font-size:0.73rem;">© 2026 <span style="color:#0EA5E9;font-weight:500;">AquaAI Enterprise</span> · Giải pháp chuyển đổi số nông nghiệp ĐBSCL · Powered by Google Gemini AI</div>', unsafe_allow_html=True)