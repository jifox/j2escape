from pathlib import Path
import sys
from typing import Optional, Union, Generator
import jinja2
import logging

logger = logging.getLogger(__name__)


class J2Escape:
    """Escape jinja2 tags in a string."""

    def __init__(self, template) -> None:
        """Set the template(s).

        Args:
            template (str):
            - The path to a file containing the template.
            - The path to a directory containing one or more files with the extension .j2.

        Raises:
            TypeError: If template is not a string or a valid file- or directoryname.

        """
        self.j2env = jinja2.Environment()  # nosec B701
        self._template_path: Optional[Union[str, Path]] = None
        self._template_dir: Optional[Union[str, Path]] = None
        self._template: Optional[str] = None
        self._escaped: Optional[str] = None

        if template and Path(template).is_file():
            self._template_path = template
        elif template and Path(template).is_dir():
            self._template_dir = template
        else:
            raise TypeError("Error: vlue must be a string, a valid filename or a valid directory!")

    def _read_template(self, template_path: Union[str, Path]) -> str:
        """Read the template from a file.

        Args:
            template_path (str): The path to the file containing the template.

        Returns:
            str: The template.

        Raises:
            TypeError: If template_path is not a string or a valid filename.

        """
        if template_path and Path(template_path).is_file():
            logger.debug(f"Reading template from {template_path}")
            try:
                with open(template_path) as f:
                    return f.read()
            except OSError as exc:
                logger.error(f"Error reading file {template_path}: {repr(exc)}")
                raise Exception(f"Error reading file {template_path}: {repr(exc)}")
        else:
            raise TypeError("Error: template_path must be a string or a valid filename!")

    def _write_template(self, template: str, template_path: Union[str, Path]) -> None:
        """Write the template to a file.

        Args:
            template (str): The template.
            template_path (str): The path to the file containing the template.

        Raises:
            TypeError: If template_path is not a string or a valid filename.

        """
        if template_path:
            if not Path(template_path).is_dir():
                # make sure the directory exists
                Path(template_path).parent.mkdir(parents=True, exist_ok=True)
            try:
                logger.info(f"Writing template to {template_path}")
                with open(template_path, "w") as f:
                    f.write(template)
            except OSError as exc:
                logger.error(f"Error writing file {template_path}: {repr(exc)}")
                raise Exception(f"Error writing file {template_path}: {repr(exc)}")
        else:
            logger.error("Error: template_path must be a string or a valid filename!")
            raise TypeError("Error: template_path must be a string or a valid filename!")

    def _yield_files(self) -> Generator[Path, None, None]:
        """Yield the files in a directory."""
        if self._template_path:
            yield Path(self._template_path)
        if self._template_dir:
            for filename in Path(self._template_dir).glob("*.j2"):
                yield Path(filename)

    def save_to_directory(self, outputdir: Union[str, Path], create_ok: bool = False):
        """Save the escaped templates to a directory.

        Args:
            outputdir (str): The path to the directory where the escaped templates should be saved.

        Raises:
            ValueError: If outputdir is not a set and  or a valid directoryname.
        """
        if outputdir:
            if not create_ok and not Path(outputdir).is_dir():
                raise ValueError(
                    "Error: outputdir must be a valid directoryname! Use create_ok=True to create the directory!"
                )
            else:
                # make sure the directory exists
                Path(outputdir).mkdir(parents=True, exist_ok=True)
            self._outputdir = Path(outputdir)
        else:
            raise ValueError(
                "Error: outputdir must be a valid directoryname! Use create_ok=True to create the directory!"
            )

        for template_path in self._yield_files():
            self._template = self._read_template(template_path)
            self._escaped = self.get_escaped(self._template)
            self._write_template(self._escaped, self._outputdir / template_path.name)

    @property
    def template(self) -> Optional[str]:
        """Return the template."""
        return self._template

    @property
    def transformed(self) -> Optional[str]:
        """Return the transformed template."""
        return self._escaped

    @staticmethod
    def get_escaped(template: str) -> str:
        """Return the escaped template.

        Args:
            template (str): The template.

        Returns:
            str: The escaped template.
        """
        tokens = list(jinja2.Environment().lex(template))  # nosec B701
        escaped = ""
        fieldstr = ""
        for _, token in enumerate(tokens):
            if token[1].find("_") != -1 and token[1].split("_")[1] == "end":
                fieldstr += token[2]
                cleaned = fieldstr.replace(" ", "").replace('"', "").replace("'", "")
                if cleaned not in ["{{{{}}", "{{}}}}", "{{{%}}", "{{%}}}"]:
                    # not already escaped
                    if fieldstr[:2] == "{{":
                        fieldstr = "{{ '{{' }}" + fieldstr[2:-2] + "{{ '}}' }}"
                    elif fieldstr[:2] == "{%":
                        fieldstr = "{{ '{%' }}" + fieldstr[2:-2] + "{{ '%}' }}"
                escaped += fieldstr
                fieldstr = ""
            else:
                fieldstr += token[2]
        if fieldstr:
            escaped += fieldstr
        return escaped


def init_logging(level: int = logging.INFO, logfile: Optional[str] = None):
    """Initialize logging."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=logfile,
    )
    logger.level = level
    # set log to filename if specified
    if logfile:
        logger.addHandler(logging.FileHandler(logfile))
    logger.debug("Logging initialized")


def main(args=None):
    """Run the script."""
    import argparse

    parser = argparse.ArgumentParser(description="Escape jinja2 tags in a directory of templates.")
    parser.add_argument(
        "-t",
        "--templates",
        type=str,
        help="A comma-separated string of Jinja Templates (*.j2) or a directory with *.j2 files.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        help="Specifies the directory path where the escaped templates will be stored.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replaces the original templates. This is necessary if the --output-dir is not provided.",
    )
    parser.add_argument(
        "-c",
        "--create-ok",
        action="store_true",
        default=False,
        help="Generates the output directory if it doesn’t already exist.",
    )
    parser.add_argument(
        "-l",
        "--loglevel",
        type=str,
        help="log level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
    )
    parser.add_argument(
        "-f",
        "--logfile",
        type=str,
        default=None,
        help="Specifies the logfile. If not provided, the default is None",
    )

    args = parser.parse_args(args)

    if args.logfile:
        logger.addHandler(logging.FileHandler(args.logfile))
        logger.setLevel(logging.getLevelName(args.loglevel))
    else:
        # configure log to stdout
        logging.basicConfig(level=logging.getLevelName(args.loglevel))

    if not args.output_dir and not args.overwrite:
        raise ValueError("Error: output-dir must be set or parameter --overwrite must be present!")

    for template in args.templates.split(","):
        template = template.strip()
        if template and args.output_dir:
            if Path(template).resolve() == Path(args.output_dir).resolve():
                if not args.overwrite:
                    raise ValueError(
                        "Error: --templates and --output-dir must be different! Use --overwrite to overwrite the original templates."
                    )
        if not Path(template).is_file():
            if not Path(template).is_dir():
                raise ValueError("Error: --templates must be a filename or a valid directoryname!")

        logger.info(f"Starting j2escape with args: {args}")
        j2escape = J2Escape(template.strip())
        j2escape.save_to_directory(args.output_dir, create_ok=args.create_ok)
