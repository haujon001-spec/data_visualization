import pandas as pd
import numpy as np

# Load companies data
companies_df = pd.read_csv('data/raw/companies_monthly.csv')

# Find which ticker columns have actual data (not all NaN)
ticker_cols = [col for col in companies_df.columns if col.startswith('close_')]
ticker_names = [col.replace('close_', '').upper() for col in ticker_cols]

print("Company data availability:")
print("=" * 60)
for i, (col, name) in enumerate(zip(ticker_cols, ticker_names)):
    non_null = companies_df[col].notna().sum()
    pct = (non_null / len(companies_df)) * 100
    if non_null > 0:
        print(f"  {name:12} ({col:20}): {non_null:3} / {len(companies_df):3} ({pct:.1f}%)")
    else:
        print(f"  {name:12} ({col:20}): NO DATA")

# Metals
print("\nMetals data availability:")
print("=" * 60)
metals_df = pd.read_csv('data/raw/metals_monthly.csv')
print(f"Metals dates: {metals_df['date'].nunique()} unique")
print(f"Metal names: {metals_df['name'].unique()}")
print(f"Sample:")
print(metals_df.groupby('name').size())

# Crypto
print("\nCrypto data availability:")
print("=" * 60)
crypto_df = pd.read_csv('data/raw/crypto_monthly.csv')
print(f"Crypto dates: {crypto_df['date'].nunique()} unique")
print(f"Coins: {crypto_df['coin_id'].unique()}")
print(f"Rows per coin: {crypto_df.groupby('coin_id').size()}")
