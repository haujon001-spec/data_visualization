import pandas as pd

# Check the source CSVs
print("RAW DATA ANALYSIS")  
print("=" * 70)

companies_raw = pd.read_csv('data/raw/companies_monthly.csv')
crypto_raw = pd.read_csv('data/raw/crypto_monthly.csv')
metals_raw = pd.read_csv('data/raw/metals_monthly.csv')

print("\nCOMPANIES_MONTHLY.CSV:")
print(f"  Total rows: {len(companies_raw)}")
print(f"  Unique dates: {companies_raw['date'].nunique()}")
print(f"  Date range: {companies_raw['date'].min()} to {companies_raw['date'].max()}")
print(f"  Sample dates: {sorted(companies_raw['date'].unique())[:5]}")

print("\nCRYPTO_MONTHLY.CSV:")
print(f"  Total rows: {len(crypto_raw)}")
print(f"  Unique dates: {crypto_raw['date'].nunique()}")
print(f"  Date range: {crypto_raw['date'].min()} to {crypto_raw['date'].max()}")
print(f"  Sample dates: {sorted(crypto_raw['date'].unique())[:5]}")

print("\nMETALS_MONTHLY.CSV:")
print(f"  Total rows: {len(metals_raw)}")
print(f"  Unique dates: {metals_raw['date'].nunique()}")
print(f"  Date range: {metals_raw['date'].min()} to {metals_raw['date'].max()}")
print(f"  Sample dates: {sorted(metals_raw['date'].unique())[:5]}")

# Check date alignment
companies_dates = set(companies_raw['date'].unique())
crypto_dates = set(crypto_raw['date'].unique())
metals_dates = set(metals_raw['date'].unique())

print("\n\nDATE ALIGNMENT ANALYSIS:")
print("=" * 70)
all_dates = companies_dates | crypto_dates | metals_dates
companies_only = companies_dates - crypto_dates - metals_dates
crypto_only = crypto_dates - companies_dates - metals_dates
metals_only = metals_dates - companies_dates - crypto_dates
all_three = companies_dates & crypto_dates & metals_dates

print(f"Total unique dates across all files: {len(all_dates)}")
print(f"Dates in ALL THREE: {len(all_three)}")
print(f"Companies only: {len(companies_only)}")
print(f"Crypto only: {len(crypto_only)}")
print(f"Metals only: {len(metals_only)}")

print(f"\nDates in all three files: {sorted(list(all_three))[:10]}")
