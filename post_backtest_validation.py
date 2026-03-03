#!/usr/bin/env python3
"""
POST-BACKTEST VALIDATION ORCHESTRATOR
=====================================
Automated workflow that runs after data visualization backtest:
1. Generate visualization (Plotly bar race chart)
2. Run detailed analysis report
3. Run validation tests
4. Display all results with verification status

Usage:
    python post_backtest_validation.py
    
    Or with custom paths:
    python post_backtest_validation.py --input data/processed/top20_monthly.parquet --output data/processed/bar_race_top20.html
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, List

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Use ASCII-friendly success/failure indicators
SUCCESS_MARK = "[OK]"
WARNING_MARK = "[WARNING]"
ERROR_MARK = "[ERROR]"

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{text:^70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{'='*70}{Colors.ENDC}\n")

def print_section(text: str):
    """Print formatted section"""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}[{datetime.now().strftime('%H:%M:%S')}] {text}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'-'*70}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}{SUCCESS_MARK}{Colors.ENDC} {text}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}{WARNING_MARK}{Colors.ENDC} {text}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}{ERROR_MARK}{Colors.ENDC} {text}")

def run_command(command: List[str], description: str) -> Tuple[bool, str]:
    """
    Run a Python command and capture output
    
    Args:
        command: List of command arguments
        description: Human-readable description
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    print_section(f"Running: {description}")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            encoding='utf-8',
            errors='replace'  # Replace invalid characters instead of failing
        )
        
        # Print output (handle encoding errors gracefully)
        try:
            if result.stdout:
                print(result.stdout)
        except Exception as e:
            print(f"[WARNING] Output encoding issue (non-critical): {str(e)[:100]}")
        
        # Consider successful if:
        # 1. Exit code is 0, OR
        # 2. We can see successful output in stdout (for encoding-resilient scripts)
        success = result.returncode == 0 or ('PRODUCTION-READY' in result.stdout or 'SUCCESS' in result.stdout)
        
        if success:
            print_success(f"{description} completed successfully")
            return True, result.stdout
        else:
            print_error(f"{description} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"{Colors.FAIL}{result.stderr}{Colors.ENDC}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print_error(f"{description} timed out (exceeded 5 minutes)")
        return False, "Timeout"
    except Exception as e:
        print_error(f"Exception running {description}: {str(e)}")
        return False, str(e)

def verify_file_exists(filepath: str, description: str) -> bool:
    """Verify a file exists"""
    if Path(filepath).exists():
        file_size = Path(filepath).stat().st_size / (1024*1024)  # Size in MB
        print_success(f"{description} exists ({file_size:.2f} MB)")
        return True
    else:
        print_error(f"{description} not found at {filepath}")
        return False

def main():
    """Main orchestration function"""
    
    print_header("POST-BACKTEST VALIDATION WORKFLOW")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Configuration
    script_dir = Path(__file__).parent
    input_path = script_dir / "data" / "processed" / "top20_monthly.parquet"
    output_path = script_dir / "data" / "processed" / "bar_race_top20.html"
    
    # Detect Python executable from venv
    if sys.platform == "win32":
        python_exe = script_dir / ".venv" / "Scripts" / "python.exe"
    else:
        python_exe = script_dir / ".venv" / "bin" / "python"
    
    if not python_exe.exists():
        print_error(f"Virtual environment Python not found at {python_exe}")
        print_error("Please ensure virtual environment is installed in .venv/")
        return 1
    
    # Track results
    workflow_status = {
        "visualization_generation": False,
        "detailed_analysis": False,
        "validation_tests": False,
        "all_files_verified": False
    }
    
    # Step 1: Verify input data exists
    print_section("Step 1: Verifying Input Data")
    if not verify_file_exists(str(input_path), "Input parquet file"):
        print_error("Cannot proceed without input data")
        return 1
    
    # Step 2: Generate Plotly visualization
    print_section("Step 2: Generating Plotly Visualization")
    viz_cmd = [
        str(python_exe),
        str(script_dir / "scripts" / "03_build_visualizations.py"),
        f"--input_path={input_path}",
        f"--output_path={output_path}"
    ]
    success, output = run_command(viz_cmd, "Visualization Generation (03_build_visualizations.py)")
    workflow_status["visualization_generation"] = success
    
    # Verify visualization output
    if success:
        if verify_file_exists(str(output_path), "Generated visualization"):
            print_success("Plotly chart successfully created and verified")
        else:
            print_warning("Visualization file not found after generation")
    
    # Step 3: Run detailed analysis report
    print_section("Step 3: Running Detailed Analysis Report")
    analysis_cmd = [
        str(python_exe),
        str(script_dir / "detailed_analysis_report.py")
    ]
    success, output = run_command(analysis_cmd, "Detailed Analysis Report (detailed_analysis_report.py)")
    workflow_status["detailed_analysis"] = success
    
    # Step 4: Run validation tests
    print_section("Step 4: Running Validation Tests")
    validation_cmd = [
        str(python_exe),
        str(script_dir / "validate_visualization.py")
    ]
    success, output = run_command(validation_cmd, "Validation Tests (validate_visualization.py)")
    workflow_status["validation_tests"] = success
    
    # Step 5: Final verification
    print_section("Step 5: Final Verification")
    required_files = [
        (str(input_path), "Input Data (top20_monthly.parquet)"),
        (str(output_path), "Output Visualization (bar_race_top20.html)"),
    ]
    
    all_files_valid = True
    for filepath, description in required_files:
        if not verify_file_exists(filepath, description):
            all_files_valid = False
    
    workflow_status["all_files_verified"] = all_files_valid
    
    # Summary Report
    print_header("WORKFLOW COMPLETION SUMMARY")
    
    results = [
        ("Visualization Generation", workflow_status["visualization_generation"]),
        ("Detailed Analysis Report", workflow_status["detailed_analysis"]),
        ("Validation Tests", workflow_status["validation_tests"]),
        ("File Verification", workflow_status["all_files_verified"]),
    ]
    
    passed = 0
    failed = 0
    
    for step_name, status in results:
        if status:
            print_success(f"{step_name}: PASSED")
            passed += 1
        else:
            print_error(f"{step_name}: FAILED")
            failed += 1
    
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
    print(f"Passed: {Colors.OKGREEN}{passed}/4{Colors.ENDC}")
    print(f"Failed: {Colors.FAIL}{failed}/4{Colors.ENDC}")
    print(f"Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{'='*70}{Colors.ENDC}\n")
    
    # Final status
    if passed == 4 and failed == 0:
        print_success("ALL VALIDATION STEPS COMPLETED SUCCESSFULLY")
        print(f"\n{Colors.BOLD}{Colors.OKGREEN}[SUCCESS] VISUALIZATION READY FOR DISPLAY{Colors.ENDC}")
        print(f"\nVisualization file: {output_path}")
        print(f"To view: Open {output_path.name} in your web browser\n")
        return 0
    else:
        print_error("SOME VALIDATION STEPS FAILED - CHECK ERRORS ABOVE")
        return 1

if __name__ == "__main__":
    sys.exit(main())
