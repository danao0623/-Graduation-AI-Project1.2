from nicegui import ui,events,app
from controllers.project_controller import ProjectController
from controllers.user_account_controler import UserAccountControler
from agents.project_agent import ProjectAgent
from views.newusecase_view import UseCaseView
from views.projectopen_view import ProjectDetailView
from views.show_menu_view import ShowMenuView
from views.usecacedetail_view import UseCaseDetailView
from views.object_view import ObjectView
import os
import json
from views.md_view import MDView
from controllers.user_account_controler import UserAccountControler

class ProjectView:
    def __init__(self):
        # 使用與 show_menu 比較時一致的 key（英文）
        self.current_step = 'project'
        self.projects = []
        self.grid = None
        self.ai_grid = None
        self.inputs = {}
        self.next_id = 1
        self.project_name = None
        self.json_data = None  # 用來分配唯一 ID
        self.maincolum = None
        self.rightdrawer = None
        self.leftdrawer = None
        self.usecase_view = UseCaseView(project_view=self)
        self.project_open_view = ProjectDetailView()
        self.object_view = ObjectView()
        self.md_view = MDView()
        self.show_menu = ShowMenuView()

    async def menu_display(self):
        with ui.drawer('left').classes('w-64 bg-gray-100') as self.left_drawer:
            self.show_menu = ShowMenuView(self.handle_menu , current_step=self.current_step)
            self.show_menu.show_menu()

    async def display(self):
        
        
        with ui.column().classes('w-full items-center p-4 gap-4') as maincolum:

            self.maincolum = maincolum
            ui.label('專案管理系統').classes('text-xl font-bold')

            with ui.card().classes('w-full p-4'):
                with ui.column().classes('w-full gap-4'):
                    self.inputs['專案名稱'] = ui.input('專案名稱:').classes('w-full')
                    
                    with ui.grid(columns=2):                           
                            self.inputs['前端語言'] = ui.input('前端語言:').classes('w-full')
                            self.inputs['前端平台'] = ui.input('前端平台:').classes('w-full')
                    
                    self.inputs['前端函式庫'] = ui.input('前端函式庫:').classes('w-full')
                    
                    with ui.grid(columns=2):
                        self.inputs['後端語言'] = ui.input('後端語言:').classes('w-full')
                        self.inputs['後端平台'] = ui.input('後端平台:').classes('w-full')
                    
                    self.inputs['後端函式庫'] = ui.input('後端函式庫:').classes('w-full')
                    self.inputs['專案描述'] = ui.textarea(label='專案描述', placeholder='請輸入專案描述').classes('w-full')
                    self.inputs['專案架構'] = ui.textarea(label='專案架構', placeholder='請輸入專案架構').classes('w-full')
                         
        
            self.result_label = ui.label()
            
            options = { #3/7
                'columnDefs': [
                    {'headerName': '選擇', 'field': 'selected', 'width': 60, 'checkboxSelection': True},
                    {'headerName': 'ID', 'field': 'id', 'hide': True},
                    {'headerName': '專案名稱', 'field': 'name', 'width': 150},
                    {'headerName': '專案描述', 'field': 'description', 'flex': 1, 'editable': True},
                    {'headerName': '系統架構', 'field': 'architecture', 'flex': 1, 'editable': True},
                    {'headerName': '前端語言', 'field': 'frontend_language', 'width': 120, 'editable': True},
                    {'headerName': '前端平台', 'field': 'frontend_platform', 'width': 120, 'editable': True},
                    {'headerName': '前端程式庫', 'field': 'frontend_library', 'width': 120, 'editable': True},
                    {'headerName': '後端語言', 'field': 'backend_language', 'width': 120, 'editable': True},
                    {'headerName': '後端平台', 'field': 'backend_platform', 'width': 120, 'editable': True},
                    {'headerName': '後端函式庫', 'field': 'backend_library', 'width': 120, 'editable': True},
                ],
                'rowSelection': 'multiple',  # 允許多選
            }
            self.grid = ui.aggrid(options=options).classes('w-full').on('cellValueChanged',self.on_cell_value_changed)
            
            with ui.row().classes('w-full justify-center gap-4'):
                ui.button('新增', on_click=self.add_project).classes('bg-blue-500 text-white px-4 py-2')
                ui.button('刪除', on_click=self.delete_project).classes('bg-red-500 text-white px-4 py-2')
                ui.button('開啟專案', on_click=self.usecase_viewshow).classes('bg-green-500 text-white px-4 py-2')



    async def display_right_drawer(self):

        with ui.column().classes('w-full items-center p-4 gap-4') as rightdrawer:
            self.rightdrawer = rightdrawer
            ui.label('AI 模型').classes('text-lg font-bold px-4 py-2')  # 右側抽屜
            with ui.row().classes('w-full justify-center gap-4'):
                ui.button('生成專案', on_click=self.ai_new_project).classes('bg-blue-500 text-white px-4 py-2')
                ui.button('導入資料', on_click=self.import_selected_items).classes('bg-red-500 text-white px-4 py-2')
                ui.button('全部選取', on_click=self.select_all_ai_grid_rows)
                self.ai_grid = ui.aggrid(options={'columnDefs': []}).classes('w-full')
        await self.refresh()

    async def refresh(self): #3/7
        """刷新表格資料，更新專案相關欄位"""
        user_account = app.storage.user.get('current_user_account')     
        select_user_account = await UserAccountControler.select_user_account(account=user_account)
        user_id = select_user_account.id if select_user_account else None
        user_accounts = await ProjectController.get_projects_by_user_id(user_id=user_id)

        # 轉換資料格式，確保包含所有需要的欄位
        options = [
            {
                'id': u.id,
                'name': u.name,
                'description': u.description,
                'architecture': u.architecture,
                'frontend_language': u.frontend_language,
                'frontend_platform': u.frontend_platform,
                'frontend_library': u.frontend_library,
                'backend_language': u.backend_language,
                'backend_platform': u.backend_platform,
                'backend_library': u.backend_library,
            }
            for u in user_accounts
        ]

        self.grid.options['rowData'] = options  # 設定新的資料
        self.grid.update()

    async def add_project(self):
        """新增專案並分配唯一 ID"""
        user_account = app.storage.user.get('current_user_account')     
        
        select_user_account = await UserAccountControler.select_user_account(account=user_account)
        user_id = select_user_account.id if select_user_account else None

        name = self.inputs['專案名稱'].value
        description = self.inputs['專案描述'].value
        architecture = self.inputs['專案架構'].value
        frontend_language = self.inputs['前端語言'].value
        frontend_platform = self.inputs['前端平台'].value
        frontend_library = self.inputs['前端函式庫'].value
        backend_language = self.inputs['後端語言'].value
        backend_platform = self.inputs['後端平台'].value
        backend_library = self.inputs['後端函式庫'].value

        if name and description:
            project = {
                'id': self.next_id,  # 分配唯一 ID
                'name': name,
                'description': description,
                'architecture': architecture,
                'frontend_language': frontend_language,
                'frontend_platform': frontend_platform,
                'frontend_library': frontend_library,
                'backend_language': backend_language,
                'backend_platform': backend_platform,
                'backend_library': backend_library,
            }
            self.next_id += 1
            self.projects.append(project)
            await ProjectController.add_project(
                name=name,
                description=description,
                architecture=architecture,
                frontend_language=frontend_language,
                frontend_platform=frontend_platform,
                frontend_library=frontend_library,
                backend_language=backend_language,
                backend_platform=backend_platform,
                backend_library=backend_library,
                user_id=user_id  # 傳入 user_id
            )
            
            await self.refresh()
            
            # 清空輸入框
            self.inputs['專案名稱'].value = ''
            self.inputs['專案描述'].value = ''
            self.inputs['專案架構'].value = ''
            self.inputs['前端語言'].value = ''
            self.inputs['前端平台'].value = ''
            self.inputs['前端函式庫'].value = ''
            self.inputs['後端語言'].value = ''
            self.inputs['後端平台'].value = ''
            self.inputs['後端函式庫'].value = ''


    async def delete_project(self):
        """根據唯一 ID 刪除選中的專案"""
        selected_rows = await self.grid.get_selected_rows()
        selected_ids = {row['id'] for row in selected_rows}  # 取得所有選中的 ID
        self.projects = [p for p in self.projects if p['id'] not in selected_ids]
        for id in selected_ids:
            await ProjectController.delete_project(id=id)
        await self.refresh()

    async def usecase_viewshow(self):
        selected_rows = await self.grid.get_selected_rows()
        if not selected_rows:
            ui.notify('請選擇至少一個專案', color='red')
            return
        
        selected_rows = selected_rows[0]

        app.storage.user['selected_project'] = {
        'id': selected_rows.get('id'),
        'name': selected_rows.get('name'),
        'description': selected_rows.get('description'),
        'architecture': selected_rows.get('architecture'),
        'frontend_language': selected_rows.get('frontend_language'),
        'frontend_platform': selected_rows.get('frontend_platform'),
        'frontend_library': selected_rows.get('frontend_library'),
        'backend_language': selected_rows.get('backend_language'),
        'backend_platform': selected_rows.get('backend_platform'),
        'backend_library': selected_rows.get('backend_library'),
        }
        ui.notify('專案已成功開啟', color='green')
        
        await self.handle_menu('usecase')
        if self.usecase_view:
            self.show_menu.next_step()

    async def on_cell_value_changed(self, event: events.GenericEventArguments): #3/7
        
        """當表格中的值被編輯後觸發，更新資料庫中的對應欄位"""
        # 取得所有欄位
        id = event.args['data']['id']
        name = event.args['data']['name']
        description = event.args['data']['description']
        architecture = event.args['data']['architecture']
        frontend_language = event.args['data']['frontend_language']
        frontend_platform = event.args['data']['frontend_platform']
        frontend_library = event.args['data']['frontend_library']
        backend_language = event.args['data']['backend_language']
        backend_platform = event.args['data']['backend_platform']
        backend_library = event.args['data']['backend_library']

        # 更新資料
        await ProjectController.update_user_account(
            id=id,
            name=name,
            description=description,
            architecture=architecture,
            frontend_language=frontend_language,
            frontend_platform=frontend_platform,
            frontend_library=frontend_library,
            backend_language=backend_language,
            backend_platform=backend_platform,
            backend_library=backend_library
        )
        await self.refresh()

    async def ai_new_project(self):
        name = self.inputs['專案名稱'].value
        if name:
            self.project_name = name
            json_data = await ProjectAgent.get_json(project_name=name)
            ai_data = [
                {'generated_content': '專案名稱', 'content': json_data.get('project_name', '')},
                {'generated_content': '專案描述', 'content': json_data.get('description', '')},
                {'generated_content': '系統架構', 'content': json_data.get('architecture', '')},
                {'generated_content': '前端語言', 'content': json_data.get('frontend', {}).get('language', '')},
                {'generated_content': '前端平台', 'content': json_data.get('frontend', {}).get('platform', '')},
                {'generated_content': '前端函式庫', 'content': json_data.get('frontend', {}).get('library', '')},
                {'generated_content': '後端語言', 'content': json_data.get('backend', {}).get('language', '')},
                {'generated_content': '後端平台', 'content': json_data.get('backend', {}).get('platform', '')},
                {'generated_content': '後端函式庫', 'content': json_data.get('backend', {}).get('library', '')},
            ]
            self.ai_grid.options['columnDefs'] = [
                {'headerName': '選擇', 'field': 'selected', 'width': 60, 'checkboxSelection': True},  # 第一列：選擇
                {'headerName': '產生內容', 'field': 'generated_content', 'flex': 1},  # 第二列：產生內容
                {'headerName': '內容', 'field': 'content', 'flex': 1},  # 第三列：內容
            ]
            self.ai_grid.options['rowSelection'] = 'multiple' 
            self.ai_grid.options['rowData'] = ai_data  # 更新資料
            self.ai_grid.update()  # 應用更改

    async def import_selected_items(self):
        """將選擇的多個項目從 AI Grid 導入到輸入框"""
        selected_rows = await self.ai_grid.get_selected_rows()  # 獲取選擇的行
        if not selected_rows:
            ui.notify('請選擇至少一個項目進行導入', color='red')
            return

        for row in selected_rows:
            if row.get('generated_content') == '專案名稱':
                self.inputs['專案名稱'].value = '' 
                self.inputs['專案名稱'].value += row.get('content', '')  
            elif row.get('generated_content') == '專案描述':
                self.inputs['專案描述'].value = ''  
                self.inputs['專案描述'].value += row.get('content', '')  
            elif row.get('generated_content') == '系統架構':
                self.inputs['專案架構'].value = ''  
                self.inputs['專案架構'].value += row.get('content', '')  
            elif row.get('generated_content') == '前端語言':
                self.inputs['前端語言'].value = ''  
                self.inputs['前端語言'].value += row.get('content', '')  
            elif row.get('generated_content') == '前端平台':
                self.inputs['前端平台'].value = ''  
                self.inputs['前端平台'].value += row.get('content', '')  
            elif row.get('generated_content') == '前端函式庫':
                self.inputs['前端函式庫'].value = ''  
                self.inputs['前端函式庫'].value += row.get('content', '')  
            elif row.get('generated_content') == '後端語言':
                self.inputs['後端語言'].value = ''  
                self.inputs['後端語言'].value += row.get('content', '')  
            elif row.get('generated_content') == '後端平台':
                self.inputs['後端平台'].value = ''  
                self.inputs['後端平台'].value += row.get('content', '')  
            elif row.get('generated_content') == '後端函式庫':
                self.inputs['後端函式庫'].value = ''  
                self.inputs['後端函式庫'].value += row.get('content', '')  

        ui.notify('資料已成功導入', color='green')


    #開啟目前專案的    
    async def projectopen_view(self):
        selected_rows = app.storage.user.get('selected_project')

        app.storage.user['selected_project'] = {
        'id': selected_rows.get('id'),
        'name': selected_rows.get('name'),
        'description': selected_rows.get('description'),
        'architecture': selected_rows.get('architecture'),
        'frontend_language': selected_rows.get('frontend_language'),
        'frontend_platform': selected_rows.get('frontend_platform'),
        'frontend_library': selected_rows.get('frontend_library'),
        'backend_language': selected_rows.get('backend_language'),
        'backend_platform': selected_rows.get('backend_platform'),
        'backend_library': selected_rows.get('backend_library'),
        }
        self.maincolum.clear()
        self.rightdrawer.clear()

        with self.maincolum:
            await self.project_open_view.display()
        #with self.rightdrwer:    
            #await self.usecase_view.display_ai()
        ui.notify('專案已成功開啟', color='green'
                  )
        
    async def handle_menu(self, view_name):
        self.current_step = view_name  # 切換時同步更新 current_step
        # 重新渲染左側 stepper（保證 active 狀態更新）
    
        self.maincolum.clear()
        self.rightdrawer.clear()
        if view_name == 'project':
            with self.maincolum:
                await self.display()
            with self.rightdrawer:
                await self.display_right_drawer()
            ui.notify('已切換到專案管理', color='green')
        elif view_name == 'usecase':
            with self.maincolum:
                await self.usecase_view.display()
            with self.rightdrawer:
                await self.usecase_view.display_ai()
        elif view_name == 'usecase_detail':
            with self.maincolum:
                await UseCaseDetailView().display()
        elif view_name == 'project_object':
            with self.maincolum:
                await self.object_view.display()
            with self.rightdrawer:
                await self.object_view.right_drawer()
        


    def select_all_ai_grid_rows(self):
        # 取得 rowData
        row_data = self.ai_grid.options.get('rowData', [])
        for index, _ in enumerate(row_data):
            self.ai_grid.run_row_method(index, 'setSelected', True)


    def next_step(self):
        if self.show_menu and self.show_menu.stepper:
            self.show_menu.next_step()