import os
import json
import re
import httpx
from init_sys import API_URL, HEADERS
from controllers.user_account_controler import UserAccountControler
from nicegui import app 


OBJECT_FILE = "./json/object.json"
EVENT_FILE = "./json/event_summary.json"

def clean_attr(attr):
    # 移除尖括號、逗號、特殊型態，統一型態
    attr = re.sub(r'<.*?>', '', attr)
    attr = attr.replace(',', '')
    attr = re.sub(r'\b(File|Object|Boolean|Map|List|Set|Array|Dict)\b', 'string', attr)
    return attr.strip()

def extract_entities(objects_all):
    entities = {}
    for case in objects_all:
        for obj in case.get("物件結構", []):
            if obj.get("類型", "").lower() == "entity":
                attrs = []
                for attr in obj.get("屬性", []):
                    cleaned = clean_attr(attr)
                    attrs.append(cleaned)
                entities[obj.get("名稱", "")] = attrs
    return entities

def extract_events(events_all):
    event_desc = []
    for case in events_all:
        for section in ["正常程序", "例外程序"]:
            for evt in case.get(section, {}).get("事件列表", []):
                desc = evt.get("說明", "")
                if desc:
                    event_desc.append(desc)
    return event_desc

def build_ai_prompt(entities, event_desc):
    entity_desc = ""
    for name, attrs in entities.items():
        entity_desc += f"{name}:\n"
        for attr in attrs:
            entity_desc += f"  - {attr}\n"
    event_lines = "\n".join([f"- {e}" for e in event_desc])
    prompt = f"""
你是一位資深資料庫設計師，請根據下方物件結構與事件流程，產生 Mermaid ERD 語法（erDiagram）。

規則：
1. 資料表結構（table/entity）只根據物件結構（entity）推斷。
2. 請根據物件結構推斷每個類別的屬性、主鍵(PK)、外鍵(FK)，所有主鍵都加 PK，所有外鍵都加 FK。
3. 屬性型態不能用尖括號（<>）、逗號（,）、File、Map、Object、Boolean 等特殊型態，請全部轉為 string 或 int。
4. 屬性格式必須為：型態 名稱（例如：string restaurantId）。
5. 關聯必須根據物件結構與事件流程推斷，不能只產生一條，請補足所有合理關聯，且至少每個資料表都要有嘗試推斷關聯。
6. 若物件結構中沒有明確外鍵，請根據命名慣例（如 xxxId、xxx_id、xxxID），以及資料表名稱、屬性名稱的相似性，主動推斷可能的關聯。例如：如果有 Customer 和 Order，且 Order 有 customerId 屬性，請推斷 Customer 與 Order 有關聯。
7. 即使物件結構沒有明確外鍵，只要資料表名稱或屬性名稱有明顯對應（如 employeeId、orderId、restaurantId），都要主動推斷並產生關聯。
8. 關聯語意請用標準資料庫語意（如 has、belongs_to、references），不要用 included_in、contains 等模糊語意。
9. 請移除所有 markdown 標記（如 ```mermaid）。
10. 請參考範例格式：

erDiagram
    CUSTOMER {{
        string id PK
        string name
    }}
    ORDER {{
        string id PK
        string customerId FK
        float amount
    }}
    CUSTOMER ||--o{{ ORDER : places

物件結構：
{entity_desc}

事件流程：
{event_lines}

請只回傳 erDiagram 的 Mermaid 語法，不要有任何說明或註解。
"""
    return prompt

async def ask_ai(prompt: str) -> str:
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.post(API_URL, headers=HEADERS, json=data)
        res_json = res.json()
        candidates = res_json.get("candidates")
        if not candidates or not isinstance(candidates, list):
            return ""
        content = candidates[0].get("content")
        if not content or not isinstance(content, dict):
            return ""
        parts = content.get("parts")
        if not parts or not isinstance(parts, list) or not isinstance(parts[0], dict):
            return ""
        mermaid_code = parts[0].get("text", "")
        # 移除 markdown 標記
        mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
        return mermaid_code

async def generate_erd():

    user_account = app.storage.user.get('current_user_account')
    project_name = app.storage.user.get('selected_project', {}).get('name')
    select_user_account = await UserAccountControler.select_user_account(account=user_account)
    user_id = select_user_account.id if select_user_account else None
    JSON_DIR = os.path.join('.', '.home', str(user_id), project_name, 'json')
    OBJECT_FILE = os.path.join(JSON_DIR, "object.json")
    EVENT_FILE = os.path.join(JSON_DIR, f"{project_name}_event_summary.json")

    with open(OBJECT_FILE, encoding="utf-8") as f:
        objects_all = json.load(f)
    with open(EVENT_FILE, encoding="utf-8") as f:
        events_all = json.load(f)

    entities = extract_entities(objects_all)
    event_desc = extract_events(events_all)
    prompt = build_ai_prompt(entities, event_desc)
    mermaid_code = await ask_ai(prompt)
    if mermaid_code:
        out_file = os.path.join(os.path.join('.', '.home', str(user_id), project_name, 'MMD'), f"{project_name}_erd.mmd")

        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(mermaid_code)
        print(f"✅ ERD Mermaid 語法已存檔：{out_file}")
    else:
        print("AI 產生失敗")

