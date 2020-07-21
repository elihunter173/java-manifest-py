"""Dependency-free parser of Java's MANIFEST.MF file.

All of these functions are overloaded to allow for generic `Encoder`s and
`Decoder`s. Once https://github.com/python/mypy/issues/3737 lands, we should no
longer have to overload things because the default value should be accepted.

Released under the MIT license.
"""

import os
from io import StringIO, TextIOWrapper
from typing import (
    IO,
    BinaryIO,
    Callable,
    Dict,
    List,
    TextIO,
    TypeVar,
    Union,
    cast,
    overload,
)
from zipfile import ZipFile

__version__ = "1.0.0"

T = TypeVar("T")

Section = Dict[str, T]
"""Single block of key-values pairs in a Manifest"""

Manifest = List[Section[T]]
"""List of Sections, delimited by empty lines"""

Decoder = Callable[[str, str], T]
"""Gives the `T` value from some-key value pair from a raw manifest.

This function is given the raw `str` from a Manifest to convert into more
useful values.

Note: This must return useful values in all cases.
"""

Encoder = Callable[[str, T], str]
"""Gives the `str` value for some key-value pair from a dict.

This `str` encoded type `T` is then written into the Manifest.

Note: This must return useful values in all cases.
"""


LINE_CONT = " "
LINE_END = "\r\n"
LINE_LEN = 70


def default_decoder(key: str, val: str) -> str:
    return val


def default_encoder(key: str, val: str) -> str:
    if not isinstance(val, str):
        raise ValueError(f"key '{key}' has type {type(val)} value, expected str")
    return val


@overload
def loads(s: str) -> Manifest[str]:
    ...


@overload
def loads(s: str, *, decoder: Decoder[T]) -> Manifest[T]:
    ...


def loads(s, *, decoder=default_decoder):
    """Parse MANIFEST data from string.

    Args:
        s: String to parse.

    Return:
        Manifest parsed from `s`.
    """
    return load(StringIO(s), decoder=decoder)


@overload
def load(fp: TextIO) -> Manifest[str]:
    ...


@overload
def load(fp: TextIO, *, decoder: Decoder[T]) -> Manifest[T]:
    ...


def load(fp, *, decoder=default_decoder):
    """Parse MANIFEST data from the readable file-like object.

    Args:
        fp: Readable file-like object containing MANIFEST data to parse.

    Return:
        Manifest parsed from `fp`.
    """
    sections = []

    sect: Section = {}
    key, val = None, None
    for lnum, line in enumerate(fp.readlines(), 1):
        line = line.rstrip(LINE_END)
        if line.startswith(LINE_CONT):
            # Continuation line
            if val is None:
                raise ValueError(
                    f"line {lnum}: continuation line not continuing anything"
                )
            val.write(line[1:])

        else:
            # Finish off the key value pair
            if key and val:
                sect[key] = decoder(key, val.getvalue())
                key, val = None, None

            if line:
                # Normal line
                key, val_str = line.split(":", maxsplit=1)
                if key in sect:
                    raise KeyError(f"line {lnum}: duplicate key '{key}'")
                val = StringIO(newline=LINE_END)
                val.write(val_str.lstrip())
            elif sect:
                # Empty line, new section, finish off the old section
                sections.append(sect)
                sect = {}

    if key and val:
        if key in sect:
            raise KeyError(f"line {lnum}: duplicate key '{key}'")
        sect[key] = decoder(key, val.getvalue())
        key, val = None, None
    if sect:
        sections.append(sect)
        sect = {}

    return sections


@overload
def from_jar(jarfile: Union["os.PathLike[str]", IO[bytes]]) -> Manifest[str]:
    ...


@overload
def from_jar(
    jarfile: Union["os.PathLike[str]", IO[bytes]], *, decoder: Decoder[T]
) -> Manifest[T]:
    ...


def from_jar(jarfile, *, decoder=default_decoder):
    """Parse META-INF/MANIFEST.MF from jarfile

    Args:
        jarfile: Path to jar to parse or already opened jarfile.

    Return:
        Manifest parsed from META-INF/MANIFEST.MF inside of `jarfile`.
    """
    with ZipFile(jarfile) as zf:
        with TextIOWrapper(
            # IO[bytes] is BinaryIO
            cast(BinaryIO, zf.open("META-INF/MANIFEST.MF")),
            encoding="utf-8",
        ) as manifest:
            return load(manifest, decoder=decoder)


@overload
def dumps(obj: Manifest[str]) -> str:
    ...


@overload
def dumps(obj: Manifest[T], *, encoder: Encoder[T]) -> str:
    ...


def dumps(obj, *, encoder=default_encoder):
    """Return MANIFEST string from manifest object.

    Args:
        manifest: Manifest to convert to a MANIFEST formatted string.

    Return:
        MANIFEST formatted string from `manifest`.
    """
    buf = StringIO()
    dump(obj, buf, encoder=encoder)
    return buf.getvalue()


@overload
def dump(manifest: Manifest[str], fp: TextIO) -> None:
    ...


@overload
def dump(manifest: Manifest[T], fp: TextIO, *, encoder: Encoder[T]) -> None:
    ...


def dump(manifest, fp, *, encoder=default_encoder):
    """Write manifest into writable file-like object.

    Args:
        manifest: Manifest to write into `fp`.
        fp: Writable file-like object receiving the manifest.
    """
    for sect_num, sect in enumerate(manifest):
        # Prevents an additional newline
        if sect_num != 0:
            fp.write(LINE_END)
        for key, val in sect.items():
            encoded = f"{key}: {encoder(key, val)}"
            fp.write(encoded[:LINE_LEN])
            fp.write(LINE_END)
            chunk_len = LINE_LEN - 1
            for i in range(LINE_LEN, len(encoded), chunk_len):
                fp.write(LINE_CONT)
                fp.write(encoded[i : i + chunk_len])
                fp.write(LINE_END)
