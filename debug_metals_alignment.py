import pandas as pd

# Check aligned metals
metals_aligned = pd.read_csv('data/raw/metals_monthly_ALIGNED.csv')

print("Metals ALIGNED CSV:")
print(f"  Total rows: {len(metals_aligned)}")
print(f"  Columns: {list(metals_aligned.columns)}")
print(f"  Dates: {metals_aligned['date'].nunique()}")
print(f"  Date range: {metals_aligned['date'].min()} to {metals_aligned['date'].max()}")

# Check what's in there
print(f"\nSample rows:")
print(metals_aligned.head(10))

# Check if there's a 'name' column
if 'name' in metals_aligned.columns:
    print(f"\nUnique metal names: {metals_aligned['name'].unique()}")
else:
    print(f"\nColumns available: {list(metals_aligned.columns)}")

# Compare with original
print("\n\n========================================")
print("Metals ORIGINAL CSV:")
metals_orig = pd.read_csv('data/raw/metals_monthly.csv')
print(f"  Total rows: {len(metals_orig)}")
print(f"  Unique metals: {metals_orig['name'].nunique()}")
print(f"  Metals: {sorted(metals_orig['name'].unique())}")
print(f"  Sample rows:")
print(metals_orig.head(5))
