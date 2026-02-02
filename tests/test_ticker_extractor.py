"""
Behavior tests for ticker_extractor.py

Tests focus on real use cases:
- Extracting $TICKER format mentions
- Extracting action context mentions
- Validating against valid tickers list
- Handling edge cases
"""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ticker_extractor import TickerExtractor, Confidence, TickerMention


VALID_TICKERS_PATH = Path(__file__).parent.parent / "data" / "valid_tickers.txt"


@pytest.fixture
def extractor():
    """Create a TickerExtractor instance"""
    return TickerExtractor(VALID_TICKERS_PATH)


class TestDollarTickerExtraction:
    """Behavior: Should extract $TICKER format with HIGH confidence"""

    def test_extracts_dollar_ticker(self, extractor):
        """$AAPL should be extracted"""
        mentions = extractor.extract("I love $AAPL")
        assert len(mentions) == 1
        assert mentions[0].ticker == "AAPL"
        assert mentions[0].confidence == Confidence.HIGH

    def test_extracts_multiple_dollar_tickers(self, extractor):
        """Multiple $TICKER mentions should all be extracted"""
        mentions = extractor.extract("$AAPL and $TSLA are my favorites")
        tickers = {m.ticker for m in mentions}
        assert "AAPL" in tickers
        assert "TSLA" in tickers

    def test_dollar_ticker_case_insensitive(self, extractor):
        """$aapl should match as AAPL"""
        mentions = extractor.extract("bought $aapl today")
        assert len(mentions) == 1
        assert mentions[0].ticker == "AAPL"

    def test_dollar_ticker_stores_context(self, extractor):
        """Should store the matched context"""
        mentions = extractor.extract("I bought $NVDA")
        assert mentions[0].context == "$NVDA"


class TestActionContextExtraction:
    """Behavior: Should extract action context with MEDIUM confidence"""

    def test_extracts_bought_ticker(self, extractor):
        """'bought AAPL' should be extracted"""
        mentions = extractor.extract("I bought AAPL yesterday")
        assert len(mentions) == 1
        assert mentions[0].ticker == "AAPL"
        assert mentions[0].confidence == Confidence.MEDIUM

    def test_extracts_selling_ticker(self, extractor):
        """'selling TSLA' should be extracted"""
        mentions = extractor.extract("I'm selling TSLA")
        assert len(mentions) == 1
        assert mentions[0].ticker == "TSLA"

    def test_extracts_calls_puts(self, extractor):
        """'AAPL calls' and 'TSLA puts' should be extracted"""
        mentions = extractor.extract("bought AAPL calls and TSLA puts")
        tickers = {m.ticker for m in mentions}
        assert "AAPL" in tickers
        assert "TSLA" in tickers

    def test_extracts_long_short(self, extractor):
        """'long NVDA' should be extracted"""
        mentions = extractor.extract("I'm long NVDA")
        assert len(mentions) == 1
        assert mentions[0].ticker == "NVDA"

    def test_extracts_yolo(self, extractor):
        """'yolo GME' should be extracted"""
        mentions = extractor.extract("gonna yolo GME")
        assert len(mentions) == 1
        assert mentions[0].ticker == "GME"

    def test_extracts_with_words_between(self, extractor):
        """'bought some AAPL' should be extracted"""
        mentions = extractor.extract("I bought some AAPL shares")
        assert len(mentions) >= 1
        tickers = {m.ticker for m in mentions}
        assert "AAPL" in tickers


class TestValidTickerFiltering:
    """Behavior: Should only extract valid tickers"""

    def test_ignores_invalid_ticker(self, extractor):
        """$INVALIDTICKER should not be extracted"""
        mentions = extractor.extract("I bought $XYZABC")
        assert len(mentions) == 0

    def test_ignores_common_words(self, extractor):
        """Common words like THE, AND should not be extracted"""
        mentions = extractor.extract("bought THE stock and AND more")
        # Should not extract THE or AND even with action context
        tickers = {m.ticker for m in mentions}
        assert "THE" not in tickers
        assert "AND" not in tickers


class TestDeduplication:
    """Behavior: Should deduplicate tickers, keeping highest confidence"""

    def test_deduplicates_same_ticker(self, extractor):
        """Same ticker mentioned twice should appear once"""
        mentions = extractor.extract("$AAPL is great, bought AAPL")
        tickers = [m.ticker for m in mentions]
        assert tickers.count("AAPL") == 1

    def test_keeps_high_confidence_over_medium(self, extractor):
        """When same ticker has HIGH and MEDIUM, keep HIGH"""
        mentions = extractor.extract("bought AAPL, also $AAPL")
        aapl_mention = [m for m in mentions if m.ticker == "AAPL"][0]
        assert aapl_mention.confidence == Confidence.HIGH


class TestEdgeCases:
    """Behavior: Should handle edge cases gracefully"""

    def test_empty_string(self, extractor):
        """Empty string should return empty list"""
        mentions = extractor.extract("")
        assert mentions == []

    def test_none_text(self, extractor):
        """None should return empty list"""
        mentions = extractor.extract(None)
        assert mentions == []

    def test_no_tickers(self, extractor):
        """Text with no tickers should return empty list"""
        mentions = extractor.extract("I like stocks in general")
        assert mentions == []

    def test_ticker_in_url_not_extracted(self, extractor):
        """Tickers inside URLs should ideally not cause issues"""
        # This is a known limitation - we don't filter URLs
        mentions = extractor.extract("check https://example.com/AAPL")
        # May or may not extract - just shouldn't crash
        assert isinstance(mentions, list)


class TestExtractTickersOnly:
    """Behavior: extract_tickers_only should return just symbols"""

    def test_returns_list_of_strings(self, extractor):
        """Should return list of ticker strings"""
        tickers = extractor.extract_tickers_only("$AAPL and $TSLA")
        assert isinstance(tickers, list)
        assert all(isinstance(t, str) for t in tickers)
        assert "AAPL" in tickers
        assert "TSLA" in tickers
