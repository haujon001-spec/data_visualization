#!/usr/bin/env python3
"""
Comprehensive Data Quality Validator - For Parquet and Visualization Files
Validates data integrity, completeness, and visualization accuracy
"""

import pandas as pd
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataQualityValidator:
    """Comprehensive validation of parquet data and visualization"""
    
    def __init__(self):
        self.workspace = Path('c:\\Users\\haujo\\projects\\DEV\\Data_visualization')
        self.parquet_file = self.workspace / 'data' / 'processed' / 'top20_monthly.parquet'
        self.csv_file = self.workspace / 'data' / 'processed' / 'top20_monthly.csv'
        self.html_file = self.workspace / 'data' / 'processed' / 'bar_race_top20.html'
        self.issues = []
        self.warnings = []
        self.passed_checks = []
    
    def load_data(self) -> pd.DataFrame:
        """Load parquet data"""
        try:
            if self.parquet_file.exists():
                df = pd.read_parquet(self.parquet_file)
                logger.info(f"✓ Loaded parquet: {len(df)} rows, {len(df.columns)} columns")
            else:
                df = pd.read_csv(self.csv_file)
                logger.info(f"✓ Loaded CSV: {len(df)} rows, {len(df.columns)} columns")
            
            return df
        except Exception as e:
            logger.error(f"✗ Failed to load data: {e}")
            raise
    
    def inspect_columns(self, df: pd.DataFrame) -> dict:
        """Inspect all columns in dataframe"""
        logger.info("\n" + "="*80)
        logger.info("COLUMN STRUCTURE INSPECTION")
        logger.info("="*80)
        
        col_info = {}
        
        for col in df.columns:
            non_null_count = df[col].notna().sum()
            unique_count = df[col].nunique()
            dtype = str(df[col].dtype)
            
            col_info[col] = {
                'dtype': dtype,
                'non_null': non_null_count,
                'null_count': df[col].isna().sum(),
                'unique_values': unique_count,
                'sample_values': list(df[col].dropna().unique()[:3])
            }
            
            logger.info(f"\n  Column: {col}")
            logger.info(f"    Type: {dtype}")
            logger.info(f"    Non-null: {non_null_count}/{len(df)}")
            logger.info(f"    Unique: {unique_count}")
            logger.info(f"    Sample: {col_info[col]['sample_values']}")
        
        return col_info
    
    def check_data_completeness(self, df: pd.DataFrame) -> bool:
        """Check for missing required columns and data"""
        logger.info("\n" + "="*80)
        logger.info("DATA COMPLETENESS CHECK")
        logger.info("="*80)
        
        required_concepts = [
            'asset identifier',  # Could be 'asset_name', 'asset_id', 'label', etc
            'market cap value',  # Could be 'market_cap', 'market_cap_usd', etc
            'date',              # Could be 'date', 'timestamp', etc
        ]
        
        found_critical_cols = False
        
        # Check for asset name column
        asset_cols = [col for col in df.columns if 'asset' in col.lower() or 'name' in col.lower() or 'label' in col.lower()]
        if asset_cols:
            logger.info(f"✓ Found asset column(s): {asset_cols}")
            asset_col = asset_cols[0]
            
            # Check for nulls and unknowns
            null_assets = df[asset_col].isna().sum()
            unknown_assets = (df[asset_col].astype(str).str.lower() == 'unknown').sum()
            
            logger.info(f"  - Total rows: {len(df)}")
            logger.info(f"  - Null assets: {null_assets}")
            logger.info(f"  - Unknown assets: {unknown_assets}")
            logger.info(f"  - Named assets: {len(df) - null_assets - unknown_assets}")
            
            if unknown_assets > len(df) * 0.5:
                self.issues.append(f"Over 50% unknown assets ({unknown_assets}/{len(df)})")
                logger.error(f"  ✗ CRITICAL: {unknown_assets} unknown assets (>50% of data)")
            elif null_assets > 0:
                self.warnings.append(f"Found {null_assets} null asset values")
                logger.warning(f"  ⚠️  {null_assets} null asset values")
            else:
                self.passed_checks.append("Asset names complete")
                logger.info(f"  ✓ All assets named")
                found_critical_cols = True
        else:
            self.issues.append("No asset name column found")
            logger.error("✗ No asset name/label column found in data")
        
        # Check for market cap column
        cap_cols = [col for col in df.columns if 'market' in col.lower() or 'cap' in col.lower() or 'price' in col.lower()]
        if cap_cols:
            logger.info(f"\n✓ Found market cap column(s): {cap_cols}")
            cap_col = cap_cols[0]
            
            # Check for valid values
            null_caps = df[cap_col].isna().sum()
            zero_caps = (df[cap_col] == 0).sum()
            
            logger.info(f"  - Null values: {null_caps}")
            logger.info(f"  - Zero values: {zero_caps}")
            logger.info(f"  - Min value: {df[cap_col].min()}")
            logger.info(f"  - Max value: {df[cap_col].max()}")
            
            if null_caps > len(df) * 0.1:
                self.issues.append(f"Too many null market caps ({null_caps}/{len(df)})")
                logger.error(f"  ✗ {null_caps} null market cap values (>10%)")
            else:
                self.passed_checks.append("Market cap values present")
                logger.info(f"  ✓ Market cap values valid")
        else:
            self.issues.append("No market cap column found")
            logger.error("✗ No market cap/price column found in data")
        
        # Check for date column
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_cols:
            logger.info(f"\n✓ Found date column(s): {date_cols}")
            logger.info(f"  ✓ Date column present")
            self.passed_checks.append("Date column present")
        else:
            self.warnings.append("No explicit date column found")
            logger.warning("⚠️  No date column found")
        
        return found_critical_cols
    
    def check_data_consistency(self, df: pd.DataFrame) -> bool:
        """Check for data consistency issues"""
        logger.info("\n" + "="*80)
        logger.info("DATA CONSISTENCY CHECK")
        logger.info("="*80)
        
        consistency_ok = True
        
        # Get date range
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        if date_cols:
            date_col = date_cols[0]
            try:
                df[date_col] = pd.to_datetime(df[date_col])
                date_range = (df[date_col].min(), df[date_col].max())
                unique_dates = df[date_col].nunique()
                
                logger.info(f"✓ Date range: {date_range[0].date()} to {date_range[1].date()}")
                logger.info(f"  - Unique dates: {unique_dates}")
                logger.info(f"  - Total rows: {len(df)}")
                
                if unique_dates == 0:
                    self.issues.append("No unique dates in data")
                    logger.error("✗ No unique dates found")
                    consistency_ok = False
                else:
                    self.passed_checks.append(f"Date range valid ({unique_dates} unique dates)")
            except Exception as e:
                self.warnings.append(f"Could not parse date column: {e}")
                logger.warning(f"⚠️  Date parsing issue: {e}")
        
        # Check asset variety
        asset_cols = [col for col in df.columns if 'asset' in col.lower() or 'name' in col.lower()]
        if asset_cols:
            asset_col = asset_cols[0]
            unique_assets = df[asset_col].nunique()
            
            logger.info(f"\n✓ Asset diversity:")
            logger.info(f"  - Unique assets: {unique_assets}")
            
            if unique_assets < 3:
                self.issues.append(f"Only {unique_assets} unique assets (expected 20+)")
                logger.error(f"  ✗ Only {unique_assets} unique assets (expected 20+)")
                consistency_ok = False
            elif unique_assets < 20:
                self.warnings.append(f"Only {unique_assets} unique assets (expected 20)")
                logger.warning(f"  ⚠️  Only {unique_assets} unique assets (expected 20)")
            else:
                self.passed_checks.append(f"Good asset diversity ({unique_assets} assets)")
                logger.info(f"  ✓ Good diversity ({unique_assets} assets)")
        
        return consistency_ok
    
    def check_market_cap_sanity(self, df: pd.DataFrame) -> bool:
        """Sanity check market cap values"""
        logger.info("\n" + "="*80)
        logger.info("MARKET CAP SANITY CHECK")
        logger.info("="*80)
        
        cap_cols = [col for col in df.columns if 'market' in col.lower() or 'cap' in col.lower()]
        if not cap_cols:
            logger.warning("⚠️  No market cap column found, skipping sanity check")
            return True
        
        cap_col = cap_cols[0]
        
        # Get latest date data
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        if date_cols:
            date_col = date_cols[0]
            df[date_col] = pd.to_datetime(df[date_col])
            latest_date = df[date_col].max()
            latest_df = df[df[date_col] == latest_date]
        else:
            latest_df = df.tail(20)
        
        # Expected ranges for various assets
        expected_ranges = {
            'Apple': (2e12, 3.5e12),
            'Microsoft': (3e12, 4e12),
            'Bitcoin': (1e12, 3e12),
            'Gold': (0.4e12, 1.2e12),  # After correction
            'Silver': (0.03e12, 0.2e12),  # After correction
        }
        
        asset_cols = [col for col in latest_df.columns if 'asset' in col.lower() or 'name' in col.lower()]
        if asset_cols:
            asset_col = asset_cols[0]
            
            logger.info(f"\nLatest data snapshot ({len(latest_df)} assets):")
            
            for _, row in latest_df.iterrows():
                asset_name = row[asset_col]
                cap_value = row[cap_col]
                
                # Check if asset has expected range
                for expected_asset, (min_cap, max_cap) in expected_ranges.items():
                    if expected_asset.lower() in str(asset_name).lower():
                        logger.info(f"\n  {asset_name}: ${cap_value/1e12:.2f}T")
                        
                        if cap_value < min_cap or cap_value > max_cap:
                            msg = f"{asset_name} value ${cap_value/1e12:.2f}T outside expected range ${min_cap/1e12:.2f}T-${max_cap/1e12:.2f}T"
                            self.warnings.append(msg)
                            logger.warning(f"    ⚠️  {msg}")
                        else:
                            logger.info(f"    ✓ Value in expected range")
                            self.passed_checks.append(f"{asset_name} value reasonable")
        
        return True
    
    def check_html_structure(self) -> bool:
        """Check if HTML file contains proper data structure"""
        logger.info("\n" + "="*80)
        logger.info("HTML VISUALIZATION CHECK")
        logger.info("="*80)
        
        if not self.html_file.exists():
            self.issues.append("HTML visualization file not found")
            logger.error(f"✗ HTML file not found: {self.html_file}")
            return False
        
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Check for Plotly data
            if 'Plotly' in html_content:
                logger.info("✓ HTML contains Plotly library")
                self.passed_checks.append("Plotly library present")
            else:
                self.warnings.append("Plotly library not found in HTML")
                logger.warning("⚠️  Plotly library reference missing")
            
            # Check for trace data
            if '"x":' in html_content or '"y":' in html_content:
                logger.info("✓ HTML contains trace data")
                self.passed_checks.append("Chart trace data present")
            else:
                self.issues.append("No chart trace data found in HTML")
                logger.error("✗ Chart trace data missing from HTML")
                return False
            
            # Check for frames
            if '"frames"' in html_content:
                logger.info("✓ HTML contains animation frames")
                self.passed_checks.append("Animation frames present")
            else:
                self.warnings.append("Animation frames not found in HTML")
                logger.warning("⚠️  No animation frames detected")
            
            file_size_mb = self.html_file.stat().st_size / 1024 / 1024
            logger.info(f"✓ HTML file size: {file_size_mb:.2f} MB")
            
            if file_size_mb < 1:
                self.issues.append(f"HTML file very small ({file_size_mb:.2f} MB) - may contain no data")
                logger.error(f"✗ HTML file too small: {file_size_mb:.2f} MB")
                return False
            
            return True
            
        except Exception as e:
            self.issues.append(f"Error reading HTML: {e}")
            logger.error(f"✗ Error reading HTML: {e}")
            return False
    
    def generate_report(self):
        """Generate comprehensive validation report"""
        logger.info("\n" + "="*80)
        logger.info("DATA QUALITY VALIDATION SUMMARY")
        logger.info("="*80)
        
        total_checks = len(self.passed_checks) + len(self.issues) + len(self.warnings)
        
        logger.info(f"\n✓ Passed: {len(self.passed_checks)}")
        logger.info(f"⚠️  Warnings: {len(self.warnings)}")
        logger.info(f"✗ Issues: {len(self.issues)}")
        
        if self.issues:
            logger.error(f"\n❌ CRITICAL ISSUES FOUND ({len(self.issues)}):")
            for issue in self.issues:
                logger.error(f"   - {issue}")
        
        if self.warnings:
            logger.warning(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.warning(f"   - {warning}")
        
        if not self.issues:
            logger.info("\n✅ DATA QUALITY VALIDATION PASSED")
        else:
            logger.error("\n❌ DATA QUALITY VALIDATION FAILED")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'passed': len(self.passed_checks),
            'warnings': len(self.warnings),
            'issues': len(self.issues),
            'issue_list': self.issues,
            'warning_list': self.warnings,
            'status': 'PASSED' if not self.issues else 'FAILED'
        }
    
    def run_validation(self) -> dict:
        """Run complete validation"""
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE DATA QUALITY VALIDATION")
        logger.info("="*80 + "\n")
        
        try:
            # Load data
            df = self.load_data()
            
            # Run all checks
            self.inspect_columns(df)
            self.check_data_completeness(df)
            self.check_data_consistency(df)
            self.check_market_cap_sanity(df)
            self.check_html_structure()
            
            # Generate report
            report = self.generate_report()
            
            return report
            
        except Exception as e:
            logger.error(f"\n✗ VALIDATION FAILED: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


if __name__ == '__main__':
    validator = DataQualityValidator()
    report = validator.run_validation()
    
    sys.exit(0 if report.get('status') == 'PASSED' else 1)
