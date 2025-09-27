import os
import requests
import json
from utilits.utis import clean_json_text
from init_sys import API_URL, HEADERS 

class ProjectAgent: 

    @staticmethod
    async def get_json(project_name:str): #persona:ser = 提示內容 generate 方法 get.json
        
        PROMPT_TEXT_JSON = f"""
        你是一名優秀且經驗豐富的系統設計師，你的目標是設計一個高效、可擴展且易於維護的資訊系統，而我將提供與此資訊系統的名稱，依照系統名稱設計出有關此系統的 name(專案名稱)、 description(中文的專案描述)、architecture(系統架構)、frontend_language(前端語言)、frontend_platform(前端平台)、frontend_library(前端程式庫)、backend_language(後端語言)、backend_platform(後端平台)、backend_library(後端函式庫)。

        請依照以下產生UTF-8格式的json檔案，產生中文時使用繁體(不產生除了json檔以外的文字):
        {{
            "project_name": "{project_name}",
            "description": "xxx",
            "architecture": "xxx",
            "frontend":{{
                "language": "xxx",
                "platform": "xxx",
                "library": "xxx"
            }},
            "backend": {{
                "language": "xxx",
                "platform": "xxx",
                "library": "xxx"
            }}
        }}

        我的系統提示如下:
        -資訊系統名稱:{project_name}
        """

        DATA = {
            "contents": [{"parts": [{"text": PROMPT_TEXT_JSON}]}],
            "generationConfig": {
                "temperature": 1.0,
                "maxOutputTokens": 2048,
                "topP": 0.8,
                "topK": 10
            }
        }

        response = requests.post(API_URL, headers=HEADERS, json=DATA)
        if response.status_code == 200:
            reply_text = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
            try:
                cleaned_text = clean_json_text(reply_text)  # **清理 Markdown 格式**
                print(f"Gemini 回覆: {cleaned_text}")
                json_data = json.loads(cleaned_text)
                print(f"Gemini 回覆: {json_data}")
                return json_data
            except json.JSONDecodeError:
                print("無法解析 API 回應的 JSON")
        else:
            print(f"API 請求失敗，狀態碼: {response.status_code}")


