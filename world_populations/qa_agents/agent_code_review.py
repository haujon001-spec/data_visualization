# -*- coding: utf-8 -*-
"""
Phase 3 - Code Review Agent
Review ETL and visualization scripts for quality, maintainability, and best practices.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import re


def review_imports(file_path: Path, content: str) -> dict:
    """
    Review import statements for best practices.
    
    Args:
        file_path: Path to file being reviewed
        content: File content as string
    
    Returns:
        Review result dict
    """
    issues = []
    suggestions = []
    
    # Check for unused imports (basic check)
    import_pattern = r'^import\s+(\w+)|^from\s+\w+\s+import\s+(.+)$'
    imports = re.findall(import_pattern, content, re.MULTILINE)
    
    # Check for UTF-8 encoding declaration
    has_utf8 = content.startswith('# -*- coding: utf-8 -*-')
    if not has_utf8:
        issues.append("Missing UTF-8 encoding declaration at top of file")
    
    # Check for docstring
    has_docstring = '"""' in content[:200] or "'''" in content[:200]
    if not has_docstring:
        issues.append("Missing module-level docstring")
    
    result = {
        "passed": len(issues) == 0,
        "has_utf8_encoding": has_utf8,
        "has_module_docstring": has_docstring,
        "issues": issues,
        "suggestions": suggestions
    }
    
    return result


def review_functions(file_path: Path, content: str) -> dict:
    """
    Review function definitions for best practices.
    
    Args:
        file_path: Path to file being reviewed
        content: File content as string
    
    Returns:
        Review result dict
    """
    issues = []
    suggestions = []
    
    # Find all function definitions
    func_pattern = r'def\s+(\w+)\s*\('
    functions = re.findall(func_pattern, content)
    
    # Check for type hints
    type_hint_pattern = r'def\s+\w+\s*\([^)]*:\s*\w+'
    functions_with_hints = re.findall(type_hint_pattern, content)
    
    # Check for docstrings in functions
    func_docstring_pattern = r'def\s+\w+\s*\([^)]*\).*?:\s*\n\s*"""'
    functions_with_docstrings = re.findall(func_docstring_pattern, content, re.DOTALL)
    
    type_hint_ratio = len(functions_with_hints) / len(functions) if functions else 0
    docstring_ratio = len(functions_with_docstrings) / len(functions) if functions else 0
    
    if type_hint_ratio < 0.8:
        suggestions.append(f"Only {type_hint_ratio*100:.0f}% of functions have type hints (recommend >80%)")
    
    if docstring_ratio < 0.8:
        suggestions.append(f"Only {docstring_ratio*100:.0f}% of functions have docstrings (recommend >80%)")
    
    result = {
        "passed": True,  # Suggestions, not failures
        "total_functions": len(functions),
        "functions_with_type_hints": len(functions_with_hints),
        "functions_with_docstrings": len(functions_with_docstrings),
        "type_hint_coverage": f"{type_hint_ratio*100:.0f}%",
        "docstring_coverage": f"{docstring_ratio*100:.0f}%",
        "issues": issues,
        "suggestions": suggestions
    }
    
    return result


def review_error_handling(file_path: Path, content: str) -> dict:
    """
    Review error handling practices.
    
    Args:
        file_path: Path to file being reviewed
        content: File content as string
    
    Returns:
        Review result dict
    """
    issues = []
    suggestions = []
    
    # Check for try/except blocks
    has_try_except = 'try:' in content and 'except' in content
    
    # Check for file operations with 'with' statement
    file_ops = content.count('open(')
    with_statements = content.count('with open(')
    
    if file_ops > 0 and with_statements < file_ops:
        suggestions.append(f"Consider using 'with' statement for all file operations ({with_statements}/{file_ops} currently use 'with')")
    
    # Check for bare except clauses
    bare_except = re.findall(r'except\s*:', content)
    if bare_except:
        issues.append(f"Found {len(bare_except)} bare 'except:' clause(s) - specify exception types")
    
    result = {
        "passed": len(issues) == 0,
        "has_error_handling": has_try_except,
        "file_operations": file_ops,
        "safe_file_operations": with_statements,
        "bare_except_count": len(bare_except),
        "issues": issues,
        "suggestions": suggestions
    }
    
    return result


