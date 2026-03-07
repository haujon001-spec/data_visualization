#!/usr/bin/env python3
"""
Data Repair Toolkit - Fixes parquet file with missing asset names and mappings
"""

import pandas as pd
import logging
import sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataRepairToolkit:
    """Repairs and reconstructs missing asset data"""
    
    # Asset name mappings from raw data
    ASSET_MAPPINGS = {
        # Companies (from yfinance era)
        'MSFT': 'Microsoft',
        'AAPL': 'Apple',
        'GOOGL': 'Alphabet',
        'AMZN': 'Amazon',
        'NVDA': 'NVIDIA',
        'META': 'Meta',
        'TSLA': 'Tesla',
        'JNJ': 'Johnson & Johnson',
        'JPM': 'JPMorgan Chase',
        'V': 'Visa',
        'WMT': 'Walmart',
        'XOM': 'ExxonMobil',
        'BRK.B': 'Berkshire Hathaway',
        'MA': 'Mastercard',
        'PG': 'Procter & Gamble',
        
        # Cryptos
        'bitcoin': 'Bitcoin',
        'BTC': 'Bitcoin',
        'ethereum': 'Ethereum',
        'ETH': 'Ethereum',
        'bnb': 'BNB',
        'BNB': 'BNB',
        'xrp': 'XRP',
        'XRP': 'XRP',
        'ada': 'Cardano',
        'ADA': 'Cardano',
        'doge': 'Dogecoin',
        'DOGE': 'Dogecoin',
        
        # Metals
        'GC=F': 'Gold',
        'Gold': 'Gold',
        'SI=F': 'Silver',
        'Silver': 'Silver',
        'PL=F': 'Platinum',
        'Platinum': 'Platinum',
        'PA=F': 'Palladium',
        'Palladium': 'Palladium',
    }
    
    def __init__(self):
        self.workspace = Path('c:\\Users\\haujo\\projects\\DEV\\Data_visualization')
        self.parquet_file = self.workspace / 'data' / 'processed' / 'top20_monthly.parquet'
        self.csv_file = self.workspace / 'data' / 'processed' / 'top20_monthly.csv'
        self.raw_dir = self.workspace / 'data' / 'raw'
    
    def load_raw_data(self):
        """Load raw data files to understand asset structure"""
        logger.info("\n" + "="*80)
        logger.info("LOADING RAW DATA FOR MAPPING")
        logger.info("="*80)
        
        raw_assets = {}
        
        # Load companies
        companies_file = self.raw_dir / 'companies_monthly.csv'
        if companies_file.exists():
            df = pd.read_csv(companies_file)
            logger.info(f"✓ Companies raw data: {len(df)} rows, columns: {df.columns.tolist()}")
            raw_assets['companies'] = df
        
        # Load crypto
        crypto_file = self.raw_dir / 'crypto_monthly.csv'
        if crypto_file.exists():
            df = pd.read_csv(crypto_file)
            logger.info(f"✓ Crypto raw data: {len(df)} rows, columns: {df.columns.tolist()}")
            raw_assets['crypto'] = df
        
        # Load metals
        metals_file = self.raw_dir / 'metals_monthly.csv'
        if metals_file.exists():
            df = pd.read_csv(metals_file)
            logger.info(f"✓ Metals raw data: {len(df)} rows, columns: {df.columns.tolist()}")
            raw_assets['metals'] = df
        
        return raw_assets
    
    def load_parquet(self):
        """Load broken parquet file"""
        logger.info("\n" + "="*80)
        logger.info("ANALYZING BROKEN PARQUET")
        logger.info("="*80)
        
        df = pd.read_parquet(self.parquet_file)
        
        logger.info(f"Rows: {len(df)}")
        logger.info(f"Columns: {df.columns.tolist()}")
        logger.info(f"\nAsset ID breakdown:")
        logger.info(f"  - Non-null asset_id: {df['asset_id'].notna().sum()}")
        logger.info(f"  - Null asset_id: {df['asset_id'].isna().sum()}")
        
        logger.info(f"\nAsset ID values (first few):")
        logger.info(f"  {df['asset_id'].dropna().unique()[:5]}")
        
        logger.info(f"\nAsset Type breakdown:")
        logger.info(f"  {df['asset_type'].value_counts()}")
        
        logger.info(f"\nLabel values (unique):")
        logger.info(f"  {df['label'].unique()}")
        
        return df
    
    def repair_asset_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Repair missing asset names in dataframe"""
        logger.info("\n" + "="*80)
        logger.info("REPAIRING ASSET NAMES")
        logger.info("="*80)
        
        df = df.copy()
        
        # Try to extract asset name from available columns
        df['asset_name_fixed'] = df['asset_id'].fillna('Unknown')
        
        # Map known asset IDs to proper names
        for old_name, proper_name in self.ASSET_MAPPINGS.items():
            mask = df['asset_name_fixed'].str.lower() == old_name.lower()
            if mask.any():
                df.loc[mask, 'asset_name_fixed'] = proper_name
                logger.info(f"✓ Mapped {old_name} → {proper_name} ({mask.sum()} rows)")
        
        # For metals (likely have null asset_id), infer from asset_type
        metal_mask = (df['asset_type'] == 'metal') & (df['asset_id'].isna())
        if metal_mask.any():
            logger.info(f"\nInferring metal names from market cap:")
            # Use market cap to infer metal type
            metal_df = df[metal_mask].copy()
            
            for idx, row in metal_df.iterrows():
                market_cap = row['market_cap']
                # Based on corrected precious metals config:
                # Gold: ~$500B-$1T
                # Silver: ~$50B-$150B
                # Platinum: ~$8B-$20B
                # Palladium: ~$6B-$12B
                
                if market_cap > 250e9:  # >$250B = Gold
                    df.loc[idx, 'asset_name_fixed'] = 'Gold'
                elif market_cap > 30e9:  # >$30B = Silver
                    df.loc[idx, 'asset_name_fixed'] = 'Silver'
                elif market_cap > 5e9:  # >$5B = Platinum or Palladium
                    df.loc[idx, 'asset_name_fixed'] = 'Platinum'
                else:
                    df.loc[idx, 'asset_name_fixed'] = 'Palladium'
            
            logger.info(f"✓ Inferred metal names for {metal_mask.sum()} rows")
        
        # Update label column
        df['label'] = df['asset_name_fixed']
        
        logger.info(f"\nRepair Summary:")
        logger.info(f"  Unknown assets remaining: {(df['label'] == 'Unknown').sum()}")
        logger.info(f"  Unique assets: {df['label'].nunique()}")
        logger.info(f"  Assets: {sorted(df['label'].unique())}")
        
        return df
    
    def save_repaired_data(self, df: pd.DataFrame) -> bool:
        """Save repaired data"""
        logger.info("\n" + "="*80)
        logger.info("SAVING REPAIRED DATA")
        logger.info("="*80)
        
        try:
            # Backup original
            backup_path = self.workspace / 'data' / 'processed' / f'top20_monthly_BACKUP_{datetime.now().strftime("%Y%m%d_%H%M%S")}.parquet'
            pd.read_parquet(self.parquet_file).to_parquet(backup_path)
            logger.info(f"✓ Backed up original: {backup_path.name}")
            
            # Save repaired
            # Remove temporary column
            if 'asset_name_fixed' in df.columns:
                df = df.drop('asset_name_fixed', axis=1)
            
            df.to_parquet(self.parquet_file)
            logger.info(f"✓ Saved repaired parquet: {self.parquet_file}")
            
            # Also save CSV
            df.to_csv(self.csv_file, index=False)
            logger.info(f"✓ Saved repaired CSV: {self.csv_file}")
            
            return True
        except Exception as e:
            logger.error(f"✗ Failed to save: {e}")
            return False
    
    def verify_repair(self):
        """Verify the repair was successful"""
        logger.info("\n" + "="*80)
        logger.info("VERIFYING REPAIR")
        logger.info("="*80)
        
        df = pd.read_parquet(self.parquet_file)
        
        logger.info(f"\n✓ Loaded repaired data: {len(df)} rows")
        logger.info(f"  Unique assets: {df['label'].nunique()}")
        logger.info(f"  Unknown assets: {(df['label'] == 'Unknown').sum()}")
        
        assets = df['label'].unique()
        logger.info(f"\n  Assets: {sorted(assets)}")
        
        # Check asset counts per date
        logger.info(f"\n  Assets per date:")
        df['date'] = pd.to_datetime(df['date'])
        assets_per_date = df.groupby('date')['label'].nunique()
        logger.info(f"    Min: {assets_per_date.min()}")
        logger.info(f"    Max: {assets_per_date.max()}")
        logger.info(f"    Average: {assets_per_date.mean():.1f}")
        
        if df['label'].nunique() >= 5:
            logger.info("\n✅ REPAIR SUCCESSFUL - Multiple assets detected")
            return True
        else:
            logger.error("\n❌ REPAIR INCOMPLETE - Still too few assets")
            return False
    
    def run_repair(self):
        """Run complete repair process"""
        logger.info("\n" + "="*80)
        logger.info("DATA REPAIR TOOLKIT")
        logger.info("="*80)
        
        # Step 1: Load and analyze
        raw_data = self.load_raw_data()
        broken_df = self.load_parquet()
        
        # Step 2: Repair
        repaired_df = self.repair_asset_names(broken_df)
        
        # Step 3: Save
        if not self.save_repaired_data(repaired_df):
            return False
        
        # Step 4: Verify
        return self.verify_repair()


if __name__ == '__main__':
    toolkit = DataRepairToolkit()
    success = toolkit.run_repair()
    
    if success:
        logger.info("\n" + "="*80)
        logger.info("✅ DATA REPAIR COMPLETE - Ready to regenerate visualization")
        logger.info("="*80)
        logger.info("\nNext step: python scripts/03_build_visualizations.py")
    
    sys.exit(0 if success else 1)
