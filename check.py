import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("🔍 Đang quét các model còn 'vé' cho bạn...\n")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        # In ra tên để mình copy vào app.py
        print(f"✅ Tên model: {m.name.replace('models/', '')}")