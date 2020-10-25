<div align="center">

<img src="https://user-images.githubusercontent.com/30027932/95400681-0a8b1f00-092d-11eb-9868-dfa8ff496565.png" alt="konfik-logo">

<strong>>> <i>The Strangely Familiar Config Parser</i> <<</strong>
<br></br>
![Codecov](https://img.shields.io/codecov/c/github/rednafi/konfik?color=pink&style=flat-square&logo=appveyor)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square&logo=appveyor)](https://github.com/python/black)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square&logo=appveyor)](./LICENSE)
<br></br>


**Konfik** is a simple configuration parser that helps you access your config variables using dot (.) notation.
This lets you to do this —

```python
foo_bar_bazz = config.FOO.BAR.BAZZ
```

— instead of this —

```python
foo_bar_bazz = config["FOO"]["BAR"]["BAZZ"]
```

Konfik currently supports **TOML**, **YAML**, **DOTENV** and **JSON** configuration formats.
</div>

## ⚙️ Installation

Install Konfik via pip:

```
pip install konfik
```


## 💡 Usage

Let's see how you can parse a TOML config file and access the variables there. For demonstration, we'll be using the following `config.toml` file:

```toml
# Contents of `config.toml`

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

To parse this in Python:

```python
from pathlib import Path
from konfik import Konfik

# Define the config path
BASE_DIR = Path(__file__).parent
CONFIG_PATH_TOML = BASE_DIR / "config.toml"

# Initialize the konfik class
konfik = Konfik(config_path=CONFIG_PATH_TOML)

# Print the config file as a Python dict
konfik.show_config()

# Get the config dict from the konfik class
config = konfik.config

# Access and print the variables
print(config.title)
print(config.owner)
print(config.owner.dob)
print(config.database.ports)
print(config.servers.alpha.ip)
print(config.clients)
```

The `.show_config()` method will print your entire config file as a colorized Python dictionary object like this:

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

Konfik also exposes a few command-line options for you to introspect your config file and variables. Run:

```
konfik --help
```

This will reveal the options associated with the CLI tool:

```
usage: konfik [-h] --path PATH [--show] [--show-literal] [--var VAR] [--version]

Konfik CLI

required arguments:
  --path PATH     add custom config file path

optional arguments:
  --show          print config as a dict
  --show-literal  print config file content literally
  --var VAR       print config variable
  --version       print konfik-cli version number
```

To inspect the value of a specific variable in a `config.toml` file you can run:

```
konfik --path=examples/config.env --var servers.alpha.ip
```

## 🎉 Contribution

* Clone the repo
* Spin up and activate your virtual environment. You can use anything between Python 3.6 to Python 3.9.
* Install [poetry](https://python-poetry.org/docs/#installation)
* Install the dependencies via:
    ```
    poetry install
    ```
* Make your changes to the `konfik/__init__.py` file

* Run the tests via the following command. Make sure you've Python 3.6 - Python 3.9 installed, otherwise **Tox** would throw an error.
    ```
    make test
    ```
* Write a simple unit test for your change
* Run the linter via:
    ```
    make linter
    ```
* Send a pull request against the master branch

<div align="center">
<i> 🍰 </i>
</div>
