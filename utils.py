"""
Utility functions for logging progress and common operations.
"""

import os
import sys
import time
from datetime import datetime
from typing import BinaryIO


class FileProgressLog:
    """
    Log progress through a file, showing % complete based on bytes read.
    """

    def __init__(self, path: str, f: BinaryIO, log_interval: int = 10000):
        self.path = path
        self.f = f
        self.log_interval = log_interval
        self.row_count = 0
        self.start_time = time.time()

        # Get file size for % calculation
        self.file_size = os.path.getsize(path)

    def onRow(self) -> None:
        """Call this for each row processed."""
        self.row_count += 1

        if self.row_count % self.log_interval == 0:
            self._logProgress()

    def _logProgress(self) -> None:
        """Log current progress with rate and % complete."""
        elapsed = time.time() - self.start_time
        rate = self.row_count / elapsed if elapsed > 0 else 0

        # Calculate % based on file position
        try:
            pos = self.f.tell()
            pct = (pos / self.file_size * 100) if self.file_size > 0 else 0
        except:
            pct = 0

        print(f"  {self.row_count:,} rows | {rate:,.0f}/sec | {pct:.1f}% | {elapsed:.1f}s", end="\r")
        sys.stdout.flush()

    def logProgress(self, end: str = "\n") -> None:
        """Log final progress."""
        elapsed = time.time() - self.start_time
        rate = self.row_count / elapsed if elapsed > 0 else 0

        print(f"  {self.row_count:,} rows | {rate:,.0f}/sec | 100% | {elapsed:.1f}s", end=end)
        sys.stdout.flush()


def log(message: str, level: str = "INFO") -> None:
    """Simple timestamped logging."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")
    sys.stdout.flush()


def format_number(n: int | float) -> str:
    """Format large numbers with commas."""
    if isinstance(n, float):
        return f"{n:,.2f}"
    return f"{n:,}"
