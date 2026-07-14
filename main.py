"""
main.py
-------
End-to-end ETL orchestration:
    Extract  -> data_pipeline.run_ingestion()   (yFinance API)
    Transform-> analysis.build_feature_set()    (moving avgs, returns, vol, volume)
    Load     -> analysis.save_processed_data()  (CSV for downstream use)
    Report   -> visualize.*                     (PNG charts) + printed sector summary

Run directly:  python main.py
Run on a schedule (cron / GitHub Actions) for continuous trend monitoring.
"""

import logging
import sys

from config import ALL_TICKERS
from data_pipeline import run_ingestion
from analysis import build_feature_set, save_processed_data, sector_summary
from visualize import (
    plot_sector_cumulative_returns,
    plot_sector_volatility,
    plot_top_movers,
    plot_moving_averages,
    plot_volume_trends,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("main")


def run_pipeline(tickers=ALL_TICKERS, sample_ticker_for_detail_charts: str = "AAPL"):
    logger.info("=== STEP 1/4: EXTRACT — fetching market data from yFinance ===")
    raw_df = run_ingestion(tickers)

    logger.info("=== STEP 2/4: TRANSFORM — engineering analytical features ===")
    features_df = build_feature_set(raw_df)

    logger.info("=== STEP 3/4: LOAD — persisting processed dataset ===")
    save_processed_data(features_df)

    logger.info("=== STEP 4/4: REPORT — generating comparative visualizations ===")
    plot_sector_cumulative_returns(features_df)
    plot_sector_volatility(features_df)
    plot_top_movers(features_df)

    if sample_ticker_for_detail_charts in features_df["Ticker"].unique():
        plot_moving_averages(features_df, sample_ticker_for_detail_charts)
        plot_volume_trends(features_df, sample_ticker_for_detail_charts)

    summary = sector_summary(features_df)
    logger.info("Sector performance summary:\n%s", summary.to_string())

    logger.info("Pipeline complete. Charts saved to /outputs, data saved to /data.")
    return features_df, summary


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as exc:
        logger.exception(f"Pipeline failed: {exc}")
        sys.exit(1)
