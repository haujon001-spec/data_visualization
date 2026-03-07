import pandas as pd

df = pd.read_parquet('data/processed/top20_monthly.parquet')
print('====== PARQUET FILE ANALYSIS ======')
print(f'Total rows: {len(df)}')
print(f'Unique dates: {df["date"].nunique()}')
print(f'Unique assets: {df["label"].nunique()}')
print(f'Asset types: {sorted(df["asset_type"].unique())}')
print()
print('Assets (first 50):')
for i, asset in enumerate(sorted(df['label'].unique())[:50]):
    if asset != 'Unknown':
        count = len(df[df['label'] == asset])
        atype = df[df['label'] == asset]['asset_type'].iloc[0]
        print(f'  {asset:20} ({atype:8}): {count:3} rows')
print()
print('Assets per date distribution:')
counts = df.groupby('date').size()
print(f'  Min: {counts.min()}')
print(f'  Max: {counts.max()}')
print(f'  Avg: {counts.mean():.1f}')
print()
print('Assets by type:')
for atype in sorted(df['asset_type'].unique()):
    count = len(df[df['asset_type'] == atype]['label'].unique())
    rows = len(df[df['asset_type'] == atype])
    print(f'  {atype:8}: {count:3} unique assets, {rows:4} rows')
