import pandas as pd
import numpy as np

# Load the companies data
df = pd.read_csv('data/raw/companies_monthly_ALIGNED.csv')

# Check Samsung prices
print("Samsung (005930.ks) - Latest prices:")
print(f"Latest date: {df['date'].iloc[-1]}")
print(f"Samsung close price (latest): {df['close_005930.ks'].iloc[-1]}")
print(f"Samsung close price range: {df['close_005930.ks'].min()} to {df['close_005930.ks'].max()}")
print()

# Check a few other international stocks
print("RELIANCE.NS prices:")
print(f"Latest: {df['close_reliance.ns'].iloc[-1]}")
print(f"Range: {df['close_reliance.ns'].min()} to {df['close_reliance.ns'].max()}")
print()

print("2222.SR (Saudi Aramco) prices:")
print(f"Latest: {df['close_2222.sr'].iloc[-1]}")
print(f"Range: {df['close_2222.sr'].min()} to {df['close_2222.sr'].max()}")
print()

# Load shares outstanding
shares_df = pd.read_csv('config/shares_outstanding.csv')
print("Shares outstanding data:")
print(shares_df.to_string())
print()

# Calculate current market caps with shares
print("Current market cap calculations (incorrectly treating all prices as USD):")
for ticker in ['005930.ks', 'reliance.ns', '2222.sr']:
    col = f'close_{ticker}'
    latest_price = df[col].iloc[-1]
    
    # Get shares from reference
    ticker_upper = ticker.upper()
    shares_row = shares_df[shares_df['ticker'] == ticker_upper]
    
    if not shares_row.empty:
        shares = shares_row['shares_outstanding'].iloc[0]
        mcap = latest_price * shares
        print(f"{ticker_upper}: Price {latest_price:.2f} × Shares {shares:,} = ${mcap/1e12:.2f}T")
