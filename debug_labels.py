import pandas as pd

df = pd.read_parquet('data/processed/top20_monthly.parquet')

print('Unique label values (first 20):')
for label in df['label'].unique()[:20]:
    print(f'  "{label}"')
print()
print('Sample rows by asset_type:')
for atype in ['company', 'crypto', 'metal']:
    subset = df[df['asset_type'] == atype]
    if len(subset) > 0:
        sample = subset.iloc[0]
        print(f'{atype:8}: label="{sample["label"]}", market_cap={sample["market_cap"]:.2e}')
print()
print('Label value counts:')
print(df['label'].value_counts())
