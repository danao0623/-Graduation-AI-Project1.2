from nicegui import ui, events
from controllers.user_account_controler import UserAccountControler 

class UserAccountView():
    def __init__(self):
        self.grid = None    # AgGrid 表格
        self.account_input = None
        self.password_input = None
        self.email_input = None
        self.address_input = None

    async def display(self):
        with ui.card():
            with ui.column().classes('w-[600px]'):
                self.account_input = ui.input(label='帳號:', placeholder='請輸入您的帳號').classes('w-full')
                self.password_input = ui.input(label='密碼:', placeholder='請輸入您的密碼', password=True).classes('w-full')
                self.email_input = ui.input(label='電子郵件:', placeholder='請輸入您的電子郵件').classes('w-full')
                self.address_input = ui.input(label='住址:', placeholder='請輸入您的住址').classes('w-full')                

            with ui.row():
                ui.button('新增', on_click=self.add_account)  # 綁定新增功能
                ui.button('刪除', on_click=self.delete_account)  # 綁定刪除功能

            options = {
                #'defaultColDef': {'flex': 1},  # 自適應列寬
                'columnDefs': [
                    {'headerName': '選擇', 'field': 'selected','width': 60, 'checkboxSelection': True},  # 增加選擇框
                    {'headerName': 'ID', 'field': 'id', 'hide': True},
                    {'headerName': '帳號', 'field': 'account', 'width': 100 },  # 可編輯的帳號欄
                    {'headerName': '密碼', 'field': 'password', 'width': 100,  'editable': True},  # 可編輯的密碼欄
                    {'headerName': '電子郵件', 'field': 'email', 'flex': 1,  'editable': True},  # 可編輯的帳號欄
                    {'headerName': '住址', 'field': 'address', 'flex': 1, 'editable': True},  # 可編輯的帳號欄                    
                ],
                'rowSelection': 'multiple',  # 支援多選
            }
            self.grid = ui.aggrid(options=options).classes('max-h-40').on('cellValueChanged', self.on_cell_value_changed)

        await self.refresh()


    async def refresh(self):
        """更新 AgGrid 表格的顯示資料。"""
        user_accounts = await UserAccountControler.select_all()
        options = [{'id':u.id, 'account':u.account, 'password':u.password, 'email':u.email, 'address':u.address} for u in user_accounts]
        self.grid.options['rowData'] = options  # 設定新的資料
        self.grid.update()  # 更新顯示

    async def add_account(self):
        account = self.account_input.value
        password = self.password_input.value
        email = self.email_input.value
        address = self.address_input.value
        if account and password:
            await UserAccountControler.add_user_account(account=account, email=email, password=password, address=address)
            await self.refresh()  # 更新表格
            self.account_input.value = ''  # 清空輸入框
            self.password_input.value = ''  # 清空輸入框
            self.email_input.value = ''  # 清空輸入框
            self.address_input.value = ''  # 清空輸入框

    async def delete_account(self):
        selected_rows = await self.grid.get_selected_rows()  # 獲取選中的行
        if selected_rows:
            selected_ids = [row['id'] for row in selected_rows]  # 提取選中的帳號
            for id in selected_ids:
                await UserAccountControler.delete_user_account(id=id)
            await self.refresh()  # 刷新顯示

    async def on_cell_value_changed(self, event: events.GenericEventArguments):
        id =  event.args['data']['id']
        account = event.args['data']['account']
        password = event.args['data']['password']
        email = event.args['data']['email']
        address = event.args['data']['address']
        await UserAccountControler.update_user_account(id=id, account=account, email=email, password=password, address=address)
        await self.refresh()        