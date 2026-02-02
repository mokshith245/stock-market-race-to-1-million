"""
Behavior tests for valid_tickers.txt

Tests focus on real use cases:
- Ticker list exists and is usable
- Key tickers for our use case are present
- Common words that cause false positives are excluded
"""

import pytest
from pathlib import Path


TICKERS_PATH = Path(__file__).parent.parent / "data" / "valid_tickers.txt"


@pytest.fixture
def tickers():
    """Load the valid tickers set"""
    with open(TICKERS_PATH, "r") as f:
        return {line.strip() for line in f if line.strip()}


class TestTickerListExists:
    """Behavior: Ticker list should exist and be usable"""

    def test_file_exists(self):
        """Ticker file should exist"""
        assert TICKERS_PATH.exists(), f"Missing {TICKERS_PATH}"

    def test_has_reasonable_count(self, tickers):
        """Should have thousands of tickers (US market has ~6000+ stocks)"""
        assert len(tickers) >= 5000, f"Only {len(tickers)} tickers - seems too few"
        assert len(tickers) <= 15000, f"{len(tickers)} tickers - seems too many"


class TestKeyTickersPresent:
    """Behavior: Key tickers for our use case should be present"""

    def test_benchmark_spy_present(self, tickers):
        """SPY (our benchmark) must be present"""
        assert "SPY" in tickers

    def test_popular_tech_stocks(self, tickers):
        """Popular tech stocks discussed on Reddit should be present"""
        tech_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "AMD", "TSLA"]
        for ticker in tech_stocks:
            assert ticker in tickers, f"Missing popular ticker: {ticker}"

    def test_meme_stocks(self, tickers):
        """Meme stocks frequently discussed should be present"""
        meme_stocks = ["GME", "AMC", "PLTR", "NIO"]
        for ticker in meme_stocks:
            assert ticker in tickers, f"Missing meme stock: {ticker}"

    def test_popular_etfs(self, tickers):
        """Popular ETFs should be present"""
        etfs = ["SPY", "QQQ", "IWM"]
        for ticker in etfs:
            assert ticker in tickers, f"Missing ETF: {ticker}"


class TestCommonWordsExcluded:
    """Behavior: Common words should be excluded to prevent false positives"""

    def test_single_letters_excluded(self, tickers):
        """Single letter tickers cause too many false positives"""
        single_letters = ["A", "B", "C", "I", "X"]
        for letter in single_letters:
            assert letter not in tickers, f"Single letter {letter} should be excluded"

    def test_common_words_excluded(self, tickers):
        """Common English words should be excluded"""
        common_words = ["THE", "AND", "FOR", "ARE", "ALL", "CAN", "HAS", "NEW"]
        for word in common_words:
            assert word not in tickers, f"Common word {word} should be excluded"

    def test_reddit_slang_excluded(self, tickers):
        """Reddit/WSB slang should be excluded"""
        slang = ["YOLO", "EDIT", "HOLD", "MOON", "PUMP", "DUMP"]
        for word in slang:
            assert word not in tickers, f"Slang word {word} should be excluded"

    def test_finance_acronyms_excluded(self, tickers):
        """Finance acronyms that aren't tickers should be excluded"""
        acronyms = ["IPO", "ATH", "EOD", "FED", "SEC", "GDP", "CPI"]
        for word in acronyms:
            assert word not in tickers, f"Acronym {word} should be excluded"


class TestTickerFormat:
    """Behavior: All tickers should be properly formatted"""

    def test_all_uppercase(self, tickers):
        """All tickers should be uppercase"""
        for ticker in tickers:
            assert ticker == ticker.upper(), f"Ticker {ticker} not uppercase"

    def test_all_alphabetic(self, tickers):
        """All tickers should be alphabetic (no numbers or special chars)"""
        for ticker in tickers:
            assert ticker.isalpha(), f"Ticker {ticker} contains non-alpha chars"

    def test_minimum_length(self, tickers):
        """All tickers should be at least 2 characters"""
        for ticker in tickers:
            assert len(ticker) >= 2, f"Ticker {ticker} too short"
