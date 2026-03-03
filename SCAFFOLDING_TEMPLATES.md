# Global Top-20 Market Cap Evolution Dashboard - Scaffolding

## 1. CONFIG CSV TEMPLATES

### universe_companies.csv
```csv
ticker,company_name,sector,region,include_flag,notes
AAPL,Apple Inc.,Information Technology,US,1,
MSFT,Microsoft Corporation,Information Technology,US,1,
NVDA,NVIDIA Corporation,Information Technology,US,1,
GOOGL,Alphabet Inc.,Communication Services,US,1,
AMZN,Amazon.com Inc.,Consumer Discretionary,US,1,
TSLA,Tesla Inc.,Consumer Discretionary,US,1,
BRK.B,Berkshire Hathaway Inc.,Financials,US,1,
JNJ,Johnson & Johnson,Health Care,US,1,
V,Visa Inc.,Financials,US,1,
WMT,Walmart Inc.,Consumer Staples,US,1,
JPM,JPMorgan Chase & Co.,Financials,US,1,
XOM,Exxon Mobil Corporation,Energy,US,1,
UNH,UnitedHealth Group Inc.,Health Care,US,1,
COST,Costco Wholesale Corporation,Consumer Staples,US,1,
BABA,Alibaba Group,Consumer Discretionary,China,1,ADR
TSM,Taiwan Semiconductor,Information Technology,Asia,1,
ORCL,Oracle Corporation,Information Technology,US,1,
LLY,Eli Lilly and Company,Health Care,US,1,
NVO,Novo Nordisk,Health Care,EU,1,
SAP,SAP SE,Software,EU,1,
```

### crypto_list.csv
```csv
id,symbol,name,weight,market_cap_rank
bitcoin,BTC,Bitcoin,0.50,1
ethereum,ETH,Ethereum,0.20,2
binancecoin,BNB,Binance Coin,0.08,3
ripple,XRP,Ripple,0.07,4
solana,SOL,Solana,0.05,5
```

### precious_metals_supply.csv
```csv
ticker,name,ounces_supply,supply_source,update_frequency
GOLD,Gold,6590000000,World Gold Council,monthly
SILVER,Silver,28000000000,US Geological Survey,annual
PLATINUM,Platinum,260000000,USGS,annual
PALLADIUM,Palladium,185000000,USGS,annual
```

### vps_list.csv
```csv
name,host,ssh_user,ssh_port,ssh_key_path,http_check_url,region,status
fetch-primary,203.0.113.10,deploy,22,~/.ssh/do_fetch_key,http://203.0.113.10/health,us-east-1,active
fetch-secondary,203.0.113.11,ubuntu,22,~/.ssh/do_fetch_key,http://203.0.113.11/health,eu-west-1,active
index-calc,203.0.113.12,ubuntu,22,~/.ssh/do_index_key,,us-west-2,active
```

---

## 2. PYTHON REQUIREMENTS (2026)

```txt
pandas==2.2.0
yfinance==0.2.38
requests==2.31.0
plotly==5.18.0
python-dateutil==2.8.2
pyarrow==15.0.0
paramiko==3.4.0
python-dotenv==1.0.0
pydantic==2.5.2
pydantic-settings==2.1.0
httpx==0.25.2
aiohttp==3.9.1
tenacity==8.2.3
tqdm==4.66.1
pytest==7.4.3
pytest-asyncio==0.21.1
```

---

## 3. SCRIPT TEMPLATES

### 00_validate_sources.py

