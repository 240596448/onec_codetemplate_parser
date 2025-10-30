"""Консольное приложение для вызова API библиотеки """

import typer
from .api import parse_to_src, render_from_src

app = typer.Typer(help="Парсер шаблонов кода 1С (*.st)")

@app.command()
def parse(path: str, src: str):
    """Разобрать шаблон из 1с-файла *.st в исходники src"""
    parse_to_src(path, src)

@app.command()
def render(src: str, path: str):
    """Собрать шаблон из исходников src в 1с-файл *.st"""
    render_from_src(src, path)

if __name__ == "__main__":
    app()
