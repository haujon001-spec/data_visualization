"""
Fix Samsung and Currency Issues
================================
Check for shares outstanding reference data and implement proper currency conversion
"""

import pandas as pd
import os

print("Looking for shares outstanding reference file...")
print("=" * 70)

# Check for shares file
shares_files = [
    'config/shares_outstanding.csv',
    'data/config/shares_outstanding.csv',
    'shares_outstanding.csv'
]

found_file = None
for shares_file in shares_files:
    if os.path.exists(shares_file):
        found_file = shares_file
        break

if found_file:
    print(f"✓ Found: {found_file}\n")
    shares_df = pd.read_csv(found_file)
    print(shares_df.head(20))
    
    # Check Samsung
    samsung = shares_df[shares_df['ticker'].str.upper().str.contains('SAMSUNG|005930', na=False)]
    if len(samsung) > 0:
        print(f"\nSamsung entry found:")
        print(samsung)
else:
    print("✗ No shares outstanding reference file found")
    print("\nWe need to create one with proper data:")
    print("  - Samsung (005930.KS): ~5.76B shares, KRW currency")
    print("  - Need EUR to USD conversion for European stocks")
    print("  - Need INR to USD conversion for Indian stocks")
    print("  - etc.")

# Check what directories exist
print("\n" + "=" * 70)
print("Directory structure:")
print("=" * 70)

for root, dirs, files in os.walk('data'):
    level = root.replace('data', '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in files[:5]:  # Limit to first 5 files per directory
        print(f'{subindent}{file}')
    if len(files) > 5:
        print(f'{subindent}... and {len(files) - 5} more files')

print("\n" + "=" * 70)
print("SOLUTION REQUIRED:")
print("=" * 70)
print("1. Create/update shares_outstanding.csv with:")
print("   - Proper share counts for each company")
print("   - Currency information (USD vs KRW vs INR vs etc)")
print("2. Implement currency conversion for non-USD stocks")
print("3. Re-run rankings with corrected calculations")
