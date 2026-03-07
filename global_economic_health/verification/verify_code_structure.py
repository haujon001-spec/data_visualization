# -*- coding: utf-8 -*-
"""
Verification Layer - Code Structure Check

Verifies that all required scripts exist and have correct structure.
Checks for required functions, imports, and configuration.

Output: verification/code_structure_report_<timestamp>.md
"""

import ast
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


class CodeStructureVerifier:
    """Verifies code structure and completeness."""
    
    def __init__(self):
        """Initialize verifier."""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': [],
            'errors': [],
            'summary': {}
        }
        
        # Define required scripts and their required functions
        self.required_scripts = {
            'scripts/01_fetch_gdp.py': [
                'fetch_worldbank_gdp',
                'validate_response',
                'save_to_csv'
            ],
            'scripts/02_fetch_population.py': [
                'fetch_worldbank_population',
                'validate_response',
                'save_to_csv'
            ],
            'scripts/03_fetch_debt.py': [
                'fetch_worldbank_debt',
                'validate_response',
                'save_to_csv'
            ],
            'scripts/04_transform_merge_clean.py': [
                'load_raw_csvs',
                'merge_datasets',
                'apply_cleaning_rules',
                'derive_metrics'
            ],
            'scripts/05_build_visualization_v3_animated_trendline.py': [
                'AnimatedPopulationAnalyzer',
                'AnimatedPopulationDashboardV3'
            ],
            'qa_agents/agent_data_qa.py': [
                'DataQAAgent'
            ],
            'verification/verify_code_structure.py': [
                'CodeStructureVerifier'
            ]
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
    
    def verify_script_exists(self, script_path: str, project_root: Path) -> bool:
        """Verify a script file exists."""
        full_path = project_root / script_path
        
        if not full_path.exists():
            self.log_check(
                f'File exists: {script_path}',
                'FAIL',
                f'File not found: {full_path}'
            )
            return False
        
        self.log_check(f'File exists: {script_path}', 'PASS')
        return True
    
    def verify_script_syntax(self, script_path: str, project_root: Path) -> bool:
        """Verify a Python script has valid syntax."""
        full_path = project_root / script_path
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()
            ast.parse(code)
            self.log_check(f'Syntax: {script_path}', 'PASS')
            return True
        
        except SyntaxError as e:
            self.log_check(
                f'Syntax: {script_path}',
                'FAIL',
                f'Syntax error: {str(e)}'
            )
            return False
    
    def verify_required_functions(self, script_path: str, required_funcs: list, project_root: Path) -> bool:
        """Verify a script contains required functions/classes."""
        full_path = project_root / script_path
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code)
            defined_items = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined_items.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    defined_items.append(node.name)
            
            missing = set(required_funcs) - set(defined_items)
            
            if missing:
                self.log_check(
                    f'Required functions: {script_path}',
                    'FAIL',
                    f'Missing: {missing}'
                )
                return False
            
            self.log_check(f'Required functions: {script_path}', 'PASS')
            return True
        
        except Exception as e:
            self.log_check(
                f'Required functions: {script_path}',
                'FAIL',
                f'Could not parse: {str(e)}'
            )
            return False
    
    def verify_no_hardcoded_paths(self, script_path: str, project_root: Path) -> bool:
        """Warn if script contains hard-coded absolute paths."""
        full_path = project_root / script_path
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple check for common hard-coded paths (C:\, /home/, etc.)
        warnings = []
        
        if 'C:\\' in content or 'c:\\' in content:
            warnings.append('Possible Windows absolute path')
        if '/home/' in content or '/root/' in content:
            warnings.append('Possible Unix absolute path')
        
        if warnings:
            self.log_check(
                f'No hardcoded paths: {script_path}',
                'WARNING',
                f'{"; ".join(warnings)}'
            )
            return True  # Warning, not failure
        
        self.log_check(f'No hardcoded paths: {script_path}', 'PASS')
        return True
    
    def run_verification(self, project_root: Path) -> bool:
        """Run full code structure verification."""
        logger.info("=" * 70)
        logger.info("VERIFYING CODE STRUCTURE")
        logger.info("=" * 70)
        
        all_pass = True
        
        for script_path, required_funcs in self.required_scripts.items():
            # Check exists
            if not self.verify_script_exists(script_path, project_root):
                all_pass = False
                continue
            
            # Check syntax
            if not self.verify_script_syntax(script_path, project_root):
                all_pass = False
                continue
            
            # Check functions
            if not self.verify_required_functions(script_path, required_funcs, project_root):
                all_pass = False
            
            # Check hardcoded paths
            self.verify_no_hardcoded_paths(script_path, project_root)
        
        # Summary
        self.results['summary'] = {
            'checks_passed': sum(1 for c in self.results['checks'] if c['status'] == 'PASS'),
            'checks_failed': sum(1 for c in self.results['checks'] if c['status'] == 'FAIL'),
            'overall_status': 'PASS' if all_pass else 'FAIL'
        }
        
        logger.info("=" * 70)
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
            f.write("# Code Structure Verification Report\n\n")
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
    
    verifier = CodeStructureVerifier()
    passed = verifier.run_verification(project_root)
    
    report_path = project_root / 'reports' / 'verification' / f'code_structure_report_{datetime.now().strftime("%d%b%Y").upper()}.md'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    verifier.save_report(report_path)
    
    if not passed:
        raise ValueError("Code structure verification failed")


if __name__ == "__main__":
    main()
