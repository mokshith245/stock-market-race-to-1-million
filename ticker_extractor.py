"""
Ticker extraction from Reddit posts and comments.

Confidence levels:
- HIGH: $TICKER format (e.g., "$AAPL", "$TSLA")
- MEDIUM: Action context (e.g., "bought AAPL", "selling TSLA calls")

Note: spaCy NER is not available due to Python 3.14 compatibility.
      TODO: Add NER-based extraction when spaCy supports Python 3.14.
"""

import re
from pathlib import Path
from typing import NamedTuple
from enum import Enum


class Confidence(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TickerMention(NamedTuple):
    """A ticker mention extracted from text."""
    ticker: str
    confidence: Confidence
    context: str  # The surrounding text that matched


class TickerExtractor:
    """
    Extract stock ticker mentions from text.

    Usage:
        extractor = TickerExtractor("data/valid_tickers.txt")
        mentions = extractor.extract("I bought $AAPL and sold TSLA")
    """

    def __init__(self, valid_tickers_path: str | Path):
        """
        Initialize with path to valid tickers file.

        Args:
            valid_tickers_path: Path to file with one ticker per line
        """
        self.valid_tickers = self._load_valid_tickers(valid_tickers_path)

        # Compile regex patterns
        self._compile_patterns()

    def _load_valid_tickers(self, path: str | Path) -> set[str]:
        """Load valid tickers from file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Valid tickers file not found: {path}")

        with open(path, "r") as f:
            return {line.strip().upper() for line in f if line.strip()}

    def _compile_patterns(self):
        """Compile regex patterns for extraction."""
        # HIGH confidence: $TICKER format
        # Matches $AAPL, $tsla, etc. (case insensitive)
        self.dollar_pattern = re.compile(
            r'\$([A-Za-z]{2,5})\b',
            re.IGNORECASE
        )

        # MEDIUM confidence: Action words followed by ticker
        # e.g., "bought AAPL", "selling TSLA", "long NVDA"
        action_words = [
            "buy", "buying", "bought",
            "sell", "selling", "sold",
            "long", "short", "shorting",
            "calls?", "puts?",  # "call" or "calls", "put" or "puts"
            "holding", "hold",
            "yolo", "yoloing", "yoloed",
            "position", "positioned",
            "added", "adding",
            "loaded", "loading",
            "grabbed", "grabbing",
            "picked", "picking",
            "dumped", "dumping",
        ]
        action_pattern = "|".join(action_words)

        # Pattern: action word + optional words + ticker
        # e.g., "bought some AAPL", "selling my TSLA calls"
        self.action_before_pattern = re.compile(
            rf'\b({action_pattern})\s+(?:\w+\s+){{0,3}}([A-Z]{{2,5}})\b',
            re.IGNORECASE
        )

        # Pattern: ticker + action word
        # e.g., "AAPL calls", "TSLA puts", "NVDA position"
        self.ticker_before_action_pattern = re.compile(
            rf'\b([A-Z]{{2,5}})\s+(calls?|puts?|position|shares?|stock)\b',
            re.IGNORECASE
        )

    def extract(self, text: str) -> list[TickerMention]:
        """
        Extract all ticker mentions from text.

        Args:
            text: The text to search for ticker mentions

        Returns:
            List of TickerMention objects, deduplicated by ticker
        """
        if not text:
            return []

        mentions = {}  # ticker -> TickerMention (keep highest confidence)

        # HIGH confidence: $TICKER format
        for match in self.dollar_pattern.finditer(text):
            ticker = match.group(1).upper()
            if ticker in self.valid_tickers:
                if ticker not in mentions or mentions[ticker].confidence != Confidence.HIGH:
                    mentions[ticker] = TickerMention(
                        ticker=ticker,
                        confidence=Confidence.HIGH,
                        context=match.group(0)
                    )

        # MEDIUM confidence: Action context
        for match in self.action_before_pattern.finditer(text):
            ticker = match.group(2).upper()
            if ticker in self.valid_tickers and ticker not in mentions:
                mentions[ticker] = TickerMention(
                    ticker=ticker,
                    confidence=Confidence.MEDIUM,
                    context=match.group(0)
                )

        for match in self.ticker_before_action_pattern.finditer(text):
            ticker = match.group(1).upper()
            if ticker in self.valid_tickers and ticker not in mentions:
                mentions[ticker] = TickerMention(
                    ticker=ticker,
                    confidence=Confidence.MEDIUM,
                    context=match.group(0)
                )

        return list(mentions.values())

    def extract_tickers_only(self, text: str) -> list[str]:
        """
        Extract just the ticker symbols (no metadata).

        Args:
            text: The text to search

        Returns:
            List of unique ticker symbols
        """
        mentions = self.extract(text)
        return [m.ticker for m in mentions]


def load_extractor_from_config(config: dict) -> TickerExtractor:
    """
    Create a TickerExtractor from config dict.

    Args:
        config: Config dict with data.valid_tickers_file path

    Returns:
        Configured TickerExtractor instance
    """
    valid_tickers_path = config["data"]["valid_tickers_file"]
    return TickerExtractor(valid_tickers_path)
