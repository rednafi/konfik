import toml
import json
from rich.console import Console
from rich.syntax import Syntax
from rich import traceback
from glom import glom
import subprocess
import shlex


traceback.install()
console = Console()


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


def access(config, expr):
    """Access vars or cmds."""
    # Raise path access error if config can't be accessed
    return glom(config, expr)


def run_cmd(cmd):
    subprocess.check_call(shlex.split(cmd))


config = load_config("./config.toml")
serializer(config)
cmd = access(config, "bash.cmd.ech")


run_cmd(cmd)
