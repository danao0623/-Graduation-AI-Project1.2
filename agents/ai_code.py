import os
import json
import asyncio
import httpx
from init_sys import API_URL, HEADERS
from utilits.utis import clean_code_block
from utilits.utis import remove_all_comments
from nicegui import ui,app
from controllers.user_account_controler import UserAccountControler


EVENT_PATH = "./json/event_summary.json"

USER_CONFIG_PATH = ".nicegui/storage-user-438d0c6f-511f-40f2-8211-055d87fa2c57.json"

def get_project_arch_info():
    try:
        
        project = app.storage.user.get('selected_project', {})
        frontend = f"{project.get('frontend_language', '')} / {project.get('frontend_platform', '')} / {project.get('frontend_library', '')}"
        backend = f"{project.get('backend_language', '')} / {project.get('backend_platform', '')} / {project.get('backend_library', '')}"
        db = project.get('architecture', '')
        frontend_language = project.get('frontend_language', '').lower()
        backend_language = project.get('backend_language', '').lower()
        return frontend, backend, db, frontend_language, backend_language
    except Exception as e:
        print(f"⚠️ 讀取 user config 失敗: {e}")
        return '', '', '', '', ''

def build_object_prompt(obj, frontend, backend, db, frontend_language, backend_language):
    en_name = obj.get('英文名') or obj['名稱']
    obj_type = obj.get('類型', '').lower()
    attrs = obj.get('屬性', [])
    methods = obj.get('方法', [])
    attr_lines = '\n'.join([f"- {a}" for a in attrs]) if attrs else '(無)'
    method_lines = '\n'.join([f"- {m}" for m in methods]) if methods else '(無)'
    if obj_type == 'boundary':
        lang = frontend_language
    else:
        lang = backend_language
    prompt = f"""
    你是一位經驗豐富的程式設計師，請根據下列資訊產生一份能在 {lang} 環境下執行的 code。
    請在第一行回傳你建議的副檔名（如 .py、.tsx、.go），第二行開始才是純 code，不要有任何註解或說明。
    我將提供該系統其中一個使用案例的主要流程的詳細事件列表，每一個事件的敘述都是由 "主詞+動詞+受詞"的語法結構所組成。
    這些語法結構中隱含了行為者(actor)、邊界物件、控制物件、實體物件的資訊。
    行為者是所有敘述中除了"系統"之外的主詞。
    邊界物件則出現在(Request)及(Response)敘述中的受詞，代表系統的輸入或輸出。
    控制物件是由出現在(Process)敘述中的不同動詞所組成，每一個動詞則為控制物件的一項操作或方法。
    實體物件會出現在(Process)敘述中的受詞且該敘述的動詞屬於資料庫的新增(Insert)、更新(Update)、刪除(Delete)、篩選(Select)、或其他的操作。
    如果物件名稱有重複，請在每個重複物件產生的 code 中疊加代碼。
    我將提示此使用案例中邊界物件、控制物件、實體物件的清單。
    我將提供指定物件的詳細提示，包含物件名稱、物件的屬性、物件的方法及該物件方法的操作說明。
    我指定該使用案例所採用的網頁前端系統架構、後端系統架構、及資料庫管理系統。
    
    【前端系統架構】：{frontend}
    【後端系統架構】：{backend}
    【資料庫管理系統】：{db}
    
    【物件名稱】：{en_name}
    【物件類型】：{obj_type}
    【屬性】：
    {attr_lines}
    【方法】：
    {method_lines}
    
    請只輸出一份完整的 {lang} code，第一行為副檔名（如 .py、.tsx），第二行開始為純 code，不要有任何多餘的說明、註解、markdown code block（如 ```python）、語言標籤、自然語言描述或任何檔案標頭，只要純 code。""".strip()
    return prompt

