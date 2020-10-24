import argparse
import json
import operator
from functools import reduce

import toml
import yaml
from dotenv import dotenv_values, find_dotenv
from rich.console import Console

from konfik import __version__

# Rich console object for object highlighting
console = Console()


class MissingVariableError(Exception):
    """Error is raised when an undefined variable is called. This
    encapsulates the built-in dict KeyError."""

    pass


class MissingConfigError(Exception):
    """Error is raised when configuration file is not found. This
    encapsulates the built-in FileNotFoundError."""

    pass


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
        try:
            super().__delitem__(key)
        except KeyError:
            raise MissingVariableError(f"No such variable '{key}' exists") from None

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
        self._config = self._load_config(config_path)
        self.config = apply_dotmap(self._config)

    def serialize(self):
        """Serializing TOML config to Python dictionary."""
        console.print(self._config)

    def _load_config(self, config_path):
        """Load config.toml file."""

        # Making sure that pathlib.Path object are converted to string
        if config_path:
            config_path = str(config_path)
            suffix = config_path.split(".")[-1]

            if suffix == "env":
                return self._load_env(config_path)

            elif suffix == "json":
                return self._load_json(config_path)

            elif suffix == "toml":
                return self._load_toml(config_path)

            elif suffix == "yaml" or suffix == "yml":
                return self._load_yaml(config_path)

            else:
                raise NotImplementedError(f"Config type {suffix} not supported")

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


class KonfikCLI:
    """Access and show config variables using CLI."""

    def __init__(self, konfik, args):
        self.konfik = konfik
        self.args = args

    def _show(self):
        if isinstance(self.args.show, str):
            query = self.args.show.split(".")
            value = self.get_by_path(self.konfik.config, query)
            if isinstance(value, DotMap):
                # Rich causes problem if the output type is DotMap
                value = dict(value)
            console.print(value)

    def _serialize(self):
        self.konfik.serialize()

    def _version(self, version=__version__):
        console.print(version)

    def run_cli(self):
        if self.args.show is not None:
            self._show()
        elif self.args.serialize is True:
            self._serialize()
        elif self.args.version is True:
            self._version()

    @staticmethod
    def get_by_path(root, items):
        """Access a nested object in root by item sequence."""
        return reduce(operator.getitem, items, root)


def cli_entrypoint():
    """CLI entrypoint callable."""

    parser = argparse.ArgumentParser(description="Konfik CLI")
    parser.add_argument("--show", help="show variables from config file")
    parser.add_argument("--path", help="add custom config file path")
    parser.add_argument(
        "--serialize", action="store_true", help="print the serialized config file"
    )
    parser.add_argument(
        "--version", action="store_true", help="print konfik-cli version number"
    )

    args = parser.parse_args()

    if args.show or args.serialize or args.version:
        if args.path:
            config_path = args.path
        else:
            config_path = "./config.toml"

        konfik = Konfik(config_path)
        konfik_cli = KonfikCLI(konfik, args)
        konfik_cli.run_cli()
