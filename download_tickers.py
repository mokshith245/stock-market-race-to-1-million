"""
Download valid ticker symbols from NASDAQ.
Filters to common stocks and saves to data/valid_tickers.txt
"""

import os
import sys
import yaml
import requests
from pathlib import Path

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


def download_exchange_tickers(exchange: str) -> set[str]:
    """Download ticker list from NASDAQ API for a given exchange."""
    url = f"https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25000&exchange={exchange}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "data" in data and "table" in data["data"] and "rows" in data["data"]["table"]:
            rows = data["data"]["table"]["rows"]
            tickers = {row["symbol"] for row in rows if row.get("symbol")}
            print(f"Downloaded {len(tickers)} {exchange} tickers")
            return tickers
    except Exception as e:
        print(f"Failed to download from {exchange}: {e}")

    return set()


def filter_tickers(tickers: set[str]) -> set[str]:
    """
    Filter tickers to reduce false positives.

    Removes:
    - Single character tickers (too ambiguous: A, B, C, etc.)
    - Common English words that happen to be tickers
    """
    # Common words that are also tickers - these cause too many false positives
    common_words = {
        "A", "I", "IT", "AT", "BE", "BY", "DO", "GO", "IF", "IN", "IS", "ME",
        "MY", "NO", "OF", "ON", "OR", "SO", "TO", "UP", "US", "WE",
        "ALL", "AM", "AN", "AND", "ANY", "ARE", "AS", "BIG", "CAN", "CEO",
        "DD", "EV", "FOR", "HAS", "HE", "HIM", "HIS", "HOW", "ITS", "LET",
        "LOW", "MAY", "MEN", "NEW", "NOT", "NOW", "OLD", "ONE", "OUR", "OUT",
        "OWN", "RUN", "SAY", "SEE", "SHE", "THE", "TOO", "TWO", "WAS", "WAY",
        "WHO", "WHY", "WIN", "YOU", "YOLO", "IMO", "TBH", "FYI", "CEO", "CFO",
        "IPO", "ATH", "EOD", "EOM", "EOY", "YTD", "QTD", "MTD", "PM", "AM",
        "USA", "UK", "EU", "GDP", "CPI", "FED", "SEC", "FDA", "CDC", "WHO",
        "CEO", "COO", "CTO", "CFO", "CIO", "VP", "SVP", "EVP", "MD", "PhD",
        "AI", "ML", "AR", "VR", "IOT", "API", "SDK", "UI", "UX",
        "EDIT", "LINK", "POST", "HOLD", "PUMP", "DUMP", "MOON", "GAIN", "LOSS",
        "CALL", "PUT", "BUY", "SELL", "LONG", "SHORT", "BEAR", "BULL",
        "FREE", "BEST", "GOOD", "REAL", "TRUE", "VERY", "WELL", "JUST",
        "LIVE", "LOVE", "LIFE", "WORK", "HOME", "NEXT", "LAST", "ONLY",
        "MOST", "MUCH", "MANY", "MORE", "SOME", "SUCH", "THAN", "THAT",
        "THEM", "THEN", "THIS", "WHAT", "WHEN", "WILL", "WITH", "YOUR",
    }

    filtered = set()
    for ticker in tickers:
        # Skip single character
        if len(ticker) <= 1:
            continue
        # Skip common words
        if ticker.upper() in common_words:
            continue
        # Skip tickers with special characters (preferred shares, warrants, etc.)
        if not ticker.isalpha():
            continue
        filtered.add(ticker.upper())

    return filtered


def add_special_tickers(tickers: set[str]) -> set[str]:
    """Add important tickers that we always want to recognize."""
    # Always include SPY (our benchmark)
    tickers.add("SPY")

    # Popular ETFs commonly discussed
    popular_etfs = {"QQQ", "IWM", "DIA", "VTI", "VOO", "ARKK", "TQQQ", "SQQQ"}
    tickers.update(popular_etfs)

    # Meme stocks and popular tickers that might get filtered
    popular_stocks = {
        "GME", "AMC", "BB", "NOK", "PLTR", "NIO", "TSLA", "AAPL", "NVDA",
        "AMD", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NFLX"
    }
    tickers.update(popular_stocks)

    return tickers


def main():
    print("Downloading ticker lists...")

    # Download from all exchanges
    all_tickers = set()
    all_tickers.update(download_exchange_tickers("NASDAQ"))
    all_tickers.update(download_exchange_tickers("NYSE"))
    all_tickers.update(download_exchange_tickers("AMEX"))

    print(f"Total raw tickers: {len(all_tickers)}")

    # Filter
    filtered = filter_tickers(all_tickers)
    print(f"After filtering common words: {len(filtered)}")

    # Add special tickers
    final = add_special_tickers(filtered)
    print(f"After adding special tickers: {len(final)}")

    # Save
    output_path = Path(config["data"]["valid_tickers_file"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for ticker in sorted(final):
            f.write(f"{ticker}\n")

    print(f"Saved {len(final)} tickers to {output_path}")


if __name__ == "__main__":
    main()