```python
"""
Validate connectivity to yfinance, CoinGecko API, and VPS SSH/HTTP endpoints.
"""

import asyncio
import logging
from typing import Dict, List, Tuple
from pathlib import Path


async def validate_yfinance() -> Tuple[bool, str]:
    """
    Test yfinance connectivity with sample ticker request.
    
    Returns:
        Tuple[bool, str]: (success, message)
        - success=True: "yfinance connectivity OK, fetched BTC=XXXX"
        - success=False: "yfinance failed: {error message}"
    """
    pass


async def validate_coingecko() -> Tuple[bool, str]:
    """
    Test CoinGecko API with sample cryptocurrency data request.
    
    Returns:
        Tuple[bool, str]: (success, message)
        - success=True: "CoinGecko API OK, fetched {count} cryptos"
        - success=False: "CoinGecko API failed: {error message}"
    """
    pass


async def validate_vps_connectivity(vps_config_path: str) -> Dict[str, Tuple[bool, str]]:
    """
    Test SSH and HTTP connectivity to all VPS hosts from config.
    
    Args:
        vps_config_path: Path to vps_list.csv
    
    Returns:
        Dict[str, Tuple[bool, str]]: {vps_name: (success, message)}
        Example: {"fetch-primary": (True, "SSH OK, HTTP 200")}
    """
    pass


def validate_data_sources(config_dir: str) -> bool:
    """
    Master validation function - runs all connectivity tests.
    
    Args:
        config_dir: Directory path containing config CSVs
    
    Returns:
        bool: True if all validations pass
    
    Success output:
        ✓ yfinance connectivity OK
        ✓ CoinGecko API OK
        ✓ VPS fetch-primary: SSH OK, HTTP 200
        ✓ VPS fetch-secondary: SSH OK, HTTP 200
        ✓ All validations passed
    """
    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate data source connectivity")
    parser.add_argument("--config-dir", default="config", help="Config directory path")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    
    args = parser.parse_args()
    validate_data_sources(args.config_dir)
```

### 01_fetch_companies.py

```python
"""
Multi-ticker monthly historical stock data downloader using yfinance.
Fetches OHLCV data for all enabled companies in universe_companies.csv.
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging


class CompanyDataFetcher:
    """Wrapper for efficient multi-ticker yfinance data retrieval."""
    
    def __init__(self, config_path: str, output_dir: str):
        """
        Initialize fetcher with company universe.
        
        Args:
            config_path: Path to universe_companies.csv
            output_dir: Output directory for parquet files
        """
        pass
    
    def load_universe(self) -> pd.DataFrame:
        """
        Load and validate company universe config.
        
        Returns:
            pd.DataFrame: Filtered to include_flag==1 only
        """
        pass
    
    def fetch_ticker_data(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1mo"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data for single ticker.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            interval: Data interval (default "1mo" for monthly)
        
        Returns:
            Optional[pd.DataFrame]: OHLCV data or None if fetch failed
        """
        pass
    
    def fetch_all_tickers(self, start_date: datetime, end_date: datetime) -> Dict[str, pd.DataFrame]:
        """
        Batch fetch all tickers with error handling and retry logic.
        
        Args:
            start_date: Start date for all tickers
            end_date: End date for all tickers
        
        Returns:
            Dict[str, pd.DataFrame]: {ticker: ohlcv_dataframe}
        
        Expected side effects:
            - Save individual parquet files to output_dir
            - Log fetch progress and failures
            - Return combined results
        """
        pass
    
    def save_to_parquet(self, ticker: str, data: pd.DataFrame) -> bool:
        """
        Save ticker data to parquet with metadata.
        
        Args:
            ticker: Ticker symbol
            data: OHLCV DataFrame
        
        Returns:
            bool: True if save successful
        """
        pass


def fetch_companies(
    config_path: str,
    output_dir: str,
    months_back: int = 12,
    verbose: bool = False
) -> Dict[str, str]:
    """
    Main entry point for company data fetching.
    
    Args:
        config_path: Path to universe_companies.csv
        output_dir: Parquet output directory
        months_back: Months of historical data to fetch (default 12)
        verbose: Enable verbose logging
    
    Returns:
        Dict[str, str]: Fetch summary {status: message}
        Example: {"success": "20/20 tickers fetched", "failed": ""}
    
    Success example:
        ✓ Loaded 20 companies from universe
        ✓ Fetching 12 months of data (2025-02-01 to 2026-02-01)
        ✓ Fetched AAPL: 12 months, 12 records
        ✓ Fetched MSFT: 12 months, 12 records
        ...
        ✓ Completed: 20/20 tickers successful, 0 failed
    """
    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch company stock data")
    parser.add_argument("--config", default="config/universe_companies.csv")
    parser.add_argument("--output", default="data/raw/stocks")
    parser.add_argument("--months", type=int, default=12)
    parser.add_argument("--verbose", action="store_true")
    
    args = parser.parse_args()
    fetch_companies(args.config, args.output, args.months, args.verbose)
```

