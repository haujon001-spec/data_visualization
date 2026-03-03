#!/usr/bin/env python3
"""
Phase 1: Fetch company stock data using yfinance.

This module fetches historical monthly stock price data for companies defined
in config/universe_companies.csv and saves both CSV and metadata JSON outputs.

Features:
- Async/concurrent ticker fetching using asyncio
- Automatic retry logic with exponential backoff
- Progress tracking with tqdm
- Shares outstanding metadata collection
- Comprehensive logging to file and console
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
file_handler = logging.FileHandler(LOGS_DIR / "01_fetch_companies.log")
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


class CompanyDataFetcher:
    """Fetches and processes company stock price data from yfinance."""

    def __init__(
        self,
        config_path: str = "config/universe_companies.csv",
        output_dir: str = "data/raw",
    ):
        """
        Initialize the CompanyDataFetcher.

        Args:
            config_path: Path to universe_companies.csv file
            output_dir: Directory to save output CSV and metadata files
        """
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.companies_df: Optional[pd.DataFrame] = None
        self.fetch_results: Dict[str, any] = {
            "successful": [],
            "failed": [],
            "skipped": [],
        }
        logger.info(f"Initialized CompanyDataFetcher with output dir: {output_dir}")

    def read_config(self) -> List[str]:
        """
        Load and filter companies from universe_companies.csv.

        Returns:
            List of tickers to fetch (filtered by include_flag=true)

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        self.companies_df = pd.read_csv(self.config_path)
        logger.info(
            f"Loaded config with {len(self.companies_df)} companies from {self.config_path}"
        )

        # Filter by include_flag = true
        filtered_df = self.companies_df[
            self.companies_df["include_flag"].astype(str).str.lower() == "true"
        ]
        tickers = filtered_df["ticker"].dropna().unique().tolist()

        logger.info(f"Filtered to {len(tickers)} companies with include_flag=true")
        logger.debug(f"Tickers: {tickers}")

        return tickers

    async def fetch_ticker_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ) -> Optional[pd.DataFrame]:
        """
        Fetch ticker data with retry logic.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            max_retries: Maximum number of retry attempts
            retry_delay: Delay in seconds between retries (exponential backoff)

        Returns:
            DataFrame with OHLCV data if successful, None if all retries failed
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
                data["ticker"] = ticker

                # Handle MultiIndex columns (returned by yfinance for some tickers)
                if isinstance(data.columns, pd.MultiIndex):
                    # Flatten multi-level column names
                    data.columns = ['_'.join(col).strip() if col[1] else col[0] for col in data.columns.values]

                # Ensure required columns exist
                required_cols = [
                    "Date",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                    "Adj Close",
                ]
                if "Adj Close" not in data.columns:
                    data["Adj Close"] = data.get("Close", 0)

                # Standardize column names
                data.columns = (
                    data.columns.str.lower().str.replace(" ", "_")
                )
                data = data.rename(columns={"adj_close": "adjusted_close"})

                logger.info(
                    f"Successfully fetched {len(data)} records for {ticker}"
                )
                return data

            except Exception as e:
                logger.debug(
                    f"Attempt {attempt + 1} failed for {ticker}: {str(e)}"
                )
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.debug(f"Retrying {ticker} in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Failed to fetch {ticker} after {max_retries} attempts: {str(e)}")
                    return None

        return None

    async def process_batch(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        max_concurrent: int = 5,
    ) -> Tuple[pd.DataFrame, Dict[str, any]]:
        """
        Fetch data for multiple tickers concurrently.

        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            max_concurrent: Maximum concurrent fetch operations

        Returns:
            Tuple of (combined DataFrame, results dictionary)
        """
        logger.info(
            f"Starting batch fetch for {len(tickers)} tickers ({start_date} to {end_date})"
        )

        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(ticker: str) -> Tuple[str, Optional[pd.DataFrame]]:
            async with semaphore:
                data = await self.fetch_ticker_data(ticker, start_date, end_date)
                return ticker, data

        # Show progress bar for async operations
        tasks = [fetch_with_semaphore(t) for t in tickers]
        results = []

        for coro in tqdm(
            asyncio.as_completed(tasks),
            total=len(tasks),
            desc="Fetching company data",
            unit="ticker",
        ):
            ticker, data = await coro
            results.append((ticker, data))

            if data is not None:
                self.fetch_results["successful"].append(ticker)
            else:
                self.fetch_results["failed"].append(ticker)

        # Combine all successful results
        dfs = [data for _, data in results if data is not None]
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Combined {len(dfs)} successful fetches into single DataFrame")
            return combined_df, self.fetch_results
        else:
            logger.warning("No successful fetches - returning empty DataFrame")
            return pd.DataFrame(), self.fetch_results

    def add_shares_outstanding(self, ticker: str) -> Optional[Dict[str, any]]:
        """
        Fetch shares outstanding for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with shares outstanding data, or None if fetch fails
        """
        try:
            logger.debug(f"Fetching shares outstanding for {ticker}")
            info = yf.Ticker(ticker).info
            shares = info.get("sharesOutstanding")
            
            if shares is None:
                logger.warning(f"No shares outstanding data available for {ticker}")
                return None

            result = {
                "ticker": ticker,
                "shares_outstanding": shares,
                "last_update": datetime.now().isoformat(),
            }
            logger.debug(f"Shares outstanding for {ticker}: {shares}")
            return result

        except Exception as e:
            logger.error(f"Failed to fetch shares outstanding for {ticker}: {str(e)}")
            return None

    async def fetch_all_shares_outstanding(
        self, tickers: List[str], max_concurrent: int = 3
    ) -> pd.DataFrame:
        """
        Fetch shares outstanding for multiple tickers concurrently.

        Args:
            tickers: List of ticker symbols
            max_concurrent: Maximum concurrent fetch operations

        Returns:
            DataFrame with shares outstanding data
        """
        logger.info(f"Fetching shares outstanding for {len(tickers)} tickers")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(ticker: str) -> Optional[Dict[str, any]]:
            async with semaphore:
                return self.add_shares_outstanding(ticker)

        tasks = [fetch_with_semaphore(t) for t in tickers]
        results = []

        for coro in tqdm(
            asyncio.as_completed(tasks),
            total=len(tasks),
            desc="Fetching shares outstanding",
            unit="ticker",
        ):
            result = await coro
            if result is not None:
                results.append(result)

        if results:
            shares_df = pd.DataFrame(results)
            logger.info(f"Retrieved shares outstanding for {len(results)} tickers")
            return shares_df
        else:
            logger.warning("No shares outstanding data retrieved")
            return pd.DataFrame()

    def save_outputs(
        self,
        data_df: pd.DataFrame,
        start_date: str,
        end_date: str,
        output_filename: str = "companies_monthly.csv",
        metadata_filename: str = "companies_fetch_metadata.json",
    ) -> None:
        """
        Save CSV data and metadata JSON.

        Args:
            data_df: DataFrame with OHLCV data
            start_date: Start date used for fetch
            end_date: End date used for fetch
            output_filename: Name of CSV output file
            metadata_filename: Name of JSON metadata file
        """
        # Save CSV
        csv_path = self.output_dir / output_filename
        data_df.to_csv(csv_path, index=False)
        logger.info(f"Saved {len(data_df)} records to {csv_path}")

        # Save metadata JSON
        metadata = {
            "start_date": start_date,
            "end_date": end_date,
            "num_records": len(data_df),
            "num_successful": len(self.fetch_results["successful"]),
            "num_failed": len(self.fetch_results["failed"]),
            "successful_tickers": self.fetch_results["successful"],
            "failed_tickers": self.fetch_results["failed"],
            "sources": ["yfinance"],
            "timestamp": datetime.now().isoformat(),
            "data_columns": list(data_df.columns),
        }

        metadata_path = self.output_dir / metadata_filename
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to {metadata_path}")

    def save_shares_outstanding(
        self,
        shares_df: pd.DataFrame,
        output_filename: str = "shares_outstanding.csv",
    ) -> None:
        """
        Save shares outstanding data to CSV.

        Args:
            shares_df: DataFrame with shares outstanding data
            output_filename: Name of CSV output file
        """
        if shares_df.empty:
            logger.warning("No shares outstanding data to save")
            return

        csv_path = Path("config") / output_filename
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        shares_df.to_csv(csv_path, index=False)
        logger.info(f"Saved shares outstanding to {csv_path}")


async def main(
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
        fetcher = CompanyDataFetcher(output_dir=output_dir)
        tickers = fetcher.read_config()

        if not tickers:
            logger.error("No tickers found with include_flag=true")
            return 1

        # Fetch data concurrently
        combined_df, results = await fetcher.process_batch(tickers, start_date, end_date)

        if combined_df.empty:
            logger.error("No data retrieved from any ticker")
            return 1

        # Save CSV and metadata
        fetcher.save_outputs(combined_df, start_date, end_date)

        # Fetch and save shares outstanding
        successful_tickers = results["successful"]
        if successful_tickers:
            shares_df = await fetcher.fetch_all_shares_outstanding(successful_tickers)
            fetcher.save_shares_outstanding(shares_df)

        logger.info("✓ Phase 1 company data fetch completed successfully")
        return 0

    except Exception as e:
        logger.exception(f"Fatal error in main: {str(e)}")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch company stock data from yfinance"
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

    # Run async main
    exit_code = asyncio.run(
        main(
            start_date=args.start_date,
            end_date=args.end_date,
            output_dir=args.output_dir,
        )
    )
    exit(exit_code)
