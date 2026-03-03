#!/usr/bin/env python3
"""
Phase 1: Fetch precious metals price data using yfinance.

This module fetches historical monthly precious metals prices and combines them
with fixed supply data from config/precious_metals_supply.csv to derive market cap.

Features:
- Monthly price data fetching via yfinance
- Market cap calculation from price and supply
- Forward-fill handling for missing dates
- Comprehensive logging to file and console
- Metadata tracking for data quality
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# File handler
file_handler = logging.FileHandler(LOGS_DIR / "01c_fetch_metals.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


class MetalsPriceFetcher:
    """Fetches and processes precious metals price data from yfinance."""

    def __init__(
        self,
        config_path: str = "config/precious_metals_supply.csv",
        output_dir: str = "data/raw",
    ):
        """
        Initialize the MetalsPriceFetcher.

        Args:
            config_path: Path to precious_metals_supply.csv file
            output_dir: Directory to save output CSV and metadata files
        """
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metals_df: Optional[pd.DataFrame] = None
        self.fetch_results: Dict[str, any] = {
            "successful": [],
            "failed": [],
            "data_gaps": {},
        }
        logger.info(f"Initialized MetalsPriceFetcher with output dir: {output_dir}")

    def read_config(self) -> pd.DataFrame:
        """
        Load precious metals configuration from precious_metals_supply.csv.

        Returns:
            DataFrame with ticker, name, supply_ounces, source, update_frequency

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        self.metals_df = pd.read_csv(self.config_path)
        logger.info(f"Loaded {len(self.metals_df)} metals from {self.config_path}")
        logger.debug(f"Metals: {self.metals_df['ticker'].tolist()}")

        return self.metals_df

    def fetch_metal_prices(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        max_retries: int = 3,
    ) -> Optional[pd.DataFrame]:
        """
        Fetch monthly metal prices from yfinance.

        Args:
            ticker: Metal ticker symbol (e.g., 'GC=F' for gold futures)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_retries: Maximum number of retry attempts

        Returns:
            DataFrame with prices if successful, None if fetch fails
        """
        for attempt in range(max_retries):
            try:
                logger.debug(f"Fetching {ticker} (attempt {attempt + 1}/{max_retries})")
                data = yf.download(
                    ticker,
                    start=start_date,
                    end=end_date,
                    interval="1mo",
                    progress=False,
                )

                if data.empty:
                    logger.warning(f"No data returned for {ticker}")
                    return None

                data = data.reset_index()
                
                # Handle MultiIndex columns (returned by yfinance for some tickers)
                if isinstance(data.columns, pd.MultiIndex):
                    # Flatten multi-level column names
                    data.columns = ['_'.join(col).strip() if col[1] else col[0] for col in data.columns.values]
                
                # Convert column names to lowercase
                data.columns = data.columns.str.lower().str.replace(" ", "_").str.replace("_gc=f", "").str.replace("_si=f", "").str.replace("_pl=f", "").str.replace("_pa=f", "")
                
                data["ticker"] = ticker

                # Find the price column (could be 'close', 'close_gc=f', etc.)
                price_col = None
                if "close" in data.columns:
                    price_col = "close"
                elif "adj close" in data.columns or "adj_close" in data.columns:
                    price_col = "adj_close" if "adj_close" in data.columns else "adj close"
                
                if price_col:
                    data = data.rename(columns={price_col: "price_per_ounce"})
                else:
                    # If no standard price col, try to find any column with "close"
                    close_cols = [col for col in data.columns if "close" in col.lower()]
                    if close_cols:
                        data = data.rename(columns={close_cols[0]: "price_per_ounce"})
                    else:
                        logger.warning(f"No price column found for {ticker}")
                        return None

                logger.info(f"Successfully fetched {len(data)} records for {ticker}")
                return data

            except Exception as e:
                logger.debug(
                    f"Attempt {attempt + 1} failed for {ticker}: {str(e)}"
                )
                if attempt < max_retries - 1:
                    import time

                    delay = 2 ** attempt
                    logger.debug(f"Retrying {ticker} in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Failed to fetch {ticker} after {max_retries} attempts: {str(e)}"
                    )
                    return None

        return None

    def compute_market_cap(
        self, ticker: str, price_df: pd.DataFrame, supply_ounces: float
    ) -> pd.DataFrame:
        """
        Compute market cap from price and supply.

        Args:
            ticker: Metal ticker symbol (for logging)
            price_df: DataFrame with price data
            supply_ounces: Total supply in ounces (fixed)

        Returns:
            DataFrame with added market_cap column
        """
        try:
            price_df = price_df.copy()

            # Get the price column (might be 'close' or 'price_per_ounce')
            price_col = None
            for col in ["price_per_ounce", "close", "adj_close"]:
                if col in price_df.columns:
                    price_col = col
                    break

            if price_col is None:
                logger.error(f"No price column found for {ticker}")
                return price_df

            # Calculate market cap: price per ounce * supply ounces
            price_df["market_cap"] = price_df[price_col] * supply_ounces

            logger.debug(
                f"Computed market cap for {ticker}: avg=${price_df['market_cap'].mean():,.0f}"
            )
            return price_df

        except Exception as e:
            logger.error(f"Failed to compute market cap for {ticker}: {str(e)}")
            return price_df

    def process_batch(
        self,
        metals_df: pd.DataFrame,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """
        Fetch and process prices for all metals.

        Args:
            metals_df: DataFrame with metal config (ticker, supply_ounces, etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Combined DataFrame with OHLCV and market cap for all metals
        """
        logger.info(
            f"Starting batch fetch for {len(metals_df)} metals ({start_date} to {end_date})"
        )

        all_dfs = []

        for idx, row in tqdm(
            metals_df.iterrows(),
            total=len(metals_df),
            desc="Fetching metals data",
            unit="metal",
        ):
            ticker = row["ticker"]
            name = row["name"]
            supply_ounces = row["supply_ounces"]

            # Fetch prices
            price_df = self.fetch_metal_prices(ticker, start_date, end_date)

            if price_df is None or price_df.empty:
                logger.warning(f"No price data for {ticker} ({name})")
                self.fetch_results["failed"].append(ticker)
                continue

            # Add metal name
            price_df["name"] = name

            # Compute market cap
            price_df = self.compute_market_cap(ticker, price_df, supply_ounces)

            # Check for data gaps (forward fill)
            original_count = len(price_df)
            if "date" in price_df.columns:
                price_df["date"] = pd.to_datetime(price_df["date"])
                # Forward fill to handle gaps
                price_df = price_df.sort_values("date").ffill()

                gap_count = len(price_df) - original_count
                if gap_count > 0:
                    self.fetch_results["data_gaps"][ticker] = gap_count
                    logger.info(
                        f"Forward-filled {gap_count} missing values for {ticker}"
                    )

            all_dfs.append(price_df)
            self.fetch_results["successful"].append(ticker)

        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            logger.info(f"Combined {len(all_dfs)} metal datasets")
            return combined_df
        else:
            logger.warning("No successful metal price fetches")
            return pd.DataFrame()

    def save_outputs(
        self,
        data_df: pd.DataFrame,
        start_date: str,
        end_date: str,
        output_filename: str = "metals_monthly.csv",
        metadata_filename: str = "metals_fetch_metadata.json",
    ) -> None:
        """
        Save CSV data and metadata JSON.

        Args:
            data_df: DataFrame with price and market cap data
            start_date: Start date used for fetch
            end_date: End date used for fetch
            output_filename: Name of CSV output file
            metadata_filename: Name of JSON metadata file
        """
        # Select and reorder columns for output
        output_cols = ["date", "ticker", "name", "price_per_ounce", "market_cap"]
        available_cols = [c for c in output_cols if c in data_df.columns]
        output_df = data_df[available_cols]

        # Save CSV
        csv_path = self.output_dir / output_filename
        output_df.to_csv(csv_path, index=False)
        logger.info(f"Saved {len(output_df)} records to {csv_path}")

        # Save metadata JSON
        metadata = {
            "start_date": start_date,
            "end_date": end_date,
            "num_records": len(output_df),
            "num_successful": len(self.fetch_results["successful"]),
            "num_failed": len(self.fetch_results["failed"]),
            "successful_metals": self.fetch_results["successful"],
            "failed_metals": self.fetch_results["failed"],
            "data_gaps": self.fetch_results["data_gaps"],
            "sources": ["yfinance"],
            "timestamp": datetime.now().isoformat(),
            "data_columns": list(output_df.columns),
            "notes": "Market cap computed as: price_per_ounce * supply_ounces (supply from config)",
        }

        metadata_path = self.output_dir / metadata_filename
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to {metadata_path}")


def main(
    start_date: str = "2016-01-01",
    end_date: str = "2026-02-24",
    output_dir: str = "data/raw",
) -> int:
    """
    Main execution function.

    Args:
        start_date: Start date for data fetch (YYYY-MM-DD)
        end_date: End date for data fetch (YYYY-MM-DD)
        output_dir: Directory for output files

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        fetcher = MetalsPriceFetcher(output_dir=output_dir)
        metals_df = fetcher.read_config()

        if metals_df.empty:
            logger.error("No metals found in config")
            return 1

        # Fetch and process data
        combined_df = fetcher.process_batch(metals_df, start_date, end_date)

        if combined_df.empty:
            logger.error("No data retrieved from any metal")
            return 1

        # Save outputs
        fetcher.save_outputs(combined_df, start_date, end_date)

        logger.info("✓ Phase 1 metals data fetch completed successfully")
        return 0

    except Exception as e:
        logger.exception(f"Fatal error in main: {str(e)}")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch precious metals price data from yfinance"
    )
    parser.add_argument(
        "--start_date",
        type=str,
        default="2016-01-01",
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end_date",
        type=str,
        default="2026-02-24",
        help="End date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/raw",
        help="Output directory for CSV files",
    )

    args = parser.parse_args()

    exit_code = main(
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=args.output_dir,
    )
    exit(exit_code)


if __name__ == "__main__":
    main()
