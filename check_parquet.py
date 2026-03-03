import pandas as pd

# Check what's actually in the parquet file
df = pd.read_parquet('data/processed/top20_monthly.parquet')

print("PARQUET CONTENT CHECK")
print("="*80)
print(f"Total rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nLatest date: {df['date'].max()}")

# Get latest data
latest = df[df['date'] == df['date'].max()].sort_values('rank')
print(f"\nRecords on latest date: {len(latest)}")
print("\nLatest data:")
print(latest[['rank', 'label', 'market_cap', 'asset_type']].to_string())

# Check all unique dates
print(f"\n\nUnique dates: {sorted(df['date'].unique())[-10:]}")  # Last 10 dates

# Check for data on different dates
for test_date in sorted(df['date'].unique())[-3:]:
    test_data = df[df['date'] == test_date].sort_values('rank')
    print(f"\n\nDate {test_date}: {len(test_data)} assets")
    print(test_data[['rank', 'label', 'market_cap']].to_string())
