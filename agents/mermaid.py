import os
import json
from pathlib import Path

MERMAID_OUTPUT_FILE = './json/mermaid.json'
OBJECT_INPUT_FILE = './json/object.json'

# 系統類別 → Mermaid 顏色
TYPE_CLASS = {
    "Boundary": "actor",
    "Control": "participant",
    "Entity": "database"
}

def object_to_mermaid_sequence(objects: list, usecase_name: str) -> str:
    """
    將物件列表轉換為 Mermaid 循序圖描述
    """
    lines = [f"sequenceDiagram", f"title 使用案例：{usecase_name}"]

    # 宣告角色
    for obj in objects:
        role_type = obj["類型"]
        name = obj["名稱"]
        mermaid_role = TYPE_CLASS.get(role_type, "participant")
        lines.append(f"{mermaid_role} {name}")

    lines.append("%% 以下為模擬事件流程（請依需求自定義）")

    # 取得各類型的第一個名稱作為目標
    control_objs = [o for o in objects if o["類型"] == "Control"]
    entity_objs = [o for o in objects if o["類型"] == "Entity"]
    control_name = control_objs[0]["名稱"] if control_objs else "Control"
    entity_name = entity_objs[0]["名稱"] if entity_objs else "Entity"

    # 假設流程：Boundary 呼叫 Control，Control 操作 Entity
    for obj in objects:
        if obj["類型"] == "Boundary":
            for method in obj["方法"]:
                lines.append(f"{obj['名稱']} ->> {control_name}: 請求 {method}")
        elif obj["類型"] == "Control":
            for method in obj["方法"]:
                lines.append(f"{obj['名稱']} ->> {entity_name}: 處理 {method}")

    return "\n".join(lines)

def generate_mermaid_from_json(input_path=OBJECT_INPUT_FILE, output_path=MERMAID_OUTPUT_FILE):
    if not Path(input_path).exists():
        print("❌ 找不到 JSON 檔案")
        return

    with open(input_path, encoding="utf-8") as f:
        object_data = json.load(f)

    output = []

    for uc in object_data:
        usecase = uc.get("使用案例名稱")
        objects = uc.get("物件結構", [])
        mermaid_code = object_to_mermaid_sequence(objects, usecase)

        output.append({
            "use_case_name": usecase,
            "mermaid_code": mermaid_code
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Mermaid 語法已儲存至：{output_path}")

# 若要測試
if __name__ == "__main__":
    generate_mermaid_from_json()