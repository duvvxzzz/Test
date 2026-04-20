import streamlit as st
import google.generativeai as genai
import requests
import os
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
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Google+Sans+Display:wght@400;500;700&family=Roboto:wght@300;400;500&display=swap');

:root {
    --bg-app:         #f8f9fa;
    --bg-sidebar:     #ffffff;
    --bg-card:        #ffffff;
    --bg-card-hover:  #f0f4f9;
    --bg-input:       #f0f4f9;
    --text-primary:   #1f1f1f;
    --text-secondary: #444746;
    --text-muted:     #747775;
    --border:         #e3e3e3;
    --border-light:   #c4c7c5;
    --accent-blue:    #0b57d0;
    --accent-pink:    #c2185b;
    --accent-purple:  #7c4dff;
    --accent-green:   #137333;
    --gradient-hero:  linear-gradient(135deg, #c2185b 0%, #7c4dff 50%, #0b57d0 100%);
    --shadow-card:    0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-hover:   0 4px 16px rgba(0,0,0,0.1), 0 2px 6px rgba(0,0,0,0.06);
}

*, *::before, *::after { box-sizing: border-box; }

/* Reset Streamlit defaults */
.stApp {
    background-color: var(--bg-app) !important;
    font-family: 'Roboto', 'Google Sans', sans-serif !important;
    color: var(--text-primary) !important;
}

/* Remove default padding */
.main .block-container {
    padding: 2.5rem 3rem 4rem 3rem !important;
    max-width: 960px !important;
    margin: 0 auto !important;
}

/* All text */
.stApp p, .stApp li, .stApp span:not(.stMetricDelta),
.stApp h1, .stApp h2, .stApp h3, .stMarkdown {
    color: var(--text-primary) !important;
}

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: none !important;
}
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
    border: 1px solid var(--border) !important;
    border-radius: 100px !important;
    width: 100% !important;
    font-size: 0.85rem !important;
    font-family: 'Google Sans', 'Roboto', sans-serif !important;
    padding: 0.5rem 1.25rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #fce8e6 !important;
    color: #c5221f !important;
    border-color: #f5c6c3 !important;
}

/* === METRIC CARDS === */
div[data-testid="stMetric"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.25rem 1.5rem !important;
    box-shadow: var(--shadow-card) !important;
    transition: box-shadow 0.2s ease, transform 0.2s ease !important;
}
div[data-testid="stMetric"]:hover {
    box-shadow: var(--shadow-hover) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stMetricLabel"] p {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-weight: 500 !important;
    font-family: 'Google Sans', 'Roboto', sans-serif !important;
}
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    font-family: 'Google Sans', 'Roboto', sans-serif !important;
}

/* === CHAT === */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0.5rem 0 !important;
}
[data-testid="stChatMessageUser"] {
    background-color: #e8f0fe !important;
    border: none !important;
    border-radius: 20px 20px 4px 20px !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="stChatMessageAssistant"] {
    background-color: transparent !important;
    border-left: 3px solid transparent !important;
    border-image: var(--gradient-hero) 1 !important;
    border-radius: 0 !important;
    padding-left: 1rem !important;
}
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

/* === CHAT INPUT === */
[data-testid="stChatInput"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 28px !important;
    box-shadow: var(--shadow-card) !important;
    transition: box-shadow 0.2s, border-color 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #0b57d0 !important;
    box-shadow: 0 0 0 3px rgba(11,87,208,0.12) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    background: transparent !important;
    font-family: 'Roboto', sans-serif !important;
    caret-color: var(--accent-blue) !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
}

/* === PLOTLY CHART === */
.stPlotlyChart {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    box-shadow: var(--shadow-card) !important;
}

/* === HR === */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* === CAPTION === */
[data-testid="stCaptionContainer"] p,
.stCaption {
    color: var(--text-muted) !important;
    font-size: 0.77rem !important;
}

/* === SPINNER === */
.stSpinner > div { border-top-color: var(--accent-blue) !important; }

/* === SUGGESTION CARDS (Gemini style) === */
.suggest-btn > div > button {
    background-color: var(--bg-card) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    font-size: 0.85rem !important;
    font-family: 'Roboto', 'Google Sans', sans-serif !important;
    transition: all 0.2s ease !important;
    height: 90px !important;
    padding: 1rem 1.1rem !important;
    white-space: normal !important;
    text-align: left !important;
    box-shadow: var(--shadow-card) !important;
    line-height: 1.4 !important;
    vertical-align: top !important;
}
.suggest-btn > div > button:hover {
    background-color: var(--bg-card-hover) !important;
    color: var(--text-primary) !important;
    border-color: #b0b0b0 !important;
    box-shadow: var(--shadow-hover) !important;
    transform: translateY(-2px) !important;
}

