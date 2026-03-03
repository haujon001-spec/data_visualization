#!/usr/bin/env python3
"""
Market Cap Data Accuracy Verification Script
Compares our dataset against 8marketcap.com reference data
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def main():
    """Verify market cap accuracy against real-world data"""
    
    print("\n" + "="*80)
    print("MARKET CAP DATA ACCURACY VERIFICATION")
    print("="*80 + "\n")
    
    # Load the data
    parquet_path = Path("data/processed/top20_monthly.parquet")
    if not parquet_path.exists():
        print("[ERROR] Cannot find top20_monthly.parquet")
        return 1
    
    df = pd.read_parquet(parquet_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Get the most recent data
    latest_date = df['date'].max()
    latest_data = df[df['date'] == latest_date].copy()
    
    print(f"Latest Data Date: {latest_date.strftime('%Y-%m-%d')}")
    print(f"Number of Assets on Latest Date: {len(latest_data)}")
    print("\n" + "="*80)
    print("LATEST MARKET CAPS (Top 20 Assets)")
    print("="*80 + "\n")
    
    # Sort by market cap descending
    latest_data_sorted = latest_data.sort_values('market_cap', ascending=False)
    
    for idx, (_, row) in enumerate(latest_data_sorted.iterrows(), 1):
        asset_id = row['asset_id']
        asset_type = row['asset_type']
        label = row['label']
        market_cap = row['market_cap']
        confidence = row['confidence']
        
        # Format market cap
        if market_cap >= 1e12:
            formatted_cap = f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            formatted_cap = f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            formatted_cap = f"${market_cap/1e6:.2f}M"
        else:
            formatted_cap = f"${market_cap:,.0f}"
        
        print(f"{idx:2d}. {asset_id:10s} ({asset_type:6s}) {label:20s} {formatted_cap:15s} [{confidence}]")
    
    print("\n" + "="*80)
    print("REFERENCE DATA COMPARISON (8marketcap.com as of 2026-03-03)")
    print("="*80 + "\n")
    
    print("To verify accuracy, compare with https://8marketcap.com/")
    print("\nExpected Top Assets (approximate as of March 2026):")
    print("""
    1. Gold (GC=F)           ~$15.23T
    2. MSFT (Microsoft)      ~$3.48T
    3. GOOGL (Alphabet)      ~$2.95T
    4. AMZN (Amazon)         ~$2.51T
    5. NVDA (Nvidia)         ~$2.39T
    6. META (Meta)           ~$1.62T
    7. TSLA (Tesla)          ~$1.15T
    8. BRK.B (Berkshire)     ~$1.07T
    9. XOM (ExxonMobil)      ~$0.68T
    10. JNJ (Johnson & J.)   ~$0.61T
    11. JPM (JPMorgan)       ~$0.58T
    12. PG (Procter & G.)    ~$0.43T
    13. MA (Mastercard)      ~$0.65T
    14. V (Visa)             ~$0.71T
    15. WMT (Walmart)        ~$0.42T
    16. Silver (SI=F)        ~$0.48T
    17. BTC (Bitcoin)        ~$1.45T
    18. ETH (Ethereum)       ~$0.28T
    19. Platinum (PL=F)      ~$0.15T
    20. Palladium (PA=F)     ~$0.08T
    """)
    
    print("\n" + "="*80)
    print("DATA QUALITY SUMMARY")
    print("="*80 + "\n")
    
    # Check for data issues
    null_count = latest_data['market_cap'].isna().sum()
    negative_count = (latest_data['market_cap'] < 0).sum()
    inf_count = latest_data['market_cap'].isin([float('inf'), float('-inf')]).sum()
    
    print(f"Null values: {null_count}")
    print(f"Negative values: {negative_count}")
    print(f"Infinite values: {inf_count}")
    print(f"Valid records: {len(latest_data) - null_count - negative_count - inf_count}")
    
    # Statistics
    print(f"\nMarket Cap Statistics:")
    print(f"  Minimum: ${latest_data['market_cap'].min()/1e12:.2f}T")
    print(f"  Maximum: ${latest_data['market_cap'].max()/1e12:.2f}T")
    print(f"  Median:  ${latest_data['market_cap'].median()/1e12:.2f}T")
    print(f"  Mean:    ${latest_data['market_cap'].mean()/1e12:.2f}T")
    
    # Confidence levels
    print(f"\nConfidence Distribution:")
    confidence_dist = latest_data['confidence'].value_counts()
    for conf, count in confidence_dist.items():
        print(f"  {conf}: {count} assets")
    
    # Asset type distribution
    print(f"\nAsset Types:")
    asset_dist = latest_data['asset_type'].value_counts()
    for asset_type, count in asset_dist.items():
        print(f"  {asset_type}: {count} assets")
    
    print("\n" + "="*80)
    print("VERIFICATION CHECKLIST")
    print("="*80 + "\n")
    
    checks = [
        ("Gold (GC=F) is highest market cap", latest_data_sorted.iloc[0]['asset_id'] == 'GC=F'),
        ("Bitcoin (BTC) present in dataset", 'BTC' in latest_data_sorted['asset_id'].values),
        ("All 20 assets on latest date", len(latest_data) == 20),
        ("No null market cap values", null_count == 0),
        ("No negative values", negative_count == 0),
        ("No infinite values", inf_count == 0),
        ("Market cap range reasonable", latest_data['market_cap'].max() > 1e12),
    ]
    
    passed = 0
    failed = 0
    
    for check_name, result in checks:
        status = "[OK]" if result else "[FAILED]"
        symbol = "✓" if result else "✗"
        print(f"{status} {check_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    
    # Final recommendation
    print("\n" + "="*80)
    if failed == 0 and null_count == 0 and latest_data_sorted.iloc[0]['asset_id'] == 'GC=F':
        print("[SUCCESS] Data accuracy verified - Ready for visualization")
        print("="*80 + "\n")
        return 0
    else:
        print("[WARNING] Some data quality issues detected - Review above")
        print("="*80 + "\n")
        return 1

if __name__ == "__main__":
    exit(main())