### 01b_fetch_crypto.py

```python
"""
Market cap historical data fetcher for top cryptocurrencies via CoinGecko API.
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging


class CryptoMarketCapFetcher:
    """Wrapper for CoinGecko API cryptocurrency market cap data retrieval."""
    
    def __init__(self, config_path: str, output_dir: str, api_base: str = "https://api.coingecko.com/api/v3"):
        """
        Initialize fetcher with crypto universe.
        
        Args:
            config_path: Path to crypto_list.csv
            output_dir: Output directory for parquet files
            api_base: CoinGecko API base URL
        """
        pass
    
    def load_universe(self) -> pd.DataFrame:
        """
        Load and validate crypto universe config.
        
        Returns:
            pd.DataFrame: Cryptocurrency list with id, symbol, name, weight
        """
        pass
    
    async def fetch_crypto_history(
        self,
        crypto_id: str,
        vs_currency: str = "usd",
        days: int = 365,
        interval: str = "monthly"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical market cap data for single cryptocurrency.
        
        Args:
            crypto_id: CoinGecko crypto ID (e.g., "bitcoin")
            vs_currency: Currency code (default "usd")
            days: Historical days to fetch
            interval: Data interval ("monthly", "daily", etc.)
        
        Returns:
            Optional[pd.DataFrame]: Historical data with timestamp, market_cap fields
        """
        pass
    
    async def fetch_all_cryptos(
        self,
        vs_currency: str = "usd",
        days: int = 365
    ) -> Dict[str, pd.DataFrame]:
        """
        Batch async fetch all cryptos with rate limiting.
        
        Args:
            vs_currency: Currency code
            days: Historical days
        
        Returns:
            Dict[str, pd.DataFrame]: {symbol: historical_dataframe}
        
        Expected side effects:
            - Save individual parquet files to output_dir
            - Log fetch progress with rate limit handling
            - Return combined results
        """
        pass
    
    def save_to_parquet(self, symbol: str, data: pd.DataFrame) -> bool:
        """
        Save crypto data to parquet with metadata.
        
        Args:
            symbol: Cryptocurrency symbol (BTC, ETH, etc.)
            data: Historical market cap DataFrame
        
        Returns:
            bool: True if save successful
        """
        pass


def fetch_cryptos(
    config_path: str,
    output_dir: str,
    days: int = 365,
    currency: str = "usd",
    verbose: bool = False
) -> Dict[str, str]:
    """
    Main entry point for crypto market cap data fetching.
    
    Args:
        config_path: Path to crypto_list.csv
        output_dir: Parquet output directory
        days: Historical days to fetch
        currency: Base currency code
        verbose: Enable verbose logging
    
    Returns:
        Dict[str, str]: Fetch summary {status: message}
        Example: {"success": "5/5 cryptos fetched", "rate_limited": false}
    
    Success example:
        ✓ Loaded 5 cryptocurrencies from universe
        ✓ Fetching 365 days of market cap history
        ✓ Fetched BTC: 365 daily records
        ✓ Fetched ETH: 365 daily records
        ...
        ✓ Completed: 5/5 cryptos successful, 0 failed
    """
    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch cryptocurrency market cap data")
    parser.add_argument("--config", default="config/crypto_list.csv")
    parser.add_argument("--output", default="data/raw/crypto")
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--currency", default="usd")
    parser.add_argument("--verbose", action="store_true")
    
    args = parser.parse_args()
    asyncio.run(fetch_cryptos(args.config, args.output, args.days, args.currency, args.verbose))
```

