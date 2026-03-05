# -*- coding: utf-8 -*-
"""Analyze country codes in raw data to identify aggregates."""

import pandas as pd
from pathlib import Path

# Load raw data
raw_csv = Path("csv/raw/worldbank_population_raw_5Mar2026.csv")
df = pd.read_csv(raw_csv)

# Get unique codes
codes = df['country_code'].dropna().unique()
print(f"Total unique codes: {len(codes)}")

# Get codes sorted
codes_sorted = sorted([str(c) for c in codes])

# Print all codes
print("\nAll country codes:")
for i in range(0, len(codes_sorted), 10):
    print(', '.join(codes_sorted[i:i+10]))

# Check which codes appear in most/all years (likely aggregates)
code_year_counts = df.groupby('country_code')['year'].nunique()
full_coverage = code_year_counts[code_year_counts == code_year_counts.max()]

print(f"\n\nCodes with full year coverage ({code_year_counts.max()} years):")
print(f"Total: {len(full_coverage)}")
for code in sorted(full_coverage.index):
    if pd.notna(code):
        name = df[df['country_code'] == code]['country_name'].iloc[0]
        print(f"  {code}: {name}")
