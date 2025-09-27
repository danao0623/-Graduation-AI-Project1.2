import json
import re
import requests
from utilits.utis import clean_json_text
from init_sys import API_URL, HEADERS

class ProjectAgent:

    @staticmethod
    async def generate_usecase_actors(project_name: str):
        """根據專案名稱產生 5 個使用者角色 (Actor) 及其描述，輸出 JSON"""

        PROMPT_TEXT_JSON = f"""
        你是一位資深系統分析師，請根據「{project_name}」的系統設計目標：
        請產生 5 位系統使用者（Actor），包含每位使用者的編號（從 1 開始）、名稱與角色描述。請以 JSON 格式回覆，不要加上解釋文字或 Markdown。
        輸出格式如下：
        {{
            "project_name": "{project_name}",
            "use_case_actor": [
                {{
                    "id": 1,
                    "name": "使用者名稱",
                    "description": "這個使用者的角色與職責描述"
                }},
                ...
            ]
        }}
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
                cleaned_text = clean_json_text(reply_text)  # 清理 Markdown 格式
                print(f"Gemini 回覆: {cleaned_text}")
                json_data = json.loads(cleaned_text)  # 將清理後的文字轉換為字典
                print(f"Gemini 回覆解析為字典: {json_data}")
                return json_data  # 返回字典
            except json.JSONDecodeError as e:
                print("❌ JSON 解析失敗：", str(e))
                return {"error": "JSON parse failed", "raw": reply_text}
        else:
            print(f"❌ API 請求失敗：{response.status_code}")
            return {"error": f"API failed", "status_code": response.status_code, "response": response.text}