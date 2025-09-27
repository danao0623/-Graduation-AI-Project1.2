import os
import json
import httpx
import asyncio
import re
from nicegui import ui,app
from controllers.usecase_controller import UseCaseController
from controllers.actors_controller import ActorController
from init_sys import API_URL, HEADERS

class UseCaseDetail:
    def __init__(self):
        self.actors = []
        self.usecases = []
        self.output = []
       
    @staticmethod
    async def generate(instance,usecase_list:list):
        """產生使用案例細節"""

        instance.output = []

        for uc in usecase_list:
            actor = uc["actor"]
            name = uc["use_case_name"]
            desc = uc["description"]

            print(f"🧠 正在產生：{name}...")
            raw_text = await instance.ask_ai(actor, name, desc)  # 使用實例來呼叫 ask_ai
            instance.output.append({
                "id":uc["id"],
                "actor": actor,
                "use_case_name": name,
                "description": desc,
                "raw_response": raw_text  # 保留原始格式
            })

        for entry in instance.output:
            cleaned = instance.clean_response(entry.get("raw_response", ""))
            try:
                entry["details"] = json.loads(cleaned)
            except Exception as e:
                print("⚠️ 清理失敗項目: ", entry.get("use_case_name"))
                print("原始文字:\n", cleaned)
                entry["details"] = {}
            entry.pop("raw_response", None)
        
            details = entry["details"]
            await UseCaseController.update_use_case(
                use_case_id=entry["id"],
                normal_process=details.get("正常程序", ""),
                exception_process=details.get("例外程序", ""),
                pre_condition=details.get("前置條件", ""),
                post_condition=details.get("後置條件", ""),
                trigger_condition=details.get("觸發條件", "")
            )

        print(json.dumps(instance.output, ensure_ascii=False, indent=2))
        

    async def ask_ai(self, actor, usecase, description):
        prompt = f"""
        你是一名專業系統分析師，請根據以下資訊為使用案例分別產生下列內容：
        1. 正常程序
        2. 例外程序
        3. 觸發條件
        4. 前置條件
        5. 後置條件

        請以 JSON 格式產出，格式如下：
        {{
        "正常程序": "1. ...\\n2. ...\\n...",
        "例外程序": "1. ...：...\\n2. ...：...\\n...",
        "觸發條件": "...",
        "前置條件": "...",
        "後置條件": "..."
        }}

        使用者角色：{actor}
        使用案例名稱：{usecase}
        使用案例描述：{description}
        """
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 1024,
                "topP": 0.9,
                "topK": 10
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, headers=HEADERS, json=data,timeout=100)
        if response.status_code == 200:
            raw = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            return raw
        else:
            print(f"AI API 回傳錯誤: {response.status_code}")
            print(f"response.text: {response.text}")
            return None 

    def clean_response(self, text):
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        return text.strip()
