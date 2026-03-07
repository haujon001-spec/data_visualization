# -*- coding: utf-8 -*-
"""
Verification Layer - Output Validation

Verifies that ETL outputs are correctly formatted and complete.
Checks CSV schemas, row counts, and value ranges.

Output: verification/outputs_report_<timestamp>.md
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class OutputVerifier:
    """Verifies ETL output files and schemas."""
    
    def __init__(self):
        """Initialize verifier."""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': [],
            'errors': [],
            'summary': {}
        }
        
        # Define required output files and their schemas
        self.required_outputs = {
            'csv/raw/gdp_raw_*.csv': {
                'columns': ['country_name', 'country_code', 'year', 'gdp_usd'],
                'description': 'GDP raw data from World Bank'
            },
            'csv/raw/population_raw_*.csv': {
                'columns': ['country_name', 'country_code', 'year', 'population'],
                'description': 'Population raw data from World Bank'
            },
            'csv/raw/debt_raw_*.csv': {
                'columns': ['country_name', 'country_code', 'year', 'debt_total_usd'],
                'description': 'Debt raw data'
            },
            'csv/processed/macro_final_*.csv': {
                'columns': ['country_name', 'country_code', 'year', 'gdp_usd', 'population', 'gdp_per_capita'],
                'description': 'Final macro-economic dataset'
            }
        }
    
    def log_check(self, check_name: str, status: str, message: str = None):
        """Log a verification check."""
        entry = {'check': check_name, 'status': status}
        if message:
            entry['message'] = message
        
        self.results['checks'].append(entry)
        
        if status == 'PASS':
            logger.info(f"[VERIFY ✓] {check_name}")
        elif status == 'FAIL':
            logger.error(f"[VERIFY ✗] {check_name}")
            if message:
                self.results['errors'].append({'check': check_name, 'message': message})
    
    def find_latest_file(self, pattern: str, project_root: Path) -> Path:
        """Find latest file matching glob pattern."""
        import glob
        
        full_pattern = str(project_root / pattern)
        matches = glob.glob(full_pattern)
        
        if not matches:
            return None
        
        # Return most recently modified
        return max(matches, key=lambda p: Path(p).stat().st_mtime)
    
    def verify_file_exists(self, pattern: str, project_root: Path) -> bool:
        """Verify output file exists."""
        file_path = self.find_latest_file(pattern, project_root)
        
        if not file_path:
            self.log_check(
                f'File exists: {pattern}',
                'FAIL',
                f'No file found matching: {pattern}'
            )
            return False
        
        self.log_check(f'File exists: {pattern}', 'PASS')
        return True
    
    def verify_schema(self, pattern: str, expected_cols: list, project_root: Path) -> bool:
        """Verify CSV schema."""
        file_path = self.find_latest_file(pattern, project_root)
        
        if not file_path:
            return False
        
        try:
            df = pd.read_csv(file_path)
            
            missing_cols = set(expected_cols) - set(df.columns)
            
            if missing_cols:
                self.log_check(
                    f'Schema: {Path(file_path).name}',
                    'FAIL',
                    f'Missing columns: {missing_cols}'
                )
                return False
            
            self.log_check(f'Schema: {Path(file_path).name}', 'PASS')
            return True
        
        except Exception as e:
            self.log_check(
                f'Schema: {pattern}',
                'FAIL',
                f'Could not read: {str(e)}'
            )
            return False
    
    def verify_row_count(self, pattern: str, project_root: Path, min_rows: int = 100) -> bool:
        """Verify CSV has reasonable row count."""
        file_path = self.find_latest_file(pattern, project_root)
        
        if not file_path:
            return False
        
        try:
            df = pd.read_csv(file_path)
            
            if len(df) < min_rows:
                self.log_check(
                    f'Row count: {Path(file_path).name}',
                    'FAIL',
                    f'{len(df)} rows (minimum: {min_rows})'
                )
                return False
            
            self.log_check(
                f'Row count: {Path(file_path).name}',
                'PASS',
                f'{len(df)} rows'
            )
            return True
        
        except Exception as e:
            self.log_check(
                f'Row count: {pattern}',
                'FAIL',
                f'Could not count rows: {str(e)}'
            )
            return False
    
    def verify_no_nulls_critical(self, pattern: str, critical_cols: list, project_root: Path) -> bool:
        """Verify no null values in critical columns."""
        file_path = self.find_latest_file(pattern, project_root)
        
        if not file_path:
            return False
        
        try:
            df = pd.read_csv(file_path)
            
            nulls = 0
            for col in critical_cols:
                if col in df.columns:
                    col_nulls = df[col].isnull().sum()
                    nulls += col_nulls
            
            if nulls > 0:
                self.log_check(
                    f'No nulls: {Path(file_path).name}',
                    'FAIL',
                    f'{nulls} null values in critical columns'
                )
                return False
            
            self.log_check(f'No nulls: {Path(file_path).name}', 'PASS')
            return True
        
        except Exception as e:
            self.log_check(
                f'No nulls: {pattern}',
                'FAIL',
                f'Could not check: {str(e)}'
            )
            return False
    
    def run_verification(self, project_root: Path) -> bool:
        """Run full output verification."""
        logger.info("=" * 70)
        logger.info("VERIFYING ETL OUTPUTS")
        logger.info("=" * 70)
        
        all_pass = True
        
        for pattern, info in self.required_outputs.items():
            logger.info(f"\n[VERIFY] {info['description']}")
            
            # Check file exists
            if not self.verify_file_exists(pattern, project_root):
                all_pass = False
                continue
            
            # Check schema
            if not self.verify_schema(pattern, info['columns'], project_root):
                all_pass = False
            
            # Check row count
            if not self.verify_row_count(pattern, project_root, min_rows=100):
                all_pass = False
            
            # Check for nulls in critical columns
            critical_cols = info['columns'][:3]  # First 3 are usually critical
            self.verify_no_nulls_critical(pattern, critical_cols, project_root)
        
        # Summary
        self.results['summary'] = {
            'checks_passed': sum(1 for c in self.results['checks'] if c['status'] == 'PASS'),
            'checks_failed': sum(1 for c in self.results['checks'] if c['status'] == 'FAIL'),
            'overall_status': 'PASS' if all_pass else 'FAIL'
        }
        
        logger.info("\n" + "=" * 70)
        logger.info(f"Verification Summary:")
        logger.info(f"  Passed: {self.results['summary']['checks_passed']}")
        logger.info(f"  Failed: {self.results['summary']['checks_failed']}")
        logger.info(f"  Status: {self.results['summary']['overall_status']}")
        logger.info("=" * 70)
        
        return all_pass
    
    def save_report(self, report_path: Path):
        """Save verification report."""
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("# Output Verification Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Status:** {self.results['summary']['overall_status']}\n")
            f.write(f"- **Checks Passed:** {self.results['summary']['checks_passed']}\n")
            f.write(f"- **Checks Failed:** {self.results['summary']['checks_failed']}\n\n")
            
            if self.results['errors']:
                f.write("## Errors\n\n")
                for error in self.results['errors']:
                    f.write(f"- **{error['check']}:** {error['message']}\n")
        
        logger.info(f"[SAVE] Verification report saved to {report_path}")


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent
    
    verifier = OutputVerifier()
    passed = verifier.run_verification(project_root)
    
    report_path = project_root / 'reports' / 'verification' / f'outputs_report_{datetime.now().strftime("%d%b%Y").upper()}.md'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    verifier.save_report(report_path)
    
    if not passed:
        raise ValueError("Output verification failed")


if __name__ == "__main__":
    main()
