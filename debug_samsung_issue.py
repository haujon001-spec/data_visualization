"""
Debug Samsung (005930.KS) Market Cap Issue
"""

import pandas as pd

# Check the aligned companies data
companies_aligned = pd.read_csv('data/raw/companies_monthly_ALIGNED.csv')

print("SAMSUNG (005930.KS) RAW DATA:")
print("=" * 70)

samsung = companies_aligned[companies_aligned['date'].str.contains('005930', case=False, na=False)]
if len(samsung) == 0:
    # Try a different approach - check columns
    print("Columns in companies_aligned:", list(companies_aligned.columns))
    print("\nFirst 5 rows:")
    print(companies_aligned.head())

# Let me check the original companies file
companies_orig = pd.read_csv('data/raw/companies_monthly.csv')
print("\nORIGINAL COMPANIES DATA:")
print("Columns:", list(companies_orig.columns))

# Find all close_005930 data
samsung_cols = [col for col in companies_orig.columns if '005930' in col.lower()]
print(f"\nSamsung columns: {samsung_cols}")

if samsung_cols:
    samsung_data = companies_orig[['date'] + samsung_cols]
    print("\nSamsung price history (first 5):")
    print(samsung_data.head())
    print("\nSamsung price statistics:")
    for col in samsung_cols:
        if col != 'date':
            print(f"  {col}: Mean={samsung_data[col].mean():.2f}, Max={samsung_data[col].max():.2f}")

# Check the parquet data
print("\n\nOUR GENERATED PARQUET DATA:")
print("=" * 70)

df = pd.read_parquet('data/processed/top20_monthly.parquet')
samsung_pq = df[df['label'] == '005930.KS']

print(f"Samsung rows in parquet: {len(samsung_pq)}")
if len(samsung_pq) > 0:
    print(f"Market cap range: {samsung_pq['market_cap'].min():.2e} to {samsung_pq['market_cap'].max():.2e}")
    print(f"Latest market cap (2026-02-01): {samsung_pq[samsung_pq['date'] == '2026-02-01']['market_cap'].values}")
    
    # Show sample rows
    print("\nSample Samsung rows:")
    print(samsung_pq[['date', 'label', 'market_cap']].tail())
