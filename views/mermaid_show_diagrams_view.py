from nicegui import ui,app
import os
from utilits.utis import clean_mermaid_code
from utilits.utis import clean_mermaid_code_for_pdf
import subprocess
import tempfile
from fastapi.responses import FileResponse
from PyPDF2 import PdfMerger
from PIL import Image
from controllers.user_account_controler import UserAccountControler


class MermaidDiagramView:
    def __init__(self, user_id, project_name, use_case_names):
        self.output_dir = os.path.join('.', '.home', str(user_id), project_name, 'MMD')
        self.image_dir = './images'
        self.pdf_dir = './pdfs'
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.pdf_dir, exist_ok=True)
        self.use_case_names = use_case_names
        self.selected = {'name': self.use_case_names[0] if self.use_case_names else None}
        self.diagram_area = ui.column()

    @classmethod
    async def create(cls):
        user_account = app.storage.user.get('current_user_account')
        project_name = app.storage.user.get('selected_project', {}).get('name')
        select_user_account = await UserAccountControler.select_user_account(account=user_account)
        user_id = select_user_account.id if select_user_account else None
        output_dir = os.path.join('.', '.home', str(user_id), project_name, 'MMD')
        use_case_names = [
            f.replace('_sequence.mmd', '') for f in os.listdir(output_dir)
            if f.endswith('_sequence.mmd')
        ]
        return cls(user_id, project_name, use_case_names)

    def png_to_pdf(self, png_path, pdf_path):
        img = Image.open(png_path)
        # 以圖片原始尺寸產生 PDF
        img.save(pdf_path, "PDF", resolution=300.0)

    def mmdc_to_png(self, input_path: str, output_path: str, width=3000, height=2000):
        subprocess.run([
            'mmdc',
            '-i', input_path,
            '-o', output_path,
            '-t', 'default',
            '-b', 'white',
            '-w', str(width),
            '-H', str(height)
        ], check=True)

    def convert_to_pdf(self, use_case_name: str) -> str:
        sequence_path = os.path.join(self.output_dir, f'{use_case_name}_sequence.mmd')
        class_path = os.path.join(self.output_dir, f'{use_case_name}_class.mmd')

        with open(sequence_path, encoding='utf-8') as f:
            seq_code = clean_mermaid_code_for_pdf(f.read())
        with open(class_path, encoding='utf-8') as f:
            cls_code = clean_mermaid_code_for_pdf(f.read())

        with tempfile.TemporaryDirectory() as tmpdir:
            seq_tmp = os.path.join(tmpdir, 'sequence.mmd')
            cls_tmp = os.path.join(tmpdir, 'class.mmd')
            with open(seq_tmp, 'w', encoding='utf-8') as f:
                f.write(seq_code)
            with open(cls_tmp, 'w', encoding='utf-8') as f:
                f.write(cls_code)

            # 產生 PNG
            sequence_png = os.path.join(self.image_dir, f'{use_case_name}_sequence.png')
            class_png = os.path.join(self.image_dir, f'{use_case_name}_class.png')
            self.mmdc_to_png(seq_tmp, sequence_png)
            self.mmdc_to_png(cls_tmp, class_png)

            sequence_pdf = os.path.join(tmpdir, 'sequence.pdf')
            class_pdf = os.path.join(tmpdir, 'class.pdf')
            self.png_to_pdf(sequence_png,sequence_pdf)
            self.png_to_pdf(class_png, class_pdf)

            # 合併 PDF
            pdf_path = os.path.join(self.pdf_dir, f'{use_case_name}.pdf')
            merger = PdfMerger()
            merger.append(sequence_pdf)
            merger.append(class_pdf)
            merger.write(pdf_path)
            merger.close()

        return pdf_path

    @ui.page('/download-pdf')
    def download_pdf(self):
        name = self.selected['name']
        try:
            pdf_path = self.convert_to_pdf(name)
            return FileResponse(path=pdf_path, filename=f'{name}.pdf', media_type='application/pdf')
        except Exception as e:
            return f"Error generating PDF: {e}"

    def show_diagrams(self, name=None):
        if name is None:
            name = self.selected['name']
        self.selected['name'] = name
        self.diagram_area.clear()

        sequence_path = os.path.join(self.output_dir, f'{name}_sequence.mmd')
        class_path = os.path.join(self.output_dir, f'{name}_class.mmd')

        try:
            with open(sequence_path, encoding='utf-8') as f:
                sequence_code = clean_mermaid_code(f.read())
        except Exception as e:
            sequence_code = f'error: {e}'

        try:
            with open(class_path, encoding='utf-8') as f:
                class_code = clean_mermaid_code(f.read())
        except Exception as e:
            class_code = f'error: {e}'

        with self.diagram_area:
            with ui.column().classes('items-center'):
                with ui.row().classes('w-full'):
                    ui.select(
                        options=self.use_case_names,
                        value=self.selected['name'],
                        on_change=lambda e: self.show_diagrams(e.value)
                    ).props('outlined label="選擇使用案例"')

                    ui.button('下載 PDF', on_click=lambda: ui.download(f'/download-pdf'))

                ui.label('循序圖').classes('text-xl mt-4')
                if sequence_code.startswith('error:'):
                    ui.label(sequence_code).classes('text-red-700')
                else:
                    ui.mermaid(sequence_code).classes('big-mermaid')

                ui.label('類別圖').classes('text-xl mt-4')
                if class_code.startswith('error:'):
                    ui.label(class_code).classes('text-red-700')
                else:
                    ui.mermaid(class_code).classes('big-mermaid')

            # Mermaid 圖表渲染後自動調整 SVG 樣式，確保最大化
            ui.run_javascript('''
            setTimeout(function() {
                document.querySelectorAll('.big-mermaid svg').forEach(function(svg) {
                    svg.removeAttribute('max-width');
                    svg.style.maxWidth = 'none';
                    svg.style.width = '100vw';
                });
            }, 100);
            ''')


## 使用範例與 Mermaid 樣式、ui.run() 移除，統一由 main2.py 控制