from nicegui import ui, app

from core.application import Application
from views.project_view import ProjectView
from views.file_explorer import FileExplorer
from views.test_view import view123
from init_db import engine, create_db_and_tables
from views.login_view import LoginView
from views.mermaid_show_diagrams_view import MermaidDiagramView
from views.projectopen_view import ProjectDetailView
from views.mermaid_erd_view import MermaidERDView


def init_app():
    async def handle_startup():
        try:
            await create_db_and_tables()
        except:
            pass    

    async def handle_shutdown():
        await engine.dispose()

    app.on_startup(handle_startup)
    app.on_shutdown(handle_shutdown)

@ui.page('/project_view')
async def project_view():
    ua = ProjectView()
    await ua.display()
    with ui.drawer('right').classes('w-[250px] bg-gray-100') as right_drawer:
        await ua.display_right_drawer()
        ui.button('前往檔案總管', on_click=lambda: ui.navigate.to('/file_explorer')).classes('w-full bg-gray-200')
        ui.button('目前開啟專案', on_click=lambda: ui.navigate.to('/open_project')).classes('w-full bg-gray-200')
    await ua.menu_display()

@ui.page('/file_explorer')
async def file_explorer():
    ui.button('回首頁', on_click=lambda: ui.navigate.to('/project_view'))
    fe_view = FileExplorer()
    await fe_view.display()

@ui.page('/')
async def login():
    login_view = LoginView()
    await login_view.display()

@ui.page('/mermaid')
async def mermaid_page():
    md_view = await MermaidDiagramView.create()
    md_view.show_diagrams()
    
    ui.button('回首頁', on_click=lambda: ui.navigate.to('/project_view'))

@ui.page('/open_project')
async def open_project():
    open_view = ProjectDetailView()
    await open_view.display()

    ui.button('回首頁', on_click=lambda: ui.navigate.to('/project_view'))

@ui.page('/mermaid-erd')
async def mermaid_erd_page():
    erd_view = await MermaidERDView.create()
    await erd_view.show_erd()

    ui.button('回首頁', on_click=lambda: ui.navigate.to('/project_view'))

init_app()
Application.initialize()
ui.run(storage_secret='private key to secure the browser session cookie',reload=False,port=8080,host='0.0.0.0',reconnect_timeout=60)
