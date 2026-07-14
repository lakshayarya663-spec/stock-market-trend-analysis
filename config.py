"""
config.py
---------
Central configuration for the Stock Market Trend Analysis pipeline.
Defines the universe of tickers (50+ stocks across sectors), default
date ranges, and file paths used across the project.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Universe: 50+ stocks across multiple sectors
# ---------------------------------------------------------------------------
SECTOR_TICKERS = {
    "Technology": [
        "AAPL", "MSFT", "GOOGL", "NVDA", "META", "ADBE", "CRM", "ORCL", "INTC", "AMD",
    ],
    "Financials": [
        "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "BLK", "SCHW", "USB",
    ],
    "Healthcare": [
        "JNJ", "UNH", "PFE", "MRK", "ABBV", "LLY", "TMO", "ABT", "BMY", "AMGN",
    ],
    "Energy": [
        "XOM", "CVX", "COP", "SLB", "EOG", "PSX", "MPC", "OXY", "VLO", "KMI",
    ],
    "Consumer": [
        "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "TGT", "LOW", "COST", "PG",
    ],
    "Industrials": [
        "BA", "CAT", "GE", "HON", "UPS", "RTX", "LMT", "DE", "MMM", "UNP",
    ],
}

# Flattened list of all tickers (60 total)
ALL_TICKERS = [t for tickers in SECTOR_TICKERS.values() for t in tickers]

# Reverse lookup: ticker -> sector
TICKER_TO_SECTOR = {t: sector for sector, tickers in SECTOR_TICKERS.items() for t in tickers}

# ---------------------------------------------------------------------------
# Date range / analysis parameters
# ---------------------------------------------------------------------------
DEFAULT_PERIOD = "1y"          # yfinance period: 1y, 6mo, 3mo, etc.
DEFAULT_INTERVAL = "1d"        # daily bars
MOVING_AVERAGE_WINDOWS = [20, 50, 200]   # short / medium / long-term MAs
VOLATILITY_WINDOW = 21         # ~1 trading month, used for rolling volatility

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_FILE = DATA_DIR / "raw_prices.csv"
PROCESSED_DATA_FILE = DATA_DIR / "processed_metrics.csv"
OUTPUT_DIR = ROOT_DIR / "outputs"

DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
