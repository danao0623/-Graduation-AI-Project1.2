import os
import json
import tempfile

from abc import ABC, abstractmethod
from pathlib import Path
from PIL import Image
from nicegui import ui, app

from vfs.abstract_vfs import AbstractVFS

class AbstractFileHandler(ABC):
    def __init__(self, vfs: AbstractVFS):
        self.vfs: AbstractVFS = vfs
        self.path: str = None
        self.content = None      

    @abstractmethod
    async def open_file(self, path: str) -> None:
        pass

    async def save_file(self) -> None:
        if self.path and self.content:
            self.vfs.write(self.path, self.content)

    @abstractmethod
    async def save_as_a_new_file(self) -> None:
        pass

    @abstractmethod
    def _display(self) -> None:
        pass

    def _get_unique_file_name(self) -> str:
        base =Path(self.path).name
        existing_names = [n.name for n in self.vfs.ls()]
        count = 1
        name = base
        while name in existing_names:
            name = f"{Path(base).stem}_new{count}{Path(base).suffix}"
            count += 1
        return name


class ContentFileHandler(AbstractFileHandler):
    async def open_file(self, path: str) -> None:
        self.path = path
        self.content = await self.vfs.read(self.path, binary=False)
        self._display()

    async def save_as_a_new_file(self) -> None:
        new_name = self._get_unique_file_name()
        self.vfs.touch(new_name)
        self.vfs.write(new_name, self.content)

    def _display(self):
        print(f"Current file: {self.path}")


class SourceFileHandler(AbstractFileHandler):
    async def open_file(self, path: str) -> None:
        self.path = path
        content = await self.vfs.read(self.path, binary=True)
        temp_dir = tempfile.gettempdir()
        filename = Path(self.path).name or ''
        full_path = os.path.join(temp_dir, filename)
        with open(full_path, "wb") as f:
            f.write(content)
        self.current_file = full_path
        self.content = None
        self._display()

    async def save_as_a_new_file(self) -> None:
        new_name = self._get_unique_file_name()
        with open(self.current_file, 'rb') as f:
            binary_data = f.read()
            self.vfs.touch(new_name)
            self.vfs.write(new_name, binary_data, binary=True)

    def _display(self) -> None:
        print(f"Current binary file: {self.current_file}")


# Concrete Handler Classes
class MarkdownViewer(ContentFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-2 justify-center content-center'):
            ui.markdown(self.content)

class ReStructuredTextViewer(ContentFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-0 justify-center content-center'):
            ui.restructured_text(self.content)

class MermaidDiagramViewer(ContentFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-0 justify-center content-center'):
            ui.mermaid(self.content)    

class HTMLViewer(ContentFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-0 justify-center content-center'):
            ui.html(self.content)       

class ImageViewer(SourceFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        if self.current_file.is_file():
            img = Image.open(self.current_file)
            width, height = img.size
            with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-0 justify-center content-center'):
                #ui.image(str(path)).classes(f"w-[{width}px] h-{height}px")
                ui.image(str(self.current_file)).classes(f"w-96")      

class AudioPlayer(SourceFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-0 justify-center content-center'):        
            ui.audio(self.current_file)  

class VideoViewer(SourceFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-0 justify-center content-center'):
            ui.video(self.current_file)

class PDFViewer(SourceFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-0 justify-center content-center'):
            path = app.add_static_file(local_file=self.current_file)
            ui.html(f'<object data="{path}" type="application/pdf" style="width: calc(100vw - 620px); height: calc(100vh - 120px)"></object>')


class JsonEditor(ContentFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)
        self.editor = None

    async def save_file(self) -> None:
        if self.editor:
            content = await self.editor.run_editor_method('get')
            if 'text' in content:
                self.content = content['text']
            elif 'json' in content:
                self.content = json.dumps(content['json'], indent=2)

        if self.node and self.content:
            self.vfs.write(self.node.virtual_path(), self.content)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-0'):
            self.editor = ui.json_editor({'content': {'text': self.content}})

class GenericFileHandler:
    def __init__(self, vfs: AbstractVFS = None):
        self.vfs: AbstractVFS = vfs
        self.file_handler: AbstractFileHandler = None
        self.container = ui.column()
        
        self.handler_mapping = {
            '.md': MarkdownViewer,
            '.rst': ReStructuredTextViewer,
            '.mmd': MermaidDiagramViewer,
            '.html': HTMLViewer,
            '.svg': HTMLViewer,
            '.jpg': ImageViewer,
            '.jpeg': ImageViewer,
            '.png': ImageViewer,
            '.gif': ImageViewer,
            '.bmp': ImageViewer,
            '.mp3': AudioPlayer,
            '.wav': AudioPlayer,
            '.mp4': VideoViewer,
            '.avi': VideoViewer,
            '.mkv': VideoViewer,
            '.pdf': PDFViewer,
            '.json': JsonEditor,
            '.py': PythonFileViewer,
            '.java': JavaFileViewer,
            '.tsx': TypeScriptFileViewer,
            '.ts': TypeScriptFileViewer,
            '.txt': TextFileViewer,
            '.xml': XMLFileViewer
        }

    async def open_file(self, path: str) -> None:
        ext = Path(path).suffix.lower()
        handler_class = self.handler_mapping.get(ext)

        if not handler_class:
            ui.notify(f"No viewer class found for file extension: {ext}")
            return

        self.file_handler = handler_class(self.vfs)
        if self.container:
            self.container.clear()
            with self.container:
                await self.file_handler.open_file(path)

    async def save_file(self) -> None:
        if self.file_handler:
            await self.file_handler.save_file()

    async def save_as_a_new_file(self) -> None:
        if self.file_handler:
            await self.file_handler.save_as_a_new_file()

class PythonFileViewer(ContentFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-2 justify-center content-center'):
            ui.code(self.content, language='python')

class JavaFileViewer(ContentFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-2 justify-center content-center'):
            ui.code(self.content, language='java')

class TypeScriptFileViewer(ContentFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-2 justify-center content-center'):
            ui.code(self.content, language='typescript')

class TextFileViewer(ContentFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-2 justify-center content-center'):
            ui.code(self.content, language='text')

class XMLFileViewer(ContentFileHandler):
    def __init__(self, vfs):
        super().__init__(vfs)

    def _display(self) -> None:
        with ui.grid(rows='auto').classes('w-full h-full m-0 gap-0 p-2 justify-center content-center'):
            ui.code(self.content, language='xml')
