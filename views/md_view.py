from nicegui import ui, app
import os

class MDView:
    def __init__(self):
        pass

    async def display(self):
        md_dir = "MD"
        md_files = [f for f in os.listdir(md_dir) if f.endswith('.md')]
        selected = {'file': md_files[0] if md_files else None}

        md_content_area = ui.markdown("")  # 預留一個 markdown 顯示區

        def show_md(e=None):
            if selected['file']:
                md_path = os.path.join(md_dir, selected['file'])
                with open(md_path, "r", encoding="utf-8") as f:
                    md_content = f.read()
                md_content_area.content = md_content
            else:
                md_content_area.content = "找不到任何 MD 檔案"

        if md_files:
            ui.select(
                md_files,
                value=selected['file'],
                on_change=lambda e: (selected.update({'file': e.value}), show_md())
            )
            show_md()  # 頁面初始化時自動顯示
        else:
            ui.markdown("MD 資料夾內沒有任何 .md 檔案")


