"""
Fix top20_monthly.parquet to ensure ALL assets appear on EVERY date.
Uses forward-fill to handle gaps in data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the parquet file
input_path = Path('data/processed/top20_monthly.parquet')
output_path = Path('data/processed/top20_monthly.parquet')

logger.info("Loading data...")
df = pd.read_parquet(input_path)

print("BEFORE FIX:")
print(f"Shape: {df.shape}")
assets_per_date_before = df.groupby('date').size()
print(f"Assets per date: min={assets_per_date_before.min()}, max={assets_per_date_before.max()}, mean={assets_per_date_before.mean():.2f}")
print(f"Unique dates: {df['date'].nunique()}")

# Define all assets
all_assets = {
    'GC=F': {'label': 'Gold', 'asset_type': 'metal', 'sector': 'Commodities', 'region': 'Global'},
    'SI=F': {'label': 'Silver', 'asset_type': 'metal', 'sector': 'Commodities', 'region': 'Global'},
    'PL=F': {'label': 'Platinum', 'asset_type': 'metal', 'sector': 'Commodities', 'region': 'Global'},
    'PA=F': {'label': 'Palladium', 'asset_type': 'metal', 'sector': 'Commodities', 'region': 'Global'},
    'BTC': {'label': 'bitcoin', 'asset_type': 'crypto', 'sector': 'Digital Assets', 'region': 'Global'}
}

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'])

# Create a complete date range
min_date = df['date'].min()
max_date = df['date'].max()
all_dates = pd.date_range(start=min_date, end=max_date, freq='D')

logger.info(f"Creating complete asset-date cross-product...")
# Create complete index of all dates x all assets
complete_data = []
for asset_id, asset_info in all_assets.items():
    for date in all_dates:
        complete_data.append({
            'date': date,
            'asset_id': asset_id,
            'label': asset_info['label'],
            'asset_type': asset_info['asset_type'],
            'sector': asset_info['sector'],
            'region': asset_info['region']
        })

complete_df = pd.DataFrame(complete_data)

logger.info(f"Merging with actual data...")
# Merge with actual data
df_merged = complete_df.merge(
    df[['date', 'asset_id', 'market_cap', 'source', 'confidence', 'rank', 'notes']],
    on=['date', 'asset_id'],
    how='left'
)

# Sort by asset_id and date
df_merged = df_merged.sort_values(['asset_id', 'date']).reset_index(drop=True)

logger.info(f"Forward-filling missing market cap values...")
# Forward fill market cap by asset
df_merged['market_cap'] = df_merged.groupby('asset_id')['market_cap'].ffill()
df_merged['market_cap'] = df_merged.groupby('asset_id')['market_cap'].bfill()

# Handle any remaining NaN
df_merged = df_merged.dropna(subset=['market_cap'])

# Forward fill other columns
for col in ['source', 'confidence', 'notes']:
    df_merged[col] = df_merged.groupby('asset_id')[col].ffill()
    df_merged[col] = df_merged.groupby('asset_id')[col].bfill()

# Fill remaining NaN in source/confidence with defaults
df_merged['source'] = df_merged['source'].fillna('yfinance/CoinGecko')
df_merged['confidence'] = df_merged['confidence'].fillna('Medium')
df_merged['notes'] = df_merged['notes'].fillna('')

# Re-rank by date
logger.info(f"Re-ranking assets by date...")
df_merged['rank'] = df_merged.groupby('date')['market_cap'].rank(method='min', ascending=False).astype(int)

print("\nAFTER FIX:")
df_merged_check = df_merged.copy()
df_merged_check['date'] = pd.to_datetime(df_merged_check['date'])
assets_per_date_after = df_merged_check.groupby('date').size()
print(f"Shape: {df_merged.shape}")
print(f"Assets per date: min={assets_per_date_after.min()}, max={assets_per_date_after.max()}, mean={assets_per_date_after.mean():.2f}")
print(f"Unique dates: {df_merged['date'].nunique()}")

# Prepare final dataframe with correct column order
final_df = df_merged[[
    'date', 'rank', 'asset_id', 'asset_type', 'label', 'market_cap', 
    'source', 'confidence', 'sector', 'region', 'notes'
]].copy()

# Convert date to string before saving
final_df['date'] = pd.to_datetime(final_df['date']).dt.strftime('%Y-%m-%d')

# Save to parquet
logger.info(f"Saving fixed data to {output_path}...")
final_df.to_parquet(output_path, index=False)

logger.info(f"✓ Fixed data saved! All {len(all_assets)} assets now appear on every date.")
logger.info(f"  Total rows: {len(final_df)}")
logger.info(f"  Total unique dates: {final_df['date'].nunique()}")
