from nicegui import ui, app
import os
from views.file_manager import FileManager
from views.file_handlers import GenericFileHandler
from views.togglable_tabs import TogglableTabs, TogglableTab
from controllers.user_account_controler import UserAccountControler

class FileExplorer():
    def __init__(self):
        self.user_account = app.storage.user.get('current_user_account')

    async def display(self):
        self.select_user_account = await UserAccountControler.select_user_account(account=self.user_account)
        self.user_id = self.select_user_account.id if self.select_user_account else None
        with ui.grid(columns='40px auto 1fr').classes('w-full h-full m-0 p-0 gap-0').style('width: calc(100vw - 20px); height: calc(100vh - 10px)'):
            with ui.column().classes('border border-gray-300 m-0 p-0 gap-0'):
                with TogglableTabs().props('vertical switch-indicator').classes('w-full') as tabs:
                    file_manager_tab = TogglableTab(name='File', label='', icon='view_list')
                    settings_tab = TogglableTab(name='Settings', label='', icon='settings')

            with ui.grid(rows='auto').classes('border border-gray-300 m-0 p-0 gap-0'):
                with ui.tab_panels(tabs, value=file_manager_tab).classes('w-[550px] h-full').props('vertical').bind_visibility_from(tabs, 'switch'):
                    with ui.tab_panel(file_manager_tab).classes('m-0 p-0 gap-0'):
                        with ui.grid(rows='auto').classes('w-full h-full'):
                            user_home_dir = os.path.join('.', '.home', str(self.user_id))
                            file_manager = FileManager(str(self.user_id))
                            await file_manager.display()                            
                    with ui.tab_panel(settings_tab).classes('m-0 p-0 gap-0'):
                        with ui.grid(rows='auto').classes('w-full h-full'):
                            ui.label('Settings').classes('text-h4')
            
            with ui.grid(rows='auto').classes('border border-gray-300 w-full h-full m-0 gap-0 p-0'):
                file_handler = GenericFileHandler()
                file_manager.set_file_handeler(file_handler)

    async def refresh(self) -> None:
        pass