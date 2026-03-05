"""
Data QA Agent - CSV Validation

Validate CSV schema, row counts, rankings, and data integrity.
"""

import pandas as pd
import json
import numpy as np
from pathlib import Path
from datetime import datetime


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def validate_schema(df: pd.DataFrame, expected_columns: list) -> dict:
    """
    Validate DataFrame schema matches expected columns.
    
    Args:
        df: DataFrame to validate
        expected_columns: List of expected column names
    
    Returns:
        Validation result dict
    """
    actual_columns = df.columns.tolist()
    missing = set(expected_columns) - set(actual_columns)
    extra = set(actual_columns) - set(expected_columns)
    
    result = {
        "passed": len(missing) == 0,
        "expected": expected_columns,
        "actual": actual_columns,
        "missing": list(missing),
        "extra": list(extra)
    }
    
    print(f"[VALIDATION] Schema check: {'PASS' if result['passed'] else 'FAIL'}")
    return result


def validate_row_count(df: pd.DataFrame, expected_per_year: int, year_range: tuple) -> dict:
    """
    Validate row count per year.
    
    Args:
        df: DataFrame to validate
        expected_per_year: Expected number of rows per year
        year_range: Tuple of (start_year, end_year)
    
    Returns:
        Validation result dict
    """
    counts = df.groupby("year").size().to_dict()
    start_year, end_year = year_range
    
    failures = []
    for year in range(start_year, end_year + 1):
        count = counts.get(year, 0)
        if count != expected_per_year:
            failures.append({
                "year": year,
                "expected": expected_per_year,
                "actual": count
            })
    
    result = {
        "passed": len(failures) == 0,
        "expected_per_year": expected_per_year,
        "failures": failures,
        "total_years_checked": len(range(start_year, end_year + 1))
    }
    
    print(f"[VALIDATION] Row count check: {'PASS' if result['passed'] else 'FAIL'}")
    return result


def validate_rankings(df: pd.DataFrame) -> dict:
    """
    Validate ranking continuity (1-50 for each year).
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Validation result dict
    """
    failures = []
    
    for year, year_df in df.groupby("year"):
        ranks = sorted(year_df["rank"].unique())
        expected_ranks = list(range(1, len(year_df) + 1))
        
        if ranks != expected_ranks:
            failures.append({
                "year": year,
                "expected": expected_ranks,
                "actual": ranks
            })
    
    result = {
        "passed": len(failures) == 0,
        "failures": failures
    }
    
    print(f"[VALIDATION] Ranking continuity: {'PASS' if result['passed'] else 'FAIL'}")
    return result


def validate_data_integrity(df: pd.DataFrame) -> dict:
    """
    Validate data integrity (no nulls, positive populations).
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Validation result dict
    """
    issues = []
    
    # Check for nulls
    null_counts = df.isnull().sum()
    if null_counts.any():
        issues.append({
            "type": "null_values",
            "columns": null_counts[null_counts > 0].to_dict()
        })
    
    # Check for non-positive populations
    if (df["population"] <= 0).any():
        count = (df["population"] <= 0).sum()
        issues.append({
            "type": "non_positive_population",
            "count": int(count)
        })
    
    result = {
        "passed": len(issues) == 0,
        "issues": issues
    }
    
    print(f"[VALIDATION] Data integrity: {'PASS' if result['passed'] else 'FAIL'}")
    return result


def generate_qa_report(validations: dict, output_path: Path) -> None:
    """
    Generate QA report JSON file.
    
    Args:
        validations: Dictionary of all validation results
        output_path: Path to output JSON file
    """
    overall_status = "PASS" if all(v["passed"] for v in validations.values()) else "FAIL"
    
    report = {
        "report_id": f"DATA_QA_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "overall_status": overall_status,
        "validations": validations,
        "summary": {
            "total_checks": len(validations),
            "passed": sum(1 for v in validations.values() if v["passed"]),
            "failed": sum(1 for v in validations.values() if not v["passed"])
        }
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(report, f, indent=2, cls=NumpyEncoder)
    
    print(f"[REPORT] QA report saved to {output_path}")
    print(f"[REPORT] Overall status: {overall_status}")
    print(f"[REPORT] Checks: {report['summary']['passed']}/{report['summary']['total_checks']} passed")


if __name__ == "__main__":
    input_file = Path("csv/processed/population_top50_1970_now_5Mar2026.csv")
    report_output = Path("reports/qa/data_qa_report_5Mar2026.json")
    expected_per_year = 50
    # Adjust year range to actual available data (World Bank has data from 1960-2024)
    year_range = (1960, 2024)
    
    print("=" * 70)
    print("DATA QA VALIDATION")
    print("=" * 70)
    
    df = pd.read_csv(input_file)
    print(f"[QA] Loaded {len(df)} records from {input_file.name}")
    
    validations = {
        "schema": validate_schema(df, ["country_name", "country_code", "year", "population", "rank"]),
        "row_count": validate_row_count(df, expected_per_year, year_range),
        "rankings": validate_rankings(df),
        "data_integrity": validate_data_integrity(df)
    }
    
    generate_qa_report(validations, report_output)
    
    overall_status = "PASS" if all(v["passed"] for v in validations.values()) else "FAIL"
    print("=" * 70)
    print(f"QA STATUS: {overall_status}")
    print("=" * 70)
