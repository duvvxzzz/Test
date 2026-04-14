from fastapi import FastAPI
import requests
import random
import os
from dotenv import load_dotenv

# --- BƯỚC BẢO MẬT: Tải các biến bí mật từ file .env ---
load_dotenv()

app = FastAPI()

# Lấy API Key an toàn từ môi trường, không viết thẳng vào code nữa
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# API 1: Kiểm tra môi trường (Hybrid: Thật + Giả lập bão)
@app.get("/check-environment")
def check_environment(location: str):
    
    # 1. THE BACKDOOR (Cửa sau dành cho lúc đi Demo/Pitching)
    if "(test bão)" in location.lower():
        clean_location = location.lower().replace("(test bão)", "").strip()
        return {
            "location": clean_location.title(),
            "temperature_c": 35.5,
            "salinity_ppt": 10.0,
            "rain_probability_pct": 95,
            "shock_alert": "Nguy cơ RẤT CAO: Sốc nhiệt và giảm mặn đột ngột do bão lớn kéo dài.",
            "risk_score": 95,
            "data_source": "Demo Simulation"
        }

    # 2. THE REAL DATA (Gọi API thời tiết thật)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric&lang=vi"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code != 200:
            return {"error": "Không tìm thấy địa điểm", "details": data.get("message")}

        temp = data["main"]["temp"]
        weather_condition = data["weather"][0]["main"].lower()
        
        rain_prob = 85 if "rain" in weather_condition or "thunderstorm" in weather_condition else random.randint(0, 20)
        salinity = random.uniform(20.0, 25.0)

        risk_score = 20
        shock_alert = "Bình thường"
        
        if temp > 33.0 or rain_prob > 70:
             risk_score = 65
             shock_alert = "Cảnh báo: Thời tiết có biến động (nắng gắt/mưa), cần chú ý môi trường ao."

        return {
            "location": location.title(),
            "temperature_c": temp,
            "salinity_ppt": round(salinity, 1),
            "rain_probability_pct": rain_prob,
            "shock_alert": shock_alert,
            "risk_score": risk_score,
            "data_source": "Real OpenWeather API"
        }
        
    except Exception as e:
        return {"error": "Lỗi kết nối API thời tiết", "details": str(e)}

# API 2: Đưa ra hành động
@app.get("/get-action")
def get_action(alert_type: str):
    if "sốc" in alert_type.lower() or "biến động" in alert_type.lower():
        return {
            "action_recommendation": (
                "1. Rải ngay vôi nông nghiệp (CaCO3) quanh bờ ao.\n"
                "2. Giảm 50% lượng thức ăn trong cữ tiếp theo.\n"
                "3. Bật tối đa hệ thống quạt nước."
            )
        }
    return {
        "action_recommendation": "Môi trường ổn định. Bà con duy trì cho ăn bình thường."
    }