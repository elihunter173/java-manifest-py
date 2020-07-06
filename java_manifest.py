"""Dependency-free parser of Java's MANIFEST.MF file.

Released under the MIT license.
"""

import os
from io import StringIO, TextIOWrapper
from typing import IO, BinaryIO, Dict, List, TextIO, Union, cast
from zipfile import ZipFile

__version__ = "0.1.0"

Section = Dict[str, Union[bool, str]]
"""Single block of key-values pairs in a Manifest"""
Manifest = List[Section]
"""List of Sections, delimited by empty lines"""

LINE_CONT = " "
LINE_END = "\r\n"
LINE_LEN = 70


def decode_val(val: str) -> Union[bool, str]:
    if val == "true":
        return True
    elif val == "false":
        return False
    else:
        return val


def encode_val(val: Union[bool, str]) -> str:
    if isinstance(val, bool):
        return "true" if val is True else "false"
    elif isinstance(val, str):
        return val
    else:
        raise ValueError(f"cannot encode {type(val)} (val={val})")


def loads(s: str) -> Manifest:
    """Parse MANIFEST data from string.

    Args:
        s: String to parse.

    Return:
        Manifest parsed from `s`.
    """
    return load(StringIO(s))


def load(fp: TextIO) -> Manifest:
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
                sect[key] = decode_val(val.getvalue())
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
        sect[key] = decode_val(val.getvalue())
        key, val = None, None
    if sect:
        sections.append(sect)
        sect = {}

    return sections


def from_jar(jarfile: Union["os.PathLike[str]", IO[bytes]]) -> Manifest:
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
            return load(manifest)


def dump(manifest: Manifest, fp: TextIO):
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
            encoded = f"{key}: {encode_val(val)}"
            fp.write(encoded[:LINE_LEN])
            fp.write(LINE_END)
            chunk_len = LINE_LEN - 1
            for i in range(LINE_LEN, len(encoded), chunk_len):
                fp.write(LINE_CONT)
                fp.write(encoded[i : i + chunk_len])
                fp.write(LINE_END)


def dumps(obj: Manifest) -> str:
    """Return MANIFEST string from manifest object.

    Args:
        manifest: Manifest to convert to a MANIFEST formatted string.

    Return:
        MANIFEST formatted string from `manifest`.
    """
    buf = StringIO()
    dump(obj, buf)
    return buf.getvalue()
