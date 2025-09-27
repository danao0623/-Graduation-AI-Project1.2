import os
import io
import zipfile
import tempfile
import asyncio

from pathlib import Path
from typing import List
from nicegui import ui, events

from core.environment import Environment
from views.file_handlers import GenericFileHandler
from views.togglable_button import TogglableButton
from vfs.real_vfs import RealVirtualFileSystem

def join_virtual_path(*parts):
    return '/' + '/'.join([str(p).strip('/') for p in parts if p and p != '/']).replace('//', '/')

class FileManager():
    def __init__(self, user: str):
        self.home_folder = Path(Environment.home_folder) / user
        print(f"[FileManager] home_folder: {self.home_folder}")
        self.home_folder.mkdir(parents=True, exist_ok=True)
        self.vfs: RealVirtualFileSystem = RealVirtualFileSystem(root_path=self.home_folder)
        self.clipboard_items: List[str] = []
        self.mount_vfs: bool = True
        self.is_cut: bool = False
        self.current_directory = '/'                
        self.file_handler = None

    def set_file_handeler(self, file_handler: GenericFileHandler) -> None:
        file_handler.vfs = self.vfs
        self.file_handler = file_handler

    async def display(self):
        await self.vfs.refresh()

        with ui.grid(rows='auto auto auto 1fr').classes('w-full h-full m-0 p-0 gap-0'):
            with ui.row().classes('w-full m-0 p-0 gap-0'): 
                self.path_input = ui.input(
                    label='Current Path', 
                    value=self.vfs.pwd()
                ).on('change', self.on_path_input_change).props('dense options-dense').classes('w-full')

            with ui.row().classes('m-0 p-0 gap-0.5'):
                ui.button(icon='o_note_add', on_click=self.add_file).props('outline').style('padding: 4px 4px; font-size: 14px;')
                ui.button(icon='o_create_new_folder', on_click=self.add_folder).props('outline').style('padding: 4px 4px; font-size: 14px;')
                ui.button(icon='drive_file_rename_outline', on_click=self.rename).props('outline').style('padding: 4px 4px; font-size: 14px;')
                ui.button(icon='content_cut', on_click=self.cut_selected).props('outline').style('padding: 4px 4px; font-size: 14px;')
                ui.button(icon='content_copy', on_click=self.copy_selected).props('outline').style('padding: 4px 4px; font-size: 14px;')
                ui.button(icon='content_paste', on_click=self.paste_items).props('outline').style('padding: 4px 4px; font-size: 14px;')
                ui.button(icon='o_delete', on_click=self.delete_selected).props('outline').style('padding: 4px 4px; font-size: 14px;')
                ui.button(icon='select_all', on_click=self.select_all).props('outline').style('padding: 4px 4px; font-size: 14px;')
                ui.button(icon='refresh', on_click=self._refresh).props('outline').style('padding: 4px 4px; font-size: 14px;')
                ui.button(icon='download', on_click=self.download_selected).props('outline').style('padding: 4px 4px; font-size: 14px;')
                bt_upload = TogglableButton(value=False, true_icon='file_upload', false_icon='o_file_upload').props('outline').style('padding: 4px 4px; font-size: 14px;')

            with ui.column().classes('m-0 py-0.5 gap-0'):
                ui.upload(
                    on_upload=self.handle_upload,
                    on_rejected=self.handle_reject,
                    multiple=True,
                ).classes('w-full').bind_visibility_from(bt_upload, 'value')

            with ui.column().classes('m-0 p-0 gap-0'):
                self.file_list = ui.aggrid({
                    'defaultColDef': {'cellStyle': {'padding': '0px 5px 0px 5px'}},
                    'columnDefs': [
                        {'field': 'type', 'headerName': 'Type', 'width': 60, 'checkboxSelection': True},
                        {'field': 'name', 'headerName': 'Name', 'flex': 1, 'editable': True},
                        {'field': 'size', 'headerName': 'Size', 'width': 100},
                        {'field': 'date', 'headerName': 'Date', 'width': 130},
                        {'field': 'path', 'hide': True},
                    ],
                    'rowSelection': 'multiple',
                    'suppressClickEdit': True,
                }, auto_size_columns=False).classes('w-full h-full')
                self.file_list.on('cellDoubleClicked', self.open_item)
                self.file_list.on('cellValueChanged', self.on_cell_value_changed)

        await self._refresh()

    async def refresh(self):
        await self.vfs.auto_mount(self.user)
        await self.vfs.refresh()
        await self._refresh()        

    async def _refresh(self):
        self.current_directory = self.vfs.pwd()
        self.path_input.value = self.current_directory
        
        entries = await self.vfs.ls(detail=True)
        file_data = []
        
        if self.current_directory != '/': 
            parent_node = await self.vfs.parent()
            parent_size = f"{parent_node.size() // 1024} KB"
            path = parent_node.virtual_path() if hasattr(parent_node, "virtual_path") else '/'
            file_data.append({
                'type': '📁',
                'name': '..',
                'size': parent_size,
                'date': '',
                'path': path
            })   
        
        for node in entries:
            size_display = f"{node.size() // 1024} KB"
            path = node.virtual_path() if hasattr(node, "virtual_path") else join_virtual_path(self.current_directory, node.name)
            file_data.append({
                'type': '📁' if node.is_directory else '📄',
                'name': node.name,
                'size': size_display,
                'date': node.modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                'path': path,
            })                

        self.file_list.options['rowData'] = file_data
        self.file_list.update()       
  
    async def _get_unique_name(self, base: str) -> str:
        count = 0
        name = base
        async def exists(name):
            entries = await self.vfs.ls(detail=True)
            return name in [node.name for node in entries]

        while await exists(name):
            count += 1
            stem = Path(base).stem
            suffix = Path(base).suffix
            name = f"{stem}_{count}{suffix}"
        return name

    async def on_path_input_change(self, e: events.ValueChangeEventArguments):
        try:
            await self.vfs.cd(e.args)
            await self._refresh()
        except Exception as ex:
            ui.notify(f"Invalid path: {e.args} ({ex})", type='negative')
            self.path_input.value = self.vfs.pwd()

    async def add_file(self):
        name = await self._get_unique_name("new_file.txt")
        try:
            await self.vfs.touch(name)
            await self._refresh()
        except Exception as ex:
            ui.notify(f"Cannot add file: {name} ({ex})", type='negative')

    async def add_folder(self):
        name = await self._get_unique_name("new_folder")
        try:
            await self.vfs.mkdir(name)
            await self._refresh()
        except Exception as ex:
            ui.notify(f"Cannot add folder: {name} ({ex})", type='negative')

    async def rename(self):
        selected = await self.file_list.get_selected_rows()
        if not selected:
            ui.notify("No file is selected to be rename", type='negative')
            return
        item = selected[0]
        await self.enter_edit_mode(item['name'])

    async def enter_edit_mode(self, name: str):
        row_data = self.file_list.options['rowData']
        for index, item in enumerate(row_data):
            if item['name'] == name:
                self.file_list.run_grid_method('startEditingCell', {
                    'rowIndex': index,
                    'colKey': 'name'
                })
                break

    async def on_cell_value_changed(self, event: events.GenericEventArguments):
        old_name = event.args['oldValue']
        new_name = event.args['newValue']
        if old_name and new_name and old_name != new_name:
            try:
                await self.vfs.rename(old_name, new_name)
                await self._refresh()
            except Exception as e:
                ui.notify(f"Rename error: {e}", type='negative')
                await self._refresh()

    async def open_item(self, event: events.GenericEventArguments):
        name = event.args['data']['name']

        if name == '..':
            await self.vfs.cd('..')
        else:
            node = await self.vfs.child(name)
            if node.is_directory:
                try:
                    await self.vfs.cd(name)
                except Exception as ex:
                    ui.notify(f"Cannot change directory: {name} ({ex})", type='negative')
            else:
                if self.file_handler:
                    try:
                        path = join_virtual_path(self.current_directory, name)
                        await self.file_handler.open_file(path)
                    except Exception as ex:
                        ui.notify(f"Error opening '{name}': {str(ex)}", type='negative')        
                else:
                    ui.notify("File handler is not initialized.", type='negative')

        await self._refresh()

    async def keep_selected(self):
        selected = await self.file_list.get_selected_rows()
        self.clipboard_items.clear()
        for item in selected:
            if item['name'] == '..':
                continue
            path = join_virtual_path(self.current_directory, item['name'])
            self.clipboard_items.append(path)

    async def cut_selected(self):
        await self.keep_selected()
        self.is_cut = True

    async def copy_selected(self):
        await self.keep_selected()
        self.is_cut = False

    async def paste_items(self):
        if not self.clipboard_items:
            ui.notify("Clipboard is empty.", type='negative')
            return

        for original_path in self.clipboard_items:
            name = original_path.strip('/').split('/')[-1]
            unique_name = await self._get_unique_name(name)
            target_path = join_virtual_path(self.current_directory, unique_name)
            if self.is_cut:
                try:
                    await self.vfs.move(original_path, target_path)
                except Exception as ex:
                    ui.notify(f"Cannot move: {name} ({ex})", type='negative')
                    continue
            else:
                try:
                    await self.vfs.copy(original_path, target_path)
                except Exception as ex:
                    ui.notify(f"Cannot copy: {name} ({ex})", type='negative')                
                    continue
        if self.is_cut:
            self.clipboard_items.clear()

        await self._refresh()    
        

    async def delete_selected(self):
        selected = await self.file_list.get_selected_rows()
        for item in selected:
            if item['name'] == '..':
                continue
            try:
                await self.vfs.rm(item['name'])
            except ValueError as e:             
                ui.notify(f"Error removing {item['name']} : {str(e)}", type='negative')
            
        await self._refresh()

    async def handle_upload(self, e: events.UploadEventArguments):
        file = e.content
        raw_bytes = file.read()
        file.seek(0)
        file_name = await self._get_unique_name(e.name)

        try:
            await self.vfs.touch(file_name)
            try:
                content = raw_bytes.decode('utf-8')
                await self.vfs.write(file_name, content)
                await self._refresh()
            except UnicodeDecodeError:        
                try:
                    await self.vfs.write(file_name, raw_bytes, binary=True) 
                    await self._refresh()  
                except Exception as ex:
                    await self._refresh() 
                    ui.notify(f"Cannot write content to file: {file_name} ({ex})", type='negative')        
        except Exception as ex:
             await self._refresh()
             ui.notify(f"Cannot add file: {file_name} ({ex})", type='negative')

    def handle_reject(self, e: events.UploadEventArguments):
        ui.notify(f"Upload rejected: {e.name}", type='negative')

    async def download_selected(self):
        selected = await self.file_list.get_selected_rows()
        if not selected:
            ui.notify("No files selected to download", type='negative')
            return

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for item in selected:
                node = await self.vfs.child(item['name'])
                await self.vfs._add_node_to_zip(zip_file, node, "")

        buffer.seek(0)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
            tmp.write(buffer.read())
            tmp_path = tmp.name
        ui.download.file(tmp_path, filename='download.zip')

        async def cleanup(path):
            await asyncio.sleep(180)
            try:
                os.remove(path)
            except Exception as e:
                ui.notify(f"[Warning] Failed to delete {path}: {e}", type='negative')
                
        asyncio.create_task(cleanup(tmp_path))

    async def select_all(self):
        row_data = self.file_list.options.get('rowData', [])
        for index, item in enumerate(row_data):
            if item.get('name') != '..':
                await self.file_list.run_row_method(index, 'setSelected', True)
