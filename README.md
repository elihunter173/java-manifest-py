# java-manifest-py

[![Build Status](https://travis-ci.com/elihunter173/java-manifest-py.svg?branch=master)](https://travis-ci.com/elihunter173/java-manifest-py)

Encode/decode Java's `META-INF/MANIFEST.MF` in Python.

## Installation

To install the latest release on PyPI, run:

```sh
$ pip install java-manifest
```

## Usage

A MANIFEST is represented by a list of dictionaries, where each dictionary
corresponds to an empty-line delimited section of the MANIFEST and each
dictionary has `str` keys and either `str` or `bool` values.

`java_manifest.loads` takes a string containing MANIFEST-formatted data and
returns a list of dictionaries, where each dictionary is a section in the
MANIFEST. `java_manifest.load` does the same, using any `typing.TextIO`
readable object.

```python
>>> import java_manifest
>>> manifest_str = """
... Name: README-Example-1
... Boolean: true
... Long-Line: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
...  aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
...
... Name: README-Example-2
... Boolean: false
... Not-Boolean: False
... """
>>> manifest = java_manifest.loads(manifest_str)
>>> print(parsed_manifest)
[{'Name': 'README-Example-1', 'Boolean': True, 'Long-Line': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}, {'Name': 'README-Example-2', 'Boolean': False, 'Not-Boolean': 'False'}]
```

Similarly, `java_manifest.dumps` returns a string of MANIFEST-formatted data
from a list of dictionaries, where each dictionary is a section in the
MANIFEST. `java_manifest.dump` does the same, writing into any `typing.TextIO`
writable object.

```python
>>> import java_manifest
>>> manifest = [
...     {
...         "Name": "README-Example",
...         "Some-Str": "Some random string",
...         "Some-Bool": True,
...     },
... ]
>>> manifest_str = java_manifest.dumps(manifest)
>>> print(manifest_str)
Name: README-Example
Some-Str: Some random string
Some-Bool: true

```

There is also a `from_jar` function that finds the `META-INF/MANIFEST.MF` file
within the jar and `java_manifest.load`s that.

```python
>>> import java_manifest
>>> manifest = java_manifest.from_jar("/path/to/jarfile.jar")
```
