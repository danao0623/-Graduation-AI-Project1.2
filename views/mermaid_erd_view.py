import os
from utilits.utis import clean_mermaid_code
from nicegui import ui, app
from controllers.user_account_controler import UserAccountControler

class MermaidERDView:
    def __init__(self, user_id, project_name):
        self.user_id = user_id  # ← 加這行
        self.output_dir = os.path.join('.', '.home', str(user_id), project_name, 'MMD')
        self.project_name = project_name
        self.diagram_area = ui.column()

    @classmethod
    async def create(cls):
        user_account = app.storage.user.get('current_user_account')
        project_name = app.storage.user.get('selected_project', {}).get('name')
        select_user_account = await UserAccountControler.select_user_account(account=user_account)
        user_id = select_user_account.id if select_user_account else None
        output_dir = os.path.join('.', '.home', str(user_id), project_name, 'MMD')
        if isinstance(user_account, dict):
            user_id = user_account.get('id')
        else:
            user_id = user_account  # 或 None，看你的需求
        return cls(user_id, project_name)

    async def show_erd(self):
        user_account = app.storage.user.get('current_user_account')
        project_name = app.storage.user.get('selected_project', {}).get('name')
        select_user_account = await UserAccountControler.select_user_account(account=user_account)
        user_id = select_user_account.id if select_user_account else None
        self.user_id = user_id
        self.project_name = project_name
        erd_path = os.path.join(
            '.', '.home', str(self.user_id), self.project_name, 'MMD', f'{self.project_name}_erd.mmd'
        )
        try:
            with open(erd_path, encoding='utf-8') as f:
                erd_code = clean_mermaid_code(f.read())
        except Exception as e:
            erd_code = f'error: {e}'
        with self.diagram_area:
            with ui.column().classes('w-full h-full items-center justify-center'):
                ui.label('ERD 類別關聯圖').classes('text-xl mt-4')
                if erd_code.startswith('error:'):
                    ui.label(erd_code).classes('text-red-700')
                else:
                    ui.mermaid(erd_code).classes('big-mermaid')
            ui.run_javascript('''
                setTimeout(function() {
                    document.querySelectorAll('.big-mermaid svg').forEach(function(svg) {
                        svg.removeAttribute('max-width');
                        svg.style.maxWidth = 'none';
                        svg.style.width = '100vw';
                    });
                }, 100);
            ''')

# Mermaid 樣式
ui.add_css('''
.big-mermaid, .big-mermaid .mermaid, .big-mermaid svg {
  min-width: 1500px;
  max-width: 1800px;
  min-height: 400px;
  height: auto;
  margin: auto;
  display: block;
}
''')

ui.add_head_html('''
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.4.0/dist/mermaid.min.js"></script>
''')


