"""fixtures for tests"""

from pathlib import Path
import pytest
import os

TEST_FILE = 'Documents/1C/1c-code-templates/Надулич.st'

def get_all_test_files():
    """Автоматически находим все файлы в директории"""
    st_files = Path(__file__).parent.glob("data/*.st")
    list_st_files = [f for f in st_files if f.is_file()]
    
    list_st_files.append(Path.home()/TEST_FILE)

    env_st_templates = os.getenv("ST_TEMPLATES")
    if env_st_templates:
        st_templates = Path(env_st_templates)
        if st_templates.is_file():
            list_st_files.append(st_templates)

    return [pytest.param(e, id=e.name) for e in list_st_files]   

@pytest.fixture(scope="class", name="test_file_path", params=get_all_test_files())
def test_data_path(request):
    return Path(request.param)

@pytest.fixture(scope="class")
def test_data(test_file_path):
    file_data = test_file_path.read_text(encoding='utf-8-sig')
    return file_data

@pytest.fixture(scope="class")
def temp_src(tmp_path_factory):
    """
    Создаёт временную папку 'src' для теста.
    Папка автоматически удаляется после теста.
    """
    return tmp_path_factory.mktemp("src")
