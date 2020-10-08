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
        self,
        config_path="config.toml",
        deep_dotmap=DeepDotMap,
    ):
        self._config = self._load_config(config_path)
        self.config = deep_dotmap(self._config)()

    def serialize(self):
        """Serializing TOML config to Python dictionary."""
        console.print(self._config)

    @staticmethod
    def _load_config(config_path):
        """Load config.toml file."""

        # Making sure that pathlib.Path object are converted to string
        if config_path:
            config_path = str(config_path)
            suffix = config_path.split(".")[-1]

            if suffix == "env":
                try:
                    # config = dotenv_values(config_path)
                    # return config
                    dotenv_file = find_dotenv(
                        filename=config_path, raise_error_if_not_found=True
                    )

                    if dotenv_file:
                        config = dotenv_values(dotenv_file)
                        return config

                except OSError:
                    console.print(
                        f"FileNotFoundError: DOTENV file not found", style="bold red"
                    )
                    sys.exit(1)

            elif suffix == "toml":
                # FileNotFound & TomlDecodeError will be raised
                try:
                    config = toml.load(config_path)
                    return config

                except FileNotFoundError:
                    console.print(
                        f"FileNotFoundError: TOML file not found", style="bold red"
                    )
                    sys.exit(1)

                except toml.TomlDecodeError as exc:
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
    parser.add_argument("--show", help="show variables from config.toml")
    parser.add_argument("--path", help="add custom config.toml path")
    parser.add_argument(
        "--serialize", action="store_true", help="print the serialized config.toml"
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
