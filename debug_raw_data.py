import pandas as pd
import os

for file in ['companies_monthly.csv', 'crypto_monthly.csv', 'metals_monthly.csv']:
    path = os.path.join('data/raw', file)
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f'{file}:')
        print(f'  Rows: {len(df)}')
        print(f'  Columns: {list(df.columns)}')
        if 'date' in df.columns:
            print(f'  Unique dates: {df["date"].nunique()}')
            print(f'  Date range: {df["date"].min()} to {df["date"].max()}')
        # Show sample
        print(f'  Sample row: {df.iloc[0].to_dict()}')
        print()
