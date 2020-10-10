import pytest

from konfik.main import DeepDotMap, DotMap, Konfik


def test_dotmap():
    """Test the DotMap class."""

    # Test dot notation features
    d = {
        "j": {
            "k": {
                "l": 1,
            },
        },
    }

    d = DotMap(d)

    # Check if d is an instance of DotMap object
    assert isinstance(d, DotMap) is True

    # Check if the dot notation key access works
    assert d.j == {"k": {"l": 1}}

    # Check if dot notation assignment works
    d.j = {"m": 2}
    assert d.j == {"m": 2}

    # Check if dot notation deletion works
    del d.j
    with pytest.raises(KeyError):
        d.j

    # Normal [] notation features
    d = {
        "j": {
            "k": {
                "l": 1,
            },
        },
    }
    d = DotMap(d)

    # Check if [] notation key access works
    assert d["j"] == {"k": {"l": 1}}

    # Check if [] notation assignment works
    d["j"] = {"m": 2}
    assert d["j"] == {"m": 2}

    # Check if [] notation deletion works
    del d["j"]
    with pytest.raises(KeyError):
        d["j"]


def test_deep_dotmap():
    """Test the DeepDotMap class that recursively applies the DotMap class."""

    # Test dot notation features
    d = {
        "j": {
            "k": {
                "l": 1,
            },
        },
    }

    d = DeepDotMap(d)()

    # DeepDotMap object is still an instance of the original DotMap object
    assert isinstance(d, DotMap) is True

    # Check if nested objects are also instances of DotMap object
    assert isinstance(d.j, DotMap) is True
    assert isinstance(d.j.k, DotMap) is True

    # Check if the chained dot notation key access works
    assert d.j == {"k": {"l": 1}}
    assert d.j.k == {"l": 1}
    assert d.j.k.l == 1

    # Check if dot notation assignment works
    d.j = DeepDotMap({"m": 2})()
    assert d.j == DeepDotMap({"m": 2})()

    d.j.m = 2
    assert d.j.m == 2

    # Check if dot notation deletion works
    del d.j.m
    with pytest.raises(KeyError):
        d.j.m

    # Normal [] notation features
    d = {
        "j": {
            "k": {
                "l": 1,
            },
        },
    }
    d = DeepDotMap(d)()

    # Check if [] notation key access works
    assert d["j"] == {"k": {"l": 1}}
    assert d["j"]["k"] == {"l": 1}
    assert d["j"]["k"]["l"] == 1

    # Check if [] notation assignment works
    d["j"] = {"m": 2}
    assert d["j"]["m"] == 2

    # Check if [] notation deletion works
    del d["j"]["m"]
    with pytest.raises(KeyError):
        d["j"]["m"]


def test_konfik_toml(tmp_path):
    """Test the Konfik class for toml."""

    toml_string = """
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
    # Making a temporary directory to hold the toml file
    # https://docs.pytest.org/en/stable/tmpdir.html#the-tmp-path-fixture
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir()

    # So the actual directory would be tmp_path/sub/test_config.toml
    test_toml_path = tmp_dir / "test_config.toml"
    test_toml_path.write_text(toml_string)

    # Load toml from the test toml path
    konfik = Konfik(config_path=test_toml_path)

    # Make sure the serializer works
    konfik.serialize()

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

    env_string = """
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
    # Making a temporary directory to hold the env file
    # https://docs.pytest.org/en/stable/tmpdir.html#the-tmp-path-fixture
    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir()

    # So the actual directory would be tmp_path/sub/test_config.toml
    test_env_path = tmp_dir / "test_config.env"
    test_env_path.write_text(env_string)

    # Load toml from the test toml path
    konfik = Konfik(config_path=test_env_path)

    # Make sure the serializer works
    konfik.serialize()

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
