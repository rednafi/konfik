import pytest

@pytest.fixture()
def config_dict():
    """Sample config dict."""

    d = {
        "title": "TOML Example",
        "owner": {
            "name": "Tom Preston-Werner",
            "dob": "1979-05-27",
        },
        "database": {
            "server": "192.168.1.1",
            "ports": [8001, 8001, 8002],
            "connection_max": 5000,
            "enabled": True,
        },
        "servers": {
            "alpha": {"ip": "10.0.0.1", "dc": "eqdc10"},
            "beta": {"ip": "10.0.0.2", "dc": "eqdc10"},
        },
        "clients": {
            "data": [["gamma", "delta"], [1, 2]],
        },
    }
    return d


@pytest.fixture
def toml_str():
    toml_str = """
    # This is a TOML document.

    title = "TOML Example"

    [owner]
    name = "Tom Preston-Werner"
    dob = 1979-05-27T07:32:00-08:00

    [database]
    server = "192.168.1.1"
    ports = [ 8001, 8001, 8002 ]
    connection_max = 5000
    enabled = true

    [servers]
    [servers.alpha]
    ip = "10.0.0.1"
    dc = "eqdc10"

    [servers.beta]
    ip = "10.0.0.2"
    dc = "eqdc10"

    [clients]
    data = [ ["gamma", "delta"], [1, 2] ]
    """

    return toml_str

@pytest.fixture
def dotenv_str():
    dotenv_str = """
    # This is an example .env document

    TITLE            = DOTENV_EXAMPLE
    NAME             = TOM
    DOB              = 1994-03-24T07:32:00-08:00
    SERVER           = 192.168.1.1
    PORT             = 8001
    CONNECTION_MAX   = 5000
    ENABLED          = True
    IP               = 10.0.0.1
    DC               = eqdc10

    """
    return dotenv_str


@pytest.fixture
def json_str():
    json_str = """
        {
        "title": "JSON Example",
        "owner": {
            "name": "Tom Preston-Werner",
            "dob": "1979-05-27"
        },
        "database": {
            "server": "192.168.1.1",
            "ports": [
                8001,
                8001,
                8002
            ],
            "connection_max": 5000,
            "enabled": true
        },
        "servers": {
            "alpha": {
                "ip": "10.0.0.1",
                "dc": "eqdc10"
            },
            "beta": {
                "ip": "10.0.0.2",
                "dc": "eqdc10"
            }
        },
        "clients": {
            "data": [
                [
                    "gamma",
                    "delta"
                ],
                [
                    1,
                    2
                ]
            ]
        }
    }
    """
    return json_str

@pytest.fixture
def yaml_str():

    yaml_str = """
title: YAML Example
owner:
  name: Tom Preston-Werner
  dob: 1979-05-27T15:32:00.000Z
database:
  server: 192.168.1.1
  ports:
    - 8001
    - 8001
    - 8002
  connection_max: 5000
  enabled: true
servers:
  alpha:
    ip: 10.0.0.1
    dc: eqdc10
  beta:
    ip: 10.0.0.2
    dc: eqdc10
clients:
  data:
    - - gamma
      - delta
    - - 1
      - 2
"""
    return yaml_str
