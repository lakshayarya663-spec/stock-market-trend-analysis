"""
data_pipeline.py
-----------------
Real-time data ingestion layer. Pulls OHLCV data for the full ticker
universe from the yFinance API, handles failed/delisted tickers
gracefully, and persists a tidy long-format CSV for downstream analysis.
"""

import logging
import time
from datetime import datetime

import pandas as pd
import yfinance as yf

from config import ALL_TICKERS, TICKER_TO_SECTOR, DEFAULT_PERIOD, DEFAULT_INTERVAL, RAW_DATA_FILE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_batch(tickers: list[str], period: str = DEFAULT_PERIOD,
                 interval: str = DEFAULT_INTERVAL, batch_size: int = 10,
                 pause: float = 1.0) -> pd.DataFrame:
    """
    Fetch OHLCV data for a list of tickers in batches to stay within
    API rate limits, and return a single tidy (long-format) DataFrame.

    Columns: Date, Ticker, Sector, Open, High, Low, Close, Adj Close, Volume
    """
    frames = []

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        logger.info(f"Fetching batch {i // batch_size + 1}: {batch}")

        try:
            raw = yf.download(
                tickers=batch,
                period=period,
                interval=interval,
                group_by="ticker",
                auto_adjust=False,
                threads=True,
                progress=False,
            )
        except Exception as exc:
            logger.warning(f"Batch fetch failed for {batch}: {exc}")
            continue

        for ticker in batch:
            try:
                df = raw[ticker].copy() if len(batch) > 1 else raw.copy()
                if df.empty:
                    logger.warning(f"No data returned for {ticker}, skipping.")
                    continue
                df = df.reset_index()
                df["Ticker"] = ticker
                df["Sector"] = TICKER_TO_SECTOR.get(ticker, "Unknown")
                frames.append(df)
            except (KeyError, AttributeError):
                logger.warning(f"Ticker {ticker} missing from response, skipping.")

        time.sleep(pause)  # be polite to the API between batches

    if not frames:
        raise RuntimeError("No data could be fetched for any ticker.")

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(["Ticker", "Date"]).reset_index(drop=True)
    return combined


def save_raw_data(df: pd.DataFrame, path=RAW_DATA_FILE) -> None:
    df.to_csv(path, index=False)
    logger.info(f"Saved {len(df):,} rows for {df['Ticker'].nunique()} tickers -> {path}")


def run_ingestion(tickers: list[str] = ALL_TICKERS) -> pd.DataFrame:
    """End-to-end ingestion entry point used by main.py / the ETL job."""
    logger.info(f"Starting ingestion for {len(tickers)} tickers at {datetime.now().isoformat()}")
    df = fetch_batch(tickers)
    save_raw_data(df)
    return df


if __name__ == "__main__":
    run_ingestion()
