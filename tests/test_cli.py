import pytest
from typer.testing import CliRunner
from onec_codetemplate_parser.cli import app

runner = CliRunner()

class TestCLI:

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

    def test_parse_command(self, file_path, temp_src):
        """Тест выполнения команды парсинга"""
        result = runner.invoke(app, ["parse", str(file_path), str(temp_src)])
        assert result.exit_code == 0, result.stdout + result.stderr

    def test_render_command(self, file_path_spec, temp_src, temp_output_st):
        """Тест выполнения команды сборки"""
        if file_path_spec.level == 0:
            pytest.skip(reason=f"Пропускаем тест {file_path_spec.name}: папка SRC будет пустой, CLI не пройдет валидацию")
            return
        file_path = file_path_spec.path
        runner.invoke(app, ["parse", str(file_path), str(temp_src)])
        result = runner.invoke(app, ["render", str(temp_output_st), str(temp_src)], catch_exceptions=False)
        assert result.exit_code == 0, result.stdout + result.stderr
        assert file_path.read_text(encoding='utf-8-sig') == temp_output_st.read_text(encoding='utf-8-sig'), 'Собранный файл не совпадает с исходным'

    def test_pretty_print_command(self, file_path_spec):
        """Тест выполнения команды парсинга"""
        result = runner.invoke(app, ["pretty", str(file_path_spec.path)])
        assert result.exit_code == 0, result.stdout + result.stderr
        if file_path_spec.objects is None:
            assert len(result.stdout.splitlines()) > 1, result.stdout + result.stderr
        else:
            assert len(result.stdout.rstrip(). splitlines()) == file_path_spec.objects + 1, result.stdout + result.stderr