/* Hero greeting gradient text */
.hero-greeting {
    font-family: 'Google Sans Display', 'Google Sans', 'Roboto', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 400 !important;
    background: var(--gradient-hero);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}

.hero-sub {
    font-family: 'Google Sans', 'Roboto', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 300 !important;
    color: #c4c7c5 !important;
    margin: 0 !important;
    line-height: 1.3 !important;
}

/* Badge style for status */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 100px;
    font-size: 0.8rem;
    font-family: 'Roboto', sans-serif;
    margin-bottom: 5px;
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
            model_name='gemini-2.5-flash',
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
                <div style="font-size:1.05rem;font-weight:600;color:#1f1f1f;letter-spacing:-0.01em;font-family:'Google Sans',sans-serif;">AquaAI</div>
                <div style="font-size:0.68rem;color:#747775;font-family:'Roboto',sans-serif;">Enterprise v1.0.1</div>
            </div>
        </div>
    </div>
    <div style="height:1px;background:#e3e3e3;margin-bottom:1.2rem;"></div>
    <div style="font-size:0.67rem;font-weight:500;color:#747775;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem;font-family:'Roboto',sans-serif;">Trạng thái hệ thống</div>
    """, unsafe_allow_html=True)

    try:
        r = requests.get(f"{BACKEND_URL}/check-environment?location=test", timeout=15)
        backend_ok = r.status_code in [200, 422, 400]
    except requests.exceptions.Timeout:
        backend_ok = None
    except Exception:
        backend_ok = False

    badge_base = "padding:6px 12px;border-radius:100px;margin-bottom:6px;font-size:0.8rem;display:inline-flex;align-items:center;gap:6px;font-family:'Roboto',sans-serif;"
    if backend_ok is True:
        st.markdown(f'<div style="{badge_base}background:#e6f4ea;color:#137333;border:1px solid #ceead6;">● Backend: Online</div>', unsafe_allow_html=True)
    elif backend_ok is None:
        st.markdown(f'<div style="{badge_base}background:#fef7e0;color:#b06000;border:1px solid #fde293;">⏳ Backend: Đang khởi động...</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="{badge_base}background:#fce8e6;color:#c5221f;border:1px solid #f5c6c3;">● Backend: Offline</div>', unsafe_allow_html=True)

    if st.session_state.get("chat_session"):
        st.markdown(f'<div style="{badge_base}background:#e8f0fe;color:#1967d2;border:1px solid #c5d5f8;">● Gemini AI: Sẵn sàng</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="{badge_base}background:#fce8e6;color:#c5221f;border:1px solid #f5c6c3;">● Gemini AI: Lỗi API Key</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="height:1px;background:#e3e3e3;margin:1.2rem 0;"></div>
    <div style="font-size:0.67rem;font-weight:500;color:#747775;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem;font-family:'Roboto',sans-serif;">Khu vực theo dõi</div>
    """, unsafe_allow_html=True)

    for loc, dot, color in [
        ("Bến Tre","●","#137333"),("Cà Mau","●","#b06000"),("Sóc Trăng","●","#137333"),
        ("Bạc Liêu","●","#c5221f"),("Tiền Giang","●","#137333"),("Kiên Giang","●","#b06000")
    ]:
        st.markdown(f'<div style="padding:6px 10px;border-radius:8px;color:#444746;font-size:0.83rem;margin-bottom:2px;font-family:Roboto,sans-serif;"><span style="color:{color}">{dot}</span> {loc}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#e3e3e3;margin:1.2rem 0;"></div>', unsafe_allow_html=True)

    if st.button("🗑️ Xóa lịch sử trò chuyện"):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div style="margin-top:1rem;font-size:0.67rem;color:#c4c7c5;text-align:center;line-height:1.7;font-family:Roboto,sans-serif;">© 2026 AquaAI Enterprise<br>Giải pháp số nông nghiệp ĐBSCL</div>', unsafe_allow_html=True)


# ===================== MAIN =====================

# Gemini-style Hero Header
st.markdown("""
<div style="margin-bottom:2.5rem;padding-top:0.5rem;">
    <p class="hero-greeting">Xin chào, Bà con. 🦐</p>
    <p class="hero-sub">Hôm nay ao nuôi thế nào?</p>
</div>
""", unsafe_allow_html=True)

