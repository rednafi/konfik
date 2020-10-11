import argparse
import json
import operator
from functools import reduce

import toml
import yaml
from dotenv import dotenv_values, find_dotenv
from rich import traceback
from rich.console import Console

from konfik import __version__

# Pretty traceback with Rich
# This is causing slowdown when keyerror is raised. Remove rich in the next version
traceback.install(word_wrap=True)

# Rich console object for object highlighting
console = Console()


class DotMap(dict):
    """Modified dictionary object where the values can be accessed
    as dotdict.key instead of dct[key]
    """

    def __getattr__(self, attr):
        # I should probably raise AttributeError here but I don't want to change dict's behavior
        return self[attr]

    def __setattr__(self, key, val):
        self.__setitem__(key, val)

    def __setitem__(self, key, val):
        super().__setitem__(key, val)
        self.__dict__.update({key: val})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.__dict__[key]


class DeepDotMap(DotMap):
    """Recursively applies DotMap object to a nested dictionary."""

    def __init__(self, dct):
        super().__init__(dct)

    def __call__(self):
        return self._dotmap_apply(self, DotMap)

    def _dotmap_apply(self, dct, dotmap):
        """Recursively applying DotMap class."""

        dct = dotmap(dct)
        for key, val in dct.items():
            if isinstance(val, dict) and not isinstance(val, dotmap):
                dct[key] = self._dotmap_apply(val, dotmap)
        return dct


class Konfik:
    def __init__(self, config_path="config.toml", deep_dotmap=DeepDotMap):
        self._config = self._load_config(config_path)
        self.config = deep_dotmap(self._config)()

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
            raise FileNotFoundError("DOTENV file not found") from None

    @staticmethod
    def _load_json(config_path):
        try:
            with open(config_path) as f:
                config = json.load(f)
                return config
        except FileNotFoundError:
            raise FileNotFoundError("JSON file not found")

    @staticmethod
    def _load_toml(config_path):
        """Load .toml file."""

        # FileNotFound & TomlDecodeError will be raised
        try:
            config = toml.load(config_path)
            return config

        except FileNotFoundError:
            raise FileNotFoundError("TOML file not found") from None

    @staticmethod
    def _load_yaml(config_path):
        try:
            with open(config_path) as f:
                config = yaml.full_load(f)
                return config
        except FileNotFoundError:
            raise FileNotFoundError("YAML file not found")


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

    def _version(self):
        console.print(__version__)

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


def deploy_cli():
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
