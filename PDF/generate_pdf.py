#!/usr/bin/env python3
# read/md2pdf.py
import sys
from pathlib import Path
import markdown
from weasyprint import HTML

class GeneratePDF:

    @staticmethod
    def generate_pdf(md_dir=None, pdf_dir=None):
        # 1. 取得專案根目錄
        SCRIPT_DIR   = Path(__file__).resolve().parent    # .../project/read
        PROJECT_ROOT = SCRIPT_DIR.parent                  # .../project

        # 2. 定義 MD 來源與 PDF 輸出路徑
        MD_DIR  = Path(md_dir) if md_dir else PROJECT_ROOT / 'MD'
        PDF_DIR = Path(pdf_dir) if pdf_dir else PROJECT_ROOT / 'PDF'
        PDF_DIR.mkdir(exist_ok=True)

        # 3. 取得要轉的檔名列表
        #    - 如果有參數，就用參數指定
        #    - 否則，就把 MD_DIR 裡的所有 .md 全部轉一遍
        if len(sys.argv) > 1:
            files_to_convert = sys.argv[1:]
        else:
            files_to_convert = [p.name for p in MD_DIR.glob('*.md')]

        # 4. 開始逐一轉檔
        for fname in files_to_convert:
            md_file = MD_DIR / fname
            if not md_file.exists():
                print(f'⚠ 找不到：{md_file}')
                continue

            pdf_file = PDF_DIR / f'{md_file.stem}.pdf'
            md_text  = md_file.read_text(encoding='utf-8')

            # 5. Markdown → HTML
            html_body = markdown.markdown(
                md_text,
                extensions=['extra', 'codehilite', 'toc']
            )

            # 6. 包裝基本 HTML + CSS
            html = f"""<!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: "Noto Serif CJK TC", serif; margin:1cm; }}
        pre {{ background:#f5f5f5; padding:.5em; overflow:auto; }}
        h1,h2,h3 {{ border-bottom:1px solid #ddd; padding-bottom:.3em; }}
    </style>
    </head>
    <body>
    {html_body}
    </body>
    </html>"""

            # 7. 輸出 PDF
            HTML(string=html).write_pdf(str(pdf_file))
            print(f'→ 已輸出：{pdf_file.name}')

