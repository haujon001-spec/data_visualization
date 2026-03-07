import pandas as pd

# Load the parquet
df = pd.read_parquet('data/processed/top20_monthly.parquet')

# Check a specific date
dates = sorted(df['date'].unique())
print(f"Sample dates: {dates[:5]} ... {dates[-5:]}")
print()

# Check data for the earliest date (2016-01-01)
sample_date = dates[0]
sample_df = df[df['date'] == sample_date].sort_values('market_cap', ascending=False)
print(f"Date: {sample_date}")
print(f"Total rows for this date: {len(sample_df)}")
print(f"Top 20 by market cap:")
print(sample_df[['label', 'asset_type', 'market_cap']].head(20).to_string())
print()

# Check for October 31, 2016 (from the screenshot)
target_date = '2016-10-31'
if target_date in df['date'].values:
    sample_df = df[df['date'] == target_date].sort_values('market_cap', ascending=False)
    print(f"Date: {target_date}")
    print(f"Total rows for this date: {len(sample_df)}")
    print(f"Top 20 by market cap:")
    print(sample_df[['label', 'asset_type', 'market_cap']].head(20).to_string())
else:
    print(f"Date {target_date} not found in data")