def review_code_structure(file_path: Path, content: str) -> dict:
    """
    Review overall code structure and organization.
    
    Args:
        file_path: Path to file being reviewed
        content: File content as string
    
    Returns:
        Review result dict
    """
    issues = []
    suggestions = []
    
    # Check for main guard
    has_main_guard = 'if __name__ == "__main__"' in content
    
    # Check for print statements (should use logging or specific output functions)
    print_count = len(re.findall(r'\bprint\s*\(', content))
    
    # Check line length (PEP 8 recommends <79 chars)
    lines = content.split('\n')
    long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
    
    if not has_main_guard and 'def main(' in content:
        suggestions.append("Add 'if __name__ == \"__main__\"' guard for main() function")
    
    if len(long_lines) > 10:
        suggestions.append(f"Found {len(long_lines)} lines longer than 100 characters (consider breaking up long lines)")
    
    # Check for magic numbers
    magic_numbers = re.findall(r'\b(1000000000|1000000|100000)\b', content)
    if magic_numbers:
        suggestions.append(f"Consider using named constants for large numbers (found {len(magic_numbers)} instances)")
    
    result = {
        "passed": True,
        "has_main_guard": has_main_guard,
        "print_statements": print_count,
        "long_lines_count": len(long_lines),
        "file_length": len(lines),
        "issues": issues,
        "suggestions": suggestions
    }
    
    return result


def review_pandas_usage(file_path: Path, content: str) -> dict:
    """
    Review pandas usage for performance and best practices.
    
    Args:
        file_path: Path to file being reviewed
        content: File content as string
    
    Returns:
        Review result dict
    """
    issues = []
    suggestions = []
    
    uses_pandas = 'import pandas' in content or 'from pandas' in content
    
    if not uses_pandas:
        return {
            "passed": True,
            "uses_pandas": False,
            "issues": [],
            "suggestions": []
        }
    
    # Check for iterrows (slow, should avoid)
    has_iterrows = '.iterrows()' in content
    if has_iterrows:
        suggestions.append("Found .iterrows() - consider vectorized operations for better performance")
    
    # Check for chained indexing
    chained_indexing = re.findall(r'\[\s*[\'"][^\'"]+[\'"]\s*\]\s*\[\s*[\'"][^\'"]+[\'"]\s*\]', content)
    if chained_indexing:
        suggestions.append("Consider using .loc[] or .iloc[] instead of chained indexing")
    
    # Check for copy() usage
    has_copy = '.copy()' in content
    
    result = {
        "passed": True,
        "uses_pandas": True,
        "uses_iterrows": has_iterrows,
        "uses_copy": has_copy,
        "issues": issues,
        "suggestions": suggestions
    }
    
    return result


