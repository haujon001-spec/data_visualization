"""
Complete ETL Rebuild with Currency Normalization
Builds verified top20 dataset matching 8marketcap.com methodology
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("COMPLETE ETL REBUILD WITH CURRENCY NORMALIZATION")
print("="*80)

# Step 1: Load company data with currency conversions
print("\n[1] Loading normalized company data...")
companies_df = pd.read_csv('data/processed/companies_normalized.csv')
print(f"    Loaded: {len(companies_df)} company records")

# Get company name mappings
companies_config = pd.read_csv('config/universe_companies.csv')
ticker_to_name = dict(zip(companies_config['ticker'], companies_config['name']))

companies_df['label'] = companies_df['ticker'].map(ticker_to_name)
companies_df['asset_type'] = 'company'
companies_df['source'] = 'yfinance + FX'
companies_df['confidence'] = 'Medium'  # Medium because of FX conversion
companies_df['sector'] = companies_df['ticker'].apply(
    lambda x: companies_config[companies_config['ticker'] == x]['sector'].values[0] if x in companies_config['ticker'].values else 'Unknown'
)
companies_df['region'] = companies_df['ticker'].apply(
    lambda x: companies_config[companies_config['ticker'] == x]['region'].values[0] if x in companies_config['ticker'].values else 'Unknown'
)

# Keep only necessary columns
companies_clean = companies_df[[
    'date', 'label', 'market_cap_usd', 'asset_type', 'source', 'confidence', 'sector', 'region'
]].copy()
companies_clean.columns = ['date', 'label', 'market_cap', 'asset_type', 'source', 'confidence', 'sector', 'region']

# Step 2: Load metals data
print("\n[2] Loading metals data...")
metals_df = pd.read_csv('data/raw/metals_monthly.csv')
metals_df = metals_df[['date', 'name', 'market_cap']].copy()
metals_df.columns = ['date', 'label', 'market_cap']
metals_df['asset_type'] = 'metal'
metals_df['source'] = 'yfinance'
metals_df['confidence'] = 'Medium'
metals_df['sector'] = np.nan
metals_df['region'] = np.nan
print(f"    Loaded: {len(metals_df)} metals records")

# Step 3: Load crypto data
print("\n[3] Loading crypto data...")
crypto_df = pd.read_csv('data/raw/crypto_monthly.csv')
crypto_df['label'] = crypto_df['coin_id'].str.capitalize()
crypto_df = crypto_df[['date', 'label', 'market_cap']].copy()
crypto_df['asset_type'] = 'crypto'
crypto_df['source'] = 'coingecko'
crypto_df['confidence'] = 'High'
crypto_df['sector'] = np.nan
crypto_df['region'] = np.nan
print(f"    Loaded: {len(crypto_df)} crypto records")

# Step 4: Combine all datasets
print("\n[4] Combining all datasets...")
all_data = pd.concat([companies_clean, metals_df, crypto_df], ignore_index=True)
all_data = all_data.sort_values('date')
all_data = all_data[all_data['market_cap'].notna()].copy()
print(f"    Combined: {len(all_data)} total records")
print(f"    Date range: {all_data['date'].min()} to {all_data['date'].max()}")
print(f"    Unique assets: {all_data['label'].nunique()}")

# Step 5: Forward-fill missing dates per asset
print("\n[5] Forward-filling sparse data...")
all_sorted = all_data.sort_values(['label', 'date']).copy()
all_sorted['market_cap'] = all_sorted.groupby('label')['market_cap'].ffill()
all_sorted = all_sorted[all_sorted['market_cap'].notna()].copy()
print(f"    After forward-fill: {len(all_sorted)} records")

# Step 6: Rank by market cap
print("\n[6] Ranking assets by market cap...")
all_sorted['rank'] = all_sorted.groupby('date')['market_cap'].rank(ascending=False, method='min')
all_sorted['rank'] = all_sorted['rank'].astype(int)

# Select top 20
top20 = all_sorted[all_sorted['rank'] <= 20].copy()
print(f"    Top 20 records: {len(top20)}")

# Step 7: Save outputs
print("\n[7] Saving outputs...")
output_dir = Path('data/processed')

csv_path = output_dir / 'top20_monthly.csv'
top20.to_csv(csv_path, index=False)
print(f"    ✓ CSV: {csv_path} ({len(top20)} rows)")

parquet_path = output_dir / 'top20_monthly.parquet'
top20.to_parquet(parquet_path, index=False)
print(f"    ✓ Parquet: {parquet_path}")

# Step 8: Display latest rankings
print("\n[8] LATEST TOP 20 (2026-02-01):")
print("="*80)
latest_date = top20['date'].max()
latest = top20[top20['date'] == latest_date].sort_values('rank')

display_df = latest[['rank', 'label', 'market_cap', 'asset_type', 'confidence']].copy()
display_df['market_cap_b'] = display_df['market_cap'] / 1e9
display_df['market_cap_t'] = display_df['market_cap'] / 1e12

for idx, row in display_df.head(15).iterrows():
    if row['market_cap_t'] >= 1:
        cap_str = f"${row['market_cap_t']:.2f}T"
    else:
        cap_str = f"${row['market_cap_b']:.1f}B"
    
    print(f"{int(row['rank']):2d}. {row['label']:<30} {cap_str:>12} [{row['asset_type']:<6}] {row['confidence']}")

print("\n" + "="*80)
print("ETL REBUILD COMPLETE - Currency-normalized data ready for visualization")
print("="*80)

# Step 9: Data quality summary
print("\n[9] DATA QUALITY SUMMARY:")
print("-" * 80)
print(f"Total records: {len(top20)}")
print(f"Date range: {top20['date'].min()} to {top20['date'].max()}")
print(f"Unique dates: {top20['date'].nunique()}")
print(f"Unique assets: {top20['label'].nunique()}")
print(f"\nAsset type breakdown:")
print(top20['asset_type'].value_counts())
print(f"\nData confidence summary:")
print(top20['confidence'].value_counts())
