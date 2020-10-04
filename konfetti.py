import toml
import json
from rich.console import Console
from rich.syntax import Syntax
from rich import traceback
import subprocess
import shlex
from functools import reduce


traceback.install()
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


def load_config(config_path):
    """Load config.toml file."""
    # FileNotFound & TomlDecodeError will be raised
    config = toml.load(config_path)
    return config


def serializer(config):
    """Serializing TOML config to JSON."""
    config_json = json.dumps(config, indent=2)
    syntax = Syntax(
        config_json,
        "json",
        background_color="default",
        theme="monokai",
    )
    console.print(syntax)


def access(config, query):
    """Access vars or cmds."""
    # Raise path access error if config can't be accessed
    config = RecursiveDotMap(config)
    return config.dotmap_query(query)
    
def run_cmd(cmd):
    subprocess.check_call(shlex.split(cmd))


# TODO
# exceptions
# detect vars and cmds

config = load_config("./config.toml")
serializer(config)

print(access(config, "bash.cmd.echo"))
# cmd = access(config, "bash.cmd.ech")
