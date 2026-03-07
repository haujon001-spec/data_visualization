import pandas as pd

df = pd.read_parquet('data/processed/top20_monthly.parquet')

print('Asset ID Analysis:')
print(f'Total rows: {len(df)}')
print(f'Rows with non-null asset_id: {df["asset_id"].notna().sum()}')
print(f'Rows with null asset_id: {df["asset_id"].isna().sum()}')
print()
print('Asset ID distribution by type:')
for atype in sorted(df['asset_type'].unique()):
    subset = df[df['asset_type'] == atype]
    non_null = subset['asset_id'].notna().sum()
    null = subset['asset_id'].isna().sum()
    print(f'  {atype:8}: {non_null:4} non-null, {null:4} null')
print()
print('Unique asset_id values (first 20):')
print(df[df['asset_id'].notna()]['asset_id'].unique()[:20])
