import json
import re
import requests
from init_sys import API_URL, HEADERS

def clean_json_text(text):
    """清理 JSON 格式的文字，去除多餘的 Markdown 標記"""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"```$", "", text)
    return text

class UseCaseListAgent:

    @staticmethod
    async def generate_usecase_list(project_name: str, actors: list):
        """根據 5 個 Actor 產出每人 3 個使用案例名稱與描述，返回 JSON 字典"""

        prompt = f"""
        你是一名系統分析師，請根據以下角色清單，為每位使用者設計 3 個最常見的使用案例，包含「使用案例名稱」與「使用案例描述」，使用繁體中文。

        輸出格式如下（共 15 筆）：
        {{
        "project_name": "{project_name}",
        "use_case_list": [
            {{
              "actor": "角色名稱",
              "use_case_name": "使用案例名稱",
              "description": "使用案例簡要描述"
            }},
            ...
        ]
        }}

        請勿產出除 JSON 以外的說明文字，也不要加上 Markdown 標記（如 ```json）。
        以下是角色清單：
        {json.dumps(actors, indent=4, ensure_ascii=False)}
        """

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 1.0,
                "maxOutputTokens": 2048,
                "topP": 0.8,
                "topK": 10
            }
        }

        response = requests.post(API_URL, headers=HEADERS, json=data)

        if response.status_code == 200:
            reply_text = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
            try:
                cleaned_text = clean_json_text(reply_text)  # 清理 Markdown 格式
                parsed_json = json.loads(cleaned_text)  # 將清理後的文字轉換為字典
                print(f"✅ 使用案例名稱與描述已生成：{parsed_json}")
                return parsed_json  # 返回 JSON 字典
            except json.JSONDecodeError as e:
                print("❌ JSON 解析失敗:", str(e))
                return {"error": "JSON parse failed", "raw": reply_text}
        else:
            print(f"❌ API 請求失敗：{response.status_code}")
            return {"error": "API failed", "status_code": response.status_code, "response": response.text}