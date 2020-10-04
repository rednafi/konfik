import toml
import json
from rich.console import Console
from rich.syntax import Syntax
from rich import traceback
import subprocess
import shlex
from functools import reduce

# Pretty traceback with Rich
traceback.install()

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


class RecursiveDotMap:
    """Recursively applies DotMap object to a nested dictionary."""

    def __init__(self, dct, dotmap=DotMap):
        self.dct = dct
        self.dotmap = dotmap

    def dotmap_query(self, query):
        dct = self._dotmap_apply(self.dct, self.dotmap)
        return self._dotmap_query(dct, query)

    @staticmethod
    def _dotmap_apply(dct, dotmap):
        """Recursively applying DotMap class."""

        dct = dotmap(dct)
        for key, val in dct.items():
            if isinstance(val, dict) and not isinstance(val, dotmap):
                dct[key] = RecursiveDotMap._dotmap_apply(val, dotmap)
        return dct

    @staticmethod
    def _dotmap_query(dct, query):
        "Chained query of dotmap object."
        return reduce(getattr, query.split("."), dct)


class ConfigParser:
    def __init__(
        self,
        config_path,
        recursive_dotmap=RecursiveDotMap,
    ):
        self.config = self._load_config(config_path)
        self.recursive_dotmap = recursive_dotmap

    def serialize(self):
        """Serializing TOML config to JSON."""

        config_json = json.dumps(self.config, indent=2)
        syntax = Syntax(
            config_json,
            "json",
            background_color="default",
            theme="monokai",
        )
        console.print(syntax)

    def get(self, query):
        """Access vars or cmds."""

        # Raise path access error if config can't be accessed
        config = self.recursive_dotmap(self.config)
        return config.dotmap_query(query)

    def run(self, query):
        "Run cmd."
        self._run(self.get(query))

    @staticmethod
    def _load_config(config_path):
        """Load config.toml file."""

        # FileNotFound & TomlDecodeError will be raised
        config = toml.load(config_path)
        return config

    @staticmethod
    def _run(cmd):
        subprocess.check_call(shlex.split(cmd))


# TODO
# exceptions
# detect vars and cmds
from pathlib import Path

BASE_DIR = Path(".").parent
CONFIG_PATH = BASE_DIR / "config.toml"

config = ConfigParser(config_path=CONFIG_PATH)
config.serialize()
