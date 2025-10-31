from typer.testing import CliRunner
from onec_codetemplate_parser.cli import app

runner = CliRunner()

class Test_CLI:

    def test_help_command(self):
        """Тест вывода справки"""
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "parse " in result.stdout
        assert "render " in result.stdout

    def test_parse_help_command(self):
        """Тест вывода справки команды парсинга"""
        result = runner.invoke(app, ["parse", "--help"])
        
        assert result.exit_code == 0
        assert "path " in result.stdout
        assert "src " in result.stdout

    def test_render_help_command(self):
        """Тест вывода справки команды сборки"""
        result = runner.invoke(app, ["render", "--help"])
        
        assert result.exit_code == 0
        assert "path " in result.stdout
        assert "src " in result.stdout

    def test_parse_command(self, test_file_path, temp_src):
        """Тест выполнения команды парсинга"""
        result = runner.invoke(app, ["parse", str(test_file_path), str(temp_src)])
        assert result.exit_code == 0

    def test_render_command(self, test_file_path, temp_src):
        """Тест выполнения команды сборки"""
        result = runner.invoke(app, ["render", str(test_file_path), str(temp_src)])
        assert result.exit_code == 0
    