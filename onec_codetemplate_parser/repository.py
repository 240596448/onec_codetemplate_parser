"""Конвертер для сохранения шаблонов в файлы и обратно"""

from pathlib import Path
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Leaf, Group, Root

class LeafRepository():
    """Объект хранения элемента шаблона"""
    path: str

    def __init__(self, leaf: "Leaf" = None):
        if leaf is None:
            return
        self.name = leaf.name
        self.menu_flag = leaf.menu_flag
        self.replace = leaf.replace
        self.text = leaf.text

    def save(self, path: str, position: int):
        """Записывает элемент в файл"""
        safe_name = safe_filename(self.name)
        file_name = f"{position:03d}.0_{safe_name}.txt"
        leaf_path = Path(path) / file_name
        self.path = str(leaf_path)

        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(f"[[ Название ]]\n{self.name}\n")
            f.write(f"[[ ВключатьВКонтекстноеМеню ]]\n{self.menu_flag}\n")
            f.write(f"[[ АвтоматическиЗаменятьСтроку ]]\n{self.replace}\n")
            f.write(f"[[ Текст ]]\n{self.text.replace('""', '"')}")

    @classmethod
    def read(cls, path: str):
        """Читает элемент из файла"""
        leaf_repo = LeafRepository()
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            leaf_repo.path = path
            leaf_repo.name = lines[1].strip()
            leaf_repo.menu_flag = int(lines[3].strip())
            leaf_repo.replace = lines[5].strip()
            leaf_repo.text = ''.join(lines[7:]).replace('"', '""')
        return leaf_repo

class GroupRepository():
    """Объект хранения группы шаблона"""
    def __init__(self, group: "Group"|"Root" = None):
        if group is None:
            return
        self.name: str = group.name
        self.path: str = ""

    @staticmethod
    def metafile() -> str:
        """Возвращает имя служебного файла с данными группы"""
        return ".group_data"
    def group_data(self) -> Path:
        """Возвращает путь к файлу с данными группы"""
        return Path(self.path) / self.metafile()

    def save(self, path: str, position: int):
        """Записывает группу в файл"""

        safe_name = safe_filename(self.name)
        dir_name = f"{position:03d}.0_{safe_name}"
        group_path = Path(path) / dir_name
        group_path.mkdir()
        self.path = str(group_path)
        # Сохраняем данные группы в служебный файл
        self.group_data().write_text(f"[[ Название ]]\n{self.name}\n", encoding='utf-8')

    @classmethod
    def read(cls, path: str):
        """Читает группу из файла"""
        group_repo = cls()
        group_repo.path = path
        group_data_path = Path(path)/".group_data"
        with open(group_data_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            group_repo.name = lines[1].strip()
        return group_repo

def safe_filename(name: str) -> str:
    """Возвращает безопасное имя файла"""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def dir_items(path: Path|str) -> list[Path]:
    """Возвращает элементы директории, отсортированные по позиции"""
    items = []
    for item in Path(path).iterdir():
        if item.name != GroupRepository.metafile():
            items.append(item)
    items.sort(key=lambda p: p.name)
    return items
