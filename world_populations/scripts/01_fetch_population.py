# -*- coding: utf-8 -*-
"""
Fetch Population Data from World Bank API

Fetch total population (SP.POP.TOTL) from World Bank API for all countries, 1960-2024.
Output: CSV file with country_name, country_code, year, population columns.

Note: World Bank data starts from 1960 (no data available for 1950-1959).
"""

import requests
import pandas as pd
from pathlib import Path
import time


def fetch_worldbank_population(
    indicator: str = "SP.POP.TOTL",
    start_year: int = 1960,
    end_year: int = 2026,
    per_page: int = 20000
) -> pd.DataFrame:
    """
    Fetch population data from World Bank API.
    
    Args:
        indicator: World Bank indicator code (default: SP.POP.TOTL)
        start_year: Start year for data fetch
        end_year: End year for data fetch
        per_page: Number of results per page
    
    Returns:
        DataFrame with columns: country_name, country_code, year, population
    """
    base_url = "https://api.worldbank.org/v2/country/all/indicator"
    url = f"{base_url}/{indicator}"
    
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": per_page
    }
    
    print(f"[FETCH] Requesting data from World Bank API...")
    print(f"[FETCH] URL: {url}")
    print(f"[FETCH] Date range: {start_year}-{end_year}")
    
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        validate_response(response)
        
        data = response.json()
        
        if not data or len(data) < 2:
            raise ValueError("Invalid API response format")
        
        records = data[1]  # Data is in second element
        print(f"[FETCH] Retrieved {len(records)} records")
        
        # Transform to DataFrame
        rows = []
        for record in records:
            if record.get("value") is not None:
                rows.append({
                    "country_name": record.get("country", {}).get("value"),
                    "country_code": record.get("countryiso3code"),
                    "year": int(record.get("date")),
                    "population": int(record.get("value"))
                })
        
        df = pd.DataFrame(rows)
        print(f"[FETCH] Converted to DataFrame: {len(df)} rows")
        return df
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch data: {str(e)}")
        raise


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
    
    if response.headers.get("content-type", "").lower() != "application/json;charset=utf-8":
        raise ValueError("Invalid content type")
    
    print(f"[VALIDATION] Response valid: {response.status_code}")


def save_to_csv(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame to save
        output_path: Path to output CSV file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SAVE] Data saved to {output_path}")
    print(f"[SAVE] File size: {output_path.stat().st_size} bytes")


if __name__ == "__main__":
    output_file = Path("csv/raw/worldbank_population_raw_5Mar2026.csv")
    
    print("=" * 70)
    print("FETCHING WORLD BANK POPULATION DATA")
    print("=" * 70)
    
    df = fetch_worldbank_population()
    save_to_csv(df, output_file)
    
    print("=" * 70)
    print(f"COMPLETE: {len(df)} records saved")
    print("=" * 70)
