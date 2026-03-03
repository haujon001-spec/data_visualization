"""
Data Recovery & Reconstruction Script
Rebuilds the proper top20_monthly.parquet with correct asset names and market cap values
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

print("="*80)
print("DATA RECOVERY AND RECONSTRUCTION")
print("="*80)

# 1. Load company mapping
print("\n[1] Loading company name mapping...")
companies_config = pd.read_csv('config/universe_companies.csv')
ticker_to_name = dict(zip(companies_config['ticker'], companies_config['name']))
print(f"    Loaded {len(ticker_to_name)} company mappings")
print(f"    Companies: {', '.join(list(ticker_to_name.keys())[:5])}...")

# 2. Load and unpivot companies data
print("\n[2] Loading and unpivoting company data...")
companies_raw = pd.read_csv('data/raw/companies_monthly.csv')
print(f"    Original shape: {companies_raw.shape}")

# Unpivot from wide format to long format
companies_list = []
for col in companies_raw.columns:
    if col == 'date':
        continue
    # Extract ticker from column name (e.g., 'close_aapl' -> 'AAPL')
    parts = col.split('_')
    if len(parts) >= 2:
        ticker = parts[-1].upper()
        metric = '_'.join(parts[:-1])
        
        if metric == 'close':
            # Create a row with date, ticker, price
            for idx, row in companies_raw.iterrows():
                date = row['date']
                price = row[col]
                
                if not pd.isna(price):
                    companies_list.append({
                        'date': date,
                        'ticker': ticker,
                        'price_per_unit': price
                    })

companies_df = pd.DataFrame(companies_list)
print(f"    Unpivoted: {len(companies_df)} records")

# 3. Load metals data
print("\n[3] Loading metals data...")
metals_df = pd.read_csv('data/raw/metals_monthly.csv')
print(f"    Loaded {len(metals_df)} records")
metals_df = metals_df[['date', 'ticker', 'name', 'price_per_ounce']].copy()
metals_df.columns = ['date', 'ticker', 'label', 'price_per_unit']
metals_df['asset_type'] = 'metal'
metals_df['source'] = 'yfinance'
metals_df['confidence'] = 'Medium'
metals_df['asset_id'] = np.nan
metals_df['sector'] = np.nan
metals_df['region'] = np.nan
metals_df['notes'] = np.nan

# 4. Load crypto data
print("\n[4] Loading crypto data...")
crypto_df = pd.read_csv('data/raw/crypto_monthly.csv')
print(f"    Loaded {len(crypto_df)} records")
crypto_df.columns = ['date', 'asset_id', 'ticker', 'market_cap', 'price_per_unit', 'circulating_supply']
crypto_df['label'] = crypto_df['asset_id'].str.capitalize()  # bitcoin -> Bitcoin
crypto_df['asset_type'] = 'crypto'
crypto_df['source'] = 'coingecko'
crypto_df['confidence'] = 'High'
crypto_df['sector'] = np.nan
crypto_df['region'] = np.nan
crypto_df['notes'] = np.nan

# Load shares outstanding
print("\n[5] Loading shares outstanding and computing market caps...")
shares_outstanding = pd.read_csv('config/shares_outstanding.csv')
ticker_to_shares = dict(zip(shares_outstanding['ticker'], shares_outstanding['shares_outstanding']))

# Add shares and compute market cap for companies
companies_df['ticker_upper'] = companies_df['ticker'].str.upper()

# Map tickers to names and shares (handle case variations)
companies_df['label'] = companies_df['ticker_upper'].apply(lambda x: ticker_to_name.get(x, x))
companies_df['shares'] = companies_df['ticker_upper'].apply(lambda x: ticker_to_shares.get(x, np.nan))

companies_df['market_cap'] = companies_df['price_per_unit'] * companies_df['shares']
companies_df = companies_df[companies_df['market_cap'].notna()].copy()  # Remove NaN market caps

# Clean up company data
companies_df['asset_type'] = 'company'
companies_df['source'] = 'yfinance'
companies_df['confidence'] = 'High'
companies_df['asset_id'] = companies_df['ticker_upper'].str.lower()
companies_df['sector'] = companies_df['ticker_upper'].apply(lambda x: companies_config[companies_config['ticker'] == x]['sector'].values[0] if x in companies_config['ticker'].values else np.nan)
companies_df['region'] = companies_df['ticker_upper'].apply(lambda x: companies_config[companies_config['ticker'] == x]['region'].values[0] if x in companies_config['ticker'].values else np.nan)
companies_df['notes'] = np.nan

print(f"    Companies with market cap: {len(companies_df)}")
print(f"    Available tickers: {companies_df['ticker_upper'].unique()}")
print(f"    Sample: {companies_df[['date', 'label', 'market_cap']].head()}")

# 6. Load metals supply config
print("\n[6] Loading metals supply config...")
metals_supply = pd.read_csv('config/precious_metals_supply.csv')
ticker_to_supply = dict(zip(metals_supply['ticker'], metals_supply['supply_ounces']))

metals_df['supply'] = metals_df['ticker'].map(ticker_to_supply)
metals_df['market_cap'] = metals_df['price_per_unit'] * metals_df['supply']
print(f"    Sample metal caps: {metals_df[['label', 'price_per_unit', 'supply', 'market_cap']].head()}")

# 7. Combine all datasets
print("\n[7] Combining all datasets...")
# Select consistent columns
common_cols = ['date', 'label', 'market_cap', 'asset_type', 'source', 'confidence', 'asset_id', 'sector', 'region', 'notes']

# Drop ticker column and keep only needed columns
companies_subset = companies_df[common_cols].copy()
metals_subset = metals_df[common_cols].copy()
crypto_subset = crypto_df[common_cols].copy()

combined = pd.concat([companies_subset, metals_subset, crypto_subset], ignore_index=True)
combined['date'] = pd.to_datetime(combined['date']).dt.strftime('%Y-%m-%d')
combined['market_cap'] = pd.to_numeric(combined['market_cap'], errors='coerce')
combined = combined[combined['market_cap'].notna()].copy()

print(f"    Combined dataset: {len(combined)} records")
print(f"    Date range: {combined['date'].min()} to {combined['date'].max()}")
print(f"    Unique assets: {combined['label'].nunique()}")

# 8. Rank assets by market cap
print("\n[8] Ranking assets by market cap...")
# Use bfill to fill gaps from the most recent available data backward
combined_filled = combined.sort_values(['label', 'date']).copy()
# For each asset, fill missing dates using the most recent available value
all_dates = pd.date_range(combined['date'].min(), combined['date'].max(), freq='MS').strftime('%Y-%m-%d').unique()
all_dates = sorted(all_dates)

result_list = []
for label in combined_filled['label'].unique():
    asset_data = combined_filled[combined_filled['label'] == label].copy()
    # Get the most recent value for this asset to use for all subsequent dates
    latest_val = asset_data.iloc[-1].copy() if len(asset_data) > 0 else None
    if latest_val is not None:
        for date in all_dates:
            date_data = asset_data[asset_data['date'] == date]
            if len(date_data) > 0:
                result_list.append(date_data.iloc[0].to_dict())
            else:
                # Use the most recent data point for this asset, but update the date
                new_row = latest_val.to_dict().copy()
                new_row['date'] = date
                result_list.append(new_row)

combined_filled_bfill = pd.DataFrame(result_list)
combined_filled_bfill = combined_filled_bfill[combined_filled_bfill['market_cap'].notna()].copy()

# Rank
combined_filled_bfill['rank'] = combined_filled_bfill.groupby('date')['market_cap'].rank(ascending=False, method='min')
combined_filled_bfill['rank'] = combined_filled_bfill['rank'].astype(int)

# Select top 20
top20 = combined_filled_bfill[combined_filled_bfill['rank'] <= 20].copy()
print(f"    Top 20 records (after backfill): {len(top20)}")

# 9. Save outputs
print("\n[9] Saving outputs...")
output_dir = Path('data/processed')
output_dir.mkdir(exist_ok=True)

# CSV
csv_path = output_dir / 'top20_monthly.csv'
top20.to_csv(csv_path, index=False)
print(f"    ✓ Saved CSV: {csv_path}")
print(f"      Rows: {len(top20)}, Columns: {len(top20.columns)}")

# Parquet
parquet_path = output_dir / 'top20_monthly.parquet'
top20.to_parquet(parquet_path, index=False)
print(f"    ✓ Saved Parquet: {parquet_path}")

# 10. Verification
print("\n[10] Verification...")
verify_df = pd.read_parquet(parquet_path)
latest_date = verify_df['date'].max()
latest_data = verify_df[verify_df['date'] == latest_date].sort_values('rank')

print(f"\n    LATEST DATA ({latest_date}):")
print(f"    {'Rank':<6} {'Asset':<20} {'Market Cap':<15}")
print("    " + "-"*50)
for _, row in latest_data.head(10).iterrows():
    market_cap_b = row['market_cap'] / 1e9
    print(f"    {int(row['rank']):<6} {row['label']:<20} ${market_cap_b:>12.2f}B")

print(f"\n{'='*80}")
print(f"DATA RECOVERY COMPLETE")
print(f"{'='*80}\n")
