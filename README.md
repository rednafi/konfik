<div align="center">

<img src="https://user-images.githubusercontent.com/30027932/95400681-0a8b1f00-092d-11eb-9868-dfa8ff496565.png" alt="konfik-logo">

<strong>>> <i>The Strangely Familiar Config Parser</i> <<</strong>

</div>

## Description

Konfik is a simple configuration parser that helps you access your TOML or DOTENV config variables using dot (.) notation. This enables you to do this —

```python
foo_bar_bazz = config.FOO.BAR.BAZZ
```

instead of this —

```python
foo_bar_bazz = config["FOO"]["BAR"]["BAZZ"]
```

## Installation

Install Konfik via pip:

```
pip install konfik
```


## Example

Let's see how you can parse a TOML config file and access the variables there. For demonstration, we'll be using the following `config.toml` file:

```toml
# example_config.toml

title = "TOML Example"

[owner]
name = "Tom Preston-Werner"
dob = 1979-05-27T07:32:00-08:00 # First class dates

[servers]
  [servers.alpha]
  ip = "10.0.0.1"
  dc = "eqdc10"

  [servers.beta]
  ip = "10.0.0.2"
  dc = "eqdc10"

[clients]
data = [ ["gamma", "delta"], [1, 2] ]
```

To parse this in Python

```python
from pathlib import Path
from konfik import Konfik

BASE_DIR = Path(".").parent

# Define the config paths
CONFIG_PATH_TOML = BASE_DIR / "example_config.toml"

# Initialize the Konfik class
konfik = Konfik(config_path=CONFIG_PATH_TOML)

# Serialize and print the config file
konfik.serialize()

# Access the serialized config object
config = konfik.config

# Use the serialized config object to acess the config variable via dot notation
title = config.title
name = config.owner.name
server_alpha_ip = config.servers.alpha.ip
clients = config.client
```

The `.serialize()` method will print your entire config file as a colorized Python dictionary object like this:

```python
{
    'title': 'TOML Example',
    'owner': {
        'name': 'Tom Preston-Werner',
        'dob': datetime.datetime(1979, 5, 27, 7, 32, tzinfo=<toml.tz.TomlTz object at
0x7f2dfca308b0>)
    },
    'database': {
        'server': '192.168.1.1',
        'ports': [8001, 8001, 8002],
        'connection_max': 5000,
        'enabled': True
    },
    'servers': {
        'alpha': {'ip': '10.0.0.1', 'dc': 'eqdc10'},
        'beta': {'ip': '10.0.0.2', 'dc': 'eqdc10'}
    },
    'clients': {'data': [['gamma', 'delta'], [1, 2]]}
}
```

Konfik also exposes a few command line options for you to instrospect you config file and variables. Run:

```
konfik --help
```

This will reveal the options associated with the CLI tool:

```
usage: konfik [-h] [--show SHOW] [--path PATH] [--serialize] [--version]

Konfik CLI

optional arguments:
  -h, --help   show this help message and exit
  --show SHOW  show variables from config.toml
  --path PATH  add custom config.toml path
  --serialize  print the serialized config.toml
  --version    print konfik-cli version number
```
