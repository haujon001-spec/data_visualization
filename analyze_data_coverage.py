import pandas as pd

# Load the parquet
df = pd.read_parquet('data/processed/top20_monthly.parquet')

print("Data Coverage by Asset Type:")
print("=" * 70)

for atype in sorted(df['asset_type'].unique()):
    subset = df[df['asset_type'] == atype]
    min_date = subset['date'].min()
    max_date = subset['date'].max()
    unique_dates = subset['date'].nunique()
    unique_assets = subset['label'].nunique()
    total_rows = len(subset)
    
    print(f"\n{atype.upper()}:")
    print(f"  Date range: {min_date} to {max_date}")
    print(f"  Unique dates: {unique_dates}")
    print(f"  Unique assets: {unique_assets}")
    print(f"  Total rows: {total_rows}")
    print(f"  Assets: {sorted(subset['label'].unique())}")

# Now check what's missing on 2016-10-31
print("\n\n2016-10-31 Data Coverage:")
print("=" * 70)
target_date = '2016-10-31'
for atype in sorted(df['asset_type'].unique()):
    subset = df[(df['date'] == target_date) & (df['asset_type'] == atype)]
    print(f"{atype:8}: {len(subset):3} rows - Assets: {list(subset['label'].unique())}")

# Check what dates have <= 3 assets (sparse data)
print("\n\nDates with fewer than 5 assets (sparse data):")
print("=" * 70)
date_counts = df.groupby('date').size()
sparse_dates = date_counts[date_counts < 5].head(10)
for date, count in sparse_dates.items():
    date_df = df[df['date'] == date]
    assets = list(date_df['label'].unique())
    print(f"{date}: {count:2} assets - {assets}")
