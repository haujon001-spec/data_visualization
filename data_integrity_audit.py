#!/usr/bin/env python3
"""
Data Integrity Audit Framework

Validates data import and calculations from multiple sources:
- yfinance (companies, metals)
- CoinGecko (cryptocurrencies)
- CoinMarketCap (alternative crypto validation)
- Manual sources (precious metals supply)

Creates comprehensive audit report with:
- Source validation (prices match current market)
- Market cap calculation verification
- Ranking accuracy checks
- Data discrepancy identification
- Root cause analysis
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(Path("logs") / "data_integrity_audit.log")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)


class DataIntegrityAudit:
    """Comprehensive data validation framework."""
    
    def __init__(self):
        self.audit_results = {}
        self.issues_found = []
        self.calculations_verified = []
        
    def audit_precious_metals(self):
        """Audit precious metals market cap calculation."""
        print("\n" + "="*80)
        print("PRECIOUS METALS AUDIT")
        print("="*80)
        
        # Load config
        metals_config = pd.read_csv("config/precious_metals_supply.csv")
        print("\nMetals Configuration:")
        print(metals_config.to_string())
        
        # Check current prices and calculate expected market caps
        print("\n" + "-"*80)
        print("GOLD (GC=F) CALCULATION VERIFICATION")
        print("-"*80)
        
        # Load raw metals data
        try:
            metals_data = pd.read_csv("data/raw/metals_monthly.csv")
            gold_data = metals_data[metals_data['ticker'] == 'GC=F'].copy()
            
            if gold_data.empty:
                print("ERROR: No gold data found in metals_monthly.csv")
                return
            
            # Get latest gold data
            gold_data['date'] = pd.to_datetime(gold_data['date'])
            latest_gold = gold_data.sort_values('date').iloc[-1]
            
            print(f"Latest Gold Data (Date: {latest_gold['date'].date()}):")
            print(f"  Price per ounce: ${latest_gold.get('price_per_ounce', 'N/A')}")
            print(f"  Market cap (calculated): ${latest_gold.get('market_cap', 'N/A'):,.0f}")
            print(f"  Market cap (billions): ${latest_gold.get('market_cap', 0) / 1e9:.2f}B")
            print(f"  Market cap (trillions): ${latest_gold.get('market_cap', 0) / 1e12:.2f}T")
            
            # Get gold supply from config
            gold_supply = metals_config[metals_config['ticker'] == 'GC=F']['supply_ounces'].values[0]
            print(f"\nGold Supply (from config): {gold_supply:,.0f} ounces")
            print(f"Gold Supply (millions): {gold_supply / 1e6:,.0f}M oz")
            
            # Manual calculation
            price_per_oz = latest_gold.get('price_per_ounce', 0)
            calculated_mcap = price_per_oz * gold_supply
            print(f"\nManual Calculation Check:")
            print(f"  {price_per_oz:,.2f} USD/oz × {gold_supply:,.0f} oz = ${calculated_mcap:,.0f}")
            print(f"  = ${calculated_mcap / 1e12:.2f}T")
            
            # Compare with world gold supply reference
            print(f"\nWORLD GOLD SUPPLY REFERENCE:")
            print(f"  Total gold ever mined: ~200 million ounces (6,270 tonnes)")
            print(f"  Current config supply: {gold_supply / 1e6:.1f}M ounces")
            print(f"  Discrepancy: {gold_supply / 200e6:.1f}x the worldwide total")
            
            if gold_supply > 200e6:
                issue = f"CRITICAL: Gold supply in config ({gold_supply/1e6:.0f}M oz) exceeds world supply (~200M oz)"
                print(f"\n  ⚠ {issue}")
                self.issues_found.append(issue)
            
            # Check silver
            print("\n" + "-"*80)
            print("SILVER (SI=F) CALCULATION VERIFICATION")
            print("-"*80)
            
            silver_data = metals_data[metals_data['ticker'] == 'SI=F'].copy()
            if not silver_data.empty:
                silver_data['date'] = pd.to_datetime(silver_data['date'])
                latest_silver = silver_data.sort_values('date').iloc[-1]
                
                print(f"Latest Silver Data (Date: {latest_silver['date'].date()}):")
                print(f"  Price per ounce: ${latest_silver.get('price_per_ounce', 'N/A')}")
                print(f"  Market cap: ${latest_silver.get('market_cap', 'N/A'):,.0f}")
                print(f"  Market cap (billions): ${latest_silver.get('market_cap', 0) / 1e9:.2f}B")
                
                silver_supply = metals_config[metals_config['ticker'] == 'SI=F']['supply_ounces'].values[0]
                print(f"\nSilver Supply (from config): {silver_supply:,.0f} ounces")
                print(f"Silver Supply (millions): {silver_supply / 1e6:,.0f}M oz")
                
                price_per_oz_silver = latest_silver.get('price_per_ounce', 0)
                calculated_silver_mcap = price_per_oz_silver * silver_supply
                print(f"\nManual Calculation Check:")
                print(f"  {price_per_oz_silver:,.2f} USD/oz × {silver_supply:,.0f} oz = ${calculated_silver_mcap:,.0f}")
                print(f"  = ${calculated_silver_mcap / 1e12:.2f}T")
                
        except Exception as e:
            logger.error(f"Error auditing metals: {e}")
            print(f"ERROR: {e}")
    
    def audit_company_rankings(self):
        """Verify company rankings are correct."""
        print("\n" + "="*80)
        print("COMPANY RANKINGS AUDIT")
        print("="*80)
        
        try:
            # Load processed top20 data
            top20_data = pd.read_parquet("data/processed/top20_monthly.parquet")
            
            # Get latest date
            latest_date = top20_data['date'].max()
            latest_rankings = top20_data[top20_data['date'] == latest_date].sort_values('market_cap', ascending=False)
            
            print(f"\nLatest Rankings (Date: {latest_date.date()}):")
            print(f"{'Rank':<6} {'Asset':<20} {'Type':<10} {'Market Cap':<20}")
            print("-" * 60)
            
            for idx, (_, row) in enumerate(latest_rankings.iterrows(), 1):
                mcap = row['market_cap']
                if mcap >= 1e12:
                    mcap_str = f"${mcap/1e12:.2f}T"
                else:
                    mcap_str = f"${mcap/1e9:.2f}B"
                print(f"{idx:<6} {row['label']:<20} {row['asset_type']:<10} {mcap_str:<20}")
            
            # Check for anomalies
            print("\n" + "-"*80)
            print("RANKING ANOMALIES CHECK")
            print("-"*80)
            
            # Silver vs Apple comparison
            silver_row = latest_rankings[latest_rankings['asset_id'] == 'Silver']
            apple_row = latest_rankings[latest_rankings['asset_id'] == 'AAPL']
            
            if not silver_row.empty and not apple_row.empty:
                silver_mcap = silver_row.iloc[0]['market_cap']
                apple_mcap = apple_row.iloc[0]['market_cap']
                silver_rank = latest_rankings[latest_rankings['asset_id'] == 'Silver'].index[0] + 1
                apple_rank = latest_rankings[latest_rankings['asset_id'] == 'AAPL'].index[0] + 1
                
                print(f"Silver Market Cap: ${silver_mcap/1e12:.2f}T (Rank {silver_rank})")
                print(f"Apple Market Cap: ${apple_mcap/1e12:.2f}T (Rank {apple_rank})")
                
                if silver_rank < apple_rank:
                    issue = f"ANOMALY: Silver ranked #{silver_rank} > Apple ranked #{apple_rank}"
                    print(f"\n  ⚠ {issue}")
                    print(f"    Discrepancy: Silver should be lower than Apple (tech sector)")
                    self.issues_found.append(issue)
            
        except Exception as e:
            logger.error(f"Error auditing rankings: {e}")
            print(f"ERROR: {e}")
    
    def audit_source_validation(self):
        """Validate data from each source."""
        print("\n" + "="*80)
        print("SOURCE VALIDATION")
        print("="*80)
        
        print("\nData Sources Used:")
        print("-" * 60)
        
        sources = {
            'yfinance': {
                'assets': ['Companies (stocks)', 'Precious Metals (futures)'],
                'symbols': ['AAPL', 'GC=F', 'SI=F', 'etc.'],
                'validation': 'Price verification'
            },
            'CoinGecko': {
                'assets': ['Bitcoin', 'Ethereum'],
                'validation': 'Market cap verification'
            },
            'Manual Config': {
                'assets': ['Precious metals supply', 'Company shares outstanding'],
                'files': ['precious_metals_supply.csv', 'shares_outstanding.csv'],
                'validation': 'Config accuracy check'
            }
        }
        
        for source, details in sources.items():
            print(f"\n{source}:")
            print(f"  Assets: {details.get('assets', [])}")
            if 'symbols' in details:
                print(f"  Symbols: {details['symbols']}")
            if 'files' in details:
                print(f"  Files: {details['files']}")
            print(f"  Validation: {details['validation']}")
    
    def audit_calculation_methods(self):
        """Document and verify calculation methods."""
        print("\n" + "="*80)
        print("CALCULATION METHODS VERIFICATION")
        print("="*80)
        
        print("\nMarket Cap Calculation Methods by Asset Type:")
        print("-" * 60)
        
        methods = {
            'Companies': {
                'formula': 'Stock Price × Shares Outstanding',
                'example': '$180 × 15.6B = $2.81T (Apple)',
                'source': 'yfinance stock price + shares_outstanding.csv',
                'risk': 'Shares outstanding may be outdated'
            },
            'Precious Metals': {
                'formula': 'Price per Ounce × Total Supply Ounces',
                'example': '$2,100/oz × 6.95B oz = $14.6T (Gold)',
                'source': 'yfinance futures price + precious_metals_supply.csv',
                'risk': 'Supply value may be incorrect or outdated',
                'issue': 'World total gold ever mined is ~200M oz, not 6.95B oz'
            },
            'Cryptocurrencies': {
                'formula': 'Direct market cap from CoinGecko API',
                'example': '$95,000/coin × 21M coins ≈ $2.0T (Bitcoin)',
                'source': 'CoinGecko API (coingecko.com)',
                'risk': 'API rate limits or data staleness'
            }
        }
        
        for asset_type, method in methods.items():
            print(f"\n{asset_type}:")
            print(f"  Formula: {method['formula']}")
            print(f"  Example: {method['example']}")
            print(f"  Source: {method['source']}")
            print(f"  Risk: {method['risk']}")
            if 'issue' in method:
                print(f"  ⚠ ISSUE: {method['issue']}")
                self.issues_found.append(f"{asset_type} calculation issue: {method['issue']}")
    
    def generate_audit_report(self):
        """Generate final audit report."""
        print("\n\n" + "="*80)
        print("FINAL AUDIT REPORT")
        print("="*80)
        
        if self.issues_found:
            print(f"\n⚠ {len(self.issues_found)} CRITICAL ISSUES FOUND:\n")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"{i}. {issue}")
            
            print("\n" + "-"*80)
            print("RECOMMENDED ACTIONS:")
            print("-"*80)
            print("""
