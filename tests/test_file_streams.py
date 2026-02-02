"""
Behavior tests for fileStreams.py

Tests focus on real use cases:
- Streaming Reddit data files in various formats (.jsonl, .gz, .zst)
- Handling malformed JSON gracefully
- Correctly identifying file types
"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from fileStreams import getFileJsonStream


FIXTURES = Path(__file__).parent / "fixtures"


class TestStreamingJsonlFiles:
    """Behavior: Should stream .jsonl files and yield parsed JSON objects"""

    def test_streams_valid_jsonl_file(self):
        """Given a valid .jsonl file, should yield all records"""
        path = FIXTURES / "sample.jsonl"
        with open(path, "rb") as f:
            records = list(getFileJsonStream(str(path), f))

        assert len(records) == 3
        assert records[0]["author"] == "user1"
        assert records[1]["author"] == "user2"
        assert records[2]["author"] == "user3"

    def test_extracts_expected_reddit_fields(self):
        """Given Reddit-like data, should preserve all fields we need"""
        path = FIXTURES / "sample.jsonl"
        with open(path, "rb") as f:
            records = list(getFileJsonStream(str(path), f))

        record = records[0]
        # These are the fields we'll use in our pipeline
        assert "author" in record
        assert "subreddit" in record
        assert "id" in record
        assert "created_utc" in record
        assert "score" in record
        assert "body" in record


class TestStreamingCompressedFiles:
    """Behavior: Should stream compressed files (.gz, .zst) transparently"""

    def test_streams_gzip_file(self):
        """Given a .gz file, should decompress and yield records"""
        path = FIXTURES / "sample.jsonl.gz"
        with open(path, "rb") as f:
            records = list(getFileJsonStream(str(path), f))

        assert len(records) == 3
        assert records[0]["author"] == "user1"

    def test_streams_zst_file(self):
        """Given a .zst file (Reddit's format), should decompress and yield records"""
        path = FIXTURES / "sample.zst"
        with open(path, "rb") as f:
            records = list(getFileJsonStream(str(path), f))

        assert len(records) == 3
        assert records[0]["author"] == "user1"


class TestMalformedJsonHandling:
    """Behavior: Should skip malformed JSON lines without crashing"""

    def test_skips_malformed_lines(self):
        """Given a file with some malformed JSON, should skip bad lines and continue"""
        path = FIXTURES / "with_malformed.jsonl"
        with open(path, "rb") as f:
            records = list(getFileJsonStream(str(path), f))

        # Should get 3 valid records, skipping 2 malformed lines
        assert len(records) == 3
        assert records[0]["author"] == "user1"
        assert records[1]["author"] == "user2"
        assert records[2]["author"] == "user3"


class TestEmptyFiles:
    """Behavior: Should handle empty files gracefully"""

    def test_empty_file_yields_nothing(self):
        """Given an empty file, should yield no records without error"""
        path = FIXTURES / "empty.jsonl"
        with open(path, "rb") as f:
            records = list(getFileJsonStream(str(path), f))

        assert len(records) == 0


class TestUnknownFileTypes:
    """Behavior: Should return None for unknown file types"""

    def test_unknown_extension_returns_none(self):
        """Given a file with unknown extension, should return None"""
        path = FIXTURES / "sample.jsonl"  # We'll pretend it's a .txt
        with open(path, "rb") as f:
            result = getFileJsonStream("unknown_file.txt", f)

        assert result is None

    def test_csv_returns_none(self):
        """Given a .csv file, should return None"""
        path = FIXTURES / "sample.jsonl"
        with open(path, "rb") as f:
            result = getFileJsonStream("data.csv", f)

        assert result is None
