import os
import json
import asyncio
import httpx
import re
from init_sys import API_URL, HEADERS
from nicegui import app, ui
from controllers.user_account_controler import UserAccountControler



async def ask_ai(prompt: str) -> str:
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(API_URL, headers=HEADERS, json=data)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            raise Exception(f"AI API 錯誤: {response.status_code} - {response.text}")

def build_prompt(use_case_name, objects, events):
    # 修改 obj_lines 以包含所有屬性和方法
    obj_lines = []
    for obj in objects:
        obj_name = obj.get("名稱", "未知物件")
        obj_type = obj.get("類型", "未知類型")
        obj_lines.append(f"- 名稱: {obj_name}, 類型: {obj_type}")
        if obj.get("屬性"):
            for attr in obj["屬性"]:
                obj_lines.append(f"  屬性: {attr}")
        if obj.get("方法"):
            for method in obj["方法"]:
                obj_lines.append(f"  方法: {method}")

    # 修改 event_lines 以包含所有事件說明和類型
    event_lines = []
    for e in events:
        event_desc = e.get("說明", "無說明")
        event_type = e.get("類型", "無類型")
        if event_desc != "無":
            event_lines.append(f"- 說明: {event_desc}, 類型: {event_type}")

    prompt = f"""
    你是一位資深系統分析師，請根據以下需求生成符合 Mermaid 語法標準的 classDiagram 代碼。請嚴格遵循以下規則：
    【使用案例名稱】：{use_case_name}
    【物件結構】：
    {chr(10).join(obj_lines)}
    【事件列表】：
    {chr(10).join(event_lines)}
    【生成規則】
    1. **物件定義**：
    - 每個「物件」必須定義為一個 class，且 class 名稱必須是英文、數字或底線，禁止空格和特殊符號。
    - **每個 class 必須用大括號 {{}} 包住所有屬性和方法。禁止使用 ClassName : ... 這種語法。**

    2. **屬性與方法**：
    - 在 class 中列出所有屬性，格式為 `-屬性名稱: 類型`。
    - 根據事件推論 class 的方法，格式為 `+方法名稱()`。

    3. **關聯性**：
    - 若物件之間存在屬性關聯或方法參照，請使用箭頭表示關聯，格式為 `ClassA --> ClassB` 表示 ClassA 依賴 ClassB。

    4. **輸出限制**：
    - 僅輸出有效且正確的 Mermaid classDiagram 區塊。
    - 禁止包含任何其他文字、說明或註解。
    - **禁止使用 `ClassName : ...` 這種語法。**

    【輸入範例格式】
    classDiagram
    class ClassName {{
        -attribute1: Type
        -attribute2: Type
        +method1()
    }}
    ClassA --> ClassB
    """.strip()
    return prompt

def clean_mermaid_markdown(text: str) -> str:
    # 去除 ```mermaid 和 ```
    lines = text.strip().splitlines()
    cleaned = []
    for line in lines:
        if line.strip().startswith('```'):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)

def clean_stereotype_and_indent(text: str) -> str:
    lines = text.strip().splitlines()
    cleaned = []
    for line in lines:
        # 移除 stereotype 標籤
        line = line.replace('<<Boundary>>', '').replace('<<Control>>', '').replace('<<Entity>>', '')
        # 移除行首空白
        cleaned.append(line.lstrip())
    return '\n'.join(cleaned)

def fix_colon_class_syntax(text: str) -> str:
    # 將 ClassName : ... 轉成 class ClassName { ... }
    lines = text.strip().splitlines()
    class_defs = {}
    relations = []
    current_class = None
    for line in lines:
        m = re.match(r'^(\w+)\s*:\s*(.+)', line)
        if m:
            cname, content = m.groups()
            if cname not in class_defs:
                class_defs[cname] = []
            class_defs[cname].append(content)
        elif re.match(r'^\w+\s*-->', line) or re.match(r'^\w+\s*-\|>', line):
            relations.append(line)
        elif line.strip().startswith('classDiagram'):
            continue
    # 組合成正確格式
    result = ['classDiagram']
    for cname, items in class_defs.items():
        result.append(f'class {cname} {{')
        for item in items:
            result.append(item)
        result.append('}')
    result.extend(relations)
    return '\n'.join(result)

async def generate_all_ai_classes():

    user_account = app.storage.user.get('current_user_account')
    project_name = app.storage.user.get('selected_project', {}).get('name')
    select_user_account = await UserAccountControler.select_user_account(account=user_account)
    user_id = select_user_account.id if select_user_account else None
    JSON_DIR = os.path.join('.', '.home', str(user_id), project_name, 'json')
    OBJECT_FILE = os.path.join(JSON_DIR, "object.json")
    EVENT_FILE = os.path.join(JSON_DIR, f"{project_name}_event_summary.json")

    # 讀取所有案例物件結構與事件
    with open(OBJECT_FILE, encoding="utf-8") as f:
        objects_all = json.loads(f.read())
    with open(EVENT_FILE, encoding="utf-8") as f:
        events_all = json.loads(f.read())

    os.makedirs("./mmd", exist_ok=True)
    for event_case in events_all:
        use_case_name = event_case.get("使用案例名稱") or event_case.get("use_case_name")
        if not use_case_name:
            continue
        # 取得該案例物件結構
        obj_case = next(
            (x for x in objects_all
             if x.get("使用案例名稱") == use_case_name or x.get("use_case_name") == use_case_name),
            None
        )
        case_objects = obj_case.get("物件結構", []) if obj_case else []
        # 合併正常程序與例外程序事件，只取說明欄位
        event_summary = event_case.get("event_summary", {})
        events = []
        for section in ["正常程序", "例外程序"]:
            for item in event_summary.get(section, {}).get("事件列表", []):
                desc = item.get("說明", "")
                if desc and desc != "無":
                    events.append({"說明": desc, "類型": item.get("類型", "")})
        if not case_objects or not events:
            print(f"⚠️ 跳過：{use_case_name}（無物件或事件）")
            continue
        prompt = build_prompt(use_case_name, case_objects, events)
        print(f"🧠 正在產生：{use_case_name} 的 Mermaid 圖...")
        try:
            mermaid = await ask_ai(prompt)
            mermaid = clean_mermaid_markdown(mermaid)
            mermaid = clean_stereotype_and_indent(mermaid)  # 新增這行
            mermaid = fix_colon_class_syntax(mermaid)
        except Exception as e:
            print(f"❌ AI 產生失敗：{use_case_name} - {e}")
            continue
        out_file = os.path.join(os.path.join('.', '.home', str(user_id), project_name, 'MMD'), f"{use_case_name}_class.mmd")
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(mermaid)
        print(f"✅ Mermaid 完成：{out_file}")