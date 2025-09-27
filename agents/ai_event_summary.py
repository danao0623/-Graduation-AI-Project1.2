import os
import json
import httpx
import asyncio
from nicegui import app
from init_sys import API_URL, HEADERS
from utilits.utis import clean_json_text
from controllers.event_list_controller import EventListController
from controllers.usecase_controller import UseCaseController
from controllers.event_controller import EventController

JSON_DIR = './json'


@staticmethod
async def ask_event_summary(prompt: str) -> str:
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
            "topP": 0.9,
            "topK": 10
        }
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=HEADERS, json=data,timeout=60.0)
        if response.status_code == 200:
            return response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        return ""

@staticmethod
async def generate_event_summary(project_name: str):

    usecases = []
    for uc in await UseCaseController.get_use_case_by_project(
            app.storage.user.get('selected_project', {}).get('id')):
            actors = [uca.actor.name for uca in uc.actors if uca.actor]
            usecases.append({
                'id': uc.id,
                'use_case_name': uc.name,
                'description': uc.description,
                'actor': actors[0],
                'normal_process': uc.normal_process,
                'exception_process': uc.exception_process,
                'pre_condition': uc.pre_condition,
                'post_condition': uc.post_condition,
            })
    output = []
    

    for uc in usecases:
        use_case_name = uc['use_case_name']
        normal = uc.get('normal_process', '')
        exception = uc.get('exception_process', '')
        print(f"正在處理：{use_case_name}")

        prompts = {
        "正常程序": f"""
        你是一位經驗豐富的系統分析師，正在分析一個資訊系統的使用案例。
        請根據以下「{use_case_name}」的「正常程序」內容，從「Actor」的角度出發，根據每個行為步驟，依照「Request / Process / Response」的順序進行拆解與重組，並轉換為事件導向的三段式結構。請以條列方式精簡描述每一事件，描述語氣務必客觀、簡潔、準確，並避免過度補充。
        ### 分析原則：
        - 每一事件請對應「Request」（使用者請求）、「Process」（系統處理）、「Response」（系統回應）其中一種類型。
        - Request 通常為使用者操作或資料輸入；Process 為系統處理或邏輯判斷；Response 為回饋、畫面更新、結果呈現等。
        - 若原始正常程序中某些步驟過於籠統，請依據常理補全為合理的三段式事件。
        - 僅輸出事件資料，不需額外說明或前後文。
        - 禁止使用 Markdown 語法（如「```」、「#」等），僅輸出純文字 JSON 格式。
        - 輸出結果格式如下：
        ### 原始正常程序：
        {normal}
        {{
        "事件列表": [
            {{ "類型": "Request", "說明": "..." }},
            {{ "類型": "Process", "說明": "..." }},
            {{ "類型": "Response", "說明": "..." }}
        ]
        }}
        """,
        "例外程序": f"""
        你是一位經驗豐富的系統分析師，正在分析一個資訊系統的使用案例。
        請根據以下「{use_case_name}」的「例外程序」內容，從「Actor」的角度出發，根據每個行為步驟，依照「Request / Process / Response」的順序進行拆解與重組，並轉換為事件導向的三段式結構。請以條列方式精簡描述每一事件，描述語氣務必客觀、簡潔、準確，並避免過度補充。
        ### 分析原則：
        - 每一事件請對應「Request」（使用者請求）、「Process」（系統處理）、「Response」（系統回應）其中一種類型。
        - Request 通常為使用者操作或資料輸入；Process 為系統處理或邏輯判斷；Response 為回饋、畫面更新、結果呈現等。
        - 若原始正常程序中某些步驟過於籠統，請依據常理補全為合理的三段式事件。
        - 僅輸出事件資料，不需額外說明或前後文。
        - 禁止使用 Markdown 語法（如「```」、「#」等），僅輸出純文字 JSON 格式。
        - 輸出結果格式如下：
        ### 原始例外程序：
        {exception}
        {{
        "事件列表": [
            {{ "類型": "Request", "說明": "..." }},
            {{ "類型": "Process", "說明": "..." }},
            {{ "類型": "Response", "說明": "..." }}
        ]
        }}
        """
        }
        summary_entry = {"use_case_name": use_case_name, "event_summary": {}}

        for event in ["正常程序", "例外程序"]:
            raw = await ask_event_summary(prompts[event])
            try:
                cleaned = clean_json_text(raw)
                parsed = json.loads(cleaned)
                summary_entry["event_summary"][event] = parsed
            except Exception as e:
                print(f"無法解析 {event}：{use_case_name}")
                print("原始輸出：", raw)
                summary_entry["event_summary"][event] = {}

        output.append(summary_entry)
    for uc in output:
        project_id = app.storage.user.get('selected_project', {}).get('id')
        found_usecase = await UseCaseController.get_use_case(
            name = uc['use_case_name']
        )
        if found_usecase and found_usecase.project_id == project_id:
            use_case_id = found_usecase.id
            print(f"已找到 UseCase '{uc['use_case_name']}'，ID: {use_case_id}")
        for event_type in ["正常程序", "例外程序"]:
            event_list_data = uc['event_summary'].get(event_type, {})
            events = event_list_data.get("事件列表", [])
            if not events:
                continue
            event_list = await EventListController.add_event_list(
                list_type = event_type,
                use_case_id = use_case_id
            )
            for idx, event in enumerate(events, start=1):
                await EventController.add_event(
                    event_list_id=event_list.id,
                    sequence_no=idx,
                    type=event['類型'],
                    description=event['說明']
                )