def review_file(file_path: Path) -> Dict:
    """
    Perform comprehensive code review on a single file.
    
    Args:
        file_path: Path to file to review
    
    Returns:
        Review results dict
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    reviews = {
        "imports": review_imports(file_path, content),
        "functions": review_functions(file_path, content),
        "error_handling": review_error_handling(file_path, content),
        "code_structure": review_code_structure(file_path, content),
        "pandas_usage": review_pandas_usage(file_path, content)
    }
    
    return reviews


def generate_code_review_report(file_reviews: Dict, output_path: Path) -> None:
    """
    Generate code review report in Markdown format.
    
    Args:
        file_reviews: Dictionary of file reviews
        output_path: Path to output MD file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate overall status
    all_passed = all(
        review["passed"] 
        for file_review in file_reviews.values() 
        for review in file_review.values()
    )
    overall_status = "PASS" if all_passed else "FAIL"
    
    # Build markdown report
    report_lines = [
        f"# Code Review Report",
        f"",
        f"**Report ID:** CODE_REVIEW_{datetime.now().strftime('%Y%m%d_%H%M%S')}  ",
        f"**Timestamp:** {timestamp}  ",
        f"**Files Reviewed:** {len(file_reviews)}  ",
        f"**Overall Status:** **{overall_status}**  ",
        f"",
        f"---",
        f"",
        f"## Summary",
        f"",
        f"| File | Issues | Suggestions |",
        f"|------|--------|-------------|"
    ]
    
    for file_name, reviews in file_reviews.items():
        total_issues = sum(len(r.get("issues", [])) for r in reviews.values())
        total_suggestions = sum(len(r.get("suggestions", [])) for r in reviews.values())
        report_lines.append(f"| {file_name} | {total_issues} | {total_suggestions} |")
    
    report_lines.extend([
        f"",
        f"---",
        f"",
        f"## Detailed Reviews",
        f""
    ])
    
    for file_name, reviews in file_reviews.items():
        report_lines.extend([
            f"",
            f"### {file_name}",
            f""
        ])
        
        for category, review in reviews.items():
            status_icon = "✅" if review["passed"] else "❌"
            report_lines.extend([
                f"",
                f"#### {category.replace('_', ' ').title()} {status_icon}",
                f""
            ])
            
            # Add metrics (exclude 'passed', 'issues', 'suggestions')
            for key, value in review.items():
                if key not in ['passed', 'issues', 'suggestions']:
                    report_lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
            
            # Add issues
            if review.get("issues"):
                report_lines.append(f"")
                report_lines.append(f"**Issues:**")
                for issue in review["issues"]:
                    report_lines.append(f"- ⚠️ {issue}")
            
            # Add suggestions
            if review.get("suggestions"):
                report_lines.append(f"")
                report_lines.append(f"**Suggestions:**")
                for suggestion in review["suggestions"]:
                    report_lines.append(f"- 💡 {suggestion}")
    
    report_lines.extend([
        f"",
        f"---",
        f"",
        f"## Recommendations",
        f""
    ])
    
    if overall_status == "PASS":
        report_lines.append(f"Code review passed with no critical issues. Address suggestions to improve code quality further.")
    else:
        report_lines.append(f"Code review found critical issues. Please address all issues before proceeding.")
    
    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    
    print(f"[REPORT] Code review report saved to {output_path}")
    print(f"[REPORT] Overall status: {overall_status}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("CODE REVIEW")
    print("=" * 70)
    
    # Define paths
    base_dir = Path(__file__).parent.parent
    scripts_dir = base_dir / "scripts"
    
    # Files to review
    files_to_review = [
        scripts_dir / "01_fetch_population.py",
        scripts_dir / "02_transform_rank_top50.py",
        scripts_dir / "03_build_visualization.py"
    ]
    
    # Review each file
    file_reviews = {}
    for file_path in files_to_review:
        if file_path.exists():
            print(f"[REVIEW] Reviewing {file_path.name}...")
            file_reviews[file_path.name] = review_file(file_path)
        else:
            print(f"[SKIP] File not found: {file_path.name}")
    
    # Generate report
    timestamp = datetime.now().strftime("%d%b%Y")
    report_output = base_dir / "reports" / "qa" / f"code_review_{timestamp}.md"
    
    generate_code_review_report(file_reviews, report_output)
    
    # Calculate final status
    all_passed = all(
        review["passed"] 
        for file_review in file_reviews.values() 
        for review in file_review.values()
    )
    overall_status = "PASS" if all_passed else "FAIL"
    
    print("=" * 70)
    print(f"REVIEW STATUS: {overall_status}")
    print("=" * 70)


if __name__ == "__main__":
    main()
