#!/usr/bin/env python3
"""Quick fix to regenerate top20_monthly.parquet with proper labels."""

import pandas as pd

# Read the CSV (which might have better structure)
df = pd.read_csv('data/processed/top20_monthly.csv')

# Create mappings for proper labels
metal_tickers = {
    'GC=F': 'Gold',
    'SI=F': 'Silver',
    'PL=F': 'Platinum',
    'PA=F': 'Palladium'
}

# Fix the label column
def fix_label(row):
    if row['asset_type'] == 'metal' and row['asset_id'] in metal_tickers:
        return metal_tickers[row['asset_id']]
    return row['label'] if pd.notna(row['label']) and row['label'] != 'Unknown' else row['asset_id']

df['label'] = df.apply(fix_label, axis=1)

# Fill any remaining NaN asset_id values with names
for ticker, name in metal_tickers.items():
    df.loc[(df['asset_type'] == 'metal') & (df['label'] == name), 'asset_id'] = ticker

# Save to parquet
df.to_parquet('data/processed/top20_monthly.parquet', index=False)
print(f"Updated parquet with {len(df)} rows")
print(f"Sample data:")
print(df[['date', 'rank', 'asset_id', 'label', 'asset_type', 'market_cap']].head(10))
