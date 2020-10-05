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


class DeepDotMap(DotMap):
    """Recursively applies DotMap object to a nested dictionary."""

    def __init__(self, dct):
        super().__init__(dct)

    def __call__(self):
        return self._dotmap_apply(self, self.__class__)

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
        config = toml.load(config_path)
        return config

    # @staticmethod
    # def _run(cmd):
    #     subprocess.check_call(shlex.split(cmd))


# # TODO
# # exceptions
# # detect vars and cmds
from pathlib import Path

BASE_DIR = Path(".").parent
CONFIG_PATH = BASE_DIR / "config.toml"

konfik = Konfik(config_path=CONFIG_PATH)
print(konfik.config.bash.var.A)
print(konfik.config.bash.cmd.ECHO)

#config.run('bash.cmd.')
