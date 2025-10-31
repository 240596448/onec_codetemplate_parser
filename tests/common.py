import re
from pathlib import Path

def check_files_sequential(files: list[str]):

    files.sort()  # Сортируем по имени

    expected_number = 1
    for name in files:
        m = re.match(r"^(\d{3})\.0_.*", name)
        assert m, f"Неверный формат имени папки: {name}"

        number = m.group(1)  # первые три цифры
        true_number = f'{expected_number:03}'
        assert number == true_number, f"Пропущен номер: ожидаем {true_number}, получили {number}"

        expected_number += 1

def folder_is_empty(path):
    return len(list(Path(path).iterdir())) != 0

def folder_contains_files(path):
    files = [f.name for f in Path(path).rglob('*') if f.is_file()]
    return len(files) > 0

