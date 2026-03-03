"""
Rebuild top20_monthly.parquet with actual Top 20 global assets.
Includes: major companies, top cryptocurrencies, and precious metals.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("REBUILDING TOP 20 GLOBAL MARKET CAP DATA")
print("=" * 80)

# Top companies by market cap (as of Feb 2024 - approximate)
top_companies = {
    'AAPL': {'name': 'Apple', 'sector': 'Technology', 'mcap_2024': 3.2e12},
    'MSFT': {'name': 'Microsoft', 'sector': 'Technology', 'mcap_2024': 3.1e12},
    'NVDA': {'name': 'NVIDIA', 'sector': 'Technology', 'mcap_2024': 2.7e12},
    'BRK.B': {'name': 'Berkshire Hathaway', 'sector': 'Diversified', 'mcap_2024': 1.1e12},
    'AMZN': {'name': 'Amazon', 'sector': 'Consumer & Tech', 'mcap_2024': 1.8e12},
    'GOOGL': {'name': 'Alphabet', 'sector': 'Technology', 'mcap_2024': 1.75e12},
    'META': {'name': 'Meta', 'sector': 'Technology', 'mcap_2024': 1.1e12},
    'TSLA': {'name': 'Tesla', 'sector': 'Automotive', 'mcap_2024': 1.0e12},
    'ASML': {'name': 'ASML', 'sector': 'Technology', 'mcap_2024': 350e9},
    'JPM': {'name': 'JPMorgan', 'sector': 'Financial', 'mcap_2024': 550e9},
}

# Top cryptos by market cap
top_cryptos = {
    'BTC': {'name': 'Bitcoin', 'sector': 'Digital Assets', 'symbol': 'BTC'},
    'ETH': {'name': 'Ethereum', 'sector': 'Digital Assets', 'symbol': 'ETH'},
}

# Precious metals
metals = {
    'GC=F': {'name': 'Gold', 'sector': 'Commodities'},
    'SI=F': {'name': 'Silver', 'sector': 'Commodities'},
    'PL=F': {'name': 'Platinum', 'sector': 'Commodities'},
    'PA=F': {'name': 'Palladium', 'sector': 'Commodities'},
}

# Build top 20 from last 10 years
date_start = pd.Timestamp('2016-01-01')
date_end = pd.Timestamp('2026-02-24')

print(f"\nFetching data from {date_start.date()} to {date_end.date()}...")

# Fetch company prices
company_data = []
for ticker, info in top_companies.items():
    try:
        print(f"  Fetching {ticker}...", end=" ")
        hist = yf.download(ticker, start=date_start, end=date_end, interval='1mo', progress=False)
        
        if len(hist) == 0:
            print("FAILED (no data)")
            continue
        
        # Get shares outstanding (approximate using latest)
        stock = yf.Ticker(ticker)
        try:
            shares = stock.info.get('sharesOutstanding', 1e9)
        except:
            shares = 1e9
        
        # Calculate market cap
        hist_df = hist[['Adj Close']].reset_index()
        hist_df['market_cap'] = hist_df['Adj Close'] * shares
        hist_df['asset_id'] = ticker
        hist_df['label'] = info['name']
        hist_df['asset_type'] = 'company'
        hist_df['sector'] = info['sector']
        hist_df['region'] = 'Global'
        hist_df['source'] = 'yfinance'
        hist_df['confidence'] = 'Medium'
        hist_df['notes'] = f'Shares: {shares:,.0f}'
        hist_df['date'] = hist_df['Date'].dt.strftime('%Y-%m-%d')
        
        company_data.append(hist_df[['date', 'asset_id', 'label', 'asset_type', 'market_cap', 'sector', 'region', 'source', 'confidence', 'notes']])
        print(f"OK ({len(hist)} months)")
    except Exception as e:
        print(f"ERROR: {str(e)[:50]}")

# Metals data (from existing file - already good)
print("\n  Loading metals data...")
try:
    metals_df = pd.read_csv('data/raw/metals_monthly.csv')
    metals_df['date'] = pd.to_datetime(metals_df['date']).dt.strftime('%Y-%m-%d')
    metals_df['region'] = 'Global'
    print(f"    Metals: {len(metals_df)} rows")
except Exception as e:
    print(f"    Metals: FAILED - {e}")
    metals_df = pd.DataFrame()

# Bitcoin from existing data
print("  Loading Bitcoin data...")
try:
    crypto_df = pd.read_csv('data/raw/crypto_monthly.csv')
    crypto_df['date'] = pd.to_datetime(crypto_df['date']).dt.strftime('%Y-%m-%d')
    crypto_df['region'] = 'Global'
    print(f"    Crypto: {len(crypto_df)} rows")
except Exception as e:
    print(f"    Crypto: FAILED - {e}")
    crypto_df = pd.DataFrame()

# Combine all
all_data = []
if company_data:
    all_data.extend(company_data)
if len(metals_df) > 0:
    all_data.append(metals_df)
if len(crypto_df) > 0:
    all_data.append(crypto_df)

if not all_data:
    print("\nERROR: No data collected!")
    exit(1)

df = pd.concat(all_data, ignore_index=True)

print(f"\nCombined {len(df)} total records from {df['date'].nunique()} unique dates")
print(f"Assets: {df['label'].nunique()} unique")
print(f"Asset types: {df['asset_type'].unique()}")

# Rank top 20 per date
print("\nRanking top 20 per date...")
df['date'] = pd.to_datetime(df['date'])

df_ranked = []
for date, group in df.groupby('date'):
    top20 = group.nlargest(20, 'market_cap').copy()
    top20['rank'] = range(1, len(top20) + 1)
    df_ranked.append(top20)

final_df = pd.concat(df_ranked, ignore_index=True)
final_df['date'] = final_df['date'].dt.strftime('%Y-%m-%d')

print(f"\nFinal dataset:")
print(f"  Shape: {final_df.shape}")
print(f"  Dates: {final_df['date'].nunique()}")
print(f"  Assets per date avg: {final_df.groupby('date').size().mean():.1f}")

# Show sample of latest date
print(f"\nLatest date ({final_df['date'].max()}) top 20:")
latest = final_df[final_df['date'] == final_df['date'].max()].nlargest(20, 'market_cap')
print(latest[['rank', 'label', 'asset_type', 'market_cap', 'sector']].to_string(index=False))

# Save
output_cols = ['date', 'rank', 'asset_id', 'asset_type', 'label', 'market_cap', 'source', 'confidence', 'sector', 'region', 'notes']
final_df[output_cols].to_parquet('data/processed/top20_monthly.parquet', index=False)

print(f"\n✓ Data saved to data/processed/top20_monthly.parquet")
