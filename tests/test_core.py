from onec_codetemplate_parser import core
from tests.common import check_files_sequential, folder_is_empty, folder_contains_files

class TestReadSkobkofile:

    def test_00_test_file_exist(self, test_file_path):
        assert test_file_path.exists()

    def test_01_parse_eq_compile(self, test_data):
        root = core.parser(test_data)
        new_data = root.compile()
        assert new_data == test_data

    def test_02_save_and_read(self, test_data, tmp_path):
        root = core.parser(test_data)
        new_data = root.compile()

        tmp_file = tmp_path / 'tmp.st'
        tmp_file.write_text(new_data, encoding='utf-8-sig')
        new_data = tmp_file.read_text(encoding='utf-8-sig')
        assert new_data == test_data


class TestWriteToFiles:

    def test_white_to_src(self, test_data, temp_src):
        root = core.parser(test_data)
        root.to_files(temp_src)

        # assert folder_contains_files(temp_src), f"В папке нет ни одного файла {temp_src}"
        # assert not folder_is_empty(temp_src), f"Папка src пустая {temp_src}"

        # Проверка: есть ли папки
        dirs = [p for p in temp_src.iterdir() if p.is_dir()]
        assert len(dirs) == 1, f"Ожидалась 1 папка в src, получили {len(dirs)}"
        assert temp_src / "001.0_Надулич" in dirs, f"Папка 001.0_Надулич не найдена в {temp_src}"

    def test_sequential_name(self, temp_src):
        d = temp_src / "001.0_Надулич" / "002.0_Комментарии"
        subfiles = [p.name for p in d.iterdir()]
        check_files_sequential(subfiles)
