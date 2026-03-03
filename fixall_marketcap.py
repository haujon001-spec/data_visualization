#!/usr/bin/env python3
"""
Fix and regenerate top20 with proper market cap calculations and Windows-compatible paths.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Use pathlib for cross-platform path handling
BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / 'config'
RAW_DIR = BASE_DIR / 'data' / 'raw'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'

print(f"Using paths:")
print(f"  Config: {CONFIG_DIR}")
print(f"  Raw: {RAW_DIR}")
print(f"  Processed: {PROCESSED_DIR}")

# Read raw data
companies = pd.read_csv(RAW_DIR / 'companies_monthly.csv')
metals = pd.read_csv(RAW_DIR / 'metals_monthly.csv')
crypto = pd.read_csv(RAW_DIR / 'crypto_monthly.csv')
shares = pd.read_csv(CONFIG_DIR / 'shares_outstanding.csv')

print(f"\nData loaded:")
print(f"  Companies: {len(companies)} rows")
print(f"  Metals: {len(metals)} rows")
print(f"  Crypto: {len(crypto)} rows")
print(f"  Shares: {len(shares)} rows")

# Prepare companies with proper market cap calculation
companies_proc = companies.copy()
companies_proc['date'] = pd.to_datetime(companies_proc['date']).astype(str)

# Merge with shares outstanding (use most recent shares for all periods)
shares_recent = shares.sort_values('last_update').drop_duplicates('ticker', keep='last')
companies_proc = companies_proc.merge(
    shares_recent[['ticker', 'shares_outstanding']],
    left_on='ticker',
    right_on='ticker',
    how='left'
)

# Calculate market cap: adjusted_close × shares_outstanding
# This is an approximation since we only have current shares outstanding
companies_proc['market_cap'] = (
    pd.to_numeric(companies_proc['adjusted_close'], errors='coerce') *
    pd.to_numeric(companies_proc['shares_outstanding'], errors='coerce')
)

# Remove entries with NaN market cap
companies_proc = companies_proc.dropna(subset=['market_cap'])
companies_proc = companies_proc[companies_proc['market_cap'] > 0]

companies_proc = companies_proc[['date', 'ticker', 'adjusted_close', 'market_cap']].copy()
companies_proc.rename(columns={'ticker': 'asset_id', 'adjusted_close': 'price'}, inplace=True)
companies_proc['asset_type'] = 'company'
companies_proc['label'] = companies_proc['asset_id']
companies_proc['source'] = 'yfinance'
companies_proc['confidence'] = 'Medium'
companies_proc['sector'] = 'Technology'
companies_proc['region'] = 'Global'
companies_proc['notes'] = ''

print(f"\nCompanies market cap stats:")
print(f"  Min: ${companies_proc['market_cap'].min():,.0f}")
print(f"  Max: ${companies_proc['market_cap'].max():,.0f}")
print(f"  Mean: ${companies_proc['market_cap'].mean():,.0f}")
print(f"  With market_cap > 0: {(companies_proc['market_cap'] > 0).sum()}")

# Prepare metals
metals_proc = metals.copy()
metals_proc['date'] = pd.to_datetime(metals_proc['date']).astype(str)
metals_proc.rename(columns={'ticker': 'asset_id', 'name': 'label', 'price_per_ounce': 'price'}, inplace=True)
metals_proc['asset_type'] = 'metal'
metals_proc['source'] = 'yfinance + WGC'
metals_proc['confidence'] = 'Medium'
metals_proc['sector'] = 'Commodities'
metals_proc['region'] = 'Global'
metals_proc['notes'] = ''
metals_proc = metals_proc[['date', 'asset_id', 'label', 'price', 'market_cap', 'asset_type', 'source', 'confidence', 'sector', 'region', 'notes']]

print(f"\nMetals market cap stats:")
print(f"  Min: ${metals_proc['market_cap'].min():,.0f}")
print(f"  Max: ${metals_proc['market_cap'].max():,.0f}")
print(f"  Mean: ${metals_proc['market_cap'].mean():,.0f}")

# Prepare crypto
crypto_proc = crypto.copy()
crypto_proc['date'] = pd.to_datetime(crypto_proc['date']).astype(str)
crypto_proc.rename(columns={'symbol': 'asset_id', 'coin_id': 'label'}, inplace=True)
crypto_proc['asset_type'] = 'crypto'
crypto_proc['source'] = 'CoinGecko'
crypto_proc['confidence'] = 'High'
crypto_proc['sector'] = 'Digital Assets'
crypto_proc['region'] = 'Global'
crypto_proc['notes'] = ''
crypto_proc = crypto_proc[['date', 'asset_id', 'label', 'price', 'market_cap', 'asset_type', 'source', 'confidence', 'sector', 'region', 'notes']]

print(f"\nCrypto market cap stats:")
print(f"  Min: ${crypto_proc['market_cap'].min():,.0f}")
print(f"  Max: ${crypto_proc['market_cap'].max():,.0f}")
print(f"  Mean: ${crypto_proc['market_cap'].mean():,.0f}")

# Merge all data
all_data = pd.concat([companies_proc, metals_proc, crypto_proc], ignore_index=True)

# Remove rows with 0 or NaN market cap
all_data = all_data[all_data['market_cap'] > 0].copy()

print(f"\nAfter filtering out zero market caps: {len(all_data)} rows")

# Sort and rank
all_data = all_data.sort_values(['date', 'market_cap'], ascending=[True, False])
all_data['rank'] = all_data.groupby('date').cumcount() + 1

# Keep top 20 per date
top20 = all_data[all_data['rank'] <= 20].copy()

print(f"\nFinal top20: {len(top20)} rows")
print(f"Date range: {top20['date'].min()} to {top20['date'].max()}")

# Reorder columns
cols = ['date', 'rank', 'asset_id', 'asset_type', 'label', 'market_cap', 'source', 'confidence', 'sector', 'region', 'notes']
top20 = top20[cols]

# Save with proper paths
top20.to_csv(PROCESSED_DIR / 'top20_monthly.csv', index=False)
top20.to_parquet(PROCESSED_DIR / 'top20_monthly.parquet', index=False)

# Save metadata with Windows-compatible paths
metadata = {
    'generated': datetime.now().isoformat(),
    'file_paths': {
        'input': str((RAW_DIR / 'top20_monthly.csv').as_posix()),
        'output': str((PROCESSED_DIR / 'top20_monthly.parquet').as_posix()),
        'config': str((CONFIG_DIR / 'shares_outstanding.csv').as_posix())
    },
    'data_stats': {
        'total_rows': int(len(top20)),
        'unique_dates': int(len(top20['date'].unique())),
        'date_range': {
            'start': str(top20['date'].min()),
            'end': str(top20['date'].max())
        },
        'top_n': 20,
        'asset_types': list(top20['asset_type'].unique()),
        'market_cap_range': {
            'min': float(top20['market_cap'].min()),
            'max': float(top20['market_cap'].max()),
            'mean': float(top20['market_cap'].mean())
        }
    }
}

with open(PROCESSED_DIR / 'top20_monthly_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\n✓ Files saved successfully:")
print(f"  - {PROCESSED_DIR / 'top20_monthly.csv'}")
print(f"  - {PROCESSED_DIR / 'top20_monthly.parquet'}")
print(f"  - {PROCESSED_DIR / 'top20_monthly_metadata.json'}")

print(f"\nSample top20 data:")
print(top20.iloc[:10][['date', 'rank', 'label', 'asset_type', 'market_cap']])
