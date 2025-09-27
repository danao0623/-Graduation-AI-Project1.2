import re

def clean_json_text(text):
    text = text.strip()  # 移除前後空白
    text = re.sub(r"^```json\s*", "", text)  # 移除開頭的 ```json
    text = re.sub(r"```$", "", text)  # 移除結尾的 ```
    return text

def clean_mermaid_code(mermaid_code: str) -> str:
    # 移除 markdown code block 標記（如 ```mermaid ... ``` 或 ``` ... ```）
    mermaid_code = re.sub(r'^```[a-zA-Z0-9]*\s*', '', mermaid_code.strip())
    mermaid_code = re.sub(r'\s*```$', '', mermaid_code.strip())
    return mermaid_code.strip()

def clean_mermaid_code_for_pdf(mermaid_code: str) -> str:
    # 先用你現有的基本清理
    code = clean_mermaid_code(mermaid_code)
    # 將 actor 改成 participant，避免 mermaid-cli 轉檔失敗
    code = code.replace('actor ', 'participant ')
    return code


def clean_code_block(text):
    text = text.strip()  # 移除前後空白
    text = re.sub(r"^```[a-zA-Z0-9]*\s*", "", text)  # 移除開頭的 ```code
    text = re.sub(r"```$", "", text)  # 移除結尾的 ```
    return text.strip()

def remove_all_comments(text):
    code = text
    # 移除 /* ... */ 多行註解
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # 移除 '''...''' 或 """...""" 多行註解
    code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
    code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
    # 移除所有單行註解（# ... 或 // ...，不含字串內）
    code = re.sub(r'(^|\s)#.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'(^|\s)//.*$', '', code, flags=re.MULTILINE)
    # 移除多餘空行
    code = re.sub(r'\n{2,}', '\n', code)
    return code.strip()
