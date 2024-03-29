# Test J2Escape

# Path: j2escape/tests/test_je2scape.py
import logging
import os
import sys
import tempfile
import pytest

# import subprocess
from pathlib import Path
from j2escape.j2escape import J2Escape, init_logging, logger, main

TEST_DATA_DIR = "tests/data"


class TemplateData:
    # odd numbers are templates that should be escaped
    # even numbers are templates that should not be escaped (already escaped)
    templates = [
        "test",  # 0
        "test",
        "{{ 'test' }}",  # 1
        "{{ '{{' }} 'test' {{ '}}' }}",
        "{% set test = 'test' %}",  # 2
        "{{ '{%' }} set test = 'test' {{ '%}' }}",
        "{# {{ commented out }} #}",  # 3
        "{# {{ commented out }} #}",
        "{% if config.allow_duplicates %}",  # 4
        "{{ '{%' }} if config.allow_duplicates {{ '%}' }}",
    ]


@pytest.fixture(autouse=True)
def setup():
    """Initialize the test."""
    # Erase the test data directory
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    for file in os.listdir(TEST_DATA_DIR):
        os.remove(os.path.join(TEST_DATA_DIR, file))

    # create the test template files in the {TEST_DATA_DIR} directory
    for idx, value in enumerate(TemplateData.templates):
        with open(f"{TEST_DATA_DIR}/template{idx}.j2", "w") as f:
            f.write(value)


def read_teplate(nr):
    """Read the plain and escaped template files.

    Args:
        nr (int): The number of the template file to read.

    Returns:
        tuple: The plain and escaped template file content.
    """
    nr *= 2
    with open(f"{TEST_DATA_DIR}/template{nr}.j2", "r") as f:
        plain = f.read()
    with open(f"{TEST_DATA_DIR}/template{nr+1}.j2", "r") as f:
        escaped = f.read()
    return plain, escaped


def test_init_with_file():
    _ = J2Escape(f"{TEST_DATA_DIR}/template1.j2")


def test_init_with_dir():
    _ = J2Escape(f"{TEST_DATA_DIR}")


def test_init_with_non_existing_file():
    with pytest.raises(TypeError):
        _ = J2Escape(f"{TEST_DATA_DIR}/does_not_exist.j2")


def test_init_with_non_existing_dir():
    with pytest.raises(TypeError):
        _ = J2Escape(f"{TEST_DATA_DIR}/does_not_exist")


def test_escape_without_fileio():
    idx = 0
    while idx < len(TemplateData.templates):
        plain = TemplateData.templates[idx]
        escaped = TemplateData.templates[idx + 1]
        computed = J2Escape.get_escaped(plain)
        assert computed == escaped, (
            f"Error idx={idx}:\n" f"plain=   {plain}\n" f"escaped= {escaped}\n" f"computed={computed}"
        )
        idx += 2


