import pandas as pd

metals_orig = pd.read_csv('data/raw/metals_monthly.csv')

print("Metals Original CSV Structure:")
print(f"Total rows: {len(metals_orig)}")
print(f"Columns: {list(metals_orig.columns)}")
print()

# Check data for first date
first_date = metals_orig['date'].min()
print(f"Date {first_date}:")
subset = metals_orig[metals_orig['date'] == first_date]
print(f"  Rows: {len(subset)}")
print(subset[['date', 'ticker', 'name', 'market_cap']].to_string())

print()

# Check structure
print("All unique dates and their metal counts:")
date_counts = metals_orig.groupby('date')['name'].nunique()
print(f"Min metals per date: {date_counts.min()}")
print(f"Max metals per date: {date_counts.max()}")
print(f"Average: {date_counts.mean():.1f}")

# All metals
print(f"\nAll metals: {sorted(metals_orig['name'].unique())}")
print(f"Dates with all 4 metals:")
for date, group in metals_orig.groupby('date'):
    if group['name'].nunique() == 4:
        print(f"  {date}: {list(group['name'].unique())}")
        break
