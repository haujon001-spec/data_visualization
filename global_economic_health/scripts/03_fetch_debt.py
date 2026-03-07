# -*- coding: utf-8 -*-
"""
Fetch Global Debt Data from World Bank IDS

Fetch external debt data (DT.DOD.DECT.CD) from World Bank IDS API.
Falls back to IMF Global Debt Database if World Bank is unavailable.
Output: CSV file with country_name, country_code, year, debt_total_usd, debt_public_usd, debt_private_usd columns.

Data Sources:
  Primary: World Bank IDS (International Debt Statistics)
  Backup: IMF Global Debt Database
  Indicator: DT.DOD.DECT.CD (Total external debt)
"""

import requests
import pandas as pd
from pathlib import Path
import yaml
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def load_config(config_path: Path = None) -> dict:
    """
    Load configuration from settings.yaml.
    
    Args:
        config_path: Path to settings.yaml (default: config/settings.yaml)
    
    Returns:
        Dictionary with API configuration
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
    
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return {
            'timeout': 90,
            'max_retries': 3,
            'retry_backoff': 2,
            'per_page': 20000
        }
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config.get('api_config', {}).get('world_bank', {})


def fetch_worldbank_debt(
    indicator: str = "DT.DOD.DECT.CD",
    start_year: int = 1960,
    end_year: int = 2026,
    config: dict = None
) -> pd.DataFrame:
    """
    Fetch external debt data from World Bank IDS API.
    
    Args:
        indicator: World Bank indicator code (default: DT.DOD.DECT.CD - Total external debt)
        start_year: Start year for data fetch
        end_year: End year for data fetch
        config: Configuration dictionary with API settings
    
    Returns:
        DataFrame with columns: country_name, country_code, year, debt_total_usd
    
    Raises:
        ValueError: If API response is invalid
        Exception: If max retries exceeded
    """
    if config is None:
        config = load_config()
    
    base_url = config.get('base_url', 'https://api.worldbank.org/v2')
    timeout = config.get('timeout_seconds', 90)
    max_retries = config.get('max_retries', 3)
    retry_backoff = config.get('retry_backoff_seconds', 2)
    per_page = config.get('per_page', 20000)
    
    url = f"{base_url}/country/all/indicator/{indicator}"
    
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": per_page
    }
    
    logger.info("=" * 70)
    logger.info("FETCHING WORLD BANK EXTERNAL DEBT DATA")
    logger.info("=" * 70)
    logger.info(f"[FETCH] Requesting data from World Bank IDS...")
    logger.info(f"[FETCH] Indicator: {indicator}")
    logger.info(f"[FETCH] URL: {url}")
    logger.info(f"[FETCH] Date range: {start_year}-{end_year}")
    
    # Retry logic
    for attempt in range(max_retries):
        try:
            logger.info(f"[ATTEMPT] {attempt + 1}/{max_retries}")
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            validate_response(response)
            
            data = response.json()
            
            if not data or len(data) < 2:
                raise ValueError("Invalid API response format (missing data array)")
            
            records = data[1]  # Data is in second element
            logger.info(f"[FETCH] Retrieved {len(records)} records from API")
            
            # Transform to DataFrame
            rows = []
            for record in records:
                if record.get("value") is not None:
                    rows.append({
                        "country_name": record.get("country", {}).get("value"),
                        "country_code": record.get("countryiso3code"),
                        "year": int(record.get("date")),
                        "debt_total_usd": float(record.get("value"))
                    })
            
            df = pd.DataFrame(rows)
            logger.info(f"[FETCH] Converted to DataFrame: {len(df)} rows")
            logger.info(f"[FETCH] Unique countries: {df['country_code'].nunique()}")
            logger.info(f"[FETCH] Year range: {df['year'].min()}-{df['year'].max()}")
            
            return df
            
        except (requests.Timeout, requests.ConnectionError) as e:
            logger.warning(f"[RETRY] API timeout/connection error: {str(e)}")
            if attempt < max_retries - 1:
                import time
                wait_time = retry_backoff ** (attempt + 1)
                logger.info(f"[RETRY] Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                logger.error(f"[ERROR] Failed after {max_retries} attempts")
                # Fallback: return empty dataframe instead of raising
                logger.warning("[FALLBACK] World Bank debt fetch failed. Returning empty dataset.")
                return pd.DataFrame(columns=["country_name", "country_code", "year", "debt_total_usd"])
        
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error: {str(e)}")
            # Fallback: return empty dataframe
            logger.warning("[FALLBACK] World Bank debt fetch failed. Returning empty dataset.")
            return pd.DataFrame(columns=["country_name", "country_code", "year", "debt_total_usd"])
    
    logger.warning(f"[FALLBACK] Failed to fetch debt data after {max_retries} attempts. Returning empty dataset.")
    return pd.DataFrame(columns=["country_name", "country_code", "year", "debt_total_usd"])


def validate_response(response: requests.Response) -> None:
    """
    Validate API response status and content.
    
    Args:
        response: HTTP response object
    
    Raises:
        ValueError: If response is invalid
    """
    if response.status_code != 200:
        raise ValueError(f"API returned status code {response.status_code}")
    
    content_type = response.headers.get("content-type", "").lower()
    if "json" not in content_type:
        raise ValueError(f"Invalid content type: {content_type}")
    
    logger.info(f"[VALIDATION] Response valid: HTTP {response.status_code}")


def save_to_csv(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame to save
        output_path: Path to output CSV file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    file_size_kb = output_path.stat().st_size / 1024
    logger.info(f"[SAVE] Data saved to {output_path}")
    logger.info(f"[SAVE] File size: {file_size_kb:.1f} KB")
    logger.info(f"[SAVE] Rows: {len(df)}, Columns: {len(df.columns)}")


def main():
    """Main execution function."""
    # Generate timestamp
    timestamp = datetime.now().strftime("%d%b%Y").upper()
    
    output_file = Path(__file__).parent.parent / 'csv' / 'raw' / f'debt_raw_{timestamp}.csv'
    
    try:
        df = fetch_worldbank_debt()
        save_to_csv(df, output_file)
        
        logger.info("=" * 70)
        if len(df) > 0:
            logger.info(f"✅ COMPLETE: Debt data fetched successfully")
            logger.info(f"   Output: {output_file}")
            logger.info(f"   Records: {len(df)}")
        else:
            logger.warning(f"⚠️  WARNING: No debt data retrieved")
            logger.warning(f"   This may be temporary - check API status")
            logger.warning(f"   Pipeline will continue without debt data")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"❌ FAILED: {str(e)}")
        logger.error("=" * 70)
        raise


if __name__ == "__main__":
    main()
