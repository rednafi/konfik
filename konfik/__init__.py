import argparse
import json
import operator
import sys
import traceback
from functools import reduce
from pprint import pformat

import pkg_resources
import toml
import yaml
from dotenv import dotenv_values, find_dotenv
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer, get_lexer_by_name

__all__ = ["Konfik"]

__version__ = pkg_resources.get_distribution("konfik").version


class Colorize:
    """Colorize tracebacks, variables and config literals."""

    def __init__(self):
        self.formatter = TerminalFormatter()
        sys.excepthook = self.colorize_traceback

    def colorize_traceback(self, type, value, tb):
        """Colorize exception tracebacks."""

        lexer = get_lexer_by_name("py3tb")
        tbtext = "".join(traceback.format_exception(type, value, tb))

        # Error needs to go to stderr
        sys.stderr.write(highlight(tbtext, lexer, self.formatter))

    def colorize_config(self, config_str, config_ext):
        """Colorize config literals."""

        lexer_map = {
            "toml": "toml",
            "json": "json",
            "env": "bash",
            "yaml": "yaml",
        }

        lexer = get_lexer_by_name(lexer_map.get(config_ext))
        print(highlight(config_str, lexer, self.formatter))

    def colorize_entity(self, entity):
        """Colorize printed Python objects."""

        lexer = PythonLexer()
        entity = pformat(entity, indent=1, compact=True, width=60)
        print(highlight(entity, lexer, self.formatter))

    def colorize_title(self, text):
        """Colorize CLI title."""

        CYAN = "\033[96m"
        BOLD = "\033[1m"
        ENDC = "\033[0m"
        print(CYAN + BOLD + text + ENDC)


colorize = Colorize()


class MissingVariableError(Exception):
    """Error is raised when an undefined variable is called. This
    encapsulates the built-in dict KeyError."""


class MissingConfigError(Exception):
    """Error is raised when the configuration file is not found. This
    encapsulates the built-in FileNotFoundError."""


class DotMap(dict):
    """Modified dictionary class that lets you access key:val via dot notation."""

    def __init__(self, *args, **kwargs):
        # We trust the dict to init itself better than we can.
        super().__init__(*args, **kwargs)
        # Because of that, we do duplicate work, but it's worth it.
        for k, v in self.items():
            self.__setitem__(k, v)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            raise MissingVariableError(f"No such variable '{key}' exists") from None

    def __setitem__(self, key, val):
        super().__setitem__(key, self._convert(val))

    def __delitem__(self, key):
        if hasattr(self, key):
            super().__delitem__(key)

    __getattr__ = __getitem__
    __setattr__ = __setitem__
    __delattr__ = __delitem__

    @classmethod
    def _convert(cls, o):
        """
        Recursively convert `dict` objects inside `dict`, `list`, `set`, and
        `tuple` objects to `DotMap` objects.
        """
        if isinstance(o, dict):
            o = cls(o)
        elif isinstance(o, list):
            o = list(cls._convert(v) for v in o)
        elif isinstance(o, set):
            o = set(cls._convert(v) for v in o)
        elif isinstance(o, tuple):
            o = tuple(cls._convert(v) for v in o)
        return o


