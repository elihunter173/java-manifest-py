# java-manifest-py

[![Build Status](https://travis-ci.com/elihunter173/java-manifest-py.svg?branch=master)](https://travis-ci.com/elihunter173/java-manifest-py)
[![PyPI version](https://badge.fury.io/py/java-manifest.svg)](https://badge.fury.io/py/java-manifest)

Encode/decode Java's `META-INF/MANIFEST.MF` in Python.

## Installation

To install the latest release on PyPI, run:

```sh
$ pip install java-manifest
```

## Usage

A manifest is represented by a list of dictionaries, where each dictionary
corresponds to an empty-line delimited section of the manifest and each
dictionary has `str` keys and `str` values.

`java_manifest.loads` takes a string containing manifest-formatted data and
returns a list of dictionaries, where each dictionary is a section in the
manifest. `java_manifest.load` does the same, using any `typing.TextIO`
readable object.

```python
>>> import java_manifest
>>> manifest_str = """
... Name: README-Example-1
... Long-Line: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
...  aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
...
... Name: README-Example-2
... Foo: Bar
... """
>>> manifest = java_manifest.loads(manifest_str)
>>> print(manifest)
[{'Name': 'README-Example-1', 'Long-Line': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}, {'Name': 'README-Example-2', 'Foo': 'Bar'}]

```

Similarly, `java_manifest.dumps` returns a string of manifest-formatted data
from a list of dictionaries, where each dictionary is a section in the
manifest. `java_manifest.dump` does the same, writing into any `typing.TextIO`
writable object.

```python
>>> import java_manifest
>>> manifest = [
...     {
...         "Name": "README-Example",
...         "Some-Str": "Some random string",
...     },
... ]
>>> manifest_str = java_manifest.dumps(manifest)
>>> print(manifest_str)
Name: README-Example
Some-Str: Some random string
<BLANKLINE>

```

There is also a `from_jar` function that finds the `META-INF/MANIFEST.MF` file
within the jar and `java_manifest.load`s that.

```python
>>> import java_manifest
>>> manifest = java_manifest.from_jar("test_files/simple.jar")

```

### Custom Encoders/Decoders

Because Java's manifest file format does not deal with structured/typed values,
specific uses of the format create ad-hoc encoding/decoding rules that convert
structured/typed data to and from a string so it can be stored in a manifest.
The `encoder` and `decoder` arguments for dumping and loading respectively are
responsible for handling this. An encoder and decoder both take in a key-value
pair. However, an encoder receives potentially structured/typed data as the
value and returns a string, while a decoder receives string values and returns
potentially structured/typed data.

As we have already see, the default encoder and decoder does no transformation
and prevents you from attempting to dump non-string data.

```python
>>> import java_manifest
>>> print(java_manifest.dumps([{"foo": "bar"}]))
foo: bar

>>> print(java_manifest.dumps([{"int": 1}]))
Traceback (most recent call last):
  ...
ValueError: key 'int' has type <class 'int'> value, expected str

```

You can however describe more custom encoders that support, for example, lists
of strings.

```python
>>> def encode(key, val):
...     if isinstance(val, list):
...         return ",".join(val)
...     return val
>>> print(java_manifest.dumps([{"foo": "bar", "names": ["alice", "bob", "charlie"]}], encoder=encode))
foo: bar
names: alice,bob,charlie
<BLANKLINE>

```

Similarly for custom decoders.

```python
>>> import java_manifest
>>> def decode(key, val):
...     # In reality you'd probably want to target only specific keys, to avoid
...     # messing up random strings containing commas. This is just an example.
...     vals = val.split(",")
...     if len(vals) == 1:
...         return val
...     else:
...         return vals
>>> manifest = java_manifest.loads("foo: bar\r\nnames: alice,bob,charlie", decoder=decode)
>>> print(manifest)
[{'foo': 'bar', 'names': ['alice', 'bob', 'charlie']}]

```
