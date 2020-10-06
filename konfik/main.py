import toml
import json
from rich.console import Console
from rich.syntax import Syntax
from rich import traceback

# from rich import print
import subprocess
import shlex
from functools import reduce
import sys
import argparse
from functools import reduce
import operator

# Pretty traceback with Rich
traceback.install(word_wrap=True)

# Rich console object for JSON highlighting
console = Console()


class DotMap(dict):
    """Modified dictionary object where the values can be accessed
    as dotdict.key instead of dct[key]
    """

    def __getattr__(self, attr):
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
        """Serializing TOML config to JSON."""

        config_json = json.dumps(self._config, indent=2)
        syntax = Syntax(
            config_json,
            "json",
            background_color="default",
            theme="monokai",
        )
        console.print(syntax)

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

    # @staticmethod
    # def _run(cmd):
    #     subprocess.check_call(shlex.split(cmd))


class KonfikCLI:
    def __init__(self, konfik):
        parser = argparse.ArgumentParser(description="Konfik CLI")
        parser.add_argument("--get", help="Get variables from config.toml")
        self.query = parser.parse_args().get
        self.konfik = konfik

    def get(self):
        if self.query is not None:
            query = self.query.split(".")
        return self.get_by_path(self.konfik.config, query)

    @staticmethod
    def get_by_path(root, items):
        """Access a nested object in root by item sequence."""
        return reduce(operator.getitem, items, root)


# konfik = Konfik("./config.toml")
# konfik_cli = KonfikCLI(konfik)
# print(konfik_cli.get())


# # TODO
#
# #
