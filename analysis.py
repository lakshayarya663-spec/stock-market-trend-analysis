"""
analysis.py
-----------
Feature engineering layer. Computes moving averages, daily returns,
rolling volatility, and volume trend metrics per ticker.
"""

import logging

import pandas as pd

from config import (
    MOVING_AVERAGE_WINDOWS,
    VOLATILITY_WINDOW,
    PROCESSED_DATA_FILE,
)

logger = logging.getLogger(__name__)


def add_moving_averages(df: pd.DataFrame, windows=MOVING_AVERAGE_WINDOWS) -> pd.DataFrame:
    """Add simple moving average columns (e.g. MA_20, MA_50, MA_200) per ticker."""
    df = df.sort_values(["Ticker", "Date"]).copy()
    for w in windows:
        df[f"MA_{w}"] = (
            df.groupby("Ticker")["Adj Close"]
            .transform(lambda s: s.rolling(window=w, min_periods=max(1, w // 2)).mean())
        )
    return df


def add_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Add daily % return and cumulative return per ticker."""
    df = df.sort_values(["Ticker", "Date"]).copy()
    df["Daily_Return"] = df.groupby("Ticker")["Adj Close"].pct_change()
    df["Cumulative_Return"] = (
        df.groupby("Ticker")["Daily_Return"]
        .transform(lambda s: (1 + s.fillna(0)).cumprod() - 1)
    )
    return df


def add_volatility(df: pd.DataFrame, window: int = VOLATILITY_WINDOW) -> pd.DataFrame:
    """Add rolling annualized volatility (std of daily returns * sqrt(252))."""
    df = df.copy()
    if "Daily_Return" not in df.columns:
        df = add_daily_returns(df)
    df["Volatility"] = (
        df.groupby("Ticker")["Daily_Return"]
        .transform(lambda s: s.rolling(window=window, min_periods=max(2, window // 2)).std() * (252 ** 0.5))
    )
    return df


def add_volume_trends(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Add rolling average volume and volume ratio (today's volume vs its rolling mean)."""
    df = df.sort_values(["Ticker", "Date"]).copy()
    df["Volume_MA"] = (
        df.groupby("Ticker")["Volume"]
        .transform(lambda s: s.rolling(window=window, min_periods=max(1, window // 2)).mean())
    )
    df["Volume_Ratio"] = df["Volume"] / df["Volume_MA"]
    return df


def build_feature_set(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full feature-engineering pipeline in one call."""
    logger.info("Computing moving averages...")
    df = add_moving_averages(df)
    logger.info("Computing daily returns...")
    df = add_daily_returns(df)
    logger.info("Computing rolling volatility...")
    df = add_volatility(df)
    logger.info("Computing volume trends...")
    df = add_volume_trends(df)
    return df


def sector_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate key metrics by sector for quick benchmarking."""
    latest = df.sort_values("Date").groupby("Ticker").tail(1)
    summary = (
        latest.groupby("Sector")
        .agg(
            avg_daily_return=("Daily_Return", "mean"),
            avg_cumulative_return=("Cumulative_Return", "mean"),
            avg_volatility=("Volatility", "mean"),
            avg_volume_ratio=("Volume_Ratio", "mean"),
            num_tickers=("Ticker", "nunique"),
        )
        .sort_values("avg_cumulative_return", ascending=False)
    )
    return summary


def save_processed_data(df: pd.DataFrame, path=PROCESSED_DATA_FILE) -> None:
    df.to_csv(path, index=False)
    logger.info(f"Saved processed feature set -> {path}")


if __name__ == "__main__":
    import pandas as pd
    from config import RAW_DATA_FILE

    raw = pd.read_csv(RAW_DATA_FILE, parse_dates=["Date"])
    processed = build_feature_set(raw)
    save_processed_data(processed)
    print(sector_summary(processed))
