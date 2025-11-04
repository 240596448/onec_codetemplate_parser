"""Парсер и компилятор файлов шаблонов кода 1С в скобочной нотации"""

import sys
import re
from typing import List, Union
from pathlib import Path
from .repository import LeafRepository, GroupRepository, dir_items

class Node:
    """Базовый класс узла дерева шаблона"""
    name: str
    parent: Union["Group", "Root", None] = None
    children: List[Union["Group", "Leaf"]] = [] # ERROR ??
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
        """Сохраняет группу в репозиторий"""
        # self.repo = GroupRepository(self)
        # self.repo.save(path, self.position)

        for child in self.children:
            # child.to_src(self.repo.path)
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

def parser(text: str) -> Root:
    pos = 0

    def skip_ws():
        nonlocal pos
        while pos < len(text) and text[pos] in " \n\r\t":
            pos += 1

    def take(s: str):
        nonlocal pos
        skip_ws()
        length = len(s)
        assert text[pos:pos+length] == s, f"Ожидалось '{s}' на позиции {pos}"
        pos += length
        skip_ws()

    def parse_value():
        nonlocal pos
        if text[pos] == '"':
            return string_value()
        else:
            return numeric_value()

    def string_value():
        nonlocal pos
        pos += 1
        start = pos
        while True:
            if text[pos] != '"':
                pos += 1
            elif text[pos:pos+2] == '""':
                pos += 2
            else:
                break
        s = text[start:pos]
        pos += 1
        return s

    def numeric_value():
        nonlocal pos
        m = re.match(r"-?\d+", text[pos:])
        if not m:
            raise ValueError(f"Ожидалось число на позиции {pos}")
        val = m.group(0)
        pos += len(val)
        return int(val)

    def parse_children(count: int):
        nonlocal pos
        children = []
        for _ in range(count):
            take(",")
            child = parse_node()
            children.append(child)
        return children

    def parse_node() -> Union[Group, Leaf]:
        """
        Парсит один объект — либо группу, либо лист
        { count, { "Имя", флаг1, флаг2, "Поле4", "Поле5" } }
        """
        nonlocal pos
        take("{")
        count = numeric_value()
        take(",")
        take("{")
        name = parse_value()
        take(",")
        is_group = numeric_value()
        take(",")
        menu_flag = numeric_value()
        take(",")
        replace = parse_value()
        take(",")
        text_val = parse_value()
        take("}")
        children = parse_children(count)
        take("}")

        # Создаем правильный тип объекта в зависимости от is_group
        if int(is_group) == 1:
            return  Group(name, children)
        elif int(is_group) == 0:
            return Leaf(name, menu_flag, replace, text_val)
        else:
            raise ValueError(f"Неизвестный значение флага is_group: {is_group}")

    take("{")
    count = numeric_value()
    root = Root(parse_children(count))
    take("}")
    assert text[pos:] == "", f"Ожидалось конец файла, но есть остаток: {text[pos:]}"
    return root

def main():
    if len(sys.argv) < 2:
        print("Использование: python parse_skobkofile.py <путь_к_файлу>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        text = f.read()

    root = parser(text)
    print("\n✅ Файл успешно прочитан\n")
    root.pretty_print()

    recompiled = root.compile()

    if recompiled == text:
        print("✅ Файл успешно скомпилирован и совпадает с исходником")
    else:
        # запись обратно в контрольный файл
        output_path = path + ".out"
        with open(output_path, "w", encoding="utf-8-sig") as f:
            f.write(recompiled)

        print("❌ Файл успешно скомпилирован, но не совпадает с исходником")
        print(f"Скомпилированный файл сохранен в {output_path}")

    source_path = 'temp/src'
    root.to_src(source_path)

    root2 = Root.from_src(source_path)

    recompiled = root2.compile()

    if recompiled == text:
        print("✅ Файл успешно скомпилирован и совпадает с исходником")
    else:
        # запись обратно в контрольный файл
        output_path = path + ".out"
        with open(output_path, "w", encoding="utf-8-sig") as f:
            f.write(recompiled)

        print("❌ Файл успешно скомпилирован, но не совпадает с исходником")
        print(f"Скомпилированный файл сохранен в {output_path}")

if __name__ == "__main__":
    main()
