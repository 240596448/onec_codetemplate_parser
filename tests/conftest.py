import pytest
from onec_codetemplate_parser import main
from pathlib import Path

TEST_FILE = 'Documents/1C/1c-text-tempates/Надулич.st'

@pytest.fixture(scope="class")
def test_file_path():    
    return Path.home() / TEST_FILE

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

@pytest.fixture(scope="class")
def temp_src2(tmp_path_factory):
    """
    Создаёт временную папку 'src' для теста.
    Папка автоматически удаляется после теста.
    """
    return tmp_path_factory.mktemp("src2")
