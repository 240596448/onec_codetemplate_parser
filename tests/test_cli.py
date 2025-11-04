import pytest
from typer.testing import CliRunner
from onec_codetemplate_parser.cli import app

runner = CliRunner()

class Test_CLI:

    def test_help_command(self):
        """Тест вывода справки"""
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "parse " in result.stdout, result.stdout
        assert "render " in result.stdout, result.stdout

    def test_parse_help_command(self):
        """Тест вывода справки команды парсинга"""
        result = runner.invoke(app, ["parse", "--help"])
        
        assert result.exit_code == 0
        assert "path " in result.stdout, result.stdout
        assert "src " in result.stdout, result.stdout

    def test_render_help_command(self):
        """Тест вывода справки команды сборки"""
        result = runner.invoke(app, ["render", "--help"])
        
        assert result.exit_code == 0
        assert "path " in result.stdout, result.stdout
        assert "src " in result.stdout, result.stdout

    def test_parse_command(self, test_file_path, temp_src):
        """Тест выполнения команды парсинга"""
        result = runner.invoke(app, ["parse", str(test_file_path), str(temp_src)])
        assert result.exit_code == 0, result.stdout + result.stderr

    def test_render_command(self, test_file_path, temp_src, temp_output_st):
        """Тест выполнения команды сборки"""
        if test_file_path.name == '00-empty.st':
            print("Пропускаем тест: папка SRC будет пустой, CLI не пройдет валидацию")
            pytest.skip(reason="Пропускаем тест: папка SRC будет пустой, CLI не пройдет валидацию")
            return
        runner.invoke(app, ["parse", str(test_file_path), str(temp_src)])
        result = runner.invoke(app, ["render", str(temp_output_st), str(temp_src)], catch_exceptions=False)
        assert result.exit_code == 0, result.stdout + result.stderr
        assert test_file_path.read_text(encoding='utf-8-sig') == temp_output_st.read_text(encoding='utf-8-sig'), 'Собранный файл не совпадает с исходным'
