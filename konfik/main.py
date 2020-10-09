import argparse
import operator
import sys
from functools import reduce

import toml
from dotenv import dotenv_values, find_dotenv
from rich import traceback
from rich.console import Console

from konfik import __version__

# Pretty traceback with Rich
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
    def __init__(
        self, config_path="config.toml", deep_dotmap=DeepDotMap, from_terminal=False
    ):
        self._config = self._load_config(config_path, from_terminal=from_terminal)
        self.config = deep_dotmap(self._config)()

    def serialize(self):
        """Serializing TOML config to Python dictionary."""
        console.print(self._config)

    def _load_config(self, config_path, from_terminal):
        """Load config.toml file."""

        # Making sure that pathlib.Path object are converted to string
        if config_path:
            config_path = str(config_path)
            suffix = config_path.split(".")[-1]

            if suffix == "env":
                return self._load_env(config_path, from_terminal)

            elif suffix == "toml":
                return self._load_toml(config_path, from_terminal)

            else:
                if not from_terminal:
                    raise NotImplementedError(f"Config type {suffix} not supported")

                console.print(f"Config type {suffix} not supported", style="bold_red")
                sys.exit(1)

    @staticmethod
    def _load_env(config_path, from_terminal):
        """Load .env file"""

        try:
            # Instead of using load_dotenv(), this is done to avoid recursively searching for dotenv file.
            # There is no element of surprise. If the file is not found in the explicit path, this will raise an error!
            dotenv_file = find_dotenv(
                filename=config_path, raise_error_if_not_found=True
            )

            if dotenv_file:
                config = dotenv_values(dotenv_file)
                return config

        except OSError:
            if not from_terminal:
                raise FileNotFoundError("DOTENV file not found") from None

            console.print(f"FileNotFoundError: DOTENV file not found", style="bold red")
            sys.exit(1)

    @staticmethod
    def _load_toml(config_path, from_terminal):
        """Load .toml file."""

        # FileNotFound & TomlDecodeError will be raised
        try:
            config = toml.load(config_path)
            return config

        except FileNotFoundError:
            if not from_terminal:
                raise FileNotFoundError("TOML file not found") from None

            console.print(f"FileNotFoundError: TOML file not found", style="bold red")
            sys.exit(1)

        except toml.TomlDecodeError as exc:
            if not from_terminal:
                raise

            console.print(f"TomlDecodeError: {exc}\n", style="bold red")
            sys.exit(1)


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

        konfik = Konfik(config_path, from_terminal=True)
        konfik_cli = KonfikCLI(konfik, args)
        konfik_cli.run_cli()
