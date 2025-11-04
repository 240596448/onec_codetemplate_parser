from onec_codetemplate_parser import parse_to_src, render_from_src
from tests.common import folder_is_empty

class Test_API:

    def test_parse(self, file_path_spec, temp_src):
        """Тест библиотеки: парсинг"""
        parse_to_src(str(file_path_spec.path), str(temp_src))
        if file_path_spec.level != 0:
            assert not folder_is_empty(temp_src), f"Папка src пустая {temp_src}"
        else:
            assert folder_is_empty(temp_src), f"Для пустого файла что-то распарсилось {temp_src}"
        
    def test_render(self, file_path, temp_src, tmp_path):
        """Тест библиотеки: сборка"""

        parse_to_src(str(file_path), str(temp_src))
        temp_file = tmp_path / "output.st"
        render_from_src(str(temp_src), str(temp_file))
        assert temp_file.exists(), f"Файл сборки не создан {temp_file}"
        assert file_path.read_text(encoding='utf-8-sig') == temp_file.read_text(encoding='utf-8-sig'), 'Собранный файл не совпадает с исходным'