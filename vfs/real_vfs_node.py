import os
import shutil
import datetime
from pathlib import Path, PurePosixPath
from typing import Optional, Union, Dict
from vfs.abstract_vfs_node import AbstractVFSNode

def virtual_to_real_path(root_path: Path, virtual_path: str) -> Path:
    virtual = PurePosixPath(virtual_path)
    if virtual.is_absolute():
        virtual = virtual.relative_to("/")
    return root_path.joinpath(*virtual.parts)

class RealVFSNode(AbstractVFSNode):
    def __init__(self, path: Union[str, Path], parent: Optional["RealVFSNode"] = None, root_path: Optional[Path] = None):
        if isinstance(path, Path):
            real_path = path.absolute()
            if parent is None:
                self.root_path = real_path
            else:
                if isinstance(parent, RealVFSNode):
                    self.root_path = parent.root_path
                else:
                    raise TypeError("Parent must be RealVFSNode if given.")
            super().__init__(real_path.name, parent)
            self.path = real_path
            self.virtual_path_str = "/" if parent is None else f"{parent.virtual_path_str}/{real_path.name}"
        elif isinstance(path, str):
            if parent and isinstance(parent, RealVFSNode):
                real_path = virtual_to_real_path(parent.path, path)
                self.root_path = parent.root_path
                self.virtual_path_str = f"{parent.virtual_path_str}/{path}".replace("//", "/")
            elif root_path:
                real_path = virtual_to_real_path(root_path, path)
                self.root_path = root_path
                self.virtual_path_str = f"/{path}".replace("//", "/")
            else:
                raise ValueError("When initializing with a virtual path (str), root_path or parent must be provided.")
            super().__init__(Path(path).name, parent)
            self.path = real_path
        else:
            raise TypeError(f"Invalid path type: {type(path)}. Must be str or Path.")

        self.is_symlink = os.path.islink(self.path)
        self.symlink_target = os.readlink(self.path) if self.is_symlink else None
        self.is_directory = self.path.is_dir() and not self.is_symlink
        if self.is_directory:
            self.children: Dict[str, AbstractVFSNode] = {}

    def _calculate_size(self) -> int:
        if self.is_directory:
            size = 0
            for child in self.children.values():
                size += child._calculate_size()
            return size
        if self.is_symlink and self.symlink_target:
            return len(self.symlink_target.encode('utf-8'))
        if self.path.exists():
            return self.path.stat().st_size
        return 0

    async def read(self, binary: bool = False) -> Union[str, bytes]:
        if self.is_directory:
            raise IsADirectoryError(f"'{self.name}' is a directory")
        actual_path = self.path
        if self.is_symlink and self.symlink_target:
            actual_path = (self.path.parent / self.symlink_target)
            if not actual_path.exists():
                raise FileNotFoundError(f"Symlink target '{self.symlink_target}' does not exist")
        mode = 'rb' if binary else 'r'
        kwargs = {} if binary else {"encoding": "utf-8"}
        with open(actual_path, mode, **kwargs) as f:
            return f.read()

    async def write(self, content: Union[str, bytes], binary: bool = False) -> None:
        if self.is_directory:
            raise IsADirectoryError(f"'{self.name}' is a directory")
        if self.is_symlink:
            raise ValueError(f"Cannot write to a symlink node: {self.name}")
        mode = 'wb' if binary else 'w'
        kwargs = {} if binary else {"encoding": "utf-8"}
        with open(self.path, mode, **kwargs) as f:
            f.write(content)
        self.modified_time = datetime.datetime.now()

    async def new_file(self, file_name: str) -> AbstractVFSNode:
        if not self.is_directory:
            raise Exception(f"Cannot create file '{file_name}' in a non-directory node '{self.name}'")
        new_node = RealVFSNode(file_name, parent=self)
        new_node.is_directory = False        
        if new_node.path.exists():
            if new_node.path.is_dir():
                raise FileExistsError(f"A directory already exists at: {new_node.path}")
        else:
            await new_node._create_physical_file()
        self.children[file_name] = new_node
        return new_node

    async def new_directory(self, dir_name: str) -> AbstractVFSNode:
        if not self.is_directory:
            raise Exception(f"Cannot create directory '{dir_name}' in a non-directory node '{self.name}'")
        new_node = RealVFSNode(dir_name, parent=self)
        new_node.is_directory = True
        if new_node.path.exists():
            if not new_node.path.is_dir():
                raise FileExistsError(f"Cannot create directory '{dir_name}', file already exists at: {new_node.path}")
            if dir_name not in self.children:
                await new_node.scan()
            self.children[dir_name] = new_node
            return new_node
        else:
            await new_node._create_physical_directory()
        self.children[dir_name] = new_node
        return new_node

    async def copy_child(self, node_to_copy: AbstractVFSNode) -> AbstractVFSNode:
        existing_names = set(self.children.keys())
        new_name = node_to_copy._generate_copy_name(existing_names)
        dest_path = self.path / new_name

        if isinstance(node_to_copy, RealVFSNode):
            if node_to_copy.is_symlink and node_to_copy.symlink_target:
                # symlink 跨平台
                try:
                    if os.name == "nt":
                        import subprocess
                        cmd = [
                            "cmd", "/c", "mklink",
                            "/D" if node_to_copy.is_directory else "",
                            str(dest_path), str(node_to_copy.symlink_target)
                        ]
                        subprocess.check_call([c for c in cmd if c])
                    else:
                        os.symlink(node_to_copy.symlink_target, dest_path)
                except Exception as e:
                    raise OSError(f"Symlink not supported or failed: {e}")
            elif node_to_copy.is_directory:
                shutil.copytree(node_to_copy.path, dest_path)
            else:
                shutil.copy2(node_to_copy.path, dest_path)

        copied_node = RealVFSNode(dest_path, parent=self)
        if copied_node.is_directory:
            await copied_node.scan()
        self.children[new_name] = copied_node
        return copied_node

    async def scan(self) -> None:
        if not self.path.exists():
            self.children.clear()
            return
        self.children.clear()
        for entry in self.path.iterdir():
            if entry.name in (".", ".."):
                continue
            try:
                child_node = RealVFSNode(entry, parent=self)
                if child_node.is_directory:
                    await child_node.scan()
                self.children[child_node.name] = child_node
            except Exception as e:
                continue

    async def _delete_physical_file(self, file_name: str) -> None:
        (self.path / file_name).unlink(missing_ok=True)

    async def _delete_physical_directory(self, dir_name: str) -> None:
        shutil.rmtree(self.path / dir_name, ignore_errors=True)

    async def _delete_physical_node(self, node: AbstractVFSNode) -> None:
        target_path = self.path / node.name
        if node.is_symlink or not node.is_directory:
            target_path.unlink(missing_ok=True)
        else:
            shutil.rmtree(target_path, ignore_errors=True)

    async def _physical_rename(self, new_name: str) -> None:
        new_path = self.path.parent / new_name
        self.path.rename(new_path)
        self.path = new_path
        self.name = new_name

    async def _create_physical_file(self) -> None:
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            if self.path.is_dir():
                raise FileExistsError(f"A directory already exists at: {self.path}")
            raise FileExistsError(f"File already exists: {self.path}")
        self.path.touch(exist_ok=False)

    async def _create_physical_directory(self) -> None:
        try:
            self.path.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            if not self.path.is_dir():
                raise
