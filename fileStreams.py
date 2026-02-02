"""
Streaming utilities for reading large JSONL and ZST compressed files.
Processes files line-by-line to handle files larger than available memory.
"""

import sys
version = sys.version_info
if version.major < 3 or (version.major == 3 and version.minor < 10):
    raise RuntimeError("This script requires Python 3.10 or higher")

import gzip
import orjson
import zstandard as zstd
from typing import Iterator, Dict, Any, BinaryIO


def getFileJsonStream(path: str, f: BinaryIO) -> Iterator[Dict[str, Any]] | None:
    """
    Get a JSON stream iterator for a file based on its extension.

    Args:
        path: File path (used to determine file type from extension)
        f: Open binary file handle

    Returns:
        Iterator yielding parsed JSON objects, or None if file type unknown
    """
    if path.endswith(".zst"):
        return _stream_zst(f)
    elif path.endswith(".gz"):
        return _stream_gz(f)
    elif path.endswith(".jsonl") or path.endswith(".json"):
        return _stream_jsonl(f)
    else:
        return None


def _stream_jsonl(f: BinaryIO) -> Iterator[Dict[str, Any]]:
    """Stream a plain JSONL file."""
    for line in f:
        line = line.strip()
        if line:
            try:
                yield orjson.loads(line)
            except orjson.JSONDecodeError:
                continue


def _stream_gz(f: BinaryIO) -> Iterator[Dict[str, Any]]:
    """Stream a gzip compressed JSONL file."""
    with gzip.open(f, 'rb') as gz:
        for line in gz:
            line = line.strip()
            if line:
                try:
                    yield orjson.loads(line)
                except orjson.JSONDecodeError:
                    continue


def _stream_zst(f: BinaryIO) -> Iterator[Dict[str, Any]]:
    """Stream a ZST (zstandard) compressed JSONL file."""
    dctx = zstd.ZstdDecompressor()

    with dctx.stream_reader(f) as reader:
        buffer = b''

        while True:
            chunk = reader.read(65536)  # 64KB chunks
            if not chunk:
                break

            buffer += chunk
            lines = buffer.split(b'\n')
            buffer = lines[-1]  # Keep incomplete line

            for line in lines[:-1]:
                line = line.strip()
                if line:
                    try:
                        yield orjson.loads(line)
                    except orjson.JSONDecodeError:
                        continue

        # Process remaining buffer
        if buffer.strip():
            try:
                yield orjson.loads(buffer)
            except orjson.JSONDecodeError:
                pass
