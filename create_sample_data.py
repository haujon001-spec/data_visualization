#!/usr/bin/env python3
"""
Create sample data for testing the Phase 3 visualization.

Generates realistic top20_monthly.csv with monthly market cap data for companies,
crypto, and precious metals from 2016-2026.
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Sample data
COMPANIES = [
    ("AAPL", "Apple", "Tech"),
    ("MSFT", "Microsoft", "Tech"),
    ("AMZN", "Amazon", "Consumer"),
    ("GOOGL", "Alphabet", "Tech"),
    ("NVDA", "NVIDIA", "Tech"),
    ("TSLA", "Tesla", "Consumer"),
    ("JPM", "JPMorgan Chase", "Finance"),
    ("V", "Visa", "Finance"),
    ("JNJ", "Johnson & Johnson", "Healthcare"),
    ("WMT", "Walmart", "Consumer"),
]

CRYPTO = [
    ("BTC", "Bitcoin", "Finance"),
    ("ETH", "Ethereum", "Finance"),
    ("BNB", "Binance Coin", "Finance"),
    ("XRP", "XRP", "Finance"),
    ("ADA", "Cardano", "Finance"),
]

METALS = [
    ("GOLD", "Gold", "Materials"),
    ("SILVER", "Silver", "Materials"),
    ("PLATINUM", "Platinum", "Materials"),
]

def generate_sample_data(start_year=2016, end_year=2026):
    """Generate realistic sample data."""
    
    dates = pd.date_range(
        start=f"{start_year}-01-01",
        end=f"{end_year}-12-31",
        freq="M"
    )
    
    rows = []
    
    # Company data with realistic growth patterns
    np.random.seed(42)
    for asset_id, label, sector in COMPANIES:
        base_cap = np.random.uniform(500e9, 3e12)
        trend = np.random.uniform(0.98, 1.02)  # Annual trend
        
        for month_idx, date in enumerate(dates):
            years_elapsed = (date - dates[0]).days / 365.25
            # Exponential growth with some volatility
            market_cap = base_cap * (trend ** years_elapsed)
            market_cap *= np.exp(np.random.normal(0, 0.15))  # Add monthly volatility
            
            rows.append({
                "year_month": date,
                "asset_id": asset_id,
                "asset_type": "company",
                "label": label,
                "market_cap": max(market_cap, 100e9),  # Min 100B
                "rank": None,  # Will be filled in
                "source": "yfinance",
                "confidence": np.random.choice(["High", "Medium", "Low"], p=[0.7, 0.25, 0.05]),
                "sector": sector,
                "notes": "",
            })
    
    # Crypto data with higher volatility
    for asset_id, label, sector in CRYPTO:
        base_cap = np.random.uniform(10e9, 500e9)
        
        for month_idx, date in enumerate(dates):
            years_elapsed = (date - dates[0]).days / 365.25
            market_cap = base_cap * (1.15 ** years_elapsed)  # Higher growth
            market_cap *= np.exp(np.random.normal(0, 0.3))  # High volatility
            
            rows.append({
                "year_month": date,
                "asset_id": asset_id,
                "asset_type": "crypto",
                "label": label,
                "market_cap": max(market_cap, 1e9),  # Min 1B
                "rank": None,
                "source": "CoinGecko",
                "confidence": np.random.choice(["High", "Medium"], p=[0.8, 0.2]),
                "sector": sector,
                "notes": "",
            })
    
    # Metals data
    for asset_id, label, sector in METALS:
        base_cap = np.random.uniform(2e11, 4e12)  # Large market
        
        for month_idx, date in enumerate(dates):
            years_elapsed = (date - dates[0]).days / 365.25
            market_cap = base_cap * (1.01 ** years_elapsed)  # Steady growth
            market_cap *= np.exp(np.random.normal(0, 0.08))  # Modest volatility
            
            rows.append({
                "year_month": date,
                "asset_id": asset_id,
                "asset_type": "metal",
                "label": label,
                "market_cap": max(market_cap, 100e9),
                "rank": None,
                "source": "World Gold Council",
                "confidence": "High" if asset_id == "GOLD" else "Medium",
                "sector": sector,
                "notes": "",
            })
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Add ranks per month
    df["rank"] = df.groupby("year_month")["market_cap"].rank(
        method="first", ascending=False
    )
    
    # Keep only top 20 per month
    df = df[df["rank"] <= 20].copy()
    df.sort_values(["year_month", "rank"], inplace=True)
    
    # Add some corporate action notes
    notes_samples = [
        "IPO completed",
        "Merger announced",
        "Stock split 3:1",
        "Dividend increase 10%",
        "Name change",
    ]
    
    sample_indices = np.random.choice(len(df), size=int(len(df) * 0.05), replace=False)
    for idx in sample_indices:
        df.loc[idx, "notes"] = np.random.choice(notes_samples)
    
    return df


def main():
    print("Generating sample data...")
    df = generate_sample_data()
    
    # Create processed directory
    output_dir = os.path.join("data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as CSV
    output_path = os.path.join(output_dir, "top20_monthly.csv")
    df.to_csv(output_path, index=False)
    print(f"✓ Saved {len(df)} rows to {output_path}")
    
    # Also save as parquet for potential future use
    try:
        import pyarrow.parquet as pq
        parquet_path = os.path.join(output_dir, "top20_monthly.parquet")
        df.to_parquet(parquet_path, index=False)
        print(f"✓ Saved parquet to {parquet_path}")
    except ImportError:
        print("  PyArrow not installed, skipping parquet")
    
    print("\nData Summary:")
    print(f"  Date range: {df['year_month'].min().date()} to {df['year_month'].max().date()}")
    print(f"  Months: {df['year_month'].nunique()}")
    print(f"  Unique assets: {df['asset_id'].nunique()}")
    print(f"  Asset types: {df['asset_type'].unique().tolist()}")
    print(f"  Sectors: {sorted(df['sector'].unique().tolist())}")
    print(f"  Sources: {sorted(df['source'].unique().tolist())}")
    print(f"  Confidence levels: {df['confidence'].value_counts().to_dict()}")
    print(f"\nTop 5 assets by avg market cap:")
    top5 = df.groupby(["asset_id", "label"])["market_cap"].mean().nlargest(5)
    for (asset_id, label), cap in top5.items():
        print(f"    {asset_id} ({label}): ${cap/1e12:.2f}T")


if __name__ == "__main__":
    main()
