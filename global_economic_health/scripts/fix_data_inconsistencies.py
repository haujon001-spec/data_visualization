#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Data Inconsistencies in macro_final_08MAR2026.csv
Addresses issues found by data_quality_validator.py

Author: AI Agent
Date: 2026-03-12
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataCorrector:
    """Fix known data quality issues in the CSV."""
    
    def __init__(self, csv_path):
        self.csv_path = Path(csv_path)
        self.df = None
        self.corrections_made = []
        
    def load_data(self):
        """Load CSV data."""
        try:
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"✓ Loaded {len(self.df)} rows from {self.csv_path.name}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to load data: {e}")
            return False
    
    def fix_debt_to_gdp_format(self):
        """Fix debt_to_gdp values stored as decimals instead of percentages."""
        logger.info("\n[FIX 1] Correcting Debt/GDP Format Inconsistencies")
        
        # Identify rows where debt_to_gdp is stored as decimal (< 10)
        # but calculated value is > 10 (indicating it should be percentage)
        mask = (
            self.df['debt_total_usd'].notna() & 
            self.df['gdp_usd'].notna() & 
            self.df['debt_to_gdp'].notna() &
            (self.df['debt_to_gdp'] < 10)
        )
        
        problematic_rows = self.df[mask].copy()
        problematic_rows['calculated_ratio'] = (
            problematic_rows['debt_total_usd'] / problematic_rows['gdp_usd']
        ) * 100
        
        # Find rows where calculated ratio is > 10 but stored is < 10
        needs_fix = problematic_rows[problematic_rows['calculated_ratio'] > 10]
        
        if len(needs_fix) > 0:
            logger.info(f"Found {len(needs_fix)} rows with decimal format (should be percentage)")
            
            # Show sample of what will be fixed
            sample_countries = needs_fix.groupby('country_name').first().head(10)
            for country, row in sample_countries.iterrows():
                logger.info(f"  {country}: {row['debt_to_gdp']:.4f} → {row['calculated_ratio']:.2f}%")
            
            # Apply the fix: multiply by 100
            fix_indices = needs_fix.index
            self.df.loc[fix_indices, 'debt_to_gdp'] = self.df.loc[fix_indices, 'debt_to_gdp'] * 100
            
            self.corrections_made.append({
                'fix': 'Debt/GDP Format',
                'rows_affected': len(fix_indices),
                'details': f"Converted decimal to percentage for {len(needs_fix['country_name'].unique())} countries"
            })
            
            logger.info(f"✓ Fixed {len(fix_indices)} rows")
        else:
            logger.info("✓ No debt/GDP format issues found")
        
        return len(needs_fix)
    
    def recalculate_all_debt_to_gdp(self):
        """Recalculate all debt_to_gdp values from source data for consistency."""
        logger.info("\n[FIX 2] Recalculating All Debt/GDP Ratios")
        
        mask = (
            self.df['debt_total_usd'].notna() & 
            self.df['gdp_usd'].notna() &
            (self.df['debt_total_usd'] > 0) &
            (self.df['gdp_usd'] > 0)
        )
        
        recalc_count = mask.sum()
        
        if recalc_count > 0:
            # Store old values for comparison
            old_values = self.df.loc[mask, 'debt_to_gdp'].copy()
            
            # Recalculate
            self.df.loc[mask, 'debt_to_gdp'] = (
                self.df.loc[mask, 'debt_total_usd'] / self.df.loc[mask, 'gdp_usd']
            ) * 100
            
            # Check how many changed significantly
            new_values = self.df.loc[mask, 'debt_to_gdp']
            differences = abs(old_values - new_values)
            significant_changes = (differences > 1.0).sum()
            
            logger.info(f"✓ Recalculated {recalc_count} debt/GDP ratios")
            logger.info(f"  {significant_changes} values changed by >1 percentage point")
            
            self.corrections_made.append({
                'fix': 'Recalculate Debt/GDP',
                'rows_affected': recalc_count,
                'details': f"{significant_changes} significant changes"
            })
        
        return recalc_count
    
    def validate_outliers(self):
        """Validate that outliers are legitimate (not calculation errors)."""
        logger.info("\n[FIX 3] Validating Outliers")
        
        df_2024 = self.df[
            (self.df['year'] == 2024) & 
            self.df['debt_to_gdp'].notna()
        ].copy()
        
        # Check for extreme outliers
        q1 = df_2024['debt_to_gdp'].quantile(0.25)
        q3 = df_2024['debt_to_gdp'].quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 3 * iqr
        
        outliers = df_2024[df_2024['debt_to_gdp'] > upper_bound].sort_values('debt_to_gdp', ascending=False)
        
        if len(outliers) > 0:
            logger.info(f"Found {len(outliers)} outliers above {upper_bound:.1f}%:")
            
            # Validate by recalculating
            for _, row in outliers.head(10).iterrows():
                calculated = (row['debt_total_usd'] / row['gdp_usd']) * 100
                logger.info(
                    f"  {row['country_name']}: {row['debt_to_gdp']:.1f}% "
                    f"(recalc: {calculated:.1f}%) - "
                    f"{'✓ VALID' if abs(row['debt_to_gdp'] - calculated) < 1 else '✗ ERROR'}"
                )
            
            logger.info("  Note: High debt/GDP ratios are legitimate for some countries (e.g., Japan)")
        else:
            logger.info("✓ No extreme outliers found")
        
        return len(outliers)
    
    def fix_negative_values(self):
        """Check for and fix any negative values that shouldn't exist."""
        logger.info("\n[FIX 4] Checking for Invalid Negative Values")
        
        fields_that_should_be_positive = ['gdp_usd', 'population', 'debt_total_usd', 'gdp_per_capita']
        
        total_fixes = 0
        for field in fields_that_should_be_positive:
            if field in self.df.columns:
                negative_mask = self.df[field] < 0
                negative_count = negative_mask.sum()
                
                if negative_count > 0:
                    logger.warning(f"✗ Found {negative_count} negative values in {field}")
                    # Set to NaN instead of keeping negative
                    self.df.loc[negative_mask, field] = np.nan
                    total_fixes += negative_count
                    
                    self.corrections_made.append({
                        'fix': f'Remove negative {field}',
                        'rows_affected': negative_count,
                        'details': 'Set to NaN'
                    })
        
        if total_fixes == 0:
            logger.info("✓ No negative values found")
        else:
            logger.info(f"✓ Fixed {total_fixes} negative values")
        
        return total_fixes
    
    def save_corrected_data(self):
        """Save corrected data with backup."""
        logger.info("\n[SAVE] Saving Corrected Data")
        
        # Create backup
        backup_path = self.csv_path.parent / f"{self.csv_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            # Backup original
            import shutil
            shutil.copy2(self.csv_path, backup_path)
            logger.info(f"✓ Backup created: {backup_path.name}")
            
            # Save corrected data
            self.df.to_csv(self.csv_path, index=False)
            logger.info(f"✓ Corrected data saved: {self.csv_path.name}")
            
            return True
        except Exception as e:
            logger.error(f"✗ Failed to save: {e}")
            return False
    
    def generate_report(self):
        """Generate correction report."""
        logger.info("\n" + "="*70)
        logger.info("DATA CORRECTION REPORT")
        logger.info("="*70)
        
        if not self.corrections_made:
            logger.info("ℹ No corrections were necessary")
        else:
            logger.info(f"✓ Applied {len(self.corrections_made)} corrections:")
            for correction in self.corrections_made:
                logger.info(f"\n  [{correction['fix']}]")
                logger.info(f"    Rows affected: {correction['rows_affected']}")
                logger.info(f"    Details: {correction['details']}")
        
        logger.info("\n" + "="*70)
        logger.info("✓ Data correction complete!")
        logger.info("="*70)
    
    def run_all_fixes(self):
        """Run all data correction fixes."""
        if not self.load_data():
            return False
        
        logger.info("Starting data correction process...")
        
        # Run all fixes
        self.fix_debt_to_gdp_format()
        self.recalculate_all_debt_to_gdp()
        self.validate_outliers()
        self.fix_negative_values()
        
        # Save corrected data
        if self.save_corrected_data():
            self.generate_report()
            return True
        else:
            return False


if __name__ == "__main__":
    csv_path = Path(__file__).parent.parent / "csv" / "processed" / "macro_final_08MAR2026.csv"
    
    corrector = DataCorrector(csv_path)
    success = corrector.run_all_fixes()
    
    import sys
    sys.exit(0 if success else 1)
