import sys, os, shutil
import re
from typing import List, Union

class Node:
    def __init__(self, name: str):
        self.name = name
        self.parent = None
        self.path = None
        self.position = None

    def set_parent(self, parent):
        self.parent = parent
        self.position = parent.children.index(self)+1

class Leaf(Node):
    """Обычный лист с пятью полями"""
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
    
    def to_files(self):

        data = [
            {"Название": self.name},
            {"ВключатьВКонтекстноеМеню": self.menu_flag},
            {"АвтоматическиЗаменятьСтроку": self.replace},
            {"Текст": self.text.replace('""', '"')},
        ]
        
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", self.name)
        self.path = f"{self.parent.path}/{self.position:03d}.0_{safe_name}.yml"

        with open(self.path, 'w', encoding='utf-8') as f:
            for item in data:
                #нужно добавить \n между записями, кроме первой
                if f.tell() > 0:
                    f.write("\n")   
                for key, value in item.items():
                    f.write(f"[{key}]\n")
                    f.write(f"{value}")

    @classmethod
    def from_files(cls, path):
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            name = lines[1].strip()
            menu_flag = int(lines[3].strip())
            replace = lines[5].strip()
            text = ''.join(lines[7:]).replace('"', '""')
            leaf = Leaf(name, menu_flag, replace, text)
            
        return leaf

class Group(Node):
    """Группа: заголовок + список подэлементов (листов/групп)"""
    def __init__(self, counter: int, name: str, children: List[Union["Group", Leaf]]):
        super().__init__(name)
        self.counter = int(counter)
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
            str(self.counter),
            ',\n{',
            f'"{self.name}"',
            ',1,0,"",""}',
        ]
        for child in self.children:
            parts.append(",\n")
            parts.append(child.compile())
        parts.append('\n}')
        return "".join(parts)
    
    def to_files(self):
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", self.name)
        self.path = f"{self.parent.path}/{self.position:03d}.0_{safe_name}"
        
        assert not os.path.isfile(self.path), f"Путь '{self.path}' является файлом, а не директорией"
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        for child in self.children:
            child.to_files()

    @classmethod
    def from_files(cls, path):
        
        entries = sorted(os.listdir(path))
        children = []
        for entry in entries:
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                child = Group.from_files(full_path)
                children.append(child)
            else:
                #лист
                children.append(Leaf.from_files(full_path))
        #создать группу
        group_name = re.sub(r'^.+?_', '', os.path.basename(path))
        return Group(len(children), group_name, children)

class Root(Node):
    def __init__(self, counter: int, children: List[Union[Group, Leaf]]):
        self.counter = int(counter)
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
        parts = [ "{", str(self.counter) ]
        for child in self.children:
            parts.append(",\n")
            parts.append(child.compile())
        parts.append("\n}")
        return "".join(parts)
    
    def to_files(self, path):
        self.path = path
        
        assert not os.path.isfile(path), f"Путь '{path}' является файлом, а не директорией"
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

        for child in self.children:
            child.to_files()
    
    @classmethod
    def from_files(cls, path):

        assert not os.path.isfile(path), f"Путь '{path}' является файлом, а не директорией"
        assert os.path.exists(path), f"Директория '{path}' не существует"

        #прочитать все файлы и собрать обратно в дерево
        entries = sorted(os.listdir(path))
        children = []
        for entry in entries:
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                child = Group.from_files(full_path)
                children.append(child)
        return Root(len(children), children)

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
            return  Group(count, name, children)
        elif int(is_group) == 0:
            return Leaf(name, menu_flag, replace, text_val)
        else:
            raise ValueError(f"Неизвестный значение флага is_group: {is_group}")

    take("{")
    count = numeric_value()
    root = Root(count, parse_children(count))
    take("}")
    assert text[pos:] == "", f"Ожидалось конец файла, но есть остаток: {text[pos:]}"
    return root

if __name__ == "__main__":
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
    root.to_files(source_path)

    root2 = Root.from_files(source_path)

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
