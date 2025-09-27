import os
import json
import httpx
import asyncio
import re
from init_sys import API_URL, HEADERS
from utilits.utis import clean_json_text
from controllers.object_controller import ObjectController
from controllers.attributes_controller import AttributeController
from controllers.methods_controller import MethodController
from nicegui import app
from controllers.user_account_controler import UserAccountControler
    
@staticmethod
async def generate_objects_from_event_summary(events:list) -> list:

    user_account = app.storage.user.get('current_user_account')
    project_name = app.storage.user.get('selected_project', {}).get('name')
    select_user_account = await UserAccountControler.select_user_account(account=user_account)
    user_id = select_user_account.id if select_user_account else None
    OUTPUT_PATH = os.path.join('.', '.home', str(user_id), project_name, 'json', 'object.json')
    # 檢查並建立目標資料夾
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    output = []
    print(f"🔍 開始分析 {len(events)} 個事件摘要...")
    for event in events:
        name = event.get("use_case_name")
        desc = event.get("use_case_description", "")
        event_lines = format_event_summary(event)
        if not event_lines:
            continue
        print(f"🔍 正在處理：{name}")
        raw = await ask_objects_from_ai(name, desc, event_lines)
        parsed = parse_ai_response_to_objects(raw)
        await import_objects_to_db(parsed)
        output.append({
            "使用案例名稱": name,
            "物件結構": parsed
        })
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"✅ 物件分析完成，儲存於：{OUTPUT_PATH}")
    return output
    
JSON_PATH = './json/event_summary.json'


@staticmethod
def format_event_summary(event: dict) -> list:
    result = []
    event_summary = event.get("event_summary", {})
    for flow_type in ["正常程序", "例外程序"]:
        event_list = event_summary.get(flow_type, {}).get("事件列表", [])
        for idx, e in enumerate(event_list, 1):
            desc = e.get("description") or e.get("說明") or str(e)
            if desc:
                result.append(f"{flow_type}{idx}: {desc}")
    return result

@staticmethod
async def ask_objects_from_ai(usecase, description, event_lines):
    prompt_lines = [
        "你是一位經驗豐富的系統分析師，你正在分析一個資訊系統，請根據下列資訊設計相關物件：",
        f"【使用案例名稱】：{usecase}",
        f"【使用案例描述】：{description}",
        "我也將提供該系統一個使用案例的正常程序與例外程序的詳細事件列表。",
        "請你從這些語法結構中生成邊界物件、控制物件、實體物件的詳細描述。",
        "邊界物件經常出現在(Request)及(Response)敘述中的受詞，代表系統的輸入或輸出。",
        "控制物件的成員函數經常出現在(Process)敘述中的不同動詞，也就是說每一個動詞可能是控制物件的一項操作或方法。",
        "實體物件會出現在(Process)敘述中的受詞且該敘述的動詞屬於資料庫的新增(Insert)、更新(Update)、刪除(Delete)、篩選(Select)、或其他的操作。",
        "每一個物件描述必須包含物件名稱、物件的屬性、物件的方法。",
        "每一個物件屬性的描述包含 屬性名稱:資料類型",
        "每一個物件的方法的描述包含 方法名稱(參數名稱: 資料類型, ...): 傳回值的資料類型。",
        "物件與物件之間可能存在 Association, Directed Association, Reflexive Association, Multiplicity, Aggregation, Composition, Inheritance, Realization 等關係。",
        "【事件清單】：",
        *event_lines,
        "請根據上述資訊，歸納並輸出下列三種類型的 UML 物件：",
        "邊界物件（<<Boundary>>）",
        "控制物件（<<Control>>）",
        "實體物件（<<Entity>>）",
        "每個物件請依照以下格式列出：",
        "- 物件名稱: xxx <<類型>>",
        "- 屬性: 屬性名稱: 型別",
        "- 方法: 方法名稱(參數: 型別): 回傳型別",
        "⚠️ 僅以純文字格式回覆，禁止使用 Markdown 或 JSON，不需額外說明或前後文。"
    ]
    data = {
        "contents": [{"parts": [{"text": "\n".join(prompt_lines)}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 2048}
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(API_URL, headers=HEADERS, json=data)
        if response.status_code == 200:
            try:
                return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            except Exception as e:
                print("⚠️ 回應解析錯誤:", e)
        else:
            print(f"❌ 請求失敗：{response.status_code} - {response.text}")
    return ""

@staticmethod
def parse_ai_response_to_objects(ai_text: str) -> list:
    objects = []
    current = None
    for line in ai_text.splitlines():
        line = line.strip()
        if not line:
            continue
        match_obj = re.match(r"-?\s*物件名稱[:：]?\s*(.+?)\s*<<(\w+)>>", line)
        if match_obj:
            if current:
                objects.append(current)
            current = {
                "類型": match_obj.group(2),
                "名稱": match_obj.group(1),
                "屬性": [],
                "方法": []
            }
            continue
        match_attr = re.match(r"-?\s*屬性[:：]?\s*(.+)", line)
        if match_attr and current:
            raw = match_attr.group(1)
            current["屬性"].extend([s.strip() for s in raw.split(",") if ":" in s])
            continue
        match_meth = re.match(r"-?\s*方法[:：]?\s*(.+)", line)
        if match_meth and current:
            raw = match_meth.group(1)
            current["方法"].extend([s.strip() for s in raw.split(",") if "(" in s and ")" in s])
            continue
    if current:
        objects.append(current)
    return objects

async def import_objects_to_db(objects: list):
    for obj in objects:
        # 新增 Object
        await ObjectController.add_object(name=obj["名稱"], obj_type=obj["類型"])
        # 取得剛剛新增的 object（假設名稱唯一）
        db_obj = await ObjectController.select_object(name=obj["名稱"])
        if not db_obj:
            continue

        # 新增 Attributes
        for attr in obj.get("屬性", []):
            if ":" in attr:
                attr_name, attr_type = [s.strip() for s in attr.split(":", 1)]
                await AttributeController.add_attribute(
                    name=attr_name,
                    datatype=attr_type,
                    visibility="public",
                    object_id=db_obj.id  # 傳入正確的 object_id
                )

        # 新增 Methods
        for method in obj.get("方法", []):
            # 方法格式: "方法名稱(參數: 型別): 回傳型別"
            import re
            m = re.match(r"(.+?)\((.*?)\):\s*(.+)", method)
            if m:
                method_name = m.group(1).strip()
                parameters = m.group(2).strip()
                return_type = m.group(3).strip()
                await MethodController.add_method(
                    name=method_name,
                    parameters=parameters,
                    visibility="public",  # 你可以根據需求調整
                    return_type=return_type,
                    object_id=db_obj.id   # <--- 這裡要加上
                )
                # 取得剛剛新增的 method 並關聯 object_id（需在 Method model 加 object_id 欄位）
                # 這裡假設 add_method 支援 object_id，否則你要自行 update


