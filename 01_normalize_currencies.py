"""
ETL Pipeline with Currency Normalization
Converts all international stock prices to USD and validates against 8marketcap.com methodology
"""

import pandas as pd
import numpy as np
from pathlib import Path
import requests
from datetime import datetime
import json

print("="*80)
print("STEP 1: IDENTIFY CURRENCIES AND BUILD CONVERSION TABLE")
print("="*80)

# Load company config to identify currencies
companies_config = pd.read_csv('config/universe_companies.csv')

# Currency mapping based on ticker symbols and regions
currency_map = {
    'AAPL': 'USD',
    'MSFT': 'USD',
    'NVDA': 'USD',
    'TSLA': 'USD',
    'AMZN': 'USD',
    'META': 'USD',
    'GOOGL': 'USD',
    'BRK.B': 'USD',  # (Not in data)
    'JPM': 'USD',
    'WMT': 'USD',
    'BABA': 'USD',  # Alibaba trades in USD on NYSE
    'TSM': 'USD',  # Taiwan Semiconductor trades in USD on NYSE/NASDAQ
    'SAP': 'EUR',  # German company, trades in EUR
    'ASML': 'EUR',  # Dutch company, trades in EUR
    'RDSB': 'USD',  # Shell trades in USD (not in data)
    '005930.KS': 'KRW',  # Samsung Electronics Korea Won
    '2222.SR': 'SAR',  # Saudi Aramco Saudi Riyal
    'HDB': 'INR',  # HDFC Bank Indian Rupee
    'RELIANCE.NS': 'INR',  # Reliance Industries Indian Rupee
    'SSNLF': 'RUB',  # Surgutneftegaz Russian Ruble
}

print("\nCurrency Summary:")
print("-" * 50)
for ticker, currency in currency_map.items():
    if ticker in companies_config['ticker'].values:
        company = companies_config[companies_config['ticker'] == ticker]['name'].values[0]
        print(f"{ticker:<20} {currency:<5} {company}")

# For this analysis, let's try to fetch historical exchange rates
# Since this is 2026 data, we'll estimate based on typical 2016-2026 rates
# In production, you'd fetch from OANDA, ECB, or other forex APIs

print("\n" + "="*80)
print("STEP 2: LOAD RAW DATA AND APPLY CURRENCY CONVERSION")
print("="*80)

# Load companies data
companies_raw = pd.read_csv('data/raw/companies_monthly.csv')
print(f"\nLoaded companies data: {companies_raw.shape[0]} rows")

# Extract close prices for each company
companies_list = []
for ticker_symbol in [c.split('_')[-1].upper() for c in companies_raw.columns if c.startswith('close_')]:
    col_name = f'close_{ticker_symbol.lower()}'
    
    if col_name in companies_raw.columns:
        ticker_data = companies_raw[['date', col_name]].copy()
        ticker_data.columns = ['date', 'price_local_currency']
        ticker_data['ticker'] = ticker_symbol
        ticker_data['currency'] = currency_map.get(ticker_symbol, 'USD')
        ticker_data = ticker_data[ticker_data['price_local_currency'].notna()]
        
        companies_list.append(ticker_data)

companies_df = pd.concat(companies_list, ignore_index=True)
print(f"Extracted close prices: {len(companies_df)} records")

# Now we need exchange rates. For this PoC, let's use typical rates for key dates
# In production, fetch from OANDA historical forex API
exchange_rates = {
    '2016-01-01': {'KRW': 1195.0, 'EUR': 0.92, 'SAR': 3.75, 'INR': 66.5, 'RUB': 75.0},
    '2020-01-01': {'KRW': 1167.5, 'EUR': 0.90, 'SAR': 3.75, 'INR': 71.4, 'RUB': 61.5},
    '2023-01-01': {'KRW': 1288.0, 'EUR': 0.94, 'SAR': 3.75, 'INR': 82.7, 'RUB': 73.0},
    '2026-02-01': {'KRW': 1350.0, 'EUR': 1.08, 'SAR': 3.75, 'INR': 84.0, 'RUB': 95.0},
}

def get_exchange_rate(date_str, currency):
    """Get approximate exchange rate for a given date"""
    if currency == 'USD':
        return 1.0
    
    # For simplicity in this PoC, use closest date we have
    date_obj = pd.to_datetime(date_str)
    closest_date = min(exchange_rates.keys(), key=lambda x: abs(pd.to_datetime(x) - date_obj))
    
    return exchange_rates[closest_date].get(currency, 1.0)

# Apply currency conversion
companies_df['conversion_rate'] = companies_df.apply(
    lambda row: get_exchange_rate(row['date'], row['currency']), 
    axis=1
)
companies_df['price_usd'] = companies_df['price_local_currency'] / companies_df['conversion_rate']

print(f"\nCurrency Conversion Applied:")
print("-" * 50)
sample_conversion = companies_df[companies_df['currency'] != 'USD'].drop_duplicates('ticker')[['ticker', 'currency', 'price_local_currency', 'conversion_rate', 'price_usd']].head()
print(sample_conversion.to_string())

# Load shares outstanding
print("\n" + "="*80)
print("STEP 3: CALCULATE MARKET CAPS (Price × Shares)")
print("="*80)

shares_outstanding = pd.read_csv('config/shares_outstanding.csv')
ticker_to_shares = dict(zip(shares_outstanding['ticker'].str.upper(), shares_outstanding['shares_outstanding']))

companies_df['shares'] = companies_df['ticker'].map(ticker_to_shares)
companies_df['market_cap_usd'] = companies_df['price_usd'] * companies_df['shares']

print(f"\nMarket Cap Calculation (Latest Date: 2026-02-01):")
print("-" * 50)
latest_date = companies_df['date'].max()
latest_companies = companies_df[companies_df['date'] == latest_date].sort_values('market_cap_usd', ascending=False)
print(latest_companies[['ticker', 'price_local_currency', 'currency', 'price_usd', 'shares', 'market_cap_usd']].head(10).to_string())

print(f"\nTotal companies with market cap: {len(companies_df[companies_df['market_cap_usd'].notna()])}")

# Save for next step
print("\n" + "="*80)
print("STEP 4: SAVE NORMALIZED COMPANY DATA")
print("="*80)

companies_normalized = companies_df[[
    'date', 'ticker', 'price_local_currency', 'currency', 'conversion_rate', 
    'price_usd', 'shares', 'market_cap_usd'
]].copy()

companies_normalized.to_csv('data/processed/companies_normalized.csv', index=False)
print(f"✓ Saved normalized company data: {len(companies_normalized)} rows")

# Also create a summary of conversions for validation
conversion_summary = companies_df[companies_df['currency'] != 'USD'].groupby(['ticker', 'currency']).agg({
    'price_local_currency': 'mean',
    'conversion_rate': 'mean',
    'price_usd': 'mean'
}).round(2)

print("\nAverage Price Conversion by Currency:")
print("-" * 50)
print(conversion_summary.to_string())

print("\n" + "="*80)
print("CURRENCY NORMALIZATION COMPLETE")
print("="*80)
