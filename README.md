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
from konfik import Konfik

# Define the config path
CONFIG_PATH_TOML = "config.toml"

# Initialize the konfik class
konfik = Konfik(config_path=CONFIG_PATH_TOML)

# Serialize and print the confile file
konfik.serialize()

# Get the configuration dictionary from the konfik class
config_toml = konfik.config

# Access and print the variables
title = config_toml.title
owner = config_toml.owner
dob = config_toml.owner.dob
database = config_toml.database.ports
server_ip = config_toml.servers.alpha.ip
clients = config_toml.clients
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

Konfik also exposes a few command-line options for you to introspect your config file and variables. Run:

```
konfik --help
```

This will reveal the options associated with the CLI tool:

```
usage: konfik [-h] [--show SHOW] [--path PATH] [--serialize] [--version]

Konfik CLI

optional arguments:
  -h, --help   show this help message and exit
  --show SHOW  show variables from config file
  --path PATH  add custom config file path
  --serialize  print the serialized config file
  --version    print konfik-cli version number
```

To inspect the value of a specific variable in a `config.toml` file you can run:

```
konfik --show servers.alpha.ip
```

If you're using a config that's not named as `config.toml` then you can deliver the path using the `--path` argument like this:

```
konfik --path examples/config.env --show name
```

## 🙋 Why

While working with machine learning models, I wanted an easier way to tune the model parameters without mutating the Python files. I needed something that would simply enable me to access tuple or dictionary data structures from a config file. I couldn't find anything that doesn't try to do a gazillion of other kinds of stuff or doesn't come with the overhead of a significant learning curve.

Neither DOTENV nor YAML catered to my need as I was after something that gives me the ability to store complex data structures without a lot of fuss — so TOML it is. However, Konfik also supports DOTENV, JSON and YAML. Moreover, not having to write angle brackets —`["key"]` — to access dictionary values is nice!

## 🎉 Contribution

* Clone the repo
* Spin up and activate your virtual environment. You can use anything between Python 3.6 to Python 3.9.
* Install [poetry](https://python-poetry.org/docs/#installation)
* Install the dependencies via:
    ```
    poetry install
    ```
* Make your changes to the `konfik/main.py` file

* Run the tests via the following command. Make sure you've Python 3.6 - Python 3.9 installed, otherwise **Tox** would throw an error.
    ```
    make test
    ```
* Write a simple unit test for your change
* Run the linter via:
    ```
    make linter
    ```

<div align="center">
<i> ⚡⚡ </i>
</div>
