"""
visualize.py
------------
Comparative, multi-sector visualizations built with Matplotlib for
performance benchmarking across timeframes.
"""

import logging

import matplotlib.pyplot as plt
import pandas as pd

from config import OUTPUT_DIR

logger = logging.getLogger(__name__)
plt.style.use("seaborn-v0_8-darkgrid")


def plot_sector_cumulative_returns(df: pd.DataFrame, save: bool = True):
    """Average cumulative return per sector over time — sector benchmarking chart."""
    sector_ts = (
        df.groupby(["Date", "Sector"])["Cumulative_Return"]
        .mean()
        .reset_index()
        .pivot(index="Date", columns="Sector", values="Cumulative_Return")
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    sector_ts.plot(ax=ax, linewidth=1.8)
    ax.set_title("Average Cumulative Return by Sector", fontsize=14, weight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.legend(title="Sector", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()

    if save:
        path = OUTPUT_DIR / "sector_cumulative_returns.png"
        fig.savefig(path, dpi=150)
        logger.info(f"Saved chart -> {path}")
    return fig


def plot_moving_averages(df: pd.DataFrame, ticker: str, save: bool = True):
    """Price with 20/50/200-day moving averages for a single ticker."""
    sub = df[df["Ticker"] == ticker].sort_values("Date")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(sub["Date"], sub["Adj Close"], label="Adj Close", linewidth=1.5)
    for ma_col in [c for c in sub.columns if c.startswith("MA_")]:
        ax.plot(sub["Date"], sub[ma_col], label=ma_col, linewidth=1.2, alpha=0.85)

    ax.set_title(f"{ticker}: Price & Moving Averages", fontsize=14, weight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    ax.legend()
    fig.tight_layout()

    if save:
        path = OUTPUT_DIR / f"{ticker}_moving_averages.png"
        fig.savefig(path, dpi=150)
        logger.info(f"Saved chart -> {path}")
    return fig


def plot_sector_volatility(df: pd.DataFrame, save: bool = True):
    """Boxplot comparing volatility distribution across sectors."""
    latest = df.sort_values("Date").groupby("Ticker").tail(60)  # last ~3 trading months

    fig, ax = plt.subplots(figsize=(12, 6))
    sectors = sorted(latest["Sector"].unique())
    data = [latest.loc[latest["Sector"] == s, "Volatility"].dropna() for s in sectors]
    ax.boxplot(data, labels=sectors, showfliers=False)
    ax.set_title("Volatility Distribution by Sector (Last ~60 Trading Days)", fontsize=14, weight="bold")
    ax.set_ylabel("Annualized Volatility")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()

    if save:
        path = OUTPUT_DIR / "sector_volatility_boxplot.png"
        fig.savefig(path, dpi=150)
        logger.info(f"Saved chart -> {path}")
    return fig


def plot_volume_trends(df: pd.DataFrame, ticker: str, save: bool = True):
    """Volume vs its rolling average for a single ticker — spot unusual activity."""
    sub = df[df["Ticker"] == ticker].sort_values("Date")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(sub["Date"], sub["Volume"], alpha=0.4, label="Daily Volume")
    ax.plot(sub["Date"], sub["Volume_MA"], color="darkred", linewidth=1.5, label="20-Day Avg Volume")
    ax.set_title(f"{ticker}: Trading Volume Trend", fontsize=14, weight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Volume")
    ax.legend()
    fig.tight_layout()

    if save:
        path = OUTPUT_DIR / f"{ticker}_volume_trend.png"
        fig.savefig(path, dpi=150)
        logger.info(f"Saved chart -> {path}")
    return fig


def plot_top_movers(df: pd.DataFrame, n: int = 10, save: bool = True):
    """Bar chart of the top N gainers/losers by cumulative return, across all sectors."""
    latest = df.sort_values("Date").groupby("Ticker").tail(1).sort_values("Cumulative_Return")
    top = pd.concat([latest.head(n), latest.tail(n)])

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ["crimson" if v < 0 else "seagreen" for v in top["Cumulative_Return"]]
    ax.barh(top["Ticker"], top["Cumulative_Return"], color=colors)
    ax.set_title(f"Top {n} Gainers & Losers (Cumulative Return)", fontsize=14, weight="bold")
    ax.set_xlabel("Cumulative Return")
    fig.tight_layout()

    if save:
        path = OUTPUT_DIR / "top_movers.png"
        fig.savefig(path, dpi=150)
        logger.info(f"Saved chart -> {path}")
    return fig


if __name__ == "__main__":
    from config import PROCESSED_DATA_FILE

    data = pd.read_csv(PROCESSED_DATA_FILE, parse_dates=["Date"])
    plot_sector_cumulative_returns(data)
    plot_sector_volatility(data)
    plot_top_movers(data)
    plot_moving_averages(data, ticker=data["Ticker"].iloc[0])
    plot_volume_trends(data, ticker=data["Ticker"].iloc[0])
