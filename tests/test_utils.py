"""
Behavior tests for utils.py

Tests focus on real use cases:
- Tracking progress through large files
- Logging with timestamps
- Formatting numbers for display
"""

import io
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import FileProgressLog, log, format_number


FIXTURES = Path(__file__).parent / "fixtures"


class TestFileProgressLog:
    """Behavior: Should track progress through file processing"""

    def test_tracks_row_count(self):
        """Given multiple onRow() calls, should count correctly"""
        path = FIXTURES / "sample.jsonl"
        with open(path, "rb") as f:
            progress = FileProgressLog(str(path), f, log_interval=1000)

            progress.onRow()
            progress.onRow()
            progress.onRow()

            assert progress.row_count == 3

    def test_calculates_file_size(self):
        """Should know the total file size for % calculation"""
        path = FIXTURES / "sample.jsonl"
        with open(path, "rb") as f:
            progress = FileProgressLog(str(path), f)

            assert progress.file_size > 0

    def test_can_complete_without_error(self):
        """Should be able to call logProgress() at end without error"""
        path = FIXTURES / "sample.jsonl"
        with open(path, "rb") as f:
            progress = FileProgressLog(str(path), f)
            progress.onRow()
            progress.onRow()
            progress.onRow()
            progress.logProgress()  # Should not raise


class TestFormatNumber:
    """Behavior: Should format numbers for human-readable display"""

    def test_formats_integer_with_commas(self):
        """Large integers should have comma separators"""
        assert format_number(1000000) == "1,000,000"
        assert format_number(1234567890) == "1,234,567,890"

    def test_formats_small_integers(self):
        """Small integers should not have commas"""
        assert format_number(100) == "100"
        assert format_number(0) == "0"

    def test_formats_floats_with_two_decimals(self):
        """Floats should show 2 decimal places"""
        assert format_number(1234.5) == "1,234.50"
        assert format_number(0.1) == "0.10"


class TestLog:
    """Behavior: Should output timestamped log messages"""

    def test_log_does_not_raise(self, capsys):
        """Calling log() should not raise any errors"""
        log("Test message")
        log("Another message", level="ERROR")

        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert "ERROR" in captured.out
