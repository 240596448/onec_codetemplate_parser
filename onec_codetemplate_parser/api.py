"""Программный интерфейс"""

from pathlib import Path
from .core import Root, parser

def parse_to_src(path: str, src: str):
    """Парсит шаблон 1С-файла и сохраняет структуру файлов в папку"""
    root = parser(path)
    root.to_files(src)

def render_from_src(src: str, path: str):
    """Генерирует код шаблона из исходников"""
    root = Root.from_files(src)
    text = root.compile()
    Path(path).write_text(text, encoding='utf-8-sig')
