"""Парсер и компилятор файлов шаблонов кода 1С в скобочной нотации"""

import re
from typing import Union
from .core import Leaf, Group, Root

def parse(text: str) -> Root:
    """Парсит текст и возвращает объект корня дерева шаблона"""
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
