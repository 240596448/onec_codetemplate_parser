"""Консольное приложение для вызова API библиотеки """

from pathlib import Path
import typer
from .api import parse_to_src, render_from_src, pretty_print

app = typer.Typer(
    help="Парсер шаблонов кода 1С.\n\n"
         "Позволяет разбирать шаблоны *.st в исходники src и обратно.")

def validate_file_enable(value: str):
    """Проверка существования и размера файла"""
    path = Path(value)
    if not path.is_file():
        raise typer.BadParameter(f"Файл отсутствует '{value}'")
    elif path.stat().st_size <=3:
        raise typer.BadParameter(f"Файл пустой '{value}'")
    return path

def validate_empty_dir(value: str):
    """Проверка существования и пустоты папки"""
    path = Path(value)
    if not path.is_dir() or not any(path.iterdir()):
        raise typer.BadParameter(f"Папка '{value}' не существует или пуста.")
    return path

@app.command(help="Разобрать шаблон из 1С-файла *.st в исходники src")
def parse(
        path: str = typer.Argument(...,
            callback=validate_file_enable,
            help="Путь к исходному 1С-файлу шаблона *.st", ),
        src: str = typer.Argument('./src', help="Папка, в которую будут сохранены исходники src")
    ):
    """
    Разбирает 1С-шаблон (*.st) на исходники для редактирования.
    
    Пример:
        onec_codetemplate_parser parse my_template.st ./src
    """
    parse_to_src(path, src)
    typer.echo(f"Шаблон {path} разобран в папку {src}")


@app.command(help="Собрать шаблон из исходников src в 1С-файл *.st")
def render(
        path: str = typer.Argument(..., help="Путь, куда будет записан собранный 1С-файл *.st"),
        src: str = typer.Argument('./src', callback=validate_empty_dir, help="Папка с исходниками src для сборки шаблона")
    ):
    """
    Собирает 1С-шаблон (*.st) из исходников.

    Пример:
        onec_codetemplate_parser render ./src my_template.st
    """
    render_from_src(src, path)
    typer.echo(f"Шаблон собран из папки {src} в файл {path}")


@app.command(help="Показать структуру файла *.st")
def pretty(
        path: str = typer.Argument(...,
            callback=validate_file_enable,
            help="Путь к исходному 1С-файлу шаблона *.st", )
    ):
    """
    Визуализация структуры 1С-шаблон (*.st) в виде дерева.
    
    Пример:
        onec_codetemplate_parser pretty my_template.st
    """
    pretty_print(path)


if __name__ == "__main__":
    app()
