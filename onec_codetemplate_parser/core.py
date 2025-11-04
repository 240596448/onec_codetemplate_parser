"""Парсер и компилятор файлов шаблонов кода 1С в скобочной нотации"""

from typing import List, Union
from pathlib import Path
from .repository import LeafRepository, GroupRepository, dir_items

class Node:
    """Базовый класс узла дерева шаблона"""
    name: str
    parent: Union["Group", "Root", None] = None
    children: List[Union["Group", "Leaf"]] = []
    position: int = 0

    def __init__(self, name: str):
        self.name = name

    def set_parent(self, parent):
        self.parent = parent
        self.position = parent.children.index(self) + 1

class Leaf(Node):
    """Обычный лист с пятью полями"""
    repo: LeafRepository = None

    def __init__(self, name: str, menu_flag: int, replace: str, text: str):
        super().__init__(name)
        self.menu_flag = int(menu_flag)
        self.replace = replace
        self.text = text

    def __repr__(self):
        return f"Leaf({self.name!r}, menu={self.menu_flag}, '{self.replace}')"

    def pretty_print(self, indent=0):
        pad = " " * indent
        print(f"{pad}* Leaf: {self.name} (key: {self.replace})")

    def compile(self) -> str:
        parts = [
            "{0,\n{",
            f'"{self.name}"',
            ",0,",
            str(self.menu_flag),
            ',"',
            self.replace,
            '","',
            self.text,
            '"}\n}',
        ]
        return "".join(parts)

    def to_src(self, path):
        """Сохраняет лист в репозиторий"""
        self.repo = LeafRepository(self)
        self.repo.save(path, self.position)

    @classmethod
    def from_src(cls, path):
        """Создает лист из репозитория по пути"""
        repo = LeafRepository.read(path)
        leaf = Leaf(repo.name, repo.menu_flag, repo.replace, repo.text)
        leaf.repo = repo
        return leaf

class Group(Node):
    """Группа: заголовок + список подэлементов (листов/групп)"""

    repo: GroupRepository = None

    def __init__(self, name: str, children: List[Union["Group", Leaf]]):
        super().__init__(name)
        self.children = children
        for child in self.children:
            child.set_parent(self)

    def __repr__(self):
        return f"Group({self.name!r}, {len(self.children)} children)"

    def pretty_print(self, indent=0):
        pad = " " * indent
        print(f"{pad}- Group: {self.name}")
        for child in self.children:
            child.pretty_print(indent + 2)

    def compile(self) -> str:
        parts = [
            '{',
            str(len(self.children)),
            ',\n{',
            f'"{self.name}"',
            ',1,0,"",""}',
        ]
        for child in self.children:
            parts.append(",\n")
            parts.append(child.compile())
        parts.append('\n}')
        return "".join(parts)

    def to_src(self, path):
        """Сохраняет группу в репозиторий"""
        self.repo = GroupRepository(self)
        self.repo.save(path, self.position)

        for child in self.children:
            child.to_src(self.repo.path)

    @classmethod
    def from_src(cls, path):
        repo = GroupRepository.read(path)
        group = Group(repo.name, src_items(path))
        group.repo = repo
        return group

class Root(Node):
    """Корневой узел дерева шаблона"""
    repo: GroupRepository = None

    def __init__(self, children: List[Union[Group, Leaf]]):
        super().__init__("root")
        self.children = children
        for child in self.children:
            child.set_parent(self)

    def __repr__(self):
        return f"Root({len(self.children)} children)"

    def pretty_print(self, indent=0):
        pad = " " * indent
        print(f"{pad}Root:")
        for child in self.children:
            child.pretty_print(indent + 2)
        print("")

    def compile(self) -> str:
        parts = [ "{", str(len(self.children)) ]
        for child in self.children:
            parts.append(",\n")
            parts.append(child.compile())
        parts.append("\n}" if self.children else "}")
        return "".join(parts)

    def to_src(self, path):
        """Сохраняет дочерние группы в репозиторий"""
        for child in self.children:
            child.to_src(path)

    @staticmethod
    def from_src(path):
        """Прочитать все файлы рекурсивно в объекты дерева"""

        assert Path(path).exists(), f"Директория '{path}' не существует"
        assert Path(path).is_dir(), f"Путь '{path}' не является директорией"

        return Root(src_items(path))

def src_items(path: Path|str) -> List[Union[Group, Leaf]]:
    children = []
    for item in dir_items(path):
        if item.is_dir():
            child = Group.from_src(item)
        else:
            child = Leaf.from_src(item)
        children.append(child)
    return children
