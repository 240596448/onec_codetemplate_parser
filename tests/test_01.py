from onec_codetemplate_parser import core
from tests.common import check_files_sequential

class Test_Read_Skobkofile:

    def test_00_test_file_exist(self, test_file_path):
        assert test_file_path.exists()

    def test_01_parse_eq_compile(self, test_data):
        root = core.parse_skobkofile(test_data)
        new_data = root.compile()
        assert new_data == test_data

    def test_02_save_and_read(self, test_data, tmp_path):
        root = core.parse_skobkofile(test_data)
        new_data = root.compile()

        tmp_file = tmp_path / 'tmp.st'
        tmp_file.write_text(new_data, encoding='utf-8-sig')
        new_data = tmp_file.read_text(encoding='utf-8-sig')
        assert new_data == test_data


class Test_Write_To_Files:

    def test_00_to_file(self, test_data, temp_src):
        root = core.parse_skobkofile(test_data)
        root.to_files(temp_src)

    def test_01_to_files(self, temp_src):
        # Проверка: есть ли файлы
        files = [p for p in temp_src.iterdir() if p.is_file()]
        assert len(files) == 0

        # Проверка: есть ли папки
        dirs = [p for p in temp_src.iterdir() if p.is_dir()]
        assert len(dirs) == 1
        assert (temp_src / "001.0_Надулич") in dirs

    def test_02_sequential_name(self, temp_src):
        d = temp_src / "001.0_Надулич" / "002.0_Комментарии"
        subfiles = [p.name for p in d.iterdir()]
        check_files_sequential(subfiles)


