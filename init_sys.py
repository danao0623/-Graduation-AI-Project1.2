import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("❌ 沒有讀到 GOOGLE_API_KEY，請確認 .env 檔案")

MODEL_NAME = "models/gemini-2.5-flash"   # 或 "models/gemini-2.5-pro"

API_URL = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent?key={API_KEY}"
HEADERS = {"Content-Type": "application/json"}
