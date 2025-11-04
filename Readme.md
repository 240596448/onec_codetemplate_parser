# onec-codetemplate-parser

Библиотека для парсинга файлов шаблонов кода 1С (.st) и работы с ними.

## Установка

```bash
pip install onec-codetemplate-parser
```

## Использование библиотеки

```python
from onec_codetemplate_parser import parse_to_src, render_from_src

# Выгрузка файла в исходники
parse_to_src("path/to/template.st", "./src")

# Сборка файла из исходников
render_from_src("path/to/template.st", "./src")
```

## Использование консольного приложения

Приложение позволяет выполнять основные команды библиотеки в командной строке.

### Основные команды:

```bash
# Вывести дерево файла шаблонов в консоль
onec_codetemplate_parser pretty path/to/template.st

# Выгрузка файла в исходники
onec_codetemplate_parser parse path/to/template.st ./src

# Сборка файла из исходников
onec_codetemplate_parser render path/to/template.st ./src

# Справка о использовании команд
onec-onec_codetemplate_parser --help

```


## Лицензия

[MIT License](LICENSE)





