import os
import json
import asyncio
import httpx
from init_sys import API_URL, HEADERS
from nicegui import app,ui
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
    # 修改 obj_lines 以包含所有物件的名稱、類型、屬性和方法
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
    你是一位資深系統工程師，請根據以下使用案例資料生成嚴格符合 Mermaid 語法標準的 sequenceDiagram 代碼。嚴格遵守以下規則：
    1. **參與者定義**：
    - 使用 `actor` 代表人、外部系統或角色（例如 `actor User`）。
    - 使用 `participant` 代表系統內部元件（例如 `participant API_Server`）。
    - 名稱必須是英文、數字或底線，禁止空格和特殊符號。

    2. **訊息格式**：
    - 同步呼叫用 `->>`（實線箭頭）。
    - 非同步呼叫用 `->>`（實線箭頭）加上 `+` 非同步標記。
    - 回應用 `-->>`（虛線箭頭）。
    - 每個訊息需明確標註動作（動詞）和參數（可選）。

    3. **結構要求**：
    - 必須包含 `alt/else` 條件分支和 `loop` 循環（如果適用）。
    - 使用 `note` 添加關鍵註解說明業務邏輯。

    4. **輸出限制**：
    - 禁止輸出任何非 Mermaid 語法的文字（包括標題、說明、註釋）。
    - 禁止使用 activate 或 deactivate 語法。
    - 禁止使用 as 語法縮寫名稱或翻譯為中文名稱。
    - 代碼必須可直接粘贴到 Mermaid 渲染器執行。

    【使用案例名稱】：{use_case_name}
    【物件結構】：
    {chr(10).join(obj_lines)}
    【事件列表】：
    {chr(10).join(event_lines)}

    【輸入範例格式】
    sequenceDiagram
    actor C as 客戶
    participant W as 網站前端
    participant B as 後端API
    participant D as 數據庫
    participant P as 支付系統
    
    box 訂單創建流程
        C->>W: 瀏覽商品
        W->>B: GET /api/products
        B->>D: 查詢商品
        D-->>B: 商品數據
        B-->>W: 商品數據
        W-->>C: 顯示商品列表
        
        C->>W: 加入購物車(商品ID, 數量)
        W->>B: POST /api/cart
        B-->>W: 購物車更新結果
        W-->>C: 顯示成功訊息
        
        alt 庫存不足
            C->>W: 結算購物車
            W->>B: POST /api/orders
            B->>D: 檢查庫存
            D-->>B: 庫存不足
            B-->>W: 錯誤:庫存不足
            W-->>C: 提示庫存不足
        else 庫存足夠
            C->>W: 結算購物車
            W->>B: POST /api/orders
            B->>D: 檢查庫存
            D-->>B: 庫存足夠
            B->>D: 鎖定庫存
            B->>P: 建立支付單
            P-->>B: 支付鏈接
            B-->>W: 訂單創建成功
            W->>C: 重定向到付款頁面
            C->>P: 完成支付
            P-->>B: 支付回呼
            B->>D: 扣減庫存
            Note right of B: 發送訂單確認郵件
            B-->>W: 付款成功
            W-->>C: 顯示訂單完成頁面
        end
    end
    
    box 後台處理
        loop 每5分鐘掃描
        B->>D: 查詢未支付訂單
        D-->>B: 訂單列表
        B->>B: 檢查超時訂單
        B->>D: 釋放庫存
        B->>P: 取消支付單
        B->>D: 更新訂單狀態
        end
    end
    """.strip()
    return prompt

def clean_mermaid_markdown(text: str) -> str:
    lines = text.strip().splitlines()
    cleaned = []
    for line in lines:
        if line.strip().startswith('```'):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)

async def generate_all_sequences():
    # 讀取所有案例物件結構與事件
    user_account = app.storage.user.get('current_user_account')
    project_name = app.storage.user.get('selected_project', {}).get('name')
    select_user_account = await UserAccountControler.select_user_account(account=user_account)
    user_id = select_user_account.id if select_user_account else None
    JSON_DIR = os.path.join('.', '.home', str(user_id), project_name, 'json')
    OBJECT_FILE = os.path.join(JSON_DIR, "object.json")
    EVENT_FILE = os.path.join(JSON_DIR, f"{project_name}_event_summary.json")


    with open(OBJECT_FILE, encoding="utf-8") as f:
        objects_all = json.loads(f.read())
    with open(EVENT_FILE, encoding="utf-8") as f:
        events_all = json.loads(f.read())

    os.makedirs("./mmd", exist_ok=True)
    for event_case in events_all:
        use_case_name = event_case.get("使用案例名稱") or event_case.get("use_case_name")
        if not use_case_name:
            continue
        # 取得該案例物件結構（同時支援物件結構/物件列表）
        obj_case = next((x for x in objects_all if x.get("使用案例名稱") == use_case_name or x.get("use_case_name") == use_case_name), None)
        case_objects = obj_case.get("物件結構") or obj_case.get("物件列表") or [] if obj_case else []
        # 合併正常程序與例外程序事件，支援 dict/str
        events = []
        for section in ["正常程序", "例外程序"]:
            for item in event_case.get("event_summary", {}).get(section, {}).get("事件列表", []):
                if isinstance(item, dict):
                    desc = item.get("說明", "")
                    event_type = item.get("類型", "")
                    if desc and desc != "無":
                        events.append({"說明": desc, "類型": event_type})
                elif isinstance(item, str):
                    parts = item.split(" - ", 1)
                    type_part = parts[0].split(". ", 1)
                    event_type = type_part[1] if len(type_part) == 2 else type_part[0]
                    event_desc = parts[1] if len(parts) > 1 else ""
                    if event_desc and event_desc != "無":
                        events.append({"說明": event_desc, "類型": event_type})
        if not events:
            print(f"⚠️ 跳過：{use_case_name}（無事件）")
            continue
        prompt = build_prompt(use_case_name, case_objects, events)
        print(f"🧠 正在產生：{use_case_name} 的 Mermaid 圖...")
        try:
            mermaid = await ask_ai(prompt)
            mermaid = clean_mermaid_markdown(mermaid)  # 新增這行
        except Exception as e:
            print(f"❌ AI 產生失敗：{use_case_name} - {e}")
            continue
        out_file = os.path.join(os.path.join('.', '.home', str(user_id), project_name, 'MMD'), f"{use_case_name}_sequence.mmd")
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(mermaid)
        print(f"✅ Mermaid 完成：{out_file}")

