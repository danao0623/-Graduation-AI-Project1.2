import os
import shutil
import asyncio
from pathlib import Path, PurePosixPath
from typing import Dict, Any

from vfs.real_vfs_node import RealVFSNode, virtual_to_real_path
from vfs.abstract_vfs import AbstractVFS, QuotaExceededError

class RealVirtualFileSystem(AbstractVFS):
    def __init__(self, root_path: Path, capacity: int = 1024 * 1024 * 1024) -> None:
        super().__init__(capacity)
        self.root = RealVFSNode(root_path)
        self.current_node = self.root

    async def initialize(self) -> None:
        await self.refresh()

    async def refresh(self) -> None:
        await self.root.scan()
        self.used = self._calculate_used()

    async def mkdir(self, dir_name: str) -> RealVFSNode:
        parent, name = await self._resolve_parent_and_name(dir_name)
        if name in parent.children:
            raise FileExistsError(f"Directory '{name}' already exists in '{parent.name}'")
        node = await parent.new_directory(name)
        self.used = self._calculate_used()
        return node

    async def touch(self, file_name: str) -> RealVFSNode:
        if self.used >= self.capacity:
            raise QuotaExceededError("Storage quota exceeded")
        parent, name = await self._resolve_parent_and_name(file_name)
        if name in parent.children:
            raise FileExistsError(f"File '{name}' already exists in '{parent.name}'")        
        node = await parent.new_file(name)
        size = node._calculate_size()
        self.used += size
        return node

    async def rm(self, name: str) -> None:
        node = await self._resolve_path(name)
        size = node._calculate_size()
        await node.parent.remove_child(node.name)
        self.used -= size

    async def ln_s(self, target_path: str, link_name: str) -> None:
        parent, name = await self._resolve_parent_and_name(link_name)
        if name in parent.children:
            raise FileExistsError(f"Link name '{name}' already exists")

        link_path = parent.path / name
        target_real = virtual_to_real_path(self.root.path, target_path)
        try:
            if os.name == "nt":
                import subprocess
                is_dir = target_real.is_dir()
                cmd = [
                    "cmd", "/c", "mklink",
                    "/D" if is_dir else "",
                    str(link_path), str(target_real)
                ]
                subprocess.check_call([c for c in cmd if c])
            else:
                os.symlink(str(target_real), str(link_path))
        except Exception as e:
            raise OSError(f"Symlink creation failed: {e}")
        link_node = RealVFSNode(link_path, parent=parent)
        link_node.is_symlink = True
        link_node.symlink_target = str(target_real)
        parent.children[name] = link_node
        self.used = self._calculate_used()

    async def export_to_dict(self) -> Dict[str, Any]:
        return self.root.to_dict()

    async def import_from_dict(self, data: Dict[str, Any], exclude_paths: list = None) -> None:
        exclude_paths = [Path(p).resolve() for p in (exclude_paths or [])]
        for child in list(self.root.path.iterdir()):
            if child.resolve() in exclude_paths:
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

        self.root = RealVFSNode(self.root.path)
        self.current_node = self.root
        self.used = 0

        def build(data: Dict[str, Any], parent: RealVFSNode):
            path = parent.path / data['name']
            if data['is_directory']:
                path.mkdir(exist_ok=True)
            else:
                path.touch(exist_ok=True)
            node = RealVFSNode(path, parent)
            if data.get('children'):
                for child in data['children']:
                    build(child, node)

        for child in data.get('children') or []:
            build(child, self.root)

        await self.root.scan()

    def _calculate_used(self) -> int:
        def recur(node: RealVFSNode) -> int:
            if node.is_directory:
                return sum([recur(c) for c in node.children.values()])
            else:
                return node._calculate_size()
        return recur(self.root)

    async def _resolve_virtual_path(self, path: str) -> PurePosixPath:
        p = PurePosixPath(path)
        if p.is_absolute():
            return p
        base = PurePosixPath(self.pwd())
        combined = base.joinpath(p)
        parts = []
        for part in combined.parts:
            if part == ".":
                continue
            elif part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return PurePosixPath(*parts)

    async def _resolve_path(self, path: str, follow_symlinks: bool = True) -> RealVFSNode:
        virtual_path = await self._resolve_virtual_path(path)
        parts = virtual_path.parts[1:] 
        node = self.root
        for part in parts:
            if part in ("", "."):
                continue
            if part == "..":
                node = node.parent if node.parent else node
            else:
                if not node.children:
                    await node.scan()
                child = node.children.get(part)
                if not child:
                    raise FileNotFoundError(f"Path not found: {virtual_path}")
                if follow_symlinks and child.is_symlink and child.symlink_target:
                    target_path = (child.path.parent / child.symlink_target).resolve()
                    return await self._resolve_path(str(target_path))
                node = child
        return node

    async def _resolve_parent_and_name(self, path: str):
        virtual_path = await self._resolve_virtual_path(path)
        parent_path = str(virtual_path.parent)
        parent_node = await self._resolve_path(parent_path) if parent_path != '/' else self.root
        return parent_node, virtual_path.name        