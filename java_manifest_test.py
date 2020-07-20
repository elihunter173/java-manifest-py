# flake8: noqa

import textwrap
from pathlib import Path

import pytest

import java_manifest

TEST_FILES = Path(__file__).parent / "test_files"


def load(s, **kwargs):
    """Short java_manifest.loads which cleans up multi-line strings"""
    return java_manifest.loads(textwrap.dedent(s).strip(), **kwargs)


def test_empty():
    data = load("")
    assert data == []


def test_string():
    data = load("key: value")
    assert data == [{"key": "value"}]


def test_bool():
    data = load(
        """
        true: true
        false: false
        """
    )
    assert data == [{"true": "true", "false": "false"}]


def test_int():
    data = load("num: 1")
    assert data == [{"num": "1"}]


def test_multiple_sections():
    data = load(
        """
        a: b

        c: d
        """
    )
    assert data == [{"a": "b"}, {"c": "d"}]


def test_trailing_newline():
    data = java_manifest.loads("foo: bar\n\n\n\n")
    assert data == [{"foo": "bar"}]


def test_initial_newline():
    data = java_manifest.loads("\n\n\n\nfoo: bar")
    assert data == [{"foo": "bar"}]


def test_duplicate_keys():
    with pytest.raises(KeyError):
        java_manifest.loads("foo: a\nfoo: b")


def test_simple_file():
    with open(TEST_FILES / "simple" / "META-INF" / "MANIFEST.MF") as f:
        data = java_manifest.load(f)
    assert data == [
        {"id": "1", "foo": "bar", "true": "true"},
        {"id": "2", "foo": "bar", "true": "true"},
    ]


def test_simple_jar():
    data = java_manifest.from_jar(TEST_FILES / "simple.jar")
    assert data == [
        {"id": "1", "foo": "bar", "true": "true"},
        {"id": "2", "foo": "bar", "true": "true"},
    ]


def test_repeated():
    original = [{"a": "b"}, {"c": "d"}]
    repeated = java_manifest.loads(java_manifest.dumps(original))
    assert repeated == original


def test_dump_bad_keys():
    with pytest.raises(ValueError):
        java_manifest.dumps([{0: 0}])


def test_dump_str():
    s = java_manifest.dumps([{"foo": "bar"}])
    assert s == "foo: bar\r\n"


def test_dump_bool():
    with pytest.raises(ValueError):
        java_manifest.dumps([{"true": True, "false": False}])


def test_dump_int():
    with pytest.raises(ValueError):
        java_manifest.dumps([{"int": 1}])


def test_dump_multiple_sections():
    s = java_manifest.dumps([{"a": "b"}, {"c": "d"}])
    assert s == "a: b\r\n\r\nc: d\r\n"


def test_dump_long_line():
    s = java_manifest.dumps(
        [{"test": "a" * (java_manifest.LINE_LEN * 2 - len("test: ") - len(" "))}]
    )
    assert (
        s
        == "test: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\r\n aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\r\n"
    )


def example_decoder(k, v):
    if v == "true":
        return True
    if v == "false":
        return False
    try:
        return int(v)
    except ValueError:
        pass
    return v


def test_decoder():
    data = load(
        """
        foo: bar
        true: true
        false: false
        int: 1
        """,
        decoder=example_decoder,
    )
    assert data == [{"foo": "bar", "true": True, "false": False, "int": 1}]


def example_encoder(k, v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    return v


def test_encoder():
    s = java_manifest.dumps(
        [{"foo": "bar", "true": True, "false": False, "int": 1}],
        encoder=example_encoder,
    )
    assert s == "foo: bar\r\ntrue: true\r\nfalse: false\r\nint: 1\r\n"
