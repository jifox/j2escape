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

### Overview

This module, written in Python, facilitates the storage of Jinja2 templates within a project managed by [Cookiecutter](https://github.com/cookiecutter/cookiecutter) or [Cruft](https://github.com/cruft/cruft).

Cookiecutter utilizes Jinja templates internally when substituting input variables in the source code. However, this can result in errors if a Jinja template, such as {% if config.allow_duplicates %}, is intended for the application rather than Cookiecutter or Cruft.

To circumvent this problem, this module employs the jinja2.lex() function to parse and appropriately escape the template blocks.

The transformation process is idempotent, meaning that an already escaped template will remain unchanged when escaped again.

Example:

| Template | Escaped Template |
|---|---|
| {{ variable }} | {{ '{{' }} variable {{ '}}' }} |
| {% if config.allow_duplicates %} | {{ '{%' }} if config.allow_duplicates {{ '%}' }} |

The module also provides a command-line interface that can be accessed using the `j2escape` command. This command can be utilized to escape jinja2 tags within a directory of templates.

### j2escape usage

```bash
j2escape --help
usage: j2escape [-h] [-t TEMPLATES] [-o OUTPUT_DIR] [--overwrite] [-c] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-f LOGFILE]

Escape jinja2 tags in a directory of templates.

options:
  -h, --help            show this help message and exit
  -t TEMPLATES, --templates TEMPLATES
                        A comma-separated string of Jinja Templates (*.j2) or a directory with *.j2 files.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Specifies the directory path where the escaped templates will be stored.
  --overwrite           Replaces the original templates. This is necessary if the --output-dir is not provided.
  -c, --create-ok       Generates the output directory if it doesn’t already exist.
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        log level
  -f LOGFILE, --logfile LOGFILE
                        Specifies the logfile. If not provided, the default is None
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


### Development

Install [poetry](https://python-poetry.org/docs/#installation) and [pre-commit](https://pre-commit.com/#install) to manage the development environment.

Clone the repository and install the development dependencies:

```bash
git clone https://github.com/jifox/j2escape.git
cd j2escape
poetry install
```

`pre-commit` hooks are used to ensure code quality. To install the pre-commit hooks, run the following command:

```bash
pre-commit install
```

Use pre-commit to run the hooks on all files:

```bash
pre-commit run --all-files
```
