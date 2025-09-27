from nicegui import ui
import asyncio
from agents.ai_class import generate_all_ai_classes
from agents.ai_sequence import generate_all_sequences
from agents.ai_code import generate_code
from agents.ai_ERD import generate_erd

class ShowMenuView:
    def __init__(self, on_select: callable = None, current_step: str = None):
        self.stepper = None
        self.current_step = current_step
        self.on_select = on_select

    def show_menu(self):
        """以 stepper 方式顯示功能選單，點選項目時呼叫 on_select(view_name)，self.current_step 用於高亮顯示目前步驟"""
        with ui.stepper().props('vertical').classes('w-full') as stepper:
            self.stepper = stepper
            with ui.step('專案管理').props('active' if self.current_step == 'project' else ''):
                ui.label('進入專案管理功能')
                with ui.stepper_navigation():
                    ui.button('下一步', on_click=stepper.next)
                    ui.button('前往', on_click=lambda: self.on_select and self.on_select('project')).props('flat')
            with ui.step('使用案例管理').props('active' if self.current_step == 'usecase' else ''):
                ui.label('進入使用案例管理功能')
                with ui.stepper_navigation():
                    ui.button('下一步', on_click=stepper.next)
                    ui.button('返回', on_click=stepper.previous).props('flat')
                    ui.button('前往', on_click=lambda: self.on_select and self.on_select('usecase')).props('flat')
            with ui.step('使用案例明細').props('active' if self.current_step == 'usecase_detail' else ''):
                ui.label('查看使用案例明細')
                with ui.stepper_navigation():
                    ui.button('下一步', on_click=stepper.next)
                    ui.button('返回', on_click=stepper.previous).props('flat')
                    ui.button('前往', on_click=lambda: self.on_select and self.on_select('usecase_detail')).props('flat')
            with ui.step('專案物件瀏覽').props('active' if self.current_step == 'project_object' else ''):
                ui.label('瀏覽專案相關物件（如資料表、類別、元件等）')
                with ui.stepper_navigation():
                    with ui.column().classes('gap-1'):
                        ui.button('生成類別', on_click=generate_all_ai_classes)
                        ui.button('生成循序', on_click=generate_all_sequences)
                        ui.button('生成ERD圖', on_click=generate_erd)
                        ui.button('查看ERD圖', on_click=lambda: ui.navigate.to('/mermaid-erd'))
                        ui.button('查看圖', on_click=lambda: ui.navigate.to('/mermaid')).classes('bg-gray-200')
                    with ui.row().classes('gap-1'):
                        ui.button('下一步', on_click=stepper.next)
                        ui.button('返回', on_click=stepper.previous).props('flat')
                        ui.button('前往', on_click=lambda: self.on_select and self.on_select('project_object')).props('flat')
            with ui.step('產生程式碼').props('active' if self.current_step == 'generate_code' else ''):
                ui.label('產生程式碼')
                with ui.stepper_navigation():
                    with ui.column().classes('gap-1'):
                        ui.button('生成程式碼', on_click=generate_code)
                    ui.button('下一步', on_click=stepper.next)
                    ui.button('返回', on_click=stepper.previous).props('flat')
                    ui.button('前往', on_click=lambda: self.on_select and self.on_select('generate_code')).props('flat')

    def next_step(self):
        if self.stepper:
            self.stepper.next()

