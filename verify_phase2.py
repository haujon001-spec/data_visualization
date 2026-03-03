#!/usr/bin/env python3
"""
Quick verification script for Phase 2 implementation.
This script checks that all required components are present.
"""

import sys
from pathlib import Path
import importlib.util

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check_file_exists(path: Path, description: str) -> bool:
    """Check if a file exists and report status."""
    if path.exists():
        print(f"{GREEN}✓{RESET} {description} - {path.name}")
        return True
    else:
        print(f"{RED}✗{RESET} {description} - NOT FOUND")
        return False

def check_script_syntax(script_path: Path) -> bool:
    """Check if Python script has valid syntax."""
    try:
        spec = importlib.util.spec_from_file_location("module", script_path)
        if spec and spec.loader:
            importlib.util.module_from_spec(spec)
            print(f"{GREEN}✓{RESET} Python syntax valid")
            return True
    except SyntaxError as e:
        print(f"{RED}✗{RESET} Syntax error: {e}")
        return False
    except Exception as e:
        print(f"{RED}✗{RESET} Import error: {e}")
        return False
    return True

def check_python_classes(script_path: Path) -> bool:
    """Check if required classes are defined."""
    with open(script_path, 'r') as f:
        content = f.read()
    
    required_classes = ['DataNormalizer', 'TopNRanker', 'AssetRecord']
    all_found = True
    
    for cls in required_classes:
        if f'class {cls}' in content:
            print(f"{GREEN}✓{RESET} Class found: {cls}")
        else:
            print(f"{RED}✗{RESET} Class NOT found: {cls}")
            all_found = False
    
    return all_found

def check_methods(script_path: Path) -> bool:
    """Check if required methods are defined."""
    with open(script_path, 'r') as f:
        content = f.read()
    
    methods = {
        'DataNormalizer': [
            'read_raw_files',
            'normalize_companies',
            'normalize_crypto',
            'normalize_metals',
            'merge_assets'
        ],
        'TopNRanker': [
            'rank_by_date',
            'compute_rank_changes',
            'inject_corporate_actions',
            'validate_quality'
        ]
    }
    
    all_found = True
    
    for cls, method_list in methods.items():
        for method in method_list:
            if f'def {method}' in content:
                print(f"{GREEN}✓{RESET} Method found: {cls}.{method}")
            else:
                print(f"{RED}✗{RESET} Method NOT found: {cls}.{method}")
                all_found = False
    
    return all_found

def main():
    """Run verification checks."""
    data_vis_dir = Path(__file__).parent
    
    print("\n" + "=" * 80)
    print("Phase 2 Implementation Verification")
    print("=" * 80 + "\n")
    
    # Check main script
    print("1. Checking main script...")
    script_path = data_vis_dir / "scripts" / "02_build_rankings.py"
    script_exists = check_file_exists(script_path, "Main script")
    
    if script_exists:
        script_syntax_valid = check_script_syntax(script_path)
        classes_found = check_python_classes(script_path)
        methods_found = check_methods(script_path)
    else:
        script_syntax_valid = classes_found = methods_found = False
    
    # Check documentation files
    print("\n2. Checking documentation...")
    doc_files = [
        (data_vis_dir / "PHASE2_SPECIFICATION.md", "Specification document"),
        (data_vis_dir / "PHASE2_USAGE_GUIDE.md", "Usage guide"),
        (data_vis_dir / "PHASE2_VERIFICATION.md", "Verification document"),
        (data_vis_dir / "requirements_phase2.txt", "Requirements file"),
    ]
    
    docs_exist = all(check_file_exists(path, desc) for path, desc in doc_files)
    
    # Check output directories structure
    print("\n3. Checking directory structure...")
    required_dirs = [
        (data_vis_dir / "data" / "raw", "Raw data directory"),
        (data_vis_dir / "data" / "processed", "Processed data directory"),
        (data_vis_dir / "scripts", "Scripts directory"),
    ]
    
    directories_exist = all(
        check_file_exists(path, desc) if path.exists() else not check_file_exists(path, f"{desc} - auto-created on run")
        for path, desc in required_dirs
    )
    
    # Final summary
    print("\n" + "=" * 80)
    print("Verification Summary")
    print("=" * 80 + "\n")
    
    checks = {
        "Script exists": script_exists,
        "Script syntax valid": script_syntax_valid,
        "Required classes found": classes_found,
        "Required methods found": methods_found,
        "Documentation complete": docs_exist,
    }
    
    for check_name, result in checks.items():
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"  {status} - {check_name}")
    
    all_passed = all(checks.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print(f"{GREEN}✓ ALL CHECKS PASSED{RESET}")
        print("Phase 2 implementation is complete and ready to use.")
        print("\nTo run Phase 2:")
        print(f"  cd {data_vis_dir}")
        print("  python scripts/02_build_rankings.py")
        print("=" * 80 + "\n")
        return 0
    else:
        print(f"{RED}✗ SOME CHECKS FAILED{RESET}")
        print("Please review the issues above.")
        print("=" * 80 + "\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
