from argparse import Namespace

import pytest

from konfik import DotMap, Konfik, KonfikCLI, MissingConfigError, MissingVariableError


@pytest.fixture
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


def make_config_path(tmp_path, config_str, config_ext):
    # Making a temporary directory to hold the config file
    # https://docs.pytest.org/en/stable/tmpdir.html#the-tmp-path-fixture
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir()

    # So the actual directory would be tmp_path/sub/test_config.extension
    test_config_path = tmp_dir / f"test_config.{config_ext}"
    test_config_path.write_text(config_str)
    return test_config_path


def test_dotmap(config_dict):
    """Test the DotMap class."""

    # Test dot notation features
    d = DotMap(config_dict)

    # Test iteration
    for (k1, v1), (k2, v2) in zip(d.items(), config_dict.items()):
        assert k1 == k2
        assert v1 == v2

    # Test pop
    d.pop("title")
    assert "title" not in d.keys()
    d.title = "TOML Example"

    # Test len
    len(d) == len(config_dict)

    # Check if d is an instance of DotMap object
    assert isinstance(d, DotMap) is True

    # Check if nested dictionary instance is also DotMap
    assert isinstance(d["database"], DotMap) is True

    # Check if the dot notation key access works
    assert d.title == "TOML Example"
    assert d.owner.name == "Tom Preston-Werner"
    assert d.owner.dob == "1979-05-27"

    assert isinstance(d.database, DotMap) is True
    assert d.database == {
        "server": "192.168.1.1",
        "ports": [8001, 8001, 8002],
        "connection_max": 5000,
        "enabled": True,
    }
    assert d.database.server == "192.168.1.1"
    assert d.database.ports == [8001, 8001, 8002]
    assert d.database.enabled is True

    assert isinstance(d.servers, DotMap) is True
    assert d.servers == {
        "alpha": {"ip": "10.0.0.1", "dc": "eqdc10"},
        "beta": {"ip": "10.0.0.2", "dc": "eqdc10"},
    }

    assert isinstance(d.servers.alpha, DotMap) is True
    assert d.servers.alpha == {"ip": "10.0.0.1", "dc": "eqdc10"}

    assert d.servers.alpha.ip == "10.0.0.1"
    assert d.servers.alpha.dc == "eqdc10"

    # Check if dot notation assignment works
    d.title = "Test Environ"
    assert d.title == "Test Environ"

    d.owner = "Redowan Delowar"
    assert d.owner == "Redowan Delowar"

    d.database = {"servers": "localhost", "ports": [5000, 5001, 5002]}

    assert isinstance(d.database, DotMap) is True

    d.servers.beta.ip = "localhost"
    assert d.servers.beta.ip == "localhost"

    # Check if dot notation deletion works
    del d.title
    with pytest.raises(MissingVariableError):
        d.title

    # Normal [] notation features
    d = config_dict
    d = DotMap(d)

    # Check if the angle notation key access works
    assert d["title"] == "TOML Example"
    assert d["owner"]["name"] == "Tom Preston-Werner"
    assert d["owner"]["dob"] == "1979-05-27"

    assert isinstance(d["database"], DotMap) is True
    assert d["database"] == {
        "server": "192.168.1.1",
        "ports": [8001, 8001, 8002],
        "connection_max": 5000,
        "enabled": True,
    }
    assert d["database"]["server"] == "192.168.1.1"
    assert d["database"]["ports"] == [8001, 8001, 8002]
    assert d["database"]["enabled"] is True

    assert isinstance(d["servers"], DotMap) is True
    assert d["servers"] == {
        "alpha": {"ip": "10.0.0.1", "dc": "eqdc10"},
        "beta": {"ip": "10.0.0.2", "dc": "eqdc10"},
    }

    assert isinstance(d["servers"]["alpha"], DotMap) is True
    assert d["servers"]["alpha"] == {"ip": "10.0.0.1", "dc": "eqdc10"}

    assert d["servers"]["alpha"]["ip"] == "10.0.0.1"
    assert d["servers"]["alpha"]["dc"] == "eqdc10"

    # Check if angle notation assignment works
    d["title"] = "Test Environ"
    assert d["title"] == "Test Environ"

    d["owner"] = "Redowan Delowar"
    assert d["owner"] == "Redowan Delowar"

    d["database"] = {"servers": "localhost", "ports": [5000, 5001, 5002]}

    assert isinstance(d["database"], DotMap) is True

    d["servers"]["beta"]["ip"] = "localhost"
    assert d["servers"]["beta"]["ip"] == "localhost"

    # Check if angle notation deletion works
    del d["title"]
    with pytest.raises(MissingVariableError):
        d["title"]

    # Check if popitem works
    d.popitem()
    assert len(d) < len(config_dict)

    # Check if clear works
    assert d.clear() is None

    # Test _convert
    m = {
        "i": {
            "j": [
                {"1": 1},
                {"2": 2},
            ],
            "k": (
                {1: 1},
                {2: 2},
            ),
        }
    }

    m = DotMap._convert(m)
    assert isinstance(m.i, DotMap) is True
    assert isinstance(m.i.j[0], DotMap) is True
    assert isinstance(m.i.k[1], DotMap) is True


def test_konfik(tmp_path):
    """Unit test different parts of the Konfik class."""

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
    test_toml_real_path = make_config_path(tmp_path, toml_str, "toml")
    test_toml_fake_path = "some/fake/path/config.toml"

    # Test if konfik raises MissingConfigError when the config is missing
    with pytest.raises(MissingConfigError):
        konfik = Konfik(config_path=test_toml_fake_path)

    konfik = Konfik(config_path=test_toml_real_path)

    # Test if a nested key can be resolved by get_by_path (used in the CLI)
    assert konfik.get_by_path({"hello": {"world": 2}}, ["hello", "world"]) == 2

    # Test if konfik can find the file path
    assert konfik._config_path == test_toml_real_path

    # Check raw config type
    assert isinstance(konfik._config_raw, dict) is True

    # Check transformed config type
    assert isinstance(konfik.config, DotMap)

    # Test if konfik can parse file extension from path
    assert konfik._config_ext == "toml"


