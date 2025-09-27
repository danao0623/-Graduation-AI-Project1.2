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





# 目錄設定
image_dir = './images'
pdf_dir = './pdfs'
os.makedirs(image_dir, exist_ok=True)
os.makedirs(pdf_dir, exist_ok=True)

# 如有需要可設定 Puppeteer Chrome 路徑（不一定必要）
os.environ["PUPPETEER_EXECUTABLE_PATH"] = os.path.expanduser(
    "/home/thegary_0517/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome"
)

diagram_area = ui.column()

def png_to_pdf(png_path, pdf_path):
    img = Image.open(png_path)
    # 以圖片原始尺寸產生 PDF
    img.save(pdf_path, "PDF", resolution=300.0)

def mmdc_to_png(input_path: str, output_path: str, width=3000, height=2000):
    subprocess.run([
        'mmdc',
        '-i', input_path,
        '-o', output_path,
        '-t', 'default',
        '-b', 'white',
        '-w', str(width),
        '-H', str(height)
    ], check=True)

def convert_to_pdf(use_case_name: str, output_dir: str) -> str:
    sequence_path = os.path.join(output_dir, f'{use_case_name}_sequence.mmd')
    class_path = os.path.join(output_dir, f'{use_case_name}_class.mmd')

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
        sequence_png = os.path.join(image_dir, f'{use_case_name}_sequence.png')
        class_png = os.path.join(image_dir, f'{use_case_name}_class.png')
        mmdc_to_png(seq_tmp, sequence_png)
        mmdc_to_png(cls_tmp, class_png)

        sequence_pdf = os.path.join(tmpdir, 'sequence.pdf')
        class_pdf = os.path.join(tmpdir, 'class.pdf')
        png_to_pdf(sequence_png,sequence_pdf)
        png_to_pdf(class_png, class_pdf)

        # 合併 PDF
        pdf_path = os.path.join(pdf_dir, f'{use_case_name}.pdf')
        merger = PdfMerger()
        merger.append(sequence_pdf)
        merger.append(class_pdf)
        merger.write(pdf_path)
        merger.close()

    return pdf_path



@ui.page('/download-pdf')
async def download_pdf():
    # 取得目前使用者與專案
    user_account = app.storage.user.get('current_user_account')
    project_name = app.storage.user.get('selected_project', {}).get('name')
    select_user_account = await UserAccountControler.select_user_account(account=user_account)
    user_id = select_user_account.id if select_user_account else None
    output_dir = os.path.join('.', '.home', str(user_id), project_name, 'MMD')
    mermaid_files = [
        f for f in os.listdir(output_dir)
        if f.endswith('_sequence.mmd')
    ]
    use_case_names = [f.replace('_sequence.mmd', '') for f in mermaid_files]
    selected = {'name': use_case_names[0] if use_case_names else None}
    name = selected['name']
    try:
        pdf_path = convert_to_pdf(name, output_dir)
        return FileResponse(path=pdf_path, filename=f'{name}.pdf', media_type='application/pdf')
    except Exception as e:
        return f"Error generating PDF: {e}"




@ui.page('/mermaid')
async def display_mermaid_page():
    # 取得目前使用者與專案
    user_account = app.storage.user.get('current_user_account')
    project_name = app.storage.user.get('selected_project', {}).get('name')
    select_user_account = await UserAccountControler.select_user_account(account=user_account)
    user_id = select_user_account.id if select_user_account else None
    output_dir = os.path.join('.', '.home', str(user_id), project_name, 'MMD')
    mermaid_files = [
        f for f in os.listdir(output_dir)
        if f.endswith('_sequence.mmd')
    ]
    use_case_names = [f.replace('_sequence.mmd', '') for f in mermaid_files]
    selected = {'name': use_case_names[0] if use_case_names else None}
    # 顯示 ERD 圖
    erd_path = os.path.join(output_dir, f'{project_name}_erd.mmd')
    print(f"ERD 檔案路徑: {erd_path}")
    if os.path.exists(erd_path):
        try:
            with open(erd_path, encoding='utf-8') as f:
                erd_code = clean_mermaid_code(f.read())
            with ui.column().classes('items-center'):
                ui.label('ERD 圖').classes('text-xl mt-4')
                ui.mermaid(erd_code).classes('big-mermaid')
        except Exception as e:
            ui.label(f'無法載入 ERD 圖: {e}').classes('text-red-700')

    # 顯示循序/類別圖
    if selected['name']:
        show_diagrams(selected['name'], use_case_names, selected, output_dir)
    else:
        ui.label("無可用的使用案例")




def show_diagrams(name: str, use_case_names, selected, output_dir):

    selected['name'] = name
    diagram_area.clear()

    sequence_path = os.path.join(output_dir, f'{name}_sequence.mmd')
    class_path = os.path.join(output_dir, f'{name}_class.mmd')

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

    with diagram_area:
        with ui.column().classes('items-center'):
            with ui.row().classes('w-full'):
                ui.select(
                    options=use_case_names,
                    value=selected['name'],
                    on_change=lambda e: show_diagrams(e.value, use_case_names, selected, output_dir)
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

            # ERD 圖顯示已移至 display_mermaid_page，這裡不重複顯示


# Mermaid 樣式
ui.add_css('''
.big-mermaid, .big-mermaid .mermaid, .big-mermaid svg {
  width: 100% !important;
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