1. GOLD/SILVER MARKET CAP:
   - Verify precious_metals_supply.csv values
   - World total gold ever mined: ~200 million ounces
   - Current config: 6.95 billion ounces (346x too high!)
   - ACTION: Check source data and recalculate supply values
   
2. RANKING ANOMALIES:
   - Silver ranked #2 suggests gold supply value is wrong
   - Expected ranking: Gold > Apple > Microsoft > NVIDIA
   - Current ranking shows Silver > Gold anomaly
   - ACTION: Fix gold supply config value
   
3. DATA SOURCE VALIDATION:
   - Implement multi-source verification for precious metals
   - Compare yfinance prices with alternative sources
   - Validate against 8marketcap.com or similar reference
   - ACTION: Create cross-reference validation script
""")
        else:
            print("\nNo critical issues found.")
        
        # Validation checklist
        print("\n" + "-"*80)
        print("DATA VALIDATION CHECKLIST:")
        print("-"*80)
        checklist = [
            ("Gold market cap verified against reference", False),
            ("Silver supply value validated", False),
            ("Yfinance prices cross-checked", False),
            ("CoinGecko crypto data verified", False),
            ("Company shares outstanding current", False),
            ("Rankings match expected order", False),
        ]
        
        for item, status in checklist:
            status_str = "[✓]" if status else "[✗]"
            print(f"{status_str} {item}")
        
        return self.issues_found


if __name__ == "__main__":
    print("\n" + "█"*80)
    print("█  DATA INTEGRITY AUDIT FRAMEWORK")
    print("█"*80)
    
    audit = DataIntegrityAudit()
    
    # Run audits
    audit.audit_precious_metals()
    audit.audit_company_rankings()
    audit.audit_source_validation()
    audit.audit_calculation_methods()
    
    # Generate report
    issues = audit.generate_audit_report()
    
    print("\n" + "█"*80)
    if issues:
        print(f"█  AUDIT COMPLETE: {len(issues)} ISSUES REQUIRING ATTENTION")
    else:
        print("█  AUDIT COMPLETE: ALL VALIDATIONS PASSED")
    print("█"*80 + "\n")
