# J2Escape

[![.github/workflows/python-package.yml](https://github.com/jifox/j2escape/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/jifox/j2escape/actions/workflows/python-package.yml)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-311/)


### Installation

```
pip install j2escape
```

### Description

This Python module enables storing Jinja2 templates in a
[Cookiecutter](https://github.com/cookiecutter/cookiecutter)
or [Cruft](https://github.com/cruft/cruft) project.

When replacing input variables in the source code, Cookiecutter internally uses
Jinja templates. However, this may lead to errors if a Jinja template such
as `{% if config.allow_duplicates %}` refers to the application instead of Cookiecutter or Cruft.

To avoid this issue, the module leverages the `jinja2.lex()` function to parse the
template and escape the blocks accordingly.

The conversion is idempodent so escaping an already escaped template will not change it.

| Template | Escaped Template |
|---|---|
| {{ variable }} | {{ '{{' }} variable {{ '}}' }} |
| {% if config.allow_duplicates %} | {{ '{%' }} if config.allow_duplicates {{ '%}' }} |

The module can be run as a command-line interface using the `j2escape`
command, which can be used to escape jinja2 tags in a directory of templates.

Here's a list of the available options:

```bash
j2escape --help
usage: j2escape [-h] [-t TEMPLATE_DIR] [-o OUTPUT_DIR] [--overwrite] [-c] [-l LOGLEVEL] [-v LOGFILE]

Escape jinja2 tags in a directory of templates.

options:
  -h, --help            show this help message and exit
  -t TEMPLATE_DIR, --template-dir TEMPLATE_DIR
                        The path to a directory containing one or more files
                        with the extension .j2.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        The path to the directory where the escaped templates should be saved.
  --overwrite           Overwrites the original templates in the --template-dir. Required if
                        --output-dir is not set.
  -c, --create-ok       Create the output directory if it does not exist.
  -l LOGLEVEL, --loglevel LOGLEVEL
                        The loglevel. Default is INFO.
  -v LOGFILE, --logfile LOGFILE
                        The logfile. Default is None.
```

To use the module in Python code, you can import it as follows:

```python
import j2escape

template_directory = "./source-dir"
output_directory = "./excaped-templates"
allow_create_output_dir = True

j2e = J2Escape(template_directory)
j2e.save_to_directory(outputdir=output_directory, create_ok=allow_create_output_dir)
```

The static method `get_escaped()` can be used to escape templates in memory:

`escaped_tamplate_string = J2Escape.get_escaped(plain_template_string)`