class Konfik:
    """Primary class that holds all the public APIs."""

    def __init__(
        self,
        config_path,
        dotmap_cls=DotMap,
    ):
        self._config_path = config_path
        self._config_ext = str(self._config_path).split(".")[-1]
        self._config_raw = self._load_config()
        self.config = dotmap_cls(self._config_raw)

    def show_config(self):
        """Printing evaluated config file as a Python dict."""

        colorize.colorize_entity(self._config_raw)

    def show_config_literal(self):
        """Print literal config file contents."""

        with open(self._config_path) as f:
            config_str = f.read()
            colorize.colorize_config(config_str, self._config_ext)

    def show_config_var(self, query):
        """Print the config variables."""

        if isinstance(query, str):
            query_lst = query.split(".")
            value = self.get_by_path(self._config_raw, query_lst)
            colorize.colorize_entity(value)

    def _load_config(self):
        """Load config.toml file."""

        # Making sure that pathlib.Path object are converted to string
        if self._config_path:
            config_path = str(self._config_path)

            if self._config_ext == "env":
                return self._load_env(config_path)

            elif self._config_ext == "json":
                return self._load_json(config_path)

            elif self._config_ext == "toml":
                return self._load_toml(config_path)

            elif self._config_ext == "yaml" or self._config_ext == "yml":
                return self._load_yaml(config_path)

            else:
                raise NotImplementedError(
                    f"Config type '{self._config_ext}' is not supported."
                )

    @staticmethod
    def _load_env(config_path):
        """Load .env file."""

        try:
            # Instead of using `load_dotenv()``, this is done to avoid recursively searching for dotenv file.
            # There is no element of surprise. If the file is not found in the explicit path, this will raise an error!
            dotenv_file = find_dotenv(
                filename=config_path, raise_error_if_not_found=True, usecwd=True
            )

            if dotenv_file:
                config = dotenv_values(dotenv_file)
                return config

        except OSError:
            raise MissingConfigError("DOTENV file not found.") from None

    @staticmethod
    def _load_json(config_path):
        try:
            with open(config_path) as f:
                config = json.load(f)
                return config
        except FileNotFoundError:
            raise MissingConfigError("JSON file not found.")

    @staticmethod
    def _load_toml(config_path):
        """Load .toml file."""

        # FileNotFound & TomlDecodeError will be raised.
        try:
            config = toml.load(config_path)
            return config

        except FileNotFoundError:
            raise MissingConfigError("TOML file not found.") from None

    @staticmethod
    def _load_yaml(config_path):
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
                return config
        except FileNotFoundError:
            raise MissingConfigError("YAML file not found.")

    @staticmethod
    def get_by_path(dct, key_list):
        """Access a nested object in root by item sequence."""

        try:
            return reduce(operator.getitem, key_list, dct)
        except KeyError as e:
            raise MissingVariableError(
                f"No such variable '{e.args[0]}' exists."
            ) from None


class KonfikCLI:
    """Access and show config variables using the CLI."""

    def build_parser(self):
        parser = argparse.ArgumentParser(
            description=colorize.colorize_title(
                "\nKonfik -- The strangely familiar config parser ⚙️\n"
            )
        )

        # Add arguments.
        parser.add_argument("--path", help="add config file path")
        parser.add_argument(
            "--show",
            action="store_true",
            help="print config as a dict",
        )
        parser.add_argument(
            "--show-literal",
            action="store_true",
            help="print config file content literally",
        )
        parser.add_argument("--var", help="print config variable")
        parser.add_argument(
            "--version",
            action="store_true",
            help="print konfik-cli version number",
        )

        return parser

    def raise_arg_error(self, parser, args):
        # Deal with argument dependencies.
        for k, v in vars(args).items():
            if k == "version":
                continue

            if k == "path":
                continue

            if v and not args.path:
                parser.error(f"The --{k} argument requires the --path argument.")

    def trigger_handler(self, args, konfik_cls=Konfik, version=__version__):
        if args.version:
            colorize.colorize_entity(version)

        if args.path:
            konfik = konfik_cls(args.path)

            if args.show:
                konfik.show_config()
            elif args.show_literal:
                konfik.show_config_literal()
            elif args.var:
                konfik.show_config_var(args.var)


def cli_entrypoint(argv=None):
    """CLI entrypoint callable."""

    konfik_cli = KonfikCLI()
    parser = konfik_cli.build_parser()
    args = parser.parse_args(argv)

    konfik_cli.raise_arg_error(parser, args)
    konfik_cli.trigger_handler(args)


# if __name__ == "__main__":
#     cli_entrypoint()
