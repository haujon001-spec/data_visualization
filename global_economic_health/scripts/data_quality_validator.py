#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Quality Validator for Global Economic Health Dashboard
Validates CSV data integrity before visualization

Author: AI Agent
Date: 2026-03-12
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataQualityValidator:
    """Validate and report data quality issues."""
    
    def __init__(self, csv_path):
        self.csv_path = Path(csv_path)
        self.df = None
        self.issues = []
        
    def load_data(self):
        """Load CSV data."""
        try:
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"✓ Loaded {len(self.df)} rows from {self.csv_path.name}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to load data: {e}")
            return False
    
    def check_debt_to_gdp_consistency(self):
        """Check if debt_to_gdp column has consistent format."""
        logger.info("\n[CHECK 1] Debt/GDP Ratio Consistency")
        
        # Sample countries to check
        test_countries = ['China', 'India', 'Brazil', 'United States', 'Japan', 
                         'Germany', 'France', 'United Kingdom', 'Italy', 'Canada']
        
        df_2024 = self.df[self.df['year'] == 2024].copy()
        df_2024 = df_2024[df_2024['country_name'].isin(test_countries)]
        df_2024 = df_2024.dropna(subset=['debt_total_usd', 'gdp_usd', 'debt_to_gdp'])
        
        inconsistencies = []
        
        for _, row in df_2024.iterrows():
            stored_ratio = float(row['debt_to_gdp'])
            calculated_ratio = (float(row['debt_total_usd']) / float(row['gdp_usd'])) * 100
            
            # Check if stored value is decimal (< 10) when it should be percentage
            if stored_ratio < 10 and calculated_ratio > 10:
                inconsistencies.append({
                    'country': row['country_name'],
                    'stored': stored_ratio,
                    'calculated': calculated_ratio,
                    'issue': 'Stored as decimal, should be percentage'
                })
            # Check if calculation differs significantly
            elif abs(stored_ratio - calculated_ratio) > 1.0:
                inconsistencies.append({
                    'country': row['country_name'],
                    'stored': stored_ratio,
                    'calculated': calculated_ratio,
                    'issue': 'Mismatch between stored and calculated'
                })
        
        if inconsistencies:
            logger.warning(f"✗ Found {len(inconsistencies)} debt/GDP inconsistencies:")
            for issue in inconsistencies:
                logger.warning(f"  {issue['country']}: Stored={issue['stored']:.2f}, Calculated={issue['calculated']:.2f}% - {issue['issue']}")
            self.issues.append(('Debt/GDP Format', inconsistencies))
        else:
            logger.info(f"✓ All {len(df_2024)} countries have consistent debt/GDP ratios")
        
        return len(inconsistencies) == 0
    
    def check_missing_data(self):
        """Check for missing critical data."""
        logger.info("\n[CHECK 2] Missing Data Analysis")
        
        critical_fields = ['gdp_usd', 'population', 'debt_total_usd']
        df_recent = self.df[self.df['year'] >= 2020]
        
        missing_summary = {}
        for field in critical_fields:
            missing_count = df_recent[field].isna().sum()
            missing_pct = (missing_count / len(df_recent)) * 100
            missing_summary[field] = {
                'count': missing_count,
                'percentage': missing_pct
            }
            
            # debt_total_usd missing data is expected (not all countries report)
            if field == 'debt_total_usd':
                logger.info(f"ℹ {field}: {missing_count} missing values ({missing_pct:.1f}%) - Expected (data availability)")
            elif missing_pct > 20:
                logger.warning(f"✗ {field}: {missing_count} missing values ({missing_pct:.1f}%)")
                self.issues.append((f'Missing {field}', missing_count))
            else:
                logger.info(f"✓ {field}: {missing_count} missing values ({missing_pct:.1f}%)")
        
        # Only fail if GDP or population are missing (debt is optional)
        return missing_summary['gdp_usd']['percentage'] < 20 and missing_summary['population']['percentage'] < 20
    
    def check_outliers(self):
        """Check for statistical outliers."""
        logger.info("\n[CHECK 3] Outlier Detection")
        
        df_2024 = self.df[self.df['year'] == 2024].copy()
        df_2024 = df_2024.dropna(subset=['gdp_usd', 'debt_total_usd'])
        
        # Recalculate debt/GDP
        df_2024['debt_to_gdp_calc'] = (df_2024['debt_total_usd'] / df_2024['gdp_usd']) * 100
        
        # Find extreme outliers
        q1 = df_2024['debt_to_gdp_calc'].quantile(0.25)
        q3 = df_2024['debt_to_gdp_calc'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 3 * iqr
        upper_bound = q3 + 3 * iqr
        
        outliers = df_2024[
            (df_2024['debt_to_gdp_calc'] < lower_bound) | 
            (df_2024['debt_to_gdp_calc'] > upper_bound)
        ]
        
        invalid_outliers = []
        
        if len(outliers) > 0:
            logger.info(f"ℹ Found {len(outliers)} statistical outliers (Debt/GDP > {upper_bound:.1f}%):")
            
            # Validate each outlier
            for _, row in outliers.head(10).iterrows():
                stored = row['debt_to_gdp']
                calculated = row['debt_to_gdp_calc']
                is_valid = abs(stored - calculated) < 1.0
                
                status = "✓ VALID (legitimate high debt)" if is_valid else "✗ CALCULATION ERROR"
                logger.info(f"  {row['country_name']}: {stored:.1f}% - {status}")
                
                if not is_valid:
                    invalid_outliers.append(row['country_name'])
            
            if invalid_outliers:
                logger.warning(f"  ✗ {len(invalid_outliers)} outliers are calculation errors")
                self.issues.append(('Debt/GDP Calculation Errors', invalid_outliers))
            else:
                logger.info(f"  ✓ All outliers are legitimate (e.g., Japan, Sudan have high debt)")
        else:
            logger.info(f"✓ No extreme outliers detected")
        
        # Return True only if there are no invalid outliers
        return len(invalid_outliers) == 0
    
    def check_data_currency_units(self):
        """Check if GDP and debt values are in consistent units."""
        logger.info("\n[CHECK 4] Currency Unit Consistency")
        
        df_2024 = self.df[self.df['year'] == 2024].copy()
        df_2024 = df_2024.dropna(subset=['gdp_usd', 'population', 'gdp_per_capita'])
        
        unit_issues = []
        for _, row in df_2024.head(20).iterrows():
            # Check if GDP per capita calculation is consistent
            calculated_gdp_pc = row['gdp_usd'] / row['population']
            stored_gdp_pc = row['gdp_per_capita']
            
            # Allow 10% tolerance
            if abs(calculated_gdp_pc - stored_gdp_pc) / stored_gdp_pc > 0.10:
                unit_issues.append({
                    'country': row['country_name'],
                    'calculated': calculated_gdp_pc,
                    'stored': stored_gdp_pc,
                    'ratio': calculated_gdp_pc / stored_gdp_pc
                })
        
        if unit_issues:
            logger.warning(f"✗ Found {len(unit_issues)} GDP per capita inconsistencies")
            for issue in unit_issues[:5]:
                logger.warning(f"  {issue['country']}: Calc={issue['calculated']:.0f}, Stored={issue['stored']:.0f} (ratio={issue['ratio']:.2f})")
            self.issues.append(('GDP per Capita Units', unit_issues))
        else:
            logger.info(f"✓ GDP per capita calculations consistent")
        
        return len(unit_issues) == 0
    
    def generate_report(self):
        """Generate validation report."""
        logger.info("\n" + "="*70)
        logger.info("DATA QUALITY VALIDATION REPORT")
        logger.info("="*70)
        
        if not self.issues:
            logger.info("✓ ALL CHECKS PASSED - Data quality is good!")
            return True
        else:
            logger.warning(f"✗ FOUND {len(self.issues)} ISSUES:")
            for issue_type, details in self.issues:
                logger.warning(f"  - {issue_type}: {len(details) if isinstance(details, list) else details} problems")
            logger.warning("\n⚠ RECOMMENDATION: Fix these issues before running visualizations")
            return False
    
    def run_all_checks(self):
        """Run all validation checks."""
        if not self.load_data():
            return False
        
        checks = [
            self.check_debt_to_gdp_consistency,
            self.check_missing_data,
            self.check_outliers,
            self.check_data_currency_units
        ]
        
        results = [check() for check in checks]
        self.generate_report()
        
        return all(results)


if __name__ == "__main__":
    csv_path = Path(__file__).parent.parent / "csv" / "processed" / "macro_final_08MAR2026.csv"
    
    validator = DataQualityValidator(csv_path)
    success = validator.run_all_checks()
    
    import sys
    sys.exit(0 if success else 1)
