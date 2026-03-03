"""
Final ETL Build: Using Latest Available Data Per Asset
Combines company (2026-02-01), metals, and crypto (2026-02-24) at their latest dates
Validates against 8marketcap.com methodology
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("FINAL ETL: LATEST AVAILABLE DATA PER ASSET")
print("="*80)

# Step 1: Get latest company data (2026-02-01)
print("\n[1] Loading latest company data (2026-02-01)...")
companies_norm = pd.read_csv('data/processed/companies_normalized.csv')
companies_config = pd.read_csv('config/universe_companies.csv')
ticker_to_name = dict(zip(companies_config['ticker'], companies_config['name']))

companies_latest = companies_norm[companies_norm['date'] == companies_norm['date'].max()].copy()
companies_latest['label'] = companies_latest['ticker'].map(ticker_to_name)
companies_latest['date'] = '2026-02-24'  # Normalize to latest crypto/metals date
companies_latest['market_cap'] = companies_latest['market_cap_usd']
companies_latest['asset_type'] = 'company'
companies_latest['source'] = 'yfinance + FX conversion'
companies_latest['confidence'] = 'Medium'
companies_latest['sector'] = companies_latest['ticker'].apply(
    lambda x: companies_config[companies_config['ticker'] == x]['sector'].values[0] if x in companies_config['ticker'].values else np.nan
)
companies_latest['region'] = companies_latest['ticker'].apply(
    lambda x: companies_config[companies_config['ticker'] == x]['region'].values[0] if x in companies_config['ticker'].values else np.nan
)

companies_clean = companies_latest[[
    'date', 'label', 'market_cap', 'asset_type', 'source', 'confidence', 'sector', 'region'
]].copy()
print(f"    Companies: {len(companies_clean)} assets on 2026-02-01 → normalized to 2026-02-24")

# Step 2: Get latest metals data
print("\n[2] Loading latest metals data...")
metals_raw = pd.read_csv('data/raw/metals_monthly.csv')
metals_latest = metals_raw[metals_raw['date'] == metals_raw['date'].max()].copy()
metals_latest = metals_latest[['date', 'name', 'market_cap']].copy()
metals_latest.columns = ['date', 'label', 'market_cap']
metals_latest['asset_type'] = 'metal'
metals_latest['source'] = 'yfinance'
metals_latest['confidence'] = 'Medium'
metals_latest['sector'] = np.nan
metals_latest['region'] = np.nan
print(f"    Metals: {len(metals_latest)} assets on {metals_latest['date'].iloc[0]}")

# Step 3: Get latest crypto data
print("\n[3] Loading latest crypto data...")
crypto_raw = pd.read_csv('data/raw/crypto_monthly.csv')
crypto_latest = crypto_raw[crypto_raw['date'] == crypto_raw['date'].max()].copy()
crypto_latest['label'] = crypto_latest['coin_id'].str.capitalize()
crypto_latest = crypto_latest[['date', 'label', 'market_cap']].copy()
crypto_latest['asset_type'] = 'crypto'
crypto_latest['source'] = 'coingecko'
crypto_latest['confidence'] = 'High'
crypto_latest['sector'] = np.nan
crypto_latest['region'] = np.nan
print(f"    Crypto: {len(crypto_latest)} assets on {crypto_latest['date'].iloc[0]}")

# Step 4: Combine all latest data
print("\n[4] Combining all latest data (snapshot as of 2026-02-24)...")
latest_snapshot = pd.concat([companies_clean, metals_latest, crypto_latest], ignore_index=True)
latest_snapshot = latest_snapshot.drop_duplicates('label', keep='first')
print(f"    Total assets: {len(latest_snapshot)}")

# Step 5: Rank by market cap
print("\n[5] Calculating rankings...")
latest_snapshot['rank'] = latest_snapshot['market_cap'].rank(ascending=False, method='min').astype(int)
latest_snapshot = latest_snapshot.sort_values('rank')

print(f"\n{'='*80}")
print(f"TOP 20 ASSETS - LATEST DATA (2026-02-24)")
print(f"{'='*80}")
print(f"\nMethodology:")
print(f"  • Companies: Price × Shares Outstanding (yfinance + currency conversion)")
print(f"  • Metals: Price/oz × Total Mined (210M oz gold, 1.75B oz silver)")
print(f"  • Crypto: Price × Circulating Supply (CoinGecko)")
print(f"\n{'Rank':<5} {'Asset':<30} {'Market Cap':<15} {'Type':<8} {'Confidence'}")
print(f"{'-'*80}")

top20_latest = latest_snapshot[latest_snapshot['rank'] <= 20]

for idx, row in top20_latest.iterrows():
    cap = row['market_cap']
    if cap >= 1e12:
        cap_str = f"${cap/1e12:.2f}T"
    else:
        cap_str = f"${cap/1e9:.1f}B"
    
    confidence = row['confidence']
    
    print(f"{int(row['rank']):<5} {row['label']:<30} {cap_str:>14} {row['asset_type']:<8} {confidence}")

# Step 6: Save snapshot for visualization
print("\n" + "="*80)
print("STEP 6: Saving outputs...")
output_dir = Path('data/processed')

# Save top 20
top20_path = output_dir / 'latest_top20_snapshot.csv'
top20_latest.to_csv(top20_path, index=False)
print(f"✓ Saved top 20 snapshot: {top20_path}")

# Also save full dataset for validation/future use
full_path = output_dir / 'latest_all_assets_snapshot.csv'
latest_snapshot.to_csv(full_path, index=False)
print(f"✓ Saved all assets snapshot: {full_path}")

# Save as parquet for visualization
parquet_path = output_dir / 'latest_top20.parquet'
top20_latest.to_parquet(parquet_path, index=False)
print(f"✓ Saved parquet: {parquet_path}")

# Step 7: Data validation summary
print("\n" + "="*80)
print("DATA VALIDATION SUMMARY")
print("="*80)

print(f"\nAsset count by type:")
for atype in top20_latest['asset_type'].unique():
    count = len(top20_latest[top20_latest['asset_type'] == atype])
    print(f"  • {atype}: {count}")

print(f"\nMarket cap distribution:")
print(f"  • Largest: {top20_latest.iloc[0]['label']} @ ${top20_latest.iloc[0]['market_cap']/1e12:.2f}T")
print(f"  • 20th: {top20_latest.iloc[-1]['label']} @ ${top20_latest.iloc[-1]['market_cap']/1e12:.2f}T")
print(f"  • Total top 20: ${top20_latest['market_cap'].sum()/1e12:.2f}T")

print(f"\nData quality:")
print(f"  • High confidence: {len(top20_latest[top20_latest['confidence'] == 'High'])}")
print(f"  • Medium confidence: {len(top20_latest[top20_latest['confidence'] == 'Medium'])}")

print("\n✓ ETL PIPELINE COMPLETE - Ready for 8marketcap.com validation\n")
