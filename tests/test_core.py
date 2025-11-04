from onec_codetemplate_parser import repository
from onec_codetemplate_parser.parser import parse
from tests.common import check_files_sequential, folder_contains_files, folder_is_empty

class TestReadSkobkofile:

    def test_00_test_file_exist(self, file_path):
        assert file_path.exists()

    def test_01_parse_eq_compile(self, file_data):
        root = parse(file_data)
        new_data = root.compile()
        assert new_data == file_data

    def test_02_save_and_read(self, file_data, tmp_path):
        root = parse(file_data)
        new_data = root.compile()

        tmp_file = tmp_path / 'tmp.st'
        tmp_file.write_text(new_data, encoding='utf-8-sig')
        new_data = tmp_file.read_text(encoding='utf-8-sig')
        assert new_data == file_data


class TestWriteToFiles:

    def test_white_to_src(self, file_data_spec, temp_src):
        root = parse(file_data_spec.data)
        root.to_src(temp_src)

        # файл не пустой - что-то в src должно быть
        if file_data_spec.level is None or file_data_spec.level > 0:
            assert folder_contains_files(temp_src), f"В папке нет ни одного файла {temp_src}"
            assert not folder_is_empty(temp_src), f"Папка src пустая {temp_src}"

        # объектов больше одного - всегда одна папка первого уровня
        if file_data_spec.objects is None or file_data_spec.objects > 1:
            dirs = [p for p in temp_src.iterdir() if p.is_dir()]
            assert len(dirs) == 1, f"Ожидалась 1 папка в src, получили {len(dirs)}"
        
        # один объект - одна папка без файлов
        if file_data_spec.objects == 1:
            dirs = [p for p in next(temp_src.iterdir()).iterdir() if p.is_dir()]
            assert len(dirs) == 0, f"Ожидалась что папок 2 уровня не будет в src/001, получили {len(dirs)}"
            
            files = [p for p in next(temp_src.iterdir()).iterdir() if p.is_file()]
            assert len(files) == 1, f"Должен быть только .мета-файл в src/001 {temp_src}"
            
        if file_data_spec.objects == 2:
            dirs = [p for p in next(temp_src.iterdir()).iterdir() if p.is_dir()]
            assert len(dirs) == 0, f"Ожидалась 1 папка в src/001, получили {len(dirs)}"
            
            files = [p for p in next(temp_src.iterdir()).iterdir() if p.is_file()]
            assert len(files) == 2, f"Ожидалось 2 файла в src/001(.meta и leaf), получили {len(files)}"
            
        if file_data_spec.name == "09-brackets":
            folder = "001.0_Новый1"
            assert (temp_src/folder).exists(), f"Папка первого уровня {folder} не найдена в {file_data_spec.name}"
            subfiles = list(p.name for p in repository.dir_items(temp_src/folder))
            check_files_sequential(subfiles)
