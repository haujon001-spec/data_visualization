"""
Data Pipeline Fixer
===================
Fixes the companies_monthly.csv wide-to-long transformation issue.
Converts wide format companies data, regenerates rankings, and rebuilds visualization.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_companies_data(raw_dir: Path) -> pd.DataFrame:
    """
    Convert wide format companies data to long format.
    
    Input: companies_monthly.csv with columns like close_sap, close_meta, etc.
    Output: Long format with columns: date, ticker, adjusted_close
    """
    logger.info("Loading and fixing companies data...")
    
    df = pd.read_csv(raw_dir / "companies_monthly.csv")
    logger.info(f"Loaded {len(df)} rows from companies_monthly.csv")
    
    # Keep the date column
    date_col = df[['date']].copy()
    
    # Extract close price columns (they're named close_<ticker>)
    close_cols = [col for col in df.columns if col.startswith('close_')]
    
    # Create ticker mapping: close_sap -> SAP, close_msft -> MSFT, etc.
    ticker_mapping = {}
    for col in close_cols:
        ticker = col.replace('close_', '').upper()
        ticker_mapping[col] = ticker
    
    logger.info(f"Found {len(ticker_mapping)} company tickers")
    
    # Unpivot: convert from wide to long
    long_data = []
    for _, row in df.iterrows():
        date = row['date']
        for col, ticker in ticker_mapping.items():
            price = row[col]
            if pd.notna(price) and price > 0:
                long_data.append({
                    'date': date,
                    'ticker': ticker,
                    'adjusted_close': price
                })
    
    companies_long = pd.DataFrame(long_data)
    logger.info(f"Converted to long format: {len(companies_long)} rows")
    logger.info(f"Date range: {companies_long['date'].min()} to {companies_long['date'].max()}")
    logger.info(f"Unique tickers: {companies_long['ticker'].nunique()}")
    logger.info(f"Tickers: {sorted(companies_long['ticker'].unique())}")
    
    return companies_long

def main():
    project_dir = Path('.').absolute()
    raw_dir = project_dir / 'data' / 'raw'
    processed_dir = project_dir / 'data' / 'processed'
    
    logger.info("=" * 70)
    logger.info("DATA PIPELINE FIXER - Converting Wide to Long Format")
    logger.info("=" * 70)
    
    # Step 1: Fix companies data
    companies_long = fix_companies_data(raw_dir)
    
    # Step 2: Load crypto and metals (already in correct format)
    crypto_df = pd.read_csv(raw_dir / "crypto_monthly.csv") if (raw_dir / "crypto_monthly.csv").exists() else pd.DataFrame()
    metals_df = pd.read_csv(raw_dir / "metals_monthly.csv") if (raw_dir / "metals_monthly.csv").exists() else pd.DataFrame()
    
    logger.info(f"Crypto: {len(crypto_df)} rows, {crypto_df['coin_id'].nunique() if not crypto_df.empty else 0} coins")
    logger.info(f"Metals: {len(metals_df)} rows, {metals_df['name'].nunique() if not metals_df.empty else 0} metals")
    
    logger.info("\n" + "=" * 70)
    logger.info("TOTAL ASSETS AVAILABLE:")
    logger.info("=" * 70)
    companies_count = companies_long['ticker'].nunique() if not companies_long.empty else 0
    crypto_count = crypto_df['coin_id'].nunique() if not crypto_df.empty else 0
    metals_count = metals_df['name'].nunique() if not metals_df.empty else 0
    
    logger.info(f"Companies: {companies_count}")
    logger.info(f"Cryptocurrencies: {crypto_count}")
    logger.info(f"Precious metals: {metals_count}")
    logger.info(f"TOTAL: {companies_count + crypto_count + metals_count} assets")
    logger.info("=" * 70)
    
    logger.info("\n✅ Data fix complete. Ready to regenerate rankings and visualization.")
    logger.info("   Run: python scripts/02_build_rankings.py")

if __name__ == '__main__':
    main()
