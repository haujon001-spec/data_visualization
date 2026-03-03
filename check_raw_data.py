import pandas as pd

print("="*80)
print("RAW DATA FILES STATUS")
print("="*80)

# Check companies
try:
    companies = pd.read_csv('data/raw/companies_monthly.csv')
    print(f"\nCompanies data: {companies.shape[0]} rows, {companies.shape[1]} columns")
    print(f"Date range: {companies.columns[1:].min()} to {companies.columns[1:].max()}")
    print(f"Assets: {companies['Ticker'].nunique()}")
    print(companies.head())
except Exception as e:
    print(f"ERROR reading companies: {e}")

# Check crypto
try:
    crypto = pd.read_csv('data/raw/crypto_monthly.csv')
    print(f"\n\nCrypto data: {crypto.shape[0]} rows, {crypto.shape[1]} columns")
    print(crypto.head())
except Exception as e:
    print(f"ERROR reading crypto: {e}")

# Check metals
try:
    metals = pd.read_csv('data/raw/metals_monthly.csv')
    print(f"\n\nMetals data: {metals.shape[0]} rows, {metals.shape[1]} columns")
    print(metals.head())
except Exception as e:
    print(f"ERROR reading metals: {e}")

# Check top20 CSV
try:
    top20_csv = pd.read_csv('data/processed/top20_monthly.csv')
    print(f"\n\nTop20 CSV: {top20_csv.shape[0]} rows, {top20_csv.shape[1]} columns")
    print(top20_csv.head(20))
    print(f"\nUnique labels: {top20_csv['label'].nunique()}")
    print(top20_csv['label'].unique())
except Exception as e:
    print(f"ERROR reading top20 CSV: {e}")
