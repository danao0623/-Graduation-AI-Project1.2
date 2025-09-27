from nicegui import ui,app
from views.newusecase_view import UseCaseView

class ProjectDetailView:

    def __init__(self):
        self.inputs = {}
        self.result_label = None
        self.rightdrwer = None
        self.maincolum = None
        self.usecase_view = UseCaseView()

    def set_project_data(self, data: dict):
        """從上一頁設定專案資料"""
        self.project_data = data

    def set_project_data(self, data: dict):
        """設置專案資料"""
        self.project_data = data
        print(f"專案資料已設定: {self.project_data}")

    async def display(self):
        selected_project = app.storage.user.get('selected_project')
        if not selected_project:
            ui.notify('找不到已選擇的專案資料', color='red')
            return

        with ui.column().classes('w-full items-center p-4 gap-4') as maincolum:
            self.maincolum = maincolum
            ui.label('專案管理系統').classes('text-xl font-bold')

            with ui.card().classes('w-full max-w-4xl p-4'):  # 整張卡片最大寬度設定
                with ui.column().classes('w-full gap-4'):
                    self.inputs['專案名稱'] = ui.input('專案名稱:').classes('w-full min-w-[400px]').props('readonly').value = selected_project.get('name', '')

                    with ui.grid(columns=2).classes('w-full'):
                        self.inputs['前端語言'] = ui.input('前端語言:').classes('w-full').props('readonly').value = selected_project.get('frontend_language', '')
                        self.inputs['前端平台'] = ui.input('前端平台:').classes('w-full').props('readonly').value = selected_project.get('frontend_platform', '')

                    self.inputs['前端函式庫'] = ui.input('前端函式庫:').classes('w-full min-w-[500px]').props('readonly').value = selected_project.get('frontend_library', '')

                    with ui.grid(columns=2).classes('w-full'):
                        self.inputs['後端語言'] = ui.input('後端語言:').classes('w-full').props('readonly').value = selected_project.get('backend_language', '')
                        self.inputs['後端平台'] = ui.input('後端平台:').classes('w-full').props('readonly').value = selected_project.get('backend_platform', '')

                    self.inputs['後端函式庫'] = ui.input('後端函式庫:').classes('w-full min-w-[500px]').props('readonly').value = selected_project.get('backend_library', '')

                    self.inputs['專案描述'] = ui.textarea(label='專案描述').classes('w-full min-h-[100px] max-w-[800px]').props('readonly').value = selected_project.get('description', '')
                    self.inputs['專案架構'] = ui.textarea(label='專案架構').classes('w-full min-h-[100px] max-w-[800px]').props('readonly').value = selected_project.get('architecture', '')

            self.result_label = ui.label()

            ui.button('返回使用案例', on_click=self.back_usecase)

    async def back_usecase(self):
        """切換畫面為 UseCaseView"""
        
        ui.notify('已返回使用案例頁面', color='green')