### 01c_fetch_metals.py

```python
"""
Precious metals historical pricing data fetcher via yfinance commodity symbols.
Supports Gold, Silver, Platinum, Palladium from World Gold Council and USGS sources.
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging


class MetalsPriceFetcher:
    """Wrapper for precious metals pricing data retrieval."""
    
    def __init__(self, config_path: str, output_dir: str):
        """
        Initialize fetcher with metals universe.
        
        Args:
            config_path: Path to precious_metals_supply.csv
            output_dir: Output directory for parquet files
        """
        pass
    
    def load_universe(self) -> pd.DataFrame:
        """
        Load and validate metals universe config.
        
        Returns:
            pd.DataFrame: Metals list with ticker, name, ounces_supply, supply_source
        """
        pass
    
    def _get_yfinance_symbol(self, metal_name: str) -> str:
        """
        Map metal name to yfinance commodity ticker symbol.
        
        Args:
            metal_name: Metal name (Gold, Silver, etc.)
        
        Returns:
            str: yfinance ticker symbol (e.g., "GC=F" for Gold futures)
        """
        pass
    
    def fetch_metal_price(
        self,
        metal_name: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1mo"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical pricing data for single metal.
        
        Args:
            metal_name: Metal name (Gold, Silver, Platinum, Palladium)
            start_date: Start date for historical data
            end_date: End date for historical data
            interval: Data interval (default "1mo" for monthly)
        
        Returns:
            Optional[pd.DataFrame]: Price data with close, volume, or None if fetch failed
        """
        pass
    
    def fetch_all_metals(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, pd.DataFrame]:
        """
        Batch fetch all metals with error handling.
        
        Args:
            start_date: Start date for all metals
            end_date: End date for all metals
        
        Returns:
            Dict[str, pd.DataFrame]: {metal_name: price_dataframe}
        
        Expected side effects:
            - Save individual parquet files to output_dir
            - Log fetch progress and failures
            - Return combined results
        """
        pass
    
    def save_to_parquet(self, metal_name: str, data: pd.DataFrame) -> bool:
        """
        Save metal price data to parquet with metadata.
        
        Args:
            metal_name: Metal name
            data: Price DataFrame
        
        Returns:
            bool: True if save successful
        """
        pass


def fetch_metals(
    config_path: str,
    output_dir: str,
    months_back: int = 12,
    verbose: bool = False
) -> Dict[str, str]:
    """
    Main entry point for metals pricing data fetching.
    
    Args:
        config_path: Path to precious_metals_supply.csv
        output_dir: Parquet output directory
        months_back: Months of historical data to fetch (default 12)
        verbose: Enable verbose logging
    
    Returns:
        Dict[str, str]: Fetch summary {status: message}
        Example: {"success": "4/4 metals fetched", "failed": ""}
    
    Success example:
        ✓ Loaded 4 metals from universe
        ✓ Fetching 12 months of price data (2025-02-01 to 2026-02-01)
        ✓ Fetched Gold: 12 months, 12 records
        ✓ Fetched Silver: 12 months, 12 records
        ✓ Fetched Platinum: 12 months, 12 records
        ✓ Fetched Palladium: 12 months, 12 records
        ✓ Completed: 4/4 metals successful, 0 failed
    """
    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch precious metals pricing data")
    parser.add_argument("--config", default="config/precious_metals_supply.csv")
    parser.add_argument("--output", default="data/raw/metals")
    parser.add_argument("--months", type=int, default=12)
    parser.add_argument("--verbose", action="store_true")
    
    args = parser.parse_args()
    fetch_metals(args.config, args.output, args.months, args.verbose)
```
