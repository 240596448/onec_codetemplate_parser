"""fixtures for tests"""

import os
from pathlib import Path
from types import SimpleNamespace
import pytest

def get_all_fixtures():
    """Автоматически находим все файлы в директории тестовых данных."""

    def from_dir():
        st_files = Path(__file__).parent.glob("fixtures/*.st")
        list_st_files = [f for f in st_files if f.is_file()]
        return list_st_files

    def from_env():
        # Добавляем файлы из внешнего списка, если он задан
        list_st_files = []
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
        return list_st_files

    list_st_files = from_dir()
    list_st_files.extend(from_env())

    result = []
    for f in list_st_files:
        if f.name.startswith("00-"):
            spec = {"level": 0, "objects": 0}
        elif f.name.startswith("01-"):
            spec = {"level": 1, "objects": 1}
        elif f.name.startswith("02-"):
            spec = {"level": 1, "objects": 2}
        else:
            spec = {"level": None, "objects": None}
        spec["name"] = f.name
        spec["path"] = f
        result.append(SimpleNamespace(**spec))

    return [pytest.param(r, id=r.name) for r in result]

@pytest.fixture(scope="class", params=get_all_fixtures())
def file_path_spec(request):
    return request.param

@pytest.fixture(scope="class")
def file_path(file_path_spec):
    """Путь к каждому тестовому файлу."""
    return file_path_spec.path

@pytest.fixture(scope="class")
def file_data_spec(file_path_spec):
    """Данные каждого тестового файла."""
    file_path_spec.data = file_path_spec.path.read_text(encoding='utf-8-sig')
    return file_path_spec

@pytest.fixture(scope="class")
def file_data(file_data_spec):
    """Данные каждого тестового файла."""
    return file_data_spec.data

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
