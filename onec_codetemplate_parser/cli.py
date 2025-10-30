"""Консольное приложение для вызова API библиотеки """

import typer
from .api import parse_to_src, render_from_src

app = typer.Typer(
    help="Парсер шаблонов кода 1С.\n\n"
         "Позволяет разбирать шаблоны *.st в исходники src и обратно.")

@app.command(help="Разобрать шаблон из 1С-файла *.st в исходники src")
def parse(
        path: str = typer.Argument(..., help="Путь к исходному 1С-файлу шаблона *.st", ),
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
        src: str = typer.Argument('./src', help="Папка с исходниками src для сборки шаблона"),
        path: str = typer.Argument(..., help="Путь, куда будет записан собранный 1С-файл *.st")
    ):
    """
    Собирает 1С-шаблон (*.st) из исходников.

    Пример:
        onec_codetemplate_parser render ./src my_template.st
    """
    render_from_src(src, path)
    typer.echo(f"Шаблон собран из папки {src} в файл {path}")


if __name__ == "__main__":
    app()
