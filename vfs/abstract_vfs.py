import json
import zipfile
import aiofiles

from io import BytesIO
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Union, Any
from pathlib import Path

class QuotaExceededError(Exception):
    pass

class AbstractVFS(ABC):
    def __init__(self, capacity: int = 1024 * 1024 * 1024) -> None:
        self.capacity = capacity
        self.used = 0
        self.root = None
        self.current_node = None

    def pwd(self) -> str:
        return self.current_node.virtual_path()
    
       
    def search(self, keyword: str) -> List[str]:
        result = []
        def recur(node):
            if keyword.lower() in node.name.lower():
                result.append(node.virtual_path())
            if node.is_directory:
                for c in node.children.values():
                    recur(c)
        recur(self.root)
        return result

    def quota_info(self) -> Dict[str, int]:
        return {"capacity": self.capacity, "used": self.used, "remaining": self.capacity - self.used}

    async def current(self) -> Any:
        return self.current_node

    async def parent(self) -> Any:
        return self.current_node.parent

    async def child(self, name: str) -> Any:
        child = self.current_node.children.get(name)
        if not child:
            raise FileNotFoundError(f"No child named '{name}'")
        return child 

    async def zip(self, names: List[str], zip_name: Optional[str] = None) -> None:
        if not names:
            raise ValueError("At least one name must be specified to zip.")

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for name in names:
                node = await self._resolve_path(name)
                await self._add_node_to_zip(zipf, node, "")

        buffer.seek(0)
        zip_file_name = zip_name or "archive.zip"
        parent, base_name = await self._resolve_parent_and_name(zip_file_name)
        if base_name in parent.children:
            raise FileExistsError(f"File '{base_name}' already exists.")
        zip_node = await parent.new_file(base_name)
        await zip_node.write(buffer.read(), binary=True)
        self.used = self._calculate_used()

    async def unzip(self, zip_names: List[str], extract_to: Optional[str] = None) -> None:
        if not zip_names:
            raise ValueError("At least one zip file must be specified to unzip.")

        for zip_name in zip_names:
            zip_node = await self._resolve_path(zip_name)
            if zip_node.is_directory:
                raise IsADirectoryError(f"'{zip_name}' is a directory.")

            data = await zip_node.read(binary=True)
            base_extract_name = extract_to or zip_node.name.rstrip(".zip")
            extract_parent, extract_dir_name = await self._resolve_parent_and_name(base_extract_name)
            if extract_dir_name in extract_parent.children:
                raise FileExistsError(f"Target '{extract_dir_name}' already exists.")

            target_root = await extract_parent.new_directory(extract_dir_name)
            with zipfile.ZipFile(BytesIO(data), 'r') as zipf:
                for file_path in zipf.namelist():
                    parts = file_path.strip("/").split("/")
                    current = target_root
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            if part in current.children:
                                raise FileExistsError(f"File '{part}' already exists in extracted path.")
                            file_node = await current.new_file(part)
                            await file_node.write(zipf.read(file_path), binary=True)
                        else:
                            if part not in current.children:
                                current = await current.new_directory(part)
                            else:
                                current = current.children[part]
        self.used = self._calculate_used()

    async def save_to_file(self, file_path: Union[str, Path]) -> None:
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            data = await self.export_to_dict()
            await f.write(json.dumps(data, indent=2))

    async def load_from_file(self, file_path: Union[str, Path]) -> None:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            await self.import_from_dict(json.loads(content), exclude_paths=[file_path])

    async def cd(self, path: str) -> None:
        node = await self._resolve_path(path, follow_symlinks=True)
        if node.is_symlink and node.symlink_target:
            node = await self._resolve_path(node.symlink_target, follow_symlinks=True)
        if not node.is_directory:
            raise NotADirectoryError(f"Cannot cd into a file: {node.name}")
        self.current_node = node

    async def ls(self, path: str = "", detail: bool = False, sort_by: str = "name",
           reverse: bool = False, filter_type: str = "all") -> List:
        
        node = await self._resolve_path(path) if path else self.current_node
        nodes = list(node.children.values()) if node.is_directory else []
        if filter_type == "file":
            nodes = [n for n in nodes if not n.is_directory]
        elif filter_type == "directory":
            nodes = [n for n in nodes if n.is_directory]

        sort_key = {
            "name": lambda n: n.name.lower(),
            "size": lambda n: n.size(),
            "created_time": lambda n: n.created_time,
            "modified_time": lambda n: n.modified_time
        }.get(sort_by, lambda n: n.name.lower())

        nodes.sort(key=sort_key, reverse=reverse)
        return nodes if detail else [n.name for n in nodes]

    async def rename(self, old_name: str, new_name: str) -> None:
        node = await self._resolve_path(old_name)
        parent = node.parent
        if new_name in parent.children:
            raise FileExistsError(f"Name '{new_name}' already exists")
        await node.rename(new_name)

    async def read(self, file_name: str, binary: bool = False) -> Union[str, bytes]:
        node = await self._resolve_path(file_name)
        return await node.read(binary)

    async def write(self, file_name: str, content: Union[str, bytes], binary: bool = False) -> None:
        node = await self._resolve_path(file_name)
        old_size = node.size()
        estimated_new_size = len(content) if isinstance(content, bytes) else len(content.encode('utf-8'))
        if self.used - old_size + estimated_new_size > self.capacity:
            raise QuotaExceededError("Storage quota exceeded")
        await node.write(content, binary)
        self.used = self._calculate_used()

    async def copy(self, source_name: str, target_name: str) -> None:
        src = await self._resolve_path(source_name)
        dst_parent, dst_name = await self._resolve_parent_and_name(target_name)
        copied = await dst_parent.copy_child(src)
        await copied.rename(dst_name)
        self.used = self._calculate_used()

    async def move(self, source_name: str, target_name: str) -> None:
        await self.copy(source_name, target_name)
        await self.rm(source_name)
        self.used = self._calculate_used()

    async def _add_node_to_zip(self, zipf, node, arc_path: str):
        arc_name = f"{arc_path}/{node.name}" if arc_path else node.name
        if node.is_directory:
            for child in node.children.values():
                await self._add_node_to_zip(zipf, child, arc_name)
        else:
            content = await node.read(binary=True)
            zipf.writestr(arc_name, content)

    @abstractmethod
    def _calculate_used(self) -> int: pass

    @abstractmethod
    async def initialize(self) -> None: pass

    @abstractmethod
    async def refresh(self) -> None: pass

    @abstractmethod
    async def mkdir(self, dir_name: str) -> Any: pass

    @abstractmethod
    async def touch(self, file_name: str) -> Any: pass

    @abstractmethod
    async def rm(self, name: str) -> None: pass

    @abstractmethod
    async def ln_s(self, target_path: str, link_name: str) -> None: pass

    @abstractmethod
    async def export_to_dict(self) -> Dict[str, Any]: pass

    @abstractmethod
    async def import_from_dict(self, data: Dict[str, Any], exclude_paths: list = None) -> None: pass

    @abstractmethod
    async def _resolve_path(self, path: str, follow_symlinks: bool = True) -> Any: pass

    @abstractmethod
    async def _resolve_parent_and_name(self, path: str): pass

