from nicegui import ui,app
import asyncio
import os
import json
from controllers.actors_controller import ActorController
from controllers.usecase_controller import UseCaseController
from controllers.usecase_actor_controller import UseCaseActorController
from controllers.aiase_controller import AiaseController
from read.usecase_read import UseCaseReader
from agents.ai_event_summary import generate_event_summary
from controllers.user_account_controler import UserAccountControler
from PDF.generate_pdf import GeneratePDF

class UseCaseDetailView:

    def __init__(self):
        
        self.project_id = app.storage.user.get('selected_project', {}).get('id')
        self.detail_file = os.path.join("json", "usecase_detail.json")
        self.usecases = []
        self.master_grid = None
        self.inputs = {}
        self.user_account = app.storage.user.get('current_user_account')
        self.select_project_name = app.storage.user.get('selected_project', {}).get('name')

    async def display(self):
        self.usecases = []
        for uc in await UseCaseController.get_use_case_by_project(
            app.storage.user.get('selected_project', {}).get('id')):
            actors = [uca.actor.name for uca in uc.actors if uca.actor]
            self.usecases.append({
                'id': uc.id,
                'use_case_name': uc.name,
                'description': uc.description,
                'actor': actors[0],
                'normal_process': uc.normal_process,
                'exception_process': uc.exception_process,
                'pre_condition': uc.pre_condition,
                'post_condition': uc.post_condition,
                'trigger_condition': uc.trigger_condition
            })
        print(json.dumps(self.usecases, ensure_ascii=False, indent=2))
    
        with ui.column().classes("p-4 w-full max-w-6xl mx-auto gap-6"):
            # 上方按鈕（左對齊）
            with ui.row().classes("w-full justify-start"):
                ui.button("產生三段式事件列表", on_click=self.generate_event_summary)

            # 中間 Master 表格
            with ui.column().classes("w-full"):
                ui.label("UA - 使用案例清單").classes("text-lg font-bold")
                self.master_grid = ui.aggrid({
                    'columnDefs': [
                        {'headerName': 'Use Case', 'field': 'use_case_name', 'flex': 1},
                        {'headerName': 'Description', 'field': 'description', 'flex': 2},
                    ],
                    'rowData': self.usecases,
                    'rowSelection': 'single'
                }).classes("w-full h-64")
                self.master_grid.on("selectionChanged", self.on_master_selected)

            # 下方 Detail 表格
            with ui.column().classes("w-full"):
                ui.label("Detail - 使用案例細節").classes("text-lg font-bold")
                with ui.tabs().classes('w-full') as tabs:
                    one_tab = ui.tab('Detail')
                    two_tab = ui.tab('Event Summary')

                tabs.on('update:model-value',self.on_tab_change)
                with ui.tab_panels(tabs,value=one_tab).classes('w-full'):
                    with ui.tab_panel(one_tab):
                        with ui.card().classes('w-full max-w-4xl p-4'):  # 整張卡片最大寬度設定
                            with ui.column().classes('w-full gap-4'):
                                self.inputs['Actor1'] = ui.input('Actor:').classes('w-full min-w-[400px]').props('readonly autogrow')
                                self.inputs['正常程序'] = ui.textarea(label='正常程序:').classes('w-full min-h-[100px] max-w-[800px]').props('readonly autogrow')
                                self.inputs['例外程序'] = ui.textarea(label='例外程序:').classes('w-full min-h-[100px] max-w-[800px]').props('readonly autogrow')
                                self.inputs['觸發條件'] = ui.input('觸發條件:').classes('w-full').props('readonly autogrow')
                                self.inputs['前置條件'] = ui.textarea('前置條件:').classes('w-full').props('readonly autogrow')
                                self.inputs['後製條件'] = ui.textarea(label='後置條件:').classes('w-full min-h-[100px] max-w-[800px]').props('readonly autogrow')
                    with ui.tab_panel(two_tab):
                        with ui.card().classes('w-full max-w-4xl p-4'):  # 整張卡片最大寬度設定
                            with ui.column().classes('w-full gap-4'):
                                self.inputs['Actor'] = ui.input('Actor:').classes('w-full min-w-[400px]').props('readonly')
                                self.inputs['正常程序_event_summary'] = ui.textarea(label='正常程序:').classes('w-full min-h-[500px] ').props('readonly autogrow')
                                self.inputs['例外程序_event_summary'] = ui.textarea(label='例外程序:').classes('w-full min-h-[500px] ').props('readonly autogrow')
        ui.button("產生MD檔案和PDF檔案", on_click=self.generate_md_and_pdf).classes("mt-4")

    async def displayrightcolum(self):
        None

    def load_data(self):
        if not os.path.exists(self.detail_file):
            ui.notify("找不到 usecase_detail 的 JSON 檔案", color="negative")
            self.usecases = []
            return
        with open(self.detail_file, 'r', encoding='utf-8') as f:
            self.usecases = json.load(f)
            asyncio.create_task(self.import_usecase(self.usecases))

    def render_detail(self, selected_row):
        if not selected_row:
            if self.inputs:
                self.inputs['Actor1'].value = ""
                self.inputs['Actor'].value = ""
                self.inputs['正常程序'].value = ""
                self.inputs['例外程序'].value = ""
                self.inputs['觸發條件'].value = ""
                self.inputs['前置條件'].value = ""
                self.inputs['後製條件'].value = ""
            return

        matching = next((item for item in self.usecases
            if item['actor'] == selected_row['actor'] and item['use_case_name'] == selected_row['use_case_name']), None)

        if not matching:
            if self.inputs:
                self.inputs['Actor1'].value = ""
                self.inputs['Actor'].value = ""
                self.inputs['正常程序'].value = ""
                self.inputs['例外程序'].value = ""
                self.inputs['觸發條件'].value = ""
                self.inputs['前置條件'].value = ""
                self.inputs['後製條件'].value = ""
            return

        if self.inputs:
            self.inputs['Actor1'].value = matching.get('actor', '')
            self.inputs['Actor'].value = matching.get('actor', '')
            self.inputs['正常程序'].value = matching.get('normal_process', '')
            self.inputs['例外程序'].value = matching.get('exception_process', '')
            self.inputs['觸發條件'].value = matching.get('trigger_condition', '')  # 如果有這個欄位
            self.inputs['前置條件'].value = matching.get('pre_condition', '')
            self.inputs['後製條件'].value = matching.get('post_condition', '')
            
    async def on_master_selected(self, event):
        selected = await event.sender.get_selected_rows()
        if selected:
            self.render_detail(selected[0])
            use_case_id = await UseCaseController.get_use_case(
                name=selected[0]['use_case_name'],
            )
            if use_case_id and use_case_id.project_id == app.storage.user.get('selected_project', {}).get('id'):
                use_case_id = use_case_id.id
                
            await self.show_event_detail(use_case_id)
    
    def generate_usecase_detail(self):
        # 這裡可以加入生成 UseCase 細節的邏輯
        self.load_data()
        self.master_grid.options['rowData'] = self.usecases 
        self.master_grid.update()
    
    async def import_usecase(self,json_data):
    
        # 加入匯入 UseCase 的邏輯
        for item in json_data:
            project_id = app.storage.user.get('selected_project', {}).get('id')
            existing_usecase = await UseCaseController.get_use_case(
                name=item["use_case_name"],
            )
            if existing_usecase and existing_usecase.project_id == project_id:
                usecase_id = existing_usecase.id  # 或 existing_usecase.use_case_id
                print(f"已存在 UseCase '{item['use_case_name']}'，ID: {usecase_id}")

            details = item["details"]
            
            
            usecase = await UseCaseController.update_use_case(
                use_case_id = usecase_id,
                normal_process=details.get("正常程序"),
                exception_process=details.get("例外程序"),
                pre_condition=details.get("前置條件"),
                post_condition=details.get("後置條件"),
                trigger_condition=details.get("觸發條件"),
            )

    async def update_usecasedetail(self):
        project_id = app.storage.user.get('selected_project', {}).get('id')
        
    async def generate_event_summary(self):
        project_name = app.storage.user.get('selected_project', {}).get('name')
        await generate_event_summary(project_name)

    async def on_tab_change(self,e):
        if e.args == 'Detail':
            print("切換到 Detail 標籤")

            
        elif e.args == 'two':
            print("切換到 two 標籤")
            
        
    async def show_event_detail(self, use_case_id):
        # 1. 查詢事件資料
        events = await AiaseController.get_events_by_usecase(use_case_id)
        print(f"查詢到的事件數量: {len(events)}")
        if not isinstance(events, list):
            ui.notify("查無事件資料", color="negative")
            return

        # 2. 分類事件
        normal_events = []
        exception_events = []
        for e in events:
            if e['event_list_type'] == '正常程序':
                normal_events.append(f"{e['sequence_no']}. {e['type']} - {e['description']}")
            elif e['event_list_type'] == '例外程序':
                exception_events.append(f"{e['sequence_no']}. {e['type']} - {e['description']}")

        # 3. 顯示在 textarea
        self.inputs['正常程序_event_summary'].value = "\n".join(normal_events)
        self.inputs['例外程序_event_summary'].value = "\n".join(exception_events)
    
    async def generate_md_and_pdf(self):
        self.select_user_account = await UserAccountControler.select_user_account(account=self.user_account)
        self.user_id = self.select_user_account.id if self.select_user_account else None
        md_dir = os.path.join('.', '.home', str(self.user_id),self.select_project_name,'MD')
        pdf_dir = os.path.join('.', '.home', str(self.user_id), self.select_project_name, 'PDF')
        os.makedirs(md_dir, exist_ok=True) # 自動建立 MD 資料夾
        os.makedirs(pdf_dir, exist_ok=True) # 自動建立 PDF 資料夾
        for uc in self.usecases:
            # 查詢事件資料
            events = await AiaseController.get_events_by_usecase(uc['id'])
            normal_events = []
            exception_events = []
            for e in events:
                if e['event_list_type'] == '正常程序':
                    normal_events.append(f"{e['sequence_no']}. {e['type']} - {e['description']}")
                elif e['event_list_type'] == '例外程序':
                    exception_events.append(f"{e['sequence_no']}. {e['type']} - {e['description']}")

            filename = os.path.join(md_dir, f"{uc['use_case_name']}.md")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(
                    f"<h1 align='center'>UC-{uc['use_case_name']}</h1>\n\n"
                    f"| 欄位         | 內容 |\n"
                    f"|--------------|------|\n"
                    f"| UseCase ID   | {uc['id']} |\n"
                    f"| Actor        | {uc['actor']} |\n"
                    f"| 描述         | {uc['description']} |\n"
                    f"\n"
                    f"---\n\n"
                    f"## 正常程序\n"
                    "```text\n"
                    f"{uc['normal_process']}\n"
                    "```\n\n"
                    f"## 例外程序\n"
                    "```text\n"
                    f"{uc['exception_process']}\n"
                    "```\n\n"
                    f"## 前置條件\n"
                    "```text\n"
                    f"{self._to_md_list(uc['pre_condition'])}\n\n"
                    "```\n\n"
                    f"## 後置條件\n"
                    "```text\n"
                    f"{self._to_md_list(uc['post_condition'])}\n\n"
                    "```\n\n"
                    f"---\n\n"
                    f"## 正常程序(三段式)\n"
                    "| 步驟 | 類型 | 說明 |\n"
                    "|------|------|------|\n"
                    + "\n".join([
                        f"| {i+1} | {e.split(' - ')[0].split('. ')[1] if ' - ' in e else ''} | {e.split(' - ')[1] if ' - ' in e else e} |"
                        for i, e in enumerate(normal_events)
                    ]) + "\n\n"
                    f"## 例外程序(三段式)\n"
                    "| 步驟 | 類型 | 說明 |\n"
                    "|------|------|------|\n"
                    + "\n".join([
                        f"| {i+1} | {e.split(' - ')[0].split('. ')[1] if ' - ' in e else ''} | {e.split(' - ')[1] if ' - ' in e else e} |"
                        for i, e in enumerate(exception_events)
                    ]) + "\n"
                )
        GeneratePDF.generate_pdf(md_dir=md_dir, pdf_dir=pdf_dir)
        await self.generate_event_summary_json()
        print("已產生每個 usecase 的 MD 檔案（格式化報表）")
        print("已產生每個 usecase 的 PDF 檔案（格式化報表）")
    
    def _to_md_list(self, text):
    # 將多行字串轉成 markdown 編號清單（不加 - ）
        return "\n".join([line.strip() for line in text.replace('\r', '').split('\n') if line.strip()])
    
    async def generate_event_summary_json(self):
        def parse_event_str(event_str):
            # 假設格式為 "1. 類型 - 說明"
            parts = event_str.split(" - ", 1)
            # 去掉前面的序號
            type_part = parts[0].split(". ", 1)
            event_type = type_part[1] if len(type_part) == 2 else type_part[0]
            event_desc = parts[1] if len(parts) > 1 else ""
            return {"類型": event_type, "說明": event_desc}

        result = []
        for uc in self.usecases:
            events = await AiaseController.get_events_by_usecase(uc['id'])
            normal_events = []
            exception_events = []
            for e in events:
                if e['event_list_type'] == '正常程序':
                    # 轉成 dict 格式
                    normal_events.append(parse_event_str(f"{e['sequence_no']}. {e['type']} - {e['description']}"))
                elif e['event_list_type'] == '例外程序':
                    exception_events.append(parse_event_str(f"{e['sequence_no']}. {e['type']} - {e['description']}"))
            event_summary = {
                "正常程序": {"事件列表": normal_events},
                "例外程序": {"事件列表": exception_events}
            }
            result.append({
                "use_case_name": uc['use_case_name'],
                "event_summary": event_summary
            })

        json_dir = os.path.join('.', '.home', str(self.user_id), self.select_project_name, 'json')
        os.makedirs(json_dir, exist_ok=True)
        json_filename = os.path.join(json_dir, f"{self.select_project_name}_event_summary.json")
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"已產生：{json_filename}")