async def ask_ai(prompt: str) -> str:
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.post(API_URL, headers=HEADERS, json=data)
        print(f"API status: {res.status_code}")
        try:
            res_json = res.json()
            candidates = res_json.get("candidates")
            if not candidates or not isinstance(candidates, list):
                raise ValueError(f"API 回傳格式錯誤: candidates 欄位不存在或不是 list, res_json={res_json}")
            content = candidates[0].get("content")
            if not content or not isinstance(content, dict):
                raise ValueError(f"API 回傳格式錯誤: content 欄位不存在或不是 dict, candidates[0]={candidates[0]}")
            parts = content.get("parts")
            if not parts or not isinstance(parts, list):
                raise ValueError(f"API 回傳格式錯誤: parts 欄位不存在或不是 list, content={content}")
            text = parts[0].get("text")
            if not text or not isinstance(text, str):
                raise ValueError(f"API 回傳格式錯誤: text 欄位不存在或不是 str, parts[0]={parts[0]}")
            return text
        except Exception as e:
            print(f"❌ AI 回傳內容解析失敗: {e}")
            print(f"⚠️ 原始回傳內容: {res.text}")
            return ""

def split_code_blocks(text: str):
    return {"all": text}

async def generate_code():
    user_account = app.storage.user.get('current_user_account')
    project_name = app.storage.user.get('selected_project', {}).get('name')
    select_user_account = await UserAccountControler.select_user_account(account=user_account)
    user_id = select_user_account.id if select_user_account else None
    JSON_DIR = os.path.join('.', '.home', str(user_id), project_name, 'json')
    OBJECT_FILE = os.path.join(JSON_DIR, "object.json")
    EVENT_FILE = os.path.join(JSON_DIR, f"{project_name}_event_summary.json")
    OUTPUT_DIR = os.path.join('.', '.home', str(user_id), project_name, 'code')

    os.makedirs(f"{OUTPUT_DIR}/models", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/views", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/controllers", exist_ok=True)

    with open(OBJECT_FILE, encoding="utf-8") as f:
        objects_text = f.read()
        objects_data = json.loads(objects_text)

    frontend, backend, db, frontend_language, backend_language = get_project_arch_info()

    # 彙整所有物件（以英文名為唯一 key，允許重複，改為 key: list）
    all_objects = {}
    for case in objects_data:
        for obj in case.get("物件結構", []):
            key = obj.get('英文名') or obj.get('名稱')
            if key:
                all_objects.setdefault(key, []).append(obj)

    for key, obj_list in all_objects.items():
        code_blocks = []
        ext = None
        for obj in obj_list:
            try:
                prompt = build_object_prompt(obj, frontend, backend, db, frontend_language, backend_language)
                print(f"🚀 正在產生物件程式碼：{key}")
                result = await ask_ai(prompt)
                result = clean_code_block(result)
                result = result.strip()
                # 檢查 AI 回傳內容是否為空或明顯失敗
                if not result or "產生失敗" in result:
                    print(f"⚠️ {key} AI 回傳內容異常，已跳過存檔")
                    print(f"⚠️ 原始回傳內容: {result}")
                    continue
                lines = result.splitlines()
                if lines and lines[0].startswith('.'):
                    ext = lines[0].strip()
                    code = '\n'.join(lines[1:]).strip()
                else:
                    ext = ext or '.txt'
                    code = result
                code_blocks.append(code)
            except Exception as e:
                print(f"❌ {key} 產生失敗: {e}")
        # 合併所有 code block，僅當有內容時才存檔
        if code_blocks:
            merged_code = '\n\n'.join(code_blocks)
            obj_type = obj_list[0].get('類型', '').lower()
            if obj_type == 'boundary':
                folder = 'views'
            elif obj_type == 'control':
                folder = 'controllers'
            elif obj_type == 'entity':
                folder = 'models'
            else:
                folder = 'models'
            filename = key.lower() + ext
            with open(f"{OUTPUT_DIR}/{folder}/{filename}", "w", encoding="utf-8") as f:
                f.write(merged_code)
            print(f"✅ {key} 產生完成 ({folder})")
        else:
            print(f"⚠️ {key} 無有效程式碼，未產生檔案")

if __name__ == "__main__":
    asyncio.run(generate_code())