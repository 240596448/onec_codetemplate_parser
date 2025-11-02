from onec_codetemplate_parser import parse_to_src, render_from_src
from tests.common import folder_is_empty, folder_contains_files

class Test_API:

    def test_parse(self, test_file_path, temp_src):
        """Тест библиотеки: парсинг"""
        parse_to_src(str(test_file_path), str(temp_src))
        if test_file_path.stat().st_size > 6:
            assert folder_is_empty(temp_src), f"Папка src пустая {temp_src}"
        else:
            assert not folder_is_empty(temp_src), f"Для пустого файла что-то распарсилось {temp_src}"
        
    def test_render(self, test_file_path, temp_src, tmp_path):
        """Тест библиотеки: сборка"""

        parse_to_src(str(test_file_path), str(temp_src))
        temp_file = tmp_path / "output.st"
        render_from_src(str(temp_src), str(temp_file))
        assert temp_file.exists(), f"Файл сборки не создан {temp_file}"
        assert test_file_path.read_text(encoding='utf-8-sig') == temp_file.read_text(encoding='utf-8-sig'), 'Собранный файл не совпадает с исходным'