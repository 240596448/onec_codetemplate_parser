"""fixtures for tests"""

import os
from pathlib import Path
import pytest

def get_all_fixtures():
    """Автоматически находим все файлы в директории тестовых данных."""
    st_files = Path(__file__).parent.glob("fixtures/*.st")
    list_st_files = [f for f in st_files if f.is_file()]

    # Добавляем файлы из внешнего списка, если он задан
    file_list = os.getenv("TEMPLATES_LIST")
    if file_list:
        if not Path(file_list).is_file():
            raise FileNotFoundError(f"Файл списка дополнительных шаблонов не найден: {file_list}")
        file_lines = Path(file_list).read_text(encoding='utf-8-sig').splitlines()
        for item in file_lines:
            item_path = Path(item).expanduser() if item.startswith("~") else Path(item)
            if item_path.is_file():
                list_st_files.append(item_path)
            else:
                raise FileNotFoundError(
                    f"Файл шаблона из списка дополнительных файлов "
                    f"({Path(file_list).name}) не найден: {item_path}")

    return [pytest.param(e, id=e.name) for e in list_st_files]

@pytest.fixture(scope="class", name="test_file_path", params=get_all_fixtures())
def test_data_path(request):
    """Путь к каждому тестовому файлу."""
    return Path(request.param)

@pytest.fixture(scope="class")
def test_data(test_file_path):
    """Данные каждого тестового файла."""
    file_data = test_file_path.read_text(encoding='utf-8-sig')
    return file_data

@pytest.fixture()
def temp_src(tmp_path):
    """Создаёт временную папку 'src' для каждого теста."""
    src_path = tmp_path / "src"
    src_path.mkdir()
    return src_path

@pytest.fixture()
def temp_output_st(tmp_path):
    """Создаёт временный файл для вывода каждого теста."""
    output_path = tmp_path / "output.st"
    output_path.touch()
    return output_path
