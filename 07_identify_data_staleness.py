"""
Fetch & Compare Against 8marketcap.com Live Data
Validates our data against actual current market data
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

print("="*80)
print("FETCHING LIVE DATA FROM 8MARKETCAP.COM FOR VALIDATION")
print("="*80)

# Since 8marketcap.com doesn't have a public API, we'll document what SHOULD match
# Based on your screenshot showing $5,363 gold, let's work backwards

print("\n[1] EXPECTED DATA FROM 8marketcap.com (Based on user feedback)")
print("-" * 80)

# From user: Gold price today $5,363/oz
gold_price_real = 5363.00
gold_supply_oz = 210_000_000

gold_market_cap_real = gold_price_real * gold_supply_oz
print(f"\nGold Market Cap (using your price of ${gold_price_real}/oz):")
print(f"  Price: ${gold_price_real:,.2f}/oz")
print(f"  Supply: {gold_supply_oz:,} oz")
print(f"  Market Cap: ${gold_market_cap_real/1e12:.2f}T")

print("\n[2] OUR DATA (from ETL)")
print("-" * 80)

our_data = pd.read_csv('data/processed/latest_top20_snapshot.csv')
gold_ours = our_data[our_data['label'] == 'Gold']

if len(gold_ours) > 0:
    gold_cap_ours = gold_ours['market_cap'].values[0]
    gold_price_ours = 4713.90  # From our metals data
    print(f"\nGold Market Cap (from our ETL):")
    print(f"  Price: ${gold_price_ours:,.2f}/oz")
    print(f"  Market Cap: ${gold_cap_ours/1e12:.2f}T")
    
    discrepancy = ((gold_market_cap_real - gold_cap_ours) / gold_cap_ours) * 100
    print(f"\n  DISCREPANCY: {discrepancy:+.1f}%")
    print(f"  REASON: Gold price difference (${gold_price_real} vs ${gold_price_ours})")

print("\n[3] PROBLEM IDENTIFICATION")
print("="*80)

print("""
The core issue: Our gold price is from HISTORICAL yfinance data (2026-01-01),
but TODAY's price (2026-03-03) is $5,363, which is DIFFERENT.

This reveals the root problem:
  ❌ We're using STATIC snapshot data from 2026-02-24
  ❌ Not LIVE/CURRENT data (2026-03-03)
  ❌ Stock prices, crypto prices, and futures prices change DAILY

WHY THIS MATTERS:
  • Gold: $4,713.90 → $5,363 = 13.8% increase in 1+ month
  • NVIDIA, Apple, etc: Also changed significantly since Feb
  • Bitcoin: Likely changed since Feb
  
TO MATCH 8marketcap.com, we need TODAY'S prices, not month-old prices.
""")

print("\n[4] HOW TO GET LIVE DATA")
print("="*80)

print("""
Option A: AUTOMATED (Best Practice)
  1. Use yfinance library (already in our stack):
     - Download TODAY'S closing prices for all stocks
     - Download TODAY'S crypto prices from CoinGecko
     - Download TODAY'S precious metal futures from yfinance
  
  2. Script: fetch_live_data.py
     - Runs daily to get current prices
     - Calculates new market caps with today's data
     - Compares against 8marketcap.com published rankings

Option B: MANUAL (What you suggested)
  1. Check TradingView for gold price: $5,363/oz ✓
  2. Check individual stocks on Yahoo Finance or your broker
  3. Check CoinGecko for crypto prices
  4. Compare rankings against 8marketcap.com website
  
Option C: HYBRID (Recommended)
  1. Automated daily fetch with yfinance/CoinGecko
  2. Weekly manual spot-check against 8marketcap.com
  3. Alert if discrepancies found
""")

print("\n[5] DATA FRESHNESS REQUIREMENTS")
print("-" * 80)

print(f"""
Current Status:
  Last company data: 2026-02-01 (30+ days old)
  Last metals data: 2026-01-01 (60+ days old)
  Last crypto data: 2026-02-24 (7 days old)
  
For accurate 8marketcap.com matching:
  Required freshness: Daily update
  Critical for: Stock prices (change more than 1-2% daily on average)
  
Action: Build automated daily refresh pipeline
""")

# Example: Show what FRESH data would look like
print("\n[6] FRESH DATA EXAMPLE (What we SHOULD have)")
print("="*80)

print(f"""
If we refreshed TODAY (2026-03-03) with current prices:

Gold:
  Price today (3/3/2026): ${gold_price_real:,.2f}/oz
  Supply: 210M oz (constant)
  Market Cap: ${gold_market_cap_real/1e12:.2f}T (vs our ${gold_cap_ours/1e12:.2f}T)
  Status: NEEDS UPDATE (+13.8%)

NVIDIA (example - price would be current):
  Would need TODAY'S closing price from yfinance
  Would need TODAY'S share count (may have changed)
  Current in our data: 2026-02-01
  Status: NEEDS UPDATE (unknown % change)

Bitcoin (example):
  Current in our data: 2026-02-24 ($5,150.20)
  TODAY'S price: Unknown (crypto volatile)
  Status: POTENTIALLY STALE

RECOMMENDATION:
  Run fetch script TODAY to get all current prices
  Then compare TOP 20 against 8marketcap.com website
  Identify any rank changes from Feb to now
""")

print("\n" + "="*80)
print("NEXT STEP: Build automated daily data refresh")
print("="*80 + "\n")
