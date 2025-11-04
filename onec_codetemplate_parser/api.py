"""Программный интерфейс"""

from pathlib import Path
from .core import Root
from .parser import parse

def parse_to_src(path: str, src: str):
    """Парсит шаблон 1С-файла и сохраняет структуру файлов в папку"""
    text = Path(path).read_text(encoding='utf-8-sig')
    root = parse(text)
    root.to_src(src)

def render_from_src(src: str, path: str):
    """Генерирует код шаблона из исходников"""
    root = Root.from_src(src)
    text = root.compile()
    Path(path).write_text(text, encoding='utf-8-sig')

def pretty_print(path: str):
    """Выводит в консоль дерево шаблона"""
    text = Path(path).read_text(encoding='utf-8-sig')
    root = parse(text)
    root.pretty_print()
