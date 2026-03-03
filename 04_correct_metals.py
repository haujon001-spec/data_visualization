"""
Metals Data Correction: Recalculate market cap with correct supplies
Uses:
  - Gold: 210M oz (World Gold Council)
  - Silver: 1.75B oz (USGS)
  - Platinum: 200M oz (USGS)
  - Palladium: 150M oz (USGS)
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("CORRECTING METALS DATA WITH ACCURATE SUPPLIES")
print("="*80)

# Load raw metals data
metals_raw = pd.read_csv('data/raw/metals_monthly.csv')

# Correct supply values (in troy ounces)
CORRECT_SUPPLIES = {
    'Gold': 210_000_000,         # 210 million oz
    'Silver': 1_750_000_000,      # 1.75 billion oz
    'Platinum': 200_000_000,      # 200 million oz
    'Palladium': 150_000_000,     # 150 million oz
}

print("\nCorrect supplies (troy ounces):")
for metal, supply in CORRECT_SUPPLIES.items():
    print(f"  {metal}: {supply:,} oz ({supply/1e9:.2f}B oz)")

# Recalculate market cap with correct supplies
metals_corrected = metals_raw.copy()
metals_corrected['supply_oz'] = metals_corrected['name'].map(CORRECT_SUPPLIES)
metals_corrected['market_cap_old'] = metals_corrected['market_cap']
metals_corrected['market_cap'] = metals_corrected['price_per_ounce'] * metals_corrected['supply_oz']

# Show corrections
print(f"\n{'='*80}")
print(f"CORRECTION EXAMPLES (Latest date)")
print(f"{'='*80}\n")

latest = metals_corrected[metals_corrected['date'] == metals_corrected['date'].max()]
for idx, row in latest.iterrows():
    metal = row['name']
    old_cap = row['market_cap_old'] / 1e12
    new_cap = row['market_cap'] / 1e12
    price = row['price_per_ounce']
    reduction_factor = old_cap / new_cap if new_cap > 0 else 0
    
    print(f"{metal}:")
    print(f"  Price: ${price:.2f}/oz")
    print(f"  OLD Market Cap: ${old_cap:.2f}T")
    print(f"  NEW Market Cap: ${new_cap:.2f}T")
    print(f"  Reduction factor: {reduction_factor:.1f}x")
    print()

# Save corrected metals data
output_dir = Path('data/raw')
metals_corrected_path = output_dir / 'metals_monthly.csv'
metals_corrected.to_csv(metals_corrected_path, index=False, columns=['date', 'ticker', 'name', 'price_per_ounce', 'market_cap'])

print("="*80)
print(f"✓ Corrected metals data saved: data/raw/metals_monthly.csv")
print("="*80)
