import pandas as pd

# Load the parquet with aligned data
df = pd.read_parquet('data/processed/top20_monthly.parquet')

print("Data Coverage by Asset Type (ALIGNED):")
print("=" * 70)

for atype in sorted(df['asset_type'].unique()):
    subset = df[df['asset_type'] == atype]
    unique_dates = subset['date'].nunique()
    unique_assets = subset['label'].nunique()
    total_rows = len(subset)
    
    print(f"\n{atype.upper()}:")
    print(f"  Unique assets: {unique_assets}")
    print(f"  Unique dates: {unique_dates}")
    print(f"  Total rows: {total_rows}")

# Check distribution of assets per date
print("\n\nAssets per date distribution:")
print("=" * 70)
counts = df.groupby('date').size()
print(f"Min: {counts.min()}")
print(f"Max: {counts.max()}")
print(f"Average: {counts.mean():.1f}")

# Sample a few dates
print("\n\nSample dates with asset counts:")
print("=" * 70)
for date in sorted(df['date'].unique())[::20]:  # Every 20th date
    count = len(df[df['date'] == date])
    assets = list(df[df['date'] == date]['label'].unique())
    print(f"{date}: {count:2} assets")