def test_konfik_toml(tmp_path, capfd):
    """Test the Konfik class for toml."""

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
    test_toml_path = make_config_path(tmp_path, toml_str, "toml")

    # Load toml from the test toml path
    konfik = Konfik(config_path=test_toml_path)

    # Make sure show_config works
    konfik.show_config()

    # Make sure show_config_literal works
    konfik.show_config_literal()

    # Make sure show_var works
    konfik.show_config_var("title")
    out, _ = capfd.readouterr()
    assert "TOML Example" in out

    # Test variable access with dot notation
    config = konfik.config

    assert config.title == "TOML Example"
    assert config.owner.name == "Tom Preston-Werner"
    assert config.database == {
        "server": "192.168.1.1",
        "ports": [8001, 8001, 8002],
        "connection_max": 5000,
        "enabled": True,
    }
    assert config.database.server == "192.168.1.1"
    assert config.database.ports == [8001, 8001, 8002]
    assert config.database.connection_max == 5000
    assert config.database.enabled is True

    assert config.servers.alpha == {"ip": "10.0.0.1", "dc": "eqdc10"}
    assert config.servers.beta.dc == "eqdc10"

    assert config.clients.data == [["gamma", "delta"], [1, 2]]


def test_konfik_env(tmp_path):
    """Test the Konfik class for dotenv file."""

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

    test_env_path = make_config_path(tmp_path, dotenv_str, "env")

    # Load toml from the test toml path
    konfik = Konfik(config_path=test_env_path)

    # Make sure the serializer works
    konfik.show_config()

    # Test variable access with dot notation
    config = konfik.config

    assert config.TITLE == "DOTENV_EXAMPLE"
    assert config.NAME == "TOM"
    assert config.DOB == "1994-03-24T07:32:00-08:00"
    assert config.SERVER == "192.168.1.1"
    assert config.PORT == "8001"
    assert config.CONNECTION_MAX == "5000"
    assert config.ENABLED == "True"
    assert config.IP == "10.0.0.1"
    assert config.DC == "eqdc10"


def test_konfik_json(tmp_path, capfd):
    """Test the Konfik class for json."""

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
    test_json_path = make_config_path(tmp_path, json_str, "json")

    # Load toml from the test toml path
    konfik = Konfik(config_path=test_json_path)

    # Make sure show_config works
    konfik.show_config()

    # Make sure show_config_literal works
    konfik.show_config_literal()

    # Make sure show_var works
    konfik.show_config_var("title")
    out, _ = capfd.readouterr()
    assert "JSON Example" in out

    # Test variable access with dot notation
    config = konfik.config

    assert config.title == "JSON Example"
    assert config.owner.name == "Tom Preston-Werner"
    assert config.database == {
        "server": "192.168.1.1",
        "ports": [8001, 8001, 8002],
        "connection_max": 5000,
        "enabled": True,
    }
    assert config.database.server == "192.168.1.1"
    assert config.database.ports == [8001, 8001, 8002]
    assert config.database.connection_max == 5000
    assert config.database.enabled is True

    assert config.servers.alpha == {"ip": "10.0.0.1", "dc": "eqdc10"}
    assert config.servers.beta.dc == "eqdc10"

    assert config.clients.data == [["gamma", "delta"], [1, 2]]


def test_konfik_yaml(tmp_path, capfd):
    """Test the Konfik class for yaml."""

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
    test_yaml_path = make_config_path(tmp_path, yaml_str, "yaml")

    konfik = Konfik(config_path=test_yaml_path)

    # Make sure show_config works
    konfik.show_config()

    # Make sure show_config_literal works
    konfik.show_config_literal()

    # Make sure show_var works
    konfik.show_config_var("title")
    out, _ = capfd.readouterr()
    assert "YAML Example" in out

    # Test variable access with dot notation
    config = konfik.config
    assert config.title == "YAML Example"
    assert config.owner.name == "Tom Preston-Werner"
    assert config.database == {
        "server": "192.168.1.1",
        "ports": [8001, 8001, 8002],
        "connection_max": 5000,
        "enabled": True,
    }
    assert config.database.server == "192.168.1.1"
    assert config.database.ports == [8001, 8001, 8002]
    assert config.database.connection_max == 5000
    assert config.database.enabled is True

    assert config.servers.alpha == {"ip": "10.0.0.1", "dc": "eqdc10"}
    assert config.servers.beta.dc == "eqdc10"

    assert config.clients.data == [["gamma", "delta"], [1, 2]]


def test_argument_parser(capsys):

    captured = capsys.readouterr()
    result = captured.out
    print(result)


def test_konfik_cli(tmp_path, capfd):
    """Test the KonfikCLI class for toml."""

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
    test_toml_path = make_config_path(tmp_path, toml_str, "toml")

    # Load toml from the test toml path
    konfik = Konfik(config_path=test_toml_path)

    konfik_cli = KonfikCLI(
        konfik=konfik,
        args=Namespace(path=test_toml_path, show=True, show_literal=False, var=False, version=False),
    )

    konfik_cli.konfik.show_config()

    konfik_cli = KonfikCLI(
        konfik=konfik,
        args=Namespace(path=test_toml_path, show=None, version=True),
    )

    konfik_cli._version("5.5.5")
    out, _ = capfd.readouterr()
    assert "title" in out
    assert "owner" in out
    assert "client" in out
    assert "database" in out

    assert "5.5" in out
