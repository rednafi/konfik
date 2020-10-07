import pytest

from konfik.main import DeepDotMap, DotMap


def test_dotmap():
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
