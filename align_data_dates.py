"""
Data Date Alignment Fix
=======================
Aligns companies, crypto, and metals data to common monthly dates.
Uses forward-fill to ensure every month has complete coverage.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def align_dates_to_monthly():
    """Align all data sources to the 1st of each month."""
    
    logger.info("=" * 70)
    logger.info("DATA DATE ALIGNMENT FIX")
    logger.info("=" * 70)
    
    # Load raw files
    companies_raw = pd.read_csv('data/raw/companies_monthly.csv').copy()
    crypto_raw = pd.read_csv('data/raw/crypto_monthly.csv').copy()
    metals_raw = pd.read_csv('data/raw/metals_monthly.csv').copy()
    
    # Convert dates to datetime
    companies_raw['date'] = pd.to_datetime(companies_raw['date'])
    crypto_raw['date'] = pd.to_datetime(crypto_raw['date'])
    metals_raw['date'] = pd.to_datetime(metals_raw['date'])
    
    logger.info("Original date ranges:")
    logger.info(f"  Companies: {companies_raw['date'].min()} to {companies_raw['date'].max()}")
    logger.info(f"  Crypto:    {crypto_raw['date'].min()} to {crypto_raw['date'].max()}")
    logger.info(f"  Metals:    {metals_raw['date'].min()} to {metals_raw['date'].max()}")
    
    # Create unified monthly dates (1st of each month)
    # Use the range from earliest to latest date across all sources
    min_date = min(companies_raw['date'].min(), crypto_raw['date'].min(), metals_raw['date'].min())
    max_date = max(companies_raw['date'].max(), crypto_raw['date'].max(), metals_raw['date'].max())
    
    # Create monthly dates (1st of each month)
    monthly_dates = pd.date_range(start=min_date.replace(day=1), 
                                  end=max_date.replace(day=1), 
                                  freq='MS')
    
    logger.info(f"\nUnified monthly date range: {monthly_dates[0]} to {monthly_dates[-1]}")
    logger.info(f"Total months: {len(monthly_dates)}")
    
    # Align companies: use groupby to consolidate duplicates, then reindex  
    companies_aligned = companies_raw.copy()
    companies_aligned['date'] = companies_aligned['date'].apply(lambda x: x.replace(day=1))
    companies_aligned = companies_aligned.groupby('date').first().reset_index()
    
    # Convert to complete monthly series (forward fill)
    companies_aligned = companies_aligned.set_index('date')
    companies_aligned = companies_aligned.reindex(monthly_dates, method='ffill').reset_index()
    companies_aligned.rename(columns={'index': 'date'}, inplace=True)
    companies_aligned['date'] = companies_aligned['date'].astype(str).str[:10]
    
    logger.info(f"\nCompanies aligned: {len(companies_aligned)} rows, {companies_aligned['date'].nunique()} dates")
    
    # Align crypto: shift end-of-month dates to 1st of month, consolidate, then forward fill
    crypto_aligned = crypto_raw.copy()
    # Convert end-of-month to 1st of next month, then back to 1st of same month conceptually
    crypto_aligned['date'] = crypto_aligned['date'].apply(lambda x: x.replace(day=1))
    crypto_aligned = crypto_aligned.groupby('date').first().reset_index()
    
    # Convert to complete monthly series (forward fill)
    crypto_aligned = crypto_aligned.set_index('date')
    crypto_aligned = crypto_aligned.reindex(monthly_dates, method='ffill').reset_index()
    crypto_aligned.rename(columns={'index': 'date'}, inplace=True)
    crypto_aligned['date'] = crypto_aligned['date'].astype(str).str[:10]
    
    logger.info(f"Crypto aligned: {len(crypto_aligned)} rows, {crypto_aligned['date'].nunique()} dates")
    
    # Align metals: metals already has multiple rows per date (4 metals), 
    # need to extend dates and forward-fill all rows
    metals_aligned = metals_raw.copy()
    metals_aligned['date'] = metals_aligned['date'].apply(lambda x: x.replace(day=1))
    
    # For each date in monthly_dates, forward-fill all unique metals
    metals_expanded = []
    last_metals = None
    
    for target_date in monthly_dates:
        target_date_str = pd.Timestamp(target_date).strftime('%Y-%m-%d')
        
        # Check if we have data for this date
        matching = metals_aligned[metals_aligned['date'] == target_date]
        if len(matching) > 0:
            # Use current month's metals (all 4)
            last_metals = matching.copy()
            last_metals['date'] = target_date_str
            metals_expanded.append(last_metals)
        elif last_metals is not None:
            # Forward fill from previous months
            next_metals = last_metals.copy()
            next_metals['date'] = target_date_str
            metals_expanded.append(next_metals)
    
    metals_aligned = pd.concat(metals_expanded, ignore_index=True)
    
    logger.info(f"Metals aligned: {len(metals_aligned)} rows, {metals_aligned['date'].nunique()} dates")
    
    # Save aligned files
    companies_aligned.to_csv('data/raw/companies_monthly_ALIGNED.csv', index=False)
    crypto_aligned.to_csv('data/raw/crypto_monthly_ALIGNED.csv', index=False)
    metals_aligned.to_csv('data/raw/metals_monthly_ALIGNED.csv', index=False)
    
    logger.info("\n✅ Aligned files saved:")
    logger.info("  - data/raw/companies_monthly_ALIGNED.csv")
    logger.info("  - data/raw/crypto_monthly_ALIGNED.csv")
    logger.info("  - data/raw/metals_monthly_ALIGNED.csv")
    
    logger.info("\nNext step: Update scripts/02_build_rankings.py to use ALIGNED files")

if __name__ == '__main__':
    align_dates_to_monthly()
