from nicegui import ui,app
from views.newusecase_view import UseCaseView
from controllers.aiase_controller import AiaseController
from agents.ai_svo_object import generate_objects_from_event_summary
from controllers.user_account_controler import UserAccountControler
import json
import os

class ObjectView:

    def __init__(self):
        self.master_grid = None
        self.inputs = {}
        self.event = []
        self.generated_objects = []
        self.result_label = None
        self.rightdrawer = None
        self.maincolum = None
        self.usecase_view = UseCaseView()
        self.detail_area = None
        self.current_detail = None #暫存目前點選的物件詳細內容
        self.user_account = app.storage.user.get('current_user_account')
        self.project_name = app.storage.user.get('selected_project', {}).get('name')
        self.user_id = app.storage.user.get('selected_user_id')
    

    async def display(self):
        self.select_user_account = await UserAccountControler.select_user_account(account=self.user_account)
        self.user_id = self.select_user_account.id if self.select_user_account else None
        
        OBJECT_PATH = os.path.join('.', '.home', str(self.user_id), self.project_name, 'json', 'object.json')
        os.makedirs(os.path.dirname(OBJECT_PATH), exist_ok=True)
        with ui.column().classes('w-full items-center p-4 gap-4') as maincolum:
            self.maincolum = maincolum
            ui.label('專案物件瀏覽').classes('text-xl font-bold')
            with ui.card().classes('w-full max-w-4xl p-4'):
                with ui.column().classes('w-full gap-4'):
                    ui.label('這裡將顯示專案相關物件（如資料表、類別、元件等）的詳細資訊')
                    summary = await AiaseController.get_event_summary_by_project(
                        app.storage.user.get('selected_project', {}).get('id'))
                    async def show_summary():
                        formatted = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True)
                        # 將 summary 輸出成 JSON 檔案
                        OUTPUT_PATH = os.path.join('.', '.home', str(self.user_id), self.project_name, 'json', 'summary_output.json')
                        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

                        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                            json.dump(summary, f, indent=2, ensure_ascii=False)
                        print(f"✅ summary 已儲存於：{OUTPUT_PATH}")
                        self.generated_objects = await generate_objects_from_event_summary(summary)
                        with open(OBJECT_PATH, encoding="utf-8") as f:
                            self.event = json.load(f)
                        if self.master_grid:
                            self.master_grid.options['rowData'] = self.event
                            self.master_grid.update()

                    ui.button('匯出 summary JSON', on_click=show_summary).classes('w-full')
        with ui.column().classes('w-full max-w-4xl p-4'):
            if not os.path.exists(OBJECT_PATH):
                self.event=[]
            else:
                with open(OBJECT_PATH, encoding="utf-8") as f:
                    self.event = json.load(f)
            ui.label('master - 使用案例清單').classes('text-lg font-bold')
            self.master_grid = ui.aggrid({
                'columnDefs': [
                    {"headerName": "使用案例名稱", "field": "使用案例名稱", "flex": 1}
                ],
                'rowData': self.event,
                'rowSelection': 'single'
            }).classes('w-full h-64')
            self.master_grid.on("selectionChanged", self.on_master_selected)
            self.boundary_grid = ui.aggrid({
                'columnDefs': [
                    {"headerName": "邊界名稱", "field": "邊界名稱", "flex": 1}
                ],
                'rowData': self.event,
                'rowSelection': 'single'
            })
            self.boundary_grid.on('cellClicked', lambda event: self.show_object_detail(event.args['data'].get('邊界名稱'), "Boundary"))
            self.entity_grid = ui.aggrid({
                'columnDefs': [
                    {"headerName": "實體名稱", "field": "實體名稱", "flex": 1}
                ],
                'rowData': self.event,
                'rowSelection': 'single'
            })
            self.entity_grid.on('cellClicked', lambda event: self.show_object_detail(event.args['data'].get('實體名稱'), "Entity"))

            self.control_grid = ui.aggrid({
                'columnDefs': [
                    {"headerName": "控制名稱", "field": "控制名稱", "flex": 1}
                ],
                'rowData': self.event,
                'rowSelection': 'single'
            })
            self.control_grid.on('cellClicked', lambda event: self.show_object_detail(event.args['data'].get('控制名稱'), "Control"))


    async def right_drawer(self):
        self.detail_area = ui.textarea(
            '這裡將顯示使用案例的詳細資訊，請從清單選擇一個使用案例'
            ).classes('w-full h-32')
        
    async def on_master_selected(self, event):
        selected_rows = await self.master_grid.get_selected_rows()
        if selected_rows:
            selected_row = selected_rows[0]
            use_case_name = selected_row.get("使用案例名稱")
            if use_case_name:
                # 讀取 object.json
                OBJECT_PATH = os.path.join('.', '.home', str(self.user_id), self.project_name, 'json', 'object.json')
                with open(OBJECT_PATH, encoding="utf-8") as f:
                    all_objects = json.load(f)
                # 找到對應的使用案例
                detail = next((item for item in all_objects if item["使用案例名稱"] == use_case_name), None)
                if detail:
                    # 格式化顯示物件結構
                    formatted = json.dumps(detail["物件結構"], ensure_ascii=False, indent=2)
                    # 右側顯示
                    self.detail_area.value = formatted
                
                    boundaries = []
                    entities = []
                    controls = []
                    for obj in detail["物件結構"]:
                        obj_type = obj.get("類型")
                        if obj_type == "Boundary":
                            boundaries.append({"邊界名稱": obj.get("名稱","")})
                        elif obj_type == "Entity":
                            entities.append({"實體名稱": obj.get("名稱","")})
                        elif obj_type == "Control":
                            controls.append({"控制名稱": obj.get("名稱","")})

                    self.boundary_grid.options['rowData'] = boundaries
                    self.boundary_grid.update()
                    self.entity_grid.options['rowData'] = entities
                    self.entity_grid.update()
                    self.control_grid.options['rowData'] = controls
                    self.control_grid.update()
    
    async def show_object_detail(self, obj_name, obj_type):
        #取得目前使用案例的物件詳細資訊
        selected_rows = await self.master_grid.get_selected_rows()
        if not selected_rows:
            ui.notify('請先選擇使用案例')
            return
        use_case_name = selected_rows[0].get("使用案例名稱")
        OBJECT_PATH = os.path.join('.', '.home', str(self.user_id), self.project_name, 'json', 'object.json')  # ← 修正這裡
        with open(OBJECT_PATH, encoding="utf-8") as f:
            all_objects = json.load(f)
        # 找到對應的使用案例
        detail = next((item for item in all_objects if item["使用案例名稱"] == use_case_name), None)
        if not detail:
            ui.notify('找不到使用案例')
            return
        # 找到該物件
        obj_detail = next((obj for obj in detail["物件結構"] if obj.get("名稱") == obj_name and obj.get("類型") == obj_type), None)
        if not obj_detail:
            ui.notify('找不到物件詳細內容')
            return
        # 顯示 dialog
        with ui.dialog() as dialog, ui.card():
            ui.label(f'{obj_type}：{obj_name} 詳細內容')
            ui.textarea(value=json.dumps(obj_detail, ensure_ascii=False, indent=2)).props().classes('w-96 h-64')            
            ui.button('關閉', on_click=dialog.close)
        dialog.open()
    
    async def on_boundary_row_clicked(self, event):
        obj_name = event.args['data'].get('邊界名稱')
        await self.show_object_detail(obj_name, "Boundary")
    
    async def on_entity_row_clicked(self, event):
        obj_name = event.args['data'].get('實體名稱')
        await self.show_object_detail(obj_name, "Entity")
    
    async def on_control_row_clicked(self, event):
        obj_name = event.args['data'].get('控制名稱')
        await self.show_object_detail(obj_name, "Control")