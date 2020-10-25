import argparse
import json
import operator
from functools import reduce

import pkg_resources
import toml
import yaml
from dotenv import dotenv_values, find_dotenv
from rich.console import Console
from rich.syntax import Syntax

__version__ = pkg_resources.get_distribution("konfik").version


# Rich console object for object highlighting
console = Console()


class MissingVariableError(Exception):
    """Error is raised when an undefined variable is called. This
    encapsulates the built-in dict KeyError."""


class MissingConfigError(Exception):
    """Error is raised when configuration file is not found. This
    encapsulates the built-in FileNotFoundError."""


class DotMap(dict):
    """Modified dictionary class that lets do access key:val via dot notation."""

    def _mod_getitem(self, key):
        # Private method that gets called in self.__getitem__ method
        try:
            return super().__getitem__(key)
        except KeyError:
            raise MissingVariableError(f"No such variable '{key}' exists") from None

    def _mod_setitem(self, key, val):
        # Private method that gets called in self.__setitem__ method
        super().__setitem__(key, val)

    def _mod_delitem(self, key):
        # Private method that gets called in self.__delitem__ method
        if hasattr(self, key):
            super().__delitem__(key)

    def __getitem__(self, key):
        return self._mod_getitem(key)

    def __setitem__(self, key, val):
        self._mod_setitem(key, val)

    def __delitem__(self, key):
        self._mod_delitem(key)

    def __getattr__(self, attr_name):
        return self._mod_getitem(attr_name)

    def __setattr__(self, attr_name, attr_val):
        self._mod_setitem(attr_name, attr_val)

    def __delattr__(self, attr_name):
        self._mod_delitem(attr_name)


def apply_dotmap(dct, dotmap_cls=DotMap):
    """Recursively applies DotMap object to a nested dictionary."""

    dct = dotmap_cls(dct)
    for key, val in dct.items():
        if isinstance(val, dict) and not isinstance(val, dotmap_cls):
            dct[key] = apply_dotmap(val)
    return dct


class Konfik:
    """Primary class that holds all the public APIs."""

    def __init__(self, config_path="config.toml", apply_dotmap=apply_dotmap):
        self._config_path = config_path
        self._config_ext = str(self._config_path).split(".")[-1]
        self._config_raw = self._load_config()
        self.config = apply_dotmap(self._config_raw)

    def show_config(self):
        """Printing evaluated config file as a Python dict."""
        console.print(self._config_raw)

    def show_config_literal(self):
        """Print literal config file contents."""

        with open(self._config_path) as f:
            config_str = f.read()
            syntax = Syntax(config_str, f"{self._config_ext}", theme="ansi_dark")
            console.print(syntax)

    def show_config_var(self, query):
        """Print config variable."""

        if isinstance(query, str):
            query_lst = query.split(".")
            value = self.get_by_path(self._config_raw, query_lst)
            console.print(value)

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
                    f"Config type '{self._config_ext}' is not supported"
                )

    @staticmethod
    def _load_env(config_path):
        """Load .env file"""

        try:
            # Instead of using load_dotenv(), this is done to avoid recursively searching for dotenv file.
            # There is no element of surprise. If the file is not found in the explicit path, this will raise an error!
            dotenv_file = find_dotenv(
                filename=config_path, raise_error_if_not_found=True, usecwd=True
            )

            if dotenv_file:
                config = dotenv_values(dotenv_file)
                return config

        except OSError:
            raise MissingConfigError("DOTENV file not found") from None

    @staticmethod
    def _load_json(config_path):
        try:
            with open(config_path) as f:
                config = json.load(f)
                return config
        except FileNotFoundError:
            raise MissingConfigError("JSON file not found")

    @staticmethod
    def _load_toml(config_path):
        """Load .toml file."""

        # FileNotFound & TomlDecodeError will be raised
        try:
            config = toml.load(config_path)
            return config

        except FileNotFoundError:
            raise MissingConfigError("TOML file not found") from None

    @staticmethod
    def _load_yaml(config_path):
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
                return config
        except FileNotFoundError:
            raise MissingConfigError("YAML file not found")

    @staticmethod
    def get_by_path(dct, key_list):
        """Access a nested object in root by item sequence."""

        try:
            return reduce(operator.getitem, key_list, dct)
        except KeyError as e:
            raise MissingVariableError(
                f"No such variable '{e.args[0]}' exists"
            ) from None


class KonfikCLI:
    """Access and show config variables using CLI."""

    def __init__(self, konfik, args):
        self.konfik = konfik
        self.args = args

    @staticmethod
    def _version(version=__version__):
        console.print(version)

    def run_cli(self):
        if self.args.show is True:
            self.konfik.show_config()
        elif self.args.show_literal is True:
            self.konfik.show_config_literal()
        elif self.args.var:
            self.konfik.show_config_var(self.args.var)
        elif self.args.version is True:
            self._version()


def cli_entrypoint():
    """CLI entrypoint callable."""

    parser = argparse.ArgumentParser(description="Konfik CLI")
    parser._action_groups.pop()
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")

    # Add mandatory arguments
    required.add_argument("--path", required=True, help="add config file path")

    # Add optional arguments
    optional.add_argument(
        "--show",
        action="store_true",
        help="print config as a dict",
    )
    optional.add_argument(
        "--show-literal",
        action="store_true",
        help="print config file content literally",
    )
    optional.add_argument("--var", help="print config variable")
    optional.add_argument(
        "--version",
        action="store_true",
        help="print konfik-cli version number",
    )

    args = parser.parse_args()
    trigger = [args.show, args.show_literal, args.var, args.version]
    if any(trigger):
        konfik = Konfik(args.path)
        konfik_cli = KonfikCLI(konfik, args)
        konfik_cli.run_cli()