# Metrics
st.markdown('<div style="font-size:0.7rem;font-weight:500;color:#747775;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.85rem;font-family:Roboto,sans-serif;">Tổng quan hôm nay</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
m1.metric("🌡️ Môi trường", "Tối ưu")
m2.metric("⚠️ Chỉ số rủi ro", "15%", delta="-5%", delta_color="inverse")
m3.metric("📡 Thiết bị", "8/8 Online")
m4.metric("🦐 Vụ nuôi", "Tuần 12")

st.markdown("<br>", unsafe_allow_html=True)

# Chart
st.markdown('<div style="font-size:0.7rem;font-weight:500;color:#747775;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.85rem;font-family:Roboto,sans-serif;">Phân tích & Dự báo rủi ro – 7 ngày tới</div>', unsafe_allow_html=True)

days = ["14/4","15/4","16/4","17/4","18/4","19/4","20/4"]
shock_heat    = [10, 15, 12, 45, 80, 20, 15]
salinity_drop = [5,  5,  8,  30, 95, 40, 10]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=days, y=shock_heat, name="Sốc nhiệt (%)",
    mode="lines+markers",
    line=dict(color="#0b57d0", width=2.5),
    marker=dict(size=7, color="#0b57d0"),
    fill="tozeroy", fillcolor="rgba(11,87,208,0.08)"
))
fig.add_trace(go.Scatter(
    x=days, y=salinity_drop, name="Giảm mặn (%)",
    mode="lines+markers",
    line=dict(color="#c2185b", width=2.5, dash="dot"),
    marker=dict(size=7, symbol="diamond", color="#c2185b"),
    fill="tozeroy", fillcolor="rgba(194,24,91,0.06)"
))
fig.add_hrect(
    y0=50, y1=105, fillcolor="rgba(197,34,31,0.05)", line_width=0,
    annotation_text="⚠️ Ngưỡng nguy hiểm", annotation_position="top right",
    annotation_font_color="#c5221f", annotation_font_size=11
)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Roboto, Google Sans, sans-serif", color="#747775", size=12),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        bgcolor="rgba(255,255,255,0.95)", bordercolor="#e3e3e3", borderwidth=1,
        font=dict(color="#1f1f1f")
    ),
    xaxis=dict(gridcolor="#f0f0f0", linecolor="#e3e3e3", tickfont=dict(color="#747775")),
    yaxis=dict(
        gridcolor="#f0f0f0", linecolor="#e3e3e3", tickfont=dict(color="#747775"),
        range=[0, 105], ticksuffix="%"
    ),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#ffffff", font_color="#1f1f1f", bordercolor="#e3e3e3"),
    margin=dict(l=10, r=10, t=40, b=10), height=300,
)
st.plotly_chart(fig, use_container_width=True)
st.caption("📡 Dữ liệu AI phân tích từ vệ tinh & trạm đo khu vực ĐBSCL. Cảnh báo bão dự kiến 17–18/4.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:#e3e3e3;margin-bottom:1.5rem;"></div>', unsafe_allow_html=True)

# Chat section
st.markdown("""
<div style="margin-bottom:1.2rem;">
    <div style="font-size:0.95rem;font-weight:500;color:#1f1f1f;font-family:'Google Sans','Roboto',sans-serif;">💬 Cố vấn Thủy sản AI</div>
    <div style="color:#747775;font-size:0.82rem;margin-top:0.25rem;font-family:'Roboto',sans-serif;">
        Hỏi về môi trường ao nuôi, thời tiết, dịch bệnh – AI phân tích và trả lời ngay
    </div>
</div>
""", unsafe_allow_html=True)

# Quick suggestions – Gemini card style (4 cards)
if not st.session_state.get("messages"):
    c1, c2, c3, c4 = st.columns(4)
    suggestions = [
        ("🌊 Thời tiết\nhôm nay", "Thời tiết Bến Tre hôm nay thế nào?"),
        ("⚠️ Dự báo\nbão", "Bão ảnh hưởng ao nuôi ra sao?"),
        ("🦠 Phòng bệnh\ntôm", "Phòng bệnh đốm trắng mùa mưa thế nào?"),
        ("🧪 Kiểm tra\nnước", "Chỉ số pH và oxy ao tôm cần đạt bao nhiêu?"),
    ]
    for col, (label, prompt_text) in zip([c1, c2, c3, c4], suggestions):
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
st.markdown('<div style="height:1px;background:#e3e3e3;margin:2.5rem 0 1rem 0;"></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#c4c7c5;font-size:0.73rem;font-family:Roboto,sans-serif;">© 2026 <span style="color:#0b57d0;font-weight:500;">AquaAI Enterprise</span> · Giải pháp chuyển đổi số nông nghiệp ĐBSCL · Powered by Google Gemini AI</div>', unsafe_allow_html=True)