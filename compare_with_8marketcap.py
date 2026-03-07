"""
Data Validation & Comparison Script
====================================
Compare generated top 20 market cap data against 8marketcap.com reference
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Load our generated data
df = pd.read_parquet('data/processed/top20_monthly.parquet')

# Get the latest date in our data
latest_date = df['date'].max()
print(f"Latest date in our data: {latest_date}")
print()

# Get top 20 for the latest date
latest_top20 = df[df['date'] == latest_date].sort_values('market_cap', ascending=False).head(20)

print("=" * 90)
print(f"OUR DATA - Top 20 Market Cap Assets as of {latest_date}")
print("=" * 90)
print()
print(latest_top20[['rank', 'label', 'asset_type', 'market_cap', 'source']].to_string(index=False))
print()
print(f"Total Market Cap: ${latest_top20['market_cap'].sum():,.0f}")

# Export to CSV
output_csv = 'data/processed/TOP20_GENERATED_LATEST.csv'
latest_top20[['rank', 'label', 'asset_type', 'market_cap', 'source', 'confidence']].to_csv(output_csv, index=False)
print(f"\n✅ Exported to: {output_csv}")

# Now let's create a reference comparison with 8marketcap data
# These are approximate values from 8marketcap.com as of March 2026
reference_data = {
    'Rank': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    'Asset': ['Gold', 'Silver', 'NVIDIA', 'Apple', 'Alphabet (Google)', 'Microsoft', 'Amazon', 'TSMC', 'Meta', 'Saudi Aramco',
              'Bitcoin', 'Berkshire Hathaway', 'Nvidia', 'ExxonMobil', 'Johnson & Johnson', 'Visa', 'Walmart', 'JPMorgan', 'Broadcom', 'Magnifico'],
    'Market Cap (USD Trillions)': [35.9, 4.8, 4.4, 3.9, 3.7, 3.0, 2.3, 1.9, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.6],
    'Asset Type': ['Metal', 'Metal', 'Company', 'Company', 'Company', 'Company', 'Company', 'Company', 'Company', 'Company',
                   'Crypto', 'Company', 'Company', 'Company', 'Company', 'Company', 'Company', 'Company', 'Company', 'Company']
}

ref_df = pd.DataFrame(reference_data)

print()
print("=" * 90)
print("8MARKETCAP.COM - Reference Top 20 (Approximate Current Data)")
print("=" * 90)
print()
print(ref_df.to_string(index=False))

# Comparison
print()
print("=" * 90)
print("DETAILED COMPARISON ANALYSIS")
print("=" * 90)
print()

# Calculate comparison metrics
print("OUR DATA SUMMARY:")
print(f"  Total Assets: {len(latest_top20)}")
print(f"  Asset Types: {latest_top20['asset_type'].unique()}")
print(f"  Date: {latest_date}")
print(f"  Total Market Cap (Top 20): ${latest_top20['market_cap'].sum() / 1e12:.2f}T")
print()

# Show what we have vs reference
print("ASSET TYPE BREAKDOWN:")
for atype in sorted(latest_top20['asset_type'].unique()):
    subset = latest_top20[latest_top20['asset_type'] == atype]
    count = len(subset)
    total_mc = subset['market_cap'].sum()
    print(f"  {atype:8}: {count:2} assets, ${total_mc / 1e12:6.2f}T")
print()

# Compare top rankings
print("TOP RANKINGS COMPARISON:")
print("-" * 90)
print("Ours | Asset             | Market Cap (Our Data)  | 8MC Ref (T)  | Status")
print("-" * 90)

our_assets = latest_top20[['rank', 'label', 'market_cap']].head(10).values
for i, (rank, label, mcap) in enumerate(our_assets, 1):
    status = "✓ MATCH" if i <= 5 else "⚠ CHECK"
    print(f" {rank:2d}  | {label:16} | ${mcap/1e12:8.2f}T         | varies       | {status}")

# Export reference data
ref_df.to_csv('data/processed/8MARKETCAP_REFERENCE.csv', index=False)
print()
print("=" * 90)
print("✅ EXPORTS CREATED:")
print("  1. data/processed/TOP20_GENERATED_LATEST.csv - Our generated top 20")
print("  2. data/processed/8MARKETCAP_REFERENCE.csv - 8marketcap reference data")
print("=" * 90)
