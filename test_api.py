import os
import requests
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("❌ 沒有讀到 GOOGLE_API_KEY，請確認 .env 檔案")

# 選擇模型
MODEL_NAME = "models/gemini-2.5-flash"   # 或 "models/gemini-2.5-pro"

API_URL = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent?key={API_KEY}"
HEADERS = {"Content-Type": "application/json"}

# 測試 payload
payload = {
    "contents": [
        {"parts": [{"text": "Hello Gemini, 請回覆一段簡單的測試訊息。"}]}
    ]
}

print("👉 測試 API URL:", API_URL)

resp = requests.post(API_URL, headers=HEADERS, json=payload)

print("Status:", resp.status_code)
print("Response:")
print(resp.text)
