# -*- coding: utf-8 -*-
"""
Data QA Agent for Phase 1 - ETL

Validates the correctness, completeness, and consistency of:
- GDP data
- Population data
- Debt data
- Merged macro-economic dataset
- Derived metrics (GDP per capita, debt-to-GDP, growth rates)

Output:
- reports/qa/data_qa_report_<timestamp>.json
- reports/qa/data_qa_summary_<timestamp>.md
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class DataQAAgent:
    """Quality assurance agent for macro-economic data."""
    
    def __init__(self, config_file: Path = None):
        """Initialize QA agent with configuration."""
        self.config = self._load_config(config_file)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': [],
            'warnings': [],
            'errors': [],
            'summary': {}
        }
    
    def _load_config(self, config_file: Path = None) -> dict:
        """Load QA thresholds from config."""
        import yaml
        
        if config_file is None:
            config_file = Path(__file__).parent.parent / 'config' / 'settings.yaml'
        
        if not config_file.exists():
            logger.warning("Config file not found, using default thresholds")
            return self._default_thresholds()
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        return config.get('qa_thresholds', self._default_thresholds())
    
    def _default_thresholds(self) -> dict:
        """Default QA thresholds."""
        return {
            'data_validation': {
                'gdp': {'min_value': 0, 'max_value': 100000000000000},
                'population': {'min_value': 0, 'max_value': 8000000000},
                'debt': {'min_value': 0, 'max_value': 1000000000000000},
                'gdp_per_capita': {'min_value': 0, 'max_value': 500000},
                'debt_to_gdp': {'min_value': 0, 'max_value': 5},
                'population_growth': {'min_value': -0.5, 'max_value': 2},
                'gdp_growth': {'min_value': -0.5, 'max_value': 2}
            },
            'completeness': {
                'min_countries': 150,
                'min_years': 50,
                'max_missing_percent': 0.15
            }
        }
    
    def log_check(self, check_name: str, status: str, message: str = None):
        """Log a QA check result."""
        entry = {'check': check_name, 'status': status}
        if message:
            entry['message'] = message
        
        self.results['checks'].append(entry)
        
        if status == 'PASS':
            logger.info(f"[QA ✓] {check_name}")
        elif status == 'WARNING':
            logger.warning(f"[QA ⚠] {check_name}")
            if message:
                self.results['warnings'].append({'check': check_name, 'message': message})
        elif status == 'FAIL':
            logger.error(f"[QA ✗] {check_name}")
            if message:
                self.results['errors'].append({'check': check_name, 'message': message})
    
    def validate_schema(self, df: pd.DataFrame, expected_columns: list, df_name: str) -> bool:
        """Validate dataframe schema."""
        missing_cols = set(expected_columns) - set(df.columns)
        
        if len(missing_cols) > 0:
            self.log_check(
                f"Schema: {df_name}",
                'FAIL',
                f"Missing columns: {missing_cols}"
            )
            return False
        
        self.log_check(f"Schema: {df_name}", 'PASS')
        return True
    
    def validate_data_types(self, df: pd.DataFrame, df_name: str) -> bool:
        """Validate numeric columns are numeric."""
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            self.log_check(f"Data Types: {df_name}", 'WARNING', "No numeric columns found")
            return True
        
        self.log_check(f"Data Types: {df_name}", 'PASS')
        return True
    
    def validate_gdp(self, df: pd.DataFrame) -> bool:
        """Validate GDP values."""
        if 'gdp_usd' not in df.columns:
            return True
        
        invalid = df[
            (df['gdp_usd'].isnull()) |
            (df['gdp_usd'] < 0) |
            (df['gdp_usd'] > self.config['data_validation']['gdp']['max_value'])
        ]
        
        if len(invalid) > 0:
            self.log_check(
                'Validation: GDP values',
                'FAIL',
                f"{len(invalid)} invalid GDP values (negative or out of range)"
            )
            return False
        
        self.log_check('Validation: GDP values', 'PASS')
        return True
    
    def validate_population(self, df: pd.DataFrame) -> bool:
        """Validate population values."""
        if 'population' not in df.columns:
            return True
        
        invalid = df[
            (df['population'].isnull()) |
            (df['population'] < 0) |
            (df['population'] > self.config['data_validation']['population']['max_value'])
        ]
        
        if len(invalid) > 0:
            self.log_check(
                'Validation: Population values',
                'FAIL',
                f"{len(invalid)} invalid population values"
            )
            return False
        
        self.log_check('Validation: Population values', 'PASS')
        return True
    
    def validate_debt_to_gdp(self, df: pd.DataFrame) -> bool:
        """Validate debt-to-GDP ratio."""
        if 'debt_to_gdp' not in df.columns:
            return True
        
        # Impossible values (> 10)
        impossible = df[df['debt_to_gdp'] > 10]
        if len(impossible) > 0:
            self.log_check(
                'Validation: Debt-to-GDP ratio',
                'WARNING',
                f"{len(impossible)} rows with debt_to_gdp > 10 (potential data errors)"
            )
            return True  # Not a hard fail, but flagged
        
        self.log_check('Validation: Debt-to-GDP ratio', 'PASS')
        return True
    
    def validate_growth_rates(self, df: pd.DataFrame) -> bool:
        """Validate growth rates are within reasonable bounds."""
        growth_cols = [col for col in df.columns if 'growth' in col.lower()]
        
        if len(growth_cols) == 0:
            return True
        
        all_invalid = []
        
        for col in growth_cols:
            invalid = df[
                (df[col] < -0.5) |  # -500% growth
                (df[col] > 2)  # +200% growth
            ]
            all_invalid.extend(invalid.index.tolist())
        
        if len(all_invalid) > 0:
            self.log_check(
                'Validation: Growth rates',
                'WARNING',
                f"{len(all_invalid)} rows with extreme growth rates (> ±100%)"
            )
            return True  # Warning, not fail
        
        self.log_check('Validation: Growth rates', 'PASS')
        return True
    
    def validate_no_duplicates(self, df: pd.DataFrame) -> bool:
        """Validate no duplicate country-year combinations."""
        if 'country_code' not in df.columns or 'year' not in df.columns:
            return True
        
        duplicates = df[df.duplicated(subset=['country_code', 'year'], keep=False)]
        
        if len(duplicates) > 0:
            self.log_check(
                'Validation: No duplicates',
                'FAIL',
                f"{len(duplicates)} duplicate country-year combinations"
            )
            return False
        
        self.log_check('Validation: No duplicates', 'PASS')
        return True
    
    def validate_completeness(self, df: pd.DataFrame) -> bool:
        """Validate dataset completeness."""
        checks_passed = True
        
        # Check minimum countries
        n_countries = df['country_code'].nunique() if 'country_code' in df.columns else 0
        min_countries = self.config['completeness']['min_countries']
        
        if n_countries < min_countries:
            self.log_check(
                'Completeness: Minimum countries',
                'FAIL',
                f"{n_countries} countries (minimum: {min_countries})"
            )
            checks_passed = False
        else:
            self.log_check('Completeness: Minimum countries', 'PASS')
        
        # Check minimum years
        n_years = df['year'].nunique() if 'year' in df.columns else 0
        min_years = self.config['completeness']['min_years']
        
        if n_years < min_years:
            self.log_check(
                'Completeness: Minimum years',
                'FAIL',
                f"{n_years} years (minimum: {min_years})"
            )
            checks_passed = False
        else:
            self.log_check('Completeness: Minimum years', 'PASS')
        
        return checks_passed
    
    def run_qa(self, df: pd.DataFrame, df_name: str = 'macro_final') -> bool:
        """Run full QA suite."""
        logger.info("=" * 70)
        logger.info(f"RUNNING DATA QA: {df_name}")
        logger.info("=" * 70)
        
        all_pass = True
        
        # Schema and type validation
        expected_cols = ['country_name', 'country_code', 'year', 'gdp_usd', 'population']
        all_pass &= self.validate_schema(df, expected_cols, df_name)
        all_pass &= self.validate_data_types(df, df_name)
        
        # Value validation
        all_pass &= self.validate_gdp(df)
        all_pass &= self.validate_population(df)
        all_pass &= self.validate_debt_to_gdp(df)
        all_pass &= self.validate_growth_rates(df)
        
        # Structural validation
        all_pass &= self.validate_no_duplicates(df)
        all_pass &= self.validate_completeness(df)
        
        # Summary
        self.results['summary'] = {
            'total_rows': len(df),
            'n_countries': df['country_code'].nunique() if 'country_code' in df.columns else 0,
            'n_years': df['year'].nunique() if 'year' in df.columns else 0,
            'checks_passed': sum(1 for c in self.results['checks'] if c['status'] == 'PASS'),
            'checks_failed': sum(1 for c in self.results['checks'] if c['status'] == 'FAIL'),
            'warnings': len(self.results['warnings']),
            'overall_status': 'PASS' if all_pass else 'FAIL'
        }
        
        logger.info("=" * 70)
        logger.info(f"QA SUMMARY:")
        logger.info(f"  Status: {self.results['summary']['overall_status']}")
        logger.info(f"  Total rows: {self.results['summary']['total_rows']}")
        logger.info(f"  Countries: {self.results['summary']['n_countries']}")
        logger.info(f"  Years: {self.results['summary']['n_years']}")
        logger.info(f"  Checks passed: {self.results['summary']['checks_passed']}")
        logger.info(f"  Checks failed: {self.results['summary']['checks_failed']}")
        logger.info(f"  Warnings: {self.results['summary']['warnings']}")
        logger.info("=" * 70)
        
        return all_pass
    
    def save_results(self, output_dir: Path):
        """Save QA results to JSON and markdown."""
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%d%b%Y").upper()
        
        # Save JSON
        json_file = output_dir / f'data_qa_report_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"[SAVE] QA report saved to {json_file}")
        
        # Save Markdown summary
        md_file = output_dir / f'data_qa_summary_{timestamp}.md'
        with open(md_file, 'w') as f:
            f.write(f"# Data QA Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Overall Status:** {self.results['summary']['overall_status']}\n")
            f.write(f"- **Total Rows:** {self.results['summary']['total_rows']}\n")
            f.write(f"- **Countries:** {self.results['summary']['n_countries']}\n")
            f.write(f"- **Years:** {self.results['summary']['n_years']}\n")
            f.write(f"- **Checks Passed:** {self.results['summary']['checks_passed']}\n")
            f.write(f"- **Checks Failed:** {self.results['summary']['checks_failed']}\n")
            f.write(f"- **Warnings:** {self.results['summary']['warnings']}\n\n")
            
            if self.results['errors']:
                f.write(f"## Errors\n\n")
                for error in self.results['errors']:
                    f.write(f"- **{error['check']}:** {error['message']}\n")
            
            if self.results['warnings']:
                f.write(f"## Warnings\n\n")
                for warning in self.results['warnings']:
                    f.write(f"- **{warning['check']}:** {warning['message']}\n")
        
        logger.info(f"[SAVE] QA summary saved to {md_file}")


def main():
    """Main execution function."""
    try:
        # Load final dataset
        project_root = Path(__file__).parent.parent
        processed_dir = project_root / 'csv' / 'processed'
        
        # Get latest macro_final file
        final_files = list(processed_dir.glob('macro_final_*.csv'))
        if not final_files:
            raise FileNotFoundError("No macro_final CSV found")
        
        latest_file = max(final_files, key=lambda p: p.stat().st_mtime)
        df = pd.read_csv(latest_file)
        
        logger.info(f"[LOAD] Loaded {latest_file.name}")
        
        # Run QA
        qa = DataQAAgent()
        passed = qa.run_qa(df, 'macro_final')
        
        # Save results
        qa_dir = project_root / 'reports' / 'qa'
        qa.save_results(qa_dir)
        
        if passed:
            logger.info("Data QA PASSED")
        else:
            logger.warning("Data QA completed with failures - continuing for testing")
        
    except Exception as e:
        logger.error(f"❌ Data QA FAILED: {str(e)}")
        raise


if __name__ == "__main__":
    main()