def test_escape_with_fileio():
    idx = 0
    while idx < len(TemplateData.templates):
        plain, escaped = read_teplate(idx // 2)
        assert plain == TemplateData.templates[idx], (
            f"Error idx={idx}:\n" f"plain=   {plain} != {TemplateData.templates[idx]}\n"
        )
        assert escaped == TemplateData.templates[idx + 1], (
            f"Error idx={idx}:\n" f"escaped= {escaped} != TemplateData.templates[idx + 1]\n"
        )
        idx += 2


def test_escape_write_dir_to_different_location():
    destdir = tempfile.gettempdir() + "/j2escape/test"
    j2e = J2Escape(f"{TEST_DATA_DIR}")
    j2e.save_to_directory(destdir, create_ok=True)
    idx = 0
    while idx < len(TemplateData.templates):
        # Compare only the escaped files with the expected results.
        with open(f"{destdir}/template{idx+1}.j2", "r") as f:
            escaped = f.read()
        assert escaped == TemplateData.templates[idx + 1], (
            f"Error idx={idx}:\n" f"escaped= {escaped} != TemplateData.templates[idx + 1]\n"
        )
        idx += 2
    # remove the test files
    for file in os.listdir(destdir):
        os.remove(os.path.join(destdir, file))
    os.rmdir(destdir)


def test_escape_write_dir_to_same_location():
    j2e = J2Escape(f"{TEST_DATA_DIR}")
    j2e.save_to_directory(TEST_DATA_DIR)
    idx = 0
    while idx < len(TemplateData.templates):
        # Check that the previously stored plain templates are now escaped ones too
        with open(f"{TEST_DATA_DIR}/template{idx}.j2", "r") as f:
            escaped = f.read()
        assert escaped == TemplateData.templates[idx + 1], (
            f"Error idx={idx}:\n" f"escaped= {escaped} != TemplateData.templates[idx + 1]\n"
        )
        idx += 2


def test_init_logging():
    """Test init_logging."""
    init_logging()
    assert logger.getEffectiveLevel() == logging.INFO
    init_logging(logging.DEBUG)
    assert logger.getEffectiveLevel() == logging.DEBUG
    init_logging(logging.DEBUG, "test.log")
    assert logger.getEffectiveLevel() == logging.DEBUG
    assert Path("test.log").is_file()
    Path("test.log").unlink()


# # Test the command line interface
# j2escape -h
# usage: j2escape [-h] [-t TEMPLATES] [-o OUTPUT_DIR] [--overwrite] [-c]
#                 [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-v LOGFILE]

# Escape jinja2 tags in a directory of templates.


# options:
#   -h, --help            show this help message and exit
#   -t TEMPLATES, --templates TEMPLATES
#                         A template filename or a path to a directory containing one or more
#                         files with the extension .j2.
#   -o OUTPUT_DIR, --output-dir OUTPUT_DIR
#                         The path to the directory where the escaped templates should be
#                         saved.
#   --overwrite           Overwrites the original templates. Required if --output-dir is not
#                         set.
#   -c, --create-ok       Create the output directory if it does not exist.
#   -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
#                         log level
#   -v LOGFILE, --logfile LOGFILE
#                         The logfile. Default is None
def test_cli():
    """Test the command line interface."""
    # Test the help
    with pytest.raises(SystemExit):
        main(["-h"])
    # Test the template argument
    with pytest.raises(ValueError):
        main([])
    with pytest.raises(ValueError):
        main(["-t", "does_not_exist.j2"])
    with pytest.raises(ValueError):
        main(["-t", "does_not_exist"])
    with pytest.raises(ValueError):
        main(["-t", "does_not_exist.j2", "-o", "does_not_exist"])
    with pytest.raises(ValueError):
        main(["-t", "does_not_exist", "-o", "does_not_exist"])
    with pytest.raises(ValueError):
        main(["-t", "does_not_exist.j2", "-o", "does_not_exist", "--overwrite"])
    with pytest.raises(ValueError):
        main(["-t", "does_not_exist", "-o", "does_not_exist", "--overwrite"])
    # Test the output directory argument
    with pytest.raises(ValueError):
        main(["-t", f"{TEST_DATA_DIR}/template1.j2", "-o", "does_not_exist"])
    with pytest.raises(ValueError):
        main(["-t", f"{TEST_DATA_DIR}", "-o", "does_not_exist"])
    # Test the overwrite argument
    with pytest.raises(ValueError):
        main(["-t", f"{TEST_DATA_DIR}/template1.j2", "--overwrite"])
    # Test the create-ok argument
    with pytest.raises(ValueError):
        main(["-t", f"{TEST_DATA_DIR}/template1.j2", "-c"])
    # Test the loglevel argument
    with pytest.raises(SystemExit):
        main(["-t", f"{TEST_DATA_DIR}/template1.j2", "-l", "does_not_exist"])
    # Test the logfile argument
    with pytest.raises(ValueError):
        main(["-t", f"{TEST_DATA_DIR}/template1.j2", "-f", "does_not_exist"])
    # Test the main function
    with pytest.raises(ValueError):
        # Error: output-dir must be set or parameter --overwrite must be present!
        main(["-t", f"{TEST_DATA_DIR}/template1.j2"])

    main(["-t", f"{TEST_DATA_DIR}/template1.j2", "-o", f"{TEST_DATA_DIR}"])
    main(["-t", f"{TEST_DATA_DIR}/template1.j2", "-o", f"{TEST_DATA_DIR}", "--overwrite"])
    main(["-t", f"{TEST_DATA_DIR}/template1.j2", "-o", f"{TEST_DATA_DIR}", "--overwrite", "-c"])
    main(["-t", f"{TEST_DATA_DIR}/template1.j2", "-o", f"{TEST_DATA_DIR}", "-l", "DEBUG"])
    main(["-t", f"{TEST_DATA_DIR}/template1.j2", "-o", f"{TEST_DATA_DIR}", "-f", "test.log"])
    # Check if exists before removing
    assert Path("test.log").is_file()
    Path("test.log").unlink()

    # Test the main function with a directory
    with pytest.raises(ValueError):
        # Error: --templates and --output-dir must be different! Use --overwrite to overwrite the original templates
        main(["-t", f"{TEST_DATA_DIR}", "-o", f"{TEST_DATA_DIR}"])
    main(["-t", f"{TEST_DATA_DIR}", "-o", f"{TEST_DATA_DIR}", "--overwrite"])
    main(["-t", f"{TEST_DATA_DIR}", "-o", f"{TEST_DATA_DIR}", "--overwrite", "-c"])
    main(["-t", f"{TEST_DATA_DIR}", "-o", f"{TEST_DATA_DIR}", "--overwrite", "-l", "DEBUG"])
    main(["-t", f"{TEST_DATA_DIR}", "-o", f"{TEST_DATA_DIR}", "--overwrite", "-f", "test.log"])
    assert Path("test.log").is_file()
    Path("test.log").unlink()
    # Test the main function with multiple files and a directory
    main(["-t", f"{TEST_DATA_DIR}/template1.j2, {TEST_DATA_DIR}/template2.j2", "-o", f"{TEST_DATA_DIR}", "--overwrite"])
    if Path("test.log").is_file():
        Path("test.log").unlink()
