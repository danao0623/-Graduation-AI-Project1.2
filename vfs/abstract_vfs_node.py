from __future__ import annotations

import datetime
from typing import Optional, Union, Dict, Any, Set
from abc import ABC, abstractmethod

class AbstractVFSNode(ABC):
    def __init__(self, name: str, parent: Optional[AbstractVFSNode] = None) -> None:
        self.name = name
        self.parent = parent
        self.is_directory = False
        self.is_symlink = False
        self.symlink_target: Optional[str] = None
        self.children: Dict[str, AbstractVFSNode] = {}
        self.created_time = datetime.datetime.now()
        self.modified_time = datetime.datetime.now()
        if self.parent:
            self.parent.attach_child(self)

    def size(self) -> int:
        return self._calculate_size()

    def child(self, name: str) -> Optional[AbstractVFSNode]:
        return self.children.get(name)

    def attach_child(self, node: AbstractVFSNode) -> None:
        if not self.is_directory:
            raise Exception(f"Cannot attach child to a file node: {self.name}")
        if node.name in self.children:
            raise FileExistsError(f"Child with name '{node.name}' already exists under '{self.name}'")
        node.parent = self
        self.children[node.name] = node
        self.modified_time = datetime.datetime.now()

    def detach_child(self, name: str) -> None:
        if name in self.children:
            del self.children[name]
            self.modified_time = datetime.datetime.now()

    def virtual_path(self) -> str:
        parts = []
        node = self
        while node.parent:
            parts.append(node.name)
            node = node.parent
        return '/' + '/'.join(reversed(parts))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "is_directory": self.is_directory,
            "is_symlink": self.is_symlink,
            "symlink_target": self.symlink_target,
            "created_time": self.created_time.isoformat(),
            "modified_time": self.modified_time.isoformat(),
            "children": [child.to_dict() for child in self.children.values()] if self.is_directory else None
        }

    def is_mount_point(self) -> bool:
        return False

    def _generate_copy_name(self, existing_names: Set[str]) -> str:
        name = self.name
        if name not in existing_names:
            return name
        parts = name.rsplit('.', 1)
        if len(parts) == 2:
            stem, suffix = parts
            suffix = f".{suffix}"
        else:
            stem = parts[0]
            suffix = ""
        counter = 1
        while f"{stem} (copy{counter}){suffix}" in existing_names:
            counter += 1
        return f"{stem} (copy{counter}){suffix}"

    async def del_file(self, file_name: str) -> None:
        node = self.children.get(file_name)
        if node and not node.is_directory:
            await self._delete_physical_file(file_name)
            del self.children[file_name]
        else:
            raise FileNotFoundError(f"File '{file_name}' not found")

    async def del_directory(self, dir_name: str) -> None:
        node = self.children.get(dir_name)
        if node and node.is_directory:
            await self._delete_physical_directory(dir_name)
            del self.children[dir_name]
        else:
            raise FileNotFoundError(f"Directory '{dir_name}' not found")

    async def remove_child(self, child_name: str) -> None:
        node = self.children.get(child_name)
        if node:
            await self._delete_physical_node(node)
            del self.children[child_name]
        else:
            raise FileNotFoundError(f"Child '{child_name}' not found")

    async def rename(self, new_name: str) -> None:
        if self.parent:
            del self.parent.children[self.name]
        await self._physical_rename(new_name)
        self.name = new_name
        if self.parent:
            self.parent.children[new_name] = self
        self.modified_time = datetime.datetime.now()

    @abstractmethod
    def _calculate_size(self) -> int: pass

    @abstractmethod
    async def read(self, binary: bool = False) -> Union[str, bytes]: pass

    @abstractmethod
    async def write(self, content: Union[str, bytes], binary: bool = False) -> None: pass

    @abstractmethod
    async def copy_child(self, node_to_copy: AbstractVFSNode) -> AbstractVFSNode: pass

    @abstractmethod
    async def scan(self) -> None: pass

    @abstractmethod
    async def _create_physical_file(self, file_name: str) -> None: pass

    @abstractmethod
    async def _create_physical_directory(self, dir_name: str) -> None: pass

    @abstractmethod
    async def _delete_physical_file(self, file_name: str) -> None: pass

    @abstractmethod
    async def _delete_physical_directory(self, dir_name: str) -> None: pass

    @abstractmethod
    async def _delete_physical_node(self, node: AbstractVFSNode) -> None: pass

    @abstractmethod
    async def _physical_rename(self, new_name: str) -> None: pass

    @abstractmethod
    async def new_file(self, file_name: str) -> AbstractVFSNode: pass

    @abstractmethod
    async def new_directory(self, dir_name: str) -> AbstractVFSNode: pass
