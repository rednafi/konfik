import argparse
import operator
import sys
from functools import reduce

import toml
from rich import traceback
from rich.console import Console

# Pretty traceback with Rich
traceback.install(word_wrap=True)

# Rich console object for JSON highlighting
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
        config_path,
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

        # FileNotFound & TomlDecodeError will be raised
        try:
            config = toml.load(config_path)
            return config

        except toml.TomlDecodeError as exc:
            console.print(f"\nTomlDecodeError: {exc}\n", style="bold red")
            sys.exit(1)


class KonfikCLI:
    """Access and show config variables using CLI."""

    def __init__(self, konfik, args):
        self.konfik = konfik
        self.args = args

    def _get(self):
        if isinstance(self.args.get, str):
            query = self.args.get.split(".")
            return self.get_by_path(self.konfik.config, query)

    def _show(self):
        if isinstance(self.args.show, str):
            query = self.args.show.split(".")
            console.print(self.get_by_path(self.konfik.config, query))

    def _serialize(self):
        self.konfik.serialize()

    def run_cli(self):
        if self.args.get is not None:
            self._get()
        elif self.args.show is not None:
            self._show()
        elif self.args.serialize is True:
            self._serialize()

    @staticmethod
    def get_by_path(root, items):
        """Access a nested object in root by item sequence."""
        return reduce(operator.getitem, items, root)


def deploy_cli():
    parser = argparse.ArgumentParser(description="Konfik CLI")
    parser.add_argument("--get", help="get variables from config.toml")
    parser.add_argument("--show", help="show variables from config.toml")
    parser.add_argument(
        "--serialize", action="store_true", help="print the serialized config.toml"
    )
    args = parser.parse_args()

    if args.get or args.show or args.serialize:
        konfik = Konfik("./config.toml")
        konfik_cli = KonfikCLI(konfik, args)
        konfik_cli.run_cli()
