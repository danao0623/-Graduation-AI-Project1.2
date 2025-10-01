import requests, os
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("❌ 沒有讀到 GOOGLE_API_KEY，請確認 .env 檔案")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
resp = requests.get(url)

print("Status:", resp.status_code)
print("Response:")
print(resp.text)
