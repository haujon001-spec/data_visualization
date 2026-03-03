#!/usr/bin/env python3
"""Reconstruct top20 with proper asset IDs and labels."""

import pandas as pd
from datetime import datetime

# Read raw data
companies = pd.read_csv('data/raw/companies_monthly.csv')
metals = pd.read_csv('data/raw/metals_monthly.csv')
crypto = pd.read_csv('data/raw/crypto_monthly.csv')

# Read shares outstanding for market cap calculation
shares = pd.read_csv('config/shares_outstanding.csv')

# Prepare companies
companies_proc = companies.merge(shares, left_on='ticker', right_on='ticker', how='left')
companies_proc['market_cap'] = companies_proc['adjusted_close'] * companies_proc['shares_outstanding']
companies_proc = companies_proc[['date', 'ticker', 'adjusted_close', 'market_cap']].copy()
companies_proc.rename(columns={'ticker': 'asset_id', 'adjusted_close': 'price'}, inplace=True)
companies_proc['asset_type'] = 'company'
companies_proc['label'] = companies_proc['asset_id']  # Will be updated with names later
companies_proc['source'] = 'yfinance'
companies_proc['confidence'] = 'Medium'
companies_proc['sector'] = ''
companies_proc['region'] = ''
companies_proc['notes'] = ''

# Prepare metals
metals_proc = metals.copy()
metals_proc.rename(columns={'ticker': 'asset_id', 'name': 'label', 'price_per_ounce': 'price'}, inplace=True)
metals_proc['asset_type'] = 'metal'
metals_proc['source'] = 'yfinance + WGC'
metals_proc['confidence'] = 'Medium'
metals_proc['sector'] = 'Commodities'
metals_proc['region'] = 'Global'
metals_proc['notes'] = ''
metals_proc = metals_proc[['date', 'asset_id', 'label', 'price', 'market_cap', 'asset_type', 'source', 'confidence', 'sector', 'region', 'notes']]

# Prepare crypto
crypto_proc = crypto.copy()
crypto_proc.rename(columns={'symbol': 'asset_id', 'coin_id': 'label'}, inplace=True)
crypto_proc['asset_type'] = 'crypto'
crypto_proc['source'] = 'CoinGecko'
crypto_proc['confidence'] = 'High'
crypto_proc['sector'] = 'Digital Assets'
crypto_proc['region'] = 'Global'
crypto_proc['notes'] = ''
crypto_proc = crypto_proc[['date', 'asset_id', 'label', 'price', 'market_cap', 'asset_type', 'source', 'confidence', 'sector', 'region', 'notes']]

# Merge all
all_data = pd.concat([companies_proc, metals_proc, crypto_proc], ignore_index=True)

# Parse dates
all_data['date'] = pd.to_datetime(all_data['date']).astype(str)

# Rank by date and market cap
all_data = all_data.sort_values(['date', 'market_cap'], ascending=[True, False])
all_data['rank'] = all_data.groupby('date').cumcount() + 1

# Keep top 20 per date
top20 = all_data[all_data['rank'] <= 20].copy()

# Reorder columns
cols = ['date', 'rank', 'asset_id', 'asset_type', 'label', 'market_cap', 'source', 'confidence', 'sector', 'region', 'notes']
top20 = top20[cols]

# Save
top20.to_csv('data/processed/top20_monthly.csv', index=False)
top20.to_parquet('data/processed/top20_monthly.parquet', index=False)

print(f"Reconstructed top20 with {len(top20)} rows")
print(f"Date range: {top20['date'].min()} to {top20['date'].max()}")
print(f"\nSample data:")
print(top20.head(10))
print(f"\nAsset types: {top20['asset_type'].unique()}")
print(f"Asset IDs (sample): {top20['asset_id'].unique()[:10]}")
