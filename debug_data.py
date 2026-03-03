import pandas as pd

# Load the data
df = pd.read_parquet('data/processed/top20_monthly.parquet')

print("Column names:", df.columns.tolist())
print("\nDataFrame shape:", df.shape)
print("\nDate range:", df['date'].min(), "to", df['date'].max())
print(f"\nUnique dates: {df['date'].nunique()}")

# Get latest date
latest = df[df['date'] == df['date'].max()]
print(f"\n{'='*80}")
print(f"LATEST DATE: {latest['date'].iloc[0]}")
print(f"Number of assets: {len(latest)}")
print(f"{'='*80}")
print(latest[['rank', 'label', 'market_cap', 'asset_type']].sort_values('rank').to_string())

# Show all unique assets
print(f"\n{'='*80}")
print("ALL UNIQUE ASSETS IN DATA:")
print(f"{'='*80}")
print(f"Total unique labels: {df['label'].nunique()}")
print(df['label'].unique())

# Check a specific date with full data
print(f"\n{'='*80}")
print("DATA ON LAST DATE (2026-02-24):")
print(f"{'='*80}")
last_data = df[df['date'] == '2026-02-24'].sort_values('rank')
print(last_data[['rank', 'label', 'market_cap', 'asset_type']].to_string())
