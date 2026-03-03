#!/usr/bin/env python3
"""
Phase 1: Fetch crypto market cap data from CoinGecko API.

This module fetches historical monthly market cap, price, and circulating supply
data for cryptocurrencies defined in config/crypto_list.csv using the free
CoinGecko API with rate limiting.

Features:
- CoinGecko /market_chart/range endpoint for historical data
- Rate-limited requests (1 second delay) to respect free API limits
- Automatic retry on 429 (Too Many Requests) responses
- Concurrent batch fetching with backoff
- Progress tracking with tqdm
- Comprehensive logging to file and console
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiohttp
import pandas as pd
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
file_handler = logging.FileHandler(LOGS_DIR / "01b_fetch_crypto.log")
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

# CoinGecko API configuration
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"
REQUEST_DELAY = 1.0  # seconds - respect free API rate limits
REQUEST_TIMEOUT = 30  # seconds


class CryptoMarketCapFetcher:
    """Fetches and processes crypto market cap data from CoinGecko API."""

    def __init__(
        self,
        config_path: str = "config/crypto_list.csv",
        output_dir: str = "data/raw",
    ):
        """
        Initialize the CryptoMarketCapFetcher.

        Args:
            config_path: Path to crypto_list.csv file
            output_dir: Directory to save output CSV and metadata files
        """
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.crypto_df: Optional[pd.DataFrame] = None
        self.fetch_results: Dict[str, any] = {
            "successful": [],
            "failed": [],
            "skipped": [],
        }
        self.last_request_time = 0
        logger.info(f"Initialized CryptoMarketCapFetcher with output dir: {output_dir}")

    def read_config(self) -> List[Dict[str, str]]:
        """
        Load crypto configuration from crypto_list.csv.

        Returns:
            List of dictionaries with id, symbol, name, weight, market_cap_rank

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        self.crypto_df = pd.read_csv(self.config_path)
        logger.info(f"Loaded {len(self.crypto_df)} cryptos from {self.config_path}")
        logger.debug(f"Crypto list: {self.crypto_df['symbol'].tolist()}")

        # Convert to list of dicts for easier handling
        cryptos = self.crypto_df.to_dict("records")
        return cryptos

    async def _rate_limited_request(
        self,
        session: aiohttp.ClientSession,
        url: str,
        max_retries: int = 3,
    ) -> Optional[Dict]:
        """
        Make a rate-limited HTTP request with retry logic.

        Args:
            session: aiohttp ClientSession
            url: URL to fetch
            max_retries: Maximum number of retry attempts

        Returns:
            JSON response dict if successful, None if all retries failed
        """
        # Enforce request delay to respect API rate limits
        time_since_last = time.time() - self.last_request_time
        if time_since_last < REQUEST_DELAY:
            await asyncio.sleep(REQUEST_DELAY - time_since_last)

        for attempt in range(max_retries):
            try:
                self.last_request_time = time.time()
                logger.debug(f"API request (attempt {attempt + 1}/{max_retries}): {url}")

                async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
                    if response.status == 429:  # Too Many Requests
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning(
                            f"Rate limited (429), retrying after {retry_after}s"
                        )
                        await asyncio.sleep(retry_after)
                        continue

                    if response.status != 200:
                        logger.warning(f"API returned status {response.status}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        return None

                    data = await response.json()
                    logger.debug(f"Successfully retrieved data from {url}")
                    return data

            except asyncio.TimeoutError:
                logger.warning(f"Request timeout for {url} (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Request error for {url}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None

    async def fetch_market_cap_history(
        self,
        coin_id: str,
        symbol: str,
        start_date: str,
        end_date: str,
        session: aiohttp.ClientSession,
    ) -> Optional[pd.DataFrame]:
        """
        Fetch market cap history for a single crypto from CoinGecko.

        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin')
            symbol: Coin symbol (e.g., 'BTC')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            session: aiohttp ClientSession

        Returns:
            DataFrame with market_cap, price, circulating_supply if successful,
            None if fetch fails
        """
        try:
            # Convert dates to Unix timestamps
            from datetime import datetime as dt

            start_ts = int(dt.strptime(start_date, "%Y-%m-%d").timestamp())
            end_ts = int(dt.strptime(end_date, "%Y-%m-%d").timestamp())

            url = (
                f"{COINGECKO_API_BASE}/coins/{coin_id}/market_chart/range"
                f"?vs_currency=usd&from={start_ts}&to={end_ts}"
            )

            logger.debug(f"Fetching market cap history for {symbol} (ID: {coin_id})")
            data = await self._rate_limited_request(session, url)

            if data is None:
                logger.error(f"No data retrieved for {symbol}")
                return None

            # Extract market caps, prices, and circulating supply from API response
            market_caps = data.get("market_caps", [])
            prices = data.get("prices", [])
            supplies = data.get("circulating_supplies", [])

            if not market_caps or not prices:
                logger.warning(f"Incomplete data for {symbol}: missing market_caps or prices")
                return None

            # Create DataFrame from market cap and price data
            records = []
            for i, (market_cap_entry, price_entry) in enumerate(
                zip(market_caps, prices)
            ):
                # Extract timestamps and values
                ts = market_cap_entry[0] / 1000  # Convert to seconds
                market_cap = market_cap_entry[1]
                price = price_entry[1]

                # Get supply if available
                supply = None
                if i < len(supplies):
                    supply = supplies[i][1]

                # Convert timestamp back to datetime
                date = dt.fromtimestamp(ts).date()

                records.append(
                    {
                        "date": date,
                        "coin_id": coin_id,
                        "symbol": symbol,
                        "market_cap": market_cap,
                        "price": price,
                        "circulating_supply": supply,
                    }
                )

            df = pd.DataFrame(records)
            logger.info(f"Retrieved {len(df)} historical records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch market cap history for {symbol}: {str(e)}")
            return None

    async def batch_fetch_all_cryptos(
        self,
        cryptos: List[Dict[str, str]],
        start_date: str,
        end_date: str,
        max_concurrent: int = 2,  # Conservative rate limiting
    ) -> Tuple[pd.DataFrame, Dict[str, any]]:
        """
        Fetch market cap history for multiple cryptos concurrently.

        Args:
            cryptos: List of crypto config dicts (id, symbol, name, etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_concurrent: Maximum concurrent requests

        Returns:
            Tuple of (combined DataFrame, results dictionary)
        """
        logger.info(
            f"Starting batch fetch for {len(cryptos)} cryptos ({start_date} to {end_date})"
        )

        connector = aiohttp.TCPConnector(limit=max_concurrent)
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def fetch_with_semaphore(crypto: Dict[str, str]) -> Tuple[str, Optional[pd.DataFrame]]:
                async with semaphore:
                    df = await self.fetch_market_cap_history(
                        crypto["id"],
                        crypto["symbol"],
                        start_date,
                        end_date,
                        session,
                    )
                    return crypto["symbol"], df

            tasks = [fetch_with_semaphore(c) for c in cryptos]
            results = []

            for coro in tqdm(
                asyncio.as_completed(tasks),
                total=len(tasks),
                desc="Fetching crypto data",
                unit="coin",
            ):
                symbol, df = await coro
                results.append((symbol, df))

                if df is not None:
                    self.fetch_results["successful"].append(symbol)
                else:
                    self.fetch_results["failed"].append(symbol)

            # Combine all successful results
            dfs = [df for _, df in results if df is not None]
            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                logger.info(
                    f"Combined {len(dfs)} successful fetches into single DataFrame"
                )
                return combined_df, self.fetch_results
            else:
                logger.warning("No successful fetches - returning empty DataFrame")
                return pd.DataFrame(), self.fetch_results

    def cache_results(
        self,
        data_df: pd.DataFrame,
        start_date: str,
        end_date: str,
        csv_filename: str = "crypto_monthly.csv",
        json_filename: str = "crypto_fetch_metadata.json",
    ) -> None:
        """
        Save data to both CSV and JSON formats.

        Args:
            data_df: DataFrame with market cap data
            start_date: Start date used for fetch
            end_date: End date used for fetch
            csv_filename: Name of CSV output file
            json_filename: Name of JSON metadata file
        """
        # Save CSV
        csv_path = self.output_dir / csv_filename
        data_df.to_csv(csv_path, index=False)
        logger.info(f"Saved {len(data_df)} records to {csv_path}")

        # Save metadata JSON
        metadata = {
            "start_date": start_date,
            "end_date": end_date,
            "num_records": len(data_df),
            "num_successful": len(self.fetch_results["successful"]),
            "num_failed": len(self.fetch_results["failed"]),
            "successful_coins": self.fetch_results["successful"],
            "failed_coins": self.fetch_results["failed"],
            "sources": ["CoinGecko API (free tier)"],
            "timestamp": datetime.now().isoformat(),
            "data_columns": list(data_df.columns),
            "api_base": COINGECKO_API_BASE,
            "request_delay_seconds": REQUEST_DELAY,
        }

        json_path = self.output_dir / json_filename
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to {json_path}")


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
        fetcher = CryptoMarketCapFetcher(output_dir=output_dir)
        cryptos = fetcher.read_config()

        if not cryptos:
            logger.error("No cryptos found in config")
            return 1

        # Fetch data concurrently
        combined_df, results = await fetcher.batch_fetch_all_cryptos(
            cryptos, start_date, end_date
        )

        if combined_df.empty:
            logger.error("No data retrieved from any crypto")
            return 1

        # Cache results to CSV and JSON
        fetcher.cache_results(combined_df, start_date, end_date)

        logger.info("✓ Phase 1 crypto data fetch completed successfully")
        return 0

    except Exception as e:
        logger.exception(f"Fatal error in main: {str(e)}")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch crypto market cap data from CoinGecko API"
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


if __name__ == "__main__":
    main()
