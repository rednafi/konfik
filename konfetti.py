import toml
import json
from rich.console import Console
from rich.syntax import Syntax
from rich import traceback

traceback.install()
console = Console()


def load_config(config_path):
    # FileNotFound & TomlDecodeError will be raised
    config = toml.load(config_path)
    return config


def serializer(config):
    config_json = json.dumps(config, indent=2)
    syntax = Syntax(
        config_json,
        "json",
        background_color="default",
        theme="monokai",
    )
    console.print(syntax)


config = load_config("./config.toml")
serializer(config)
