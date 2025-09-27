from nicegui import ui , app
from controllers.user_account_controler import UserAccountControler 

class LoginView():
    def __init__(self):
        self.account_input = None
        self.password_input = None

    async def display(self):
        with ui.card():
            with ui.column().classes('w-[600px]'):
                self.account_input = ui.input(label='帳號:', placeholder='請輸入您的帳號').classes('w-full')
                self.password_input = ui.input(label='密碼:', placeholder='請輸入您的密碼', password=True).classes('w-full')           
            with ui.row():
                ui.button('登入', on_click=self.login)
                ui.button('註冊', on_click=self.register)

    async def login(self):
        account = self.account_input.value
        password = self.password_input.value

        if account and password:
            user_account = await UserAccountControler.select_user_account(account=account)
            if user_account is not None and user_account.account == account and user_account.password == password:
                ui.notify('登入成功!')
                app.storage.user['current_user_account'] = user_account.account
                app.storage.user['current_user_password'] = user_account.password
                print(f"User {app.storage.user.get('current_user_account')} logged in successfully.")
                print(f"Password {app.storage.user.get('current_user_password')} logged in successfully.")
                ui.navigate.to('/project_view')
                
            else:
                ui.notify('帳號密碼錯誤!')

  
    async def register(self):
        account = self.account_input.value
        password = self.password_input.value
        if account and password:
            await UserAccountControler.add_user_account(account=account, password=password)
            ui.notify('註冊成功!')
        else:
            ui.notify('請輸入新帳號和新密碼!')

