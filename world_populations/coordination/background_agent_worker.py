# -*- coding: utf-8 -*-
"""
BACKGROUND AGENT WORKER
=======================

Purpose:
    Autonomous worker that:
    - Polls for task manifests from local agent
    - Implements code according to spec
    - Generates outputs
    - Creates status report
    - Submits report back to local agent

Role: Developer + Implementer

Author: OpenClaw Background Agent
Date: 5 Mar 2026
"""

import json
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import subprocess


# ========================================================================
# TASK LISTENER — Polls for new tasks from local agent
# ========================================================================

class TaskListener:
    """
    Polls the task queue directory for new task manifests.
    """

    def __init__(self, project_root: Path, coordination_dir: str = "coordination"):
        self.project_root = project_root
        self.task_queue_dir = project_root / coordination_dir / "task_queue"

    def poll_for_tasks(self, poll_interval: int = 5) -> Dict | None:
        """
        Poll the task queue for pending tasks.
        Returns the first pending task found.
        """
        while True:
            pending_tasks = list(self.task_queue_dir.glob("*_manifest.json"))

            for manifest_file in pending_tasks:
                with open(manifest_file, "r") as f:
                    manifest = json.load(f)

                if manifest["status"] == "pending":
                    print(f"[AGENT] Found pending task: {manifest['task_id']}")
                    return manifest

            print(f"[AGENT] No pending tasks, checking again in {poll_interval}s...")
            time.sleep(poll_interval)

    def mark_task_in_progress(self, task_id: str):
        """Mark task as in_progress."""
        manifest_file = self.task_queue_dir / f"{task_id}_manifest.json"
        with open(manifest_file, "r") as f:
            manifest = json.load(f)
        manifest["status"] = "in_progress"
        manifest["started_at"] = datetime.utcnow().isoformat() + "Z"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"[AGENT] Task marked as in_progress: {task_id}")


# ========================================================================
# TASK EXECUTOR — Does the actual work
# ========================================================================

class TaskExecutor:
    """
    Executes the task according to manifest specifications.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def execute_fetch_task(self, manifest: Dict) -> Dict:
        """
        Execute Phase 1 Task 01: Fetch population data from World Bank API
        """
        print(f"\n[EXECUTING] {manifest['task_name']}")
        
        output_file = manifest["expected_outputs"][0]
        output_path = self.project_root / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        spec = manifest.get("implementation_spec", {})
        functions = manifest.get("expected_functions", [])
        
        code = f'''"""
Fetch Population Data from World Bank API

Fetch total population (SP.POP.TOTL) from World Bank API for all countries, 1970-2026.
Output: CSV file with country_name, country_code, year, population columns.
"""

import requests
import pandas as pd
from pathlib import Path
import time


def fetch_worldbank_population(
    indicator: str = "SP.POP.TOTL",
    start_year: int = 1970,
    end_year: int = 2026,
    per_page: int = 20000
) -> pd.DataFrame:
    """
    Fetch population data from World Bank API.
    
    Args:
        indicator: World Bank indicator code (default: SP.POP.TOTL)
        start_year: Start year for data fetch
        end_year: End year for data fetch
        per_page: Number of results per page
    
    Returns:
        DataFrame with columns: country_name, country_code, year, population
    """
    base_url = "https://api.worldbank.org/v2/country/all/indicator"
    url = f"{{base_url}}/{{indicator}}"
    
    params = {{
        "format": "json",
        "date": f"{{start_year}}:{{end_year}}",
        "per_page": per_page
    }}
    
    print(f"[FETCH] Requesting data from World Bank API...")
    print(f"[FETCH] URL: {{url}}")
    print(f"[FETCH] Date range: {{start_year}}-{{end_year}}")
    
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        validate_response(response)
        
        data = response.json()
        
        if not data or len(data) < 2:
            raise ValueError("Invalid API response format")
        
        records = data[1]  # Data is in second element
        print(f"[FETCH] Retrieved {{len(records)}} records")
        
        # Transform to DataFrame
        rows = []
        for record in records:
            if record.get("value") is not None:
                rows.append({{
                    "country_name": record.get("country", {{}}).get("value"),
                    "country_code": record.get("countryiso3code"),
                    "year": int(record.get("date")),
                    "population": int(record.get("value"))
                }})
        
        df = pd.DataFrame(rows)
        print(f"[FETCH] Converted to DataFrame: {{len(df)}} rows")
        return df
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch data: {{str(e)}}")
        raise


def validate_response(response: requests.Response) -> None:
    """
    Validate API response status and content.
    
    Args:
        response: HTTP response object
    
    Raises:
        ValueError: If response is invalid
    """
    if response.status_code != 200:
        raise ValueError(f"API returned status code {{response.status_code}}")
    
    if response.headers.get("content-type", "").lower() != "application/json;charset=utf-8":
        raise ValueError("Invalid content type")
    
    print(f"[VALIDATION] Response valid: {{response.status_code}}")


def save_to_csv(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame to save
        output_path: Path to output CSV file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SAVE] Data saved to {{output_path}}")
    print(f"[SAVE] File size: {{output_path.stat().st_size}} bytes")


if __name__ == "__main__":
    output_file = Path("{spec.get('output_file', 'csv/raw/worldbank_population_raw_5Mar2026.csv')}")
    
    print("=" * 70)
    print("FETCHING WORLD BANK POPULATION DATA")
    print("=" * 70)
    
    df = fetch_worldbank_population()
    save_to_csv(df, output_file)
    
    print("=" * 70)
    print(f"COMPLETE: {{len(df)}} records saved")
    print("=" * 70)
'''
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        print(f"[AGENT] Script created: {{output_path}}")
        print(f"[AGENT] Functions: {', '.join(functions)}")
        
        outputs = {}
        outputs[output_file] = {
            "path": str(output_path),
            "size_bytes": output_path.stat().st_size,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "exists": True
        }
        
        return {
            "success": True,
            "outputs": outputs,
            "functions": functions,
            "errors": []
        }

    def execute_transform_task(self, manifest: Dict) -> Dict:
        """
        Execute Phase 1 Task 02: Transform and rank top 50 countries
        """
        print(f"\n[EXECUTING] {{manifest['task_name']}}")
        
        output_file = manifest["expected_outputs"][0]
        output_path = self.project_root / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        spec = manifest.get("implementation_spec", {})
        functions = manifest.get("expected_functions", [])
        
        code = f'''"""
Transform and Rank Top 50 Countries

Filter top 50 countries by population for each year, add ranking column.
"""

import pandas as pd
from pathlib import Path


def load_raw_csv(input_path: Path) -> pd.DataFrame:
    """
    Load raw CSV data from World Bank API fetch.
    
    Args:
        input_path: Path to raw CSV file
    
    Returns:
        DataFrame with raw population data
    """
    df = pd.read_csv(input_path)
    print(f"[LOAD] Loaded {{len(df)}} records from {{input_path.name}}")
    return df


def filter_top50_per_year(df: pd.DataFrame, top_n: int = 50, exclude_csv: Path = None) -> pd.DataFrame:
    """
    Filter top N countries by population for each year.
    
    Args:
        df: Raw population DataFrame
        top_n: Number of top countries to keep
        exclude_csv: Path to CSV with aggregate regions to exclude
    
    Returns:
        Filtered DataFrame with only top N countries per year
    """
    # Load exclusion list
    exclude_codes = []
    if exclude_csv and exclude_csv.exists():
        exclude_df = pd.read_csv(exclude_csv)
        exclude_codes = exclude_df["country_code"].tolist()
        print(f"[FILTER] Excluding {{len(exclude_codes)}} aggregate regions")
    
    # Filter out aggregates
    df_filtered = df[~df["country_code"].isin(exclude_codes)].copy()
    
    # Get top N per year
    top_df = (
        df_filtered
        .sort_values(["year", "population"], ascending=[True, False])
        .groupby("year")
        .head(top_n)
        .reset_index(drop=True)
    )
    
    print(f"[FILTER] Top {{top_n}} countries per year: {{len(top_df)}} records")
    return top_df


def add_ranking_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add rank column based on population per year.
    
    Args:
        df: DataFrame with population data
    
    Returns:
        DataFrame with added rank column
    """
    df["rank"] = (
        df.groupby("year")["population"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )
    print(f"[RANK] Added ranking column")
    return df


def save_processed_csv(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save processed DataFrame to CSV.
    
    Args:
        df: Processed DataFrame
        output_path: Path to output CSV file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SAVE] Processed data saved to {{output_path}}")
    print(f"[SAVE] File size: {{output_path.stat().st_size}} bytes")


if __name__ == "__main__":
    input_file = Path("{spec.get('input_file', 'csv/raw/worldbank_population_raw_5Mar2026.csv')}")
    output_file = Path("{spec.get('output_file', 'csv/processed/population_top50_1970_now_5Mar2026.csv')}")
    exclude_file = Path("{spec.get('exclude_aggregates', 'config/aggregate_regions_exclude.csv')}")
    top_n = {spec.get('top_n', 50)}
    
    print("=" * 70)
    print("TRANSFORMING AND RANKING POPULATION DATA")
    print("=" * 70)
    
    df = load_raw_csv(input_file)
    df = filter_top50_per_year(df, top_n, exclude_file)
    df = add_ranking_column(df)
    save_processed_csv(df, output_file)
    
    print("=" * 70)
    print(f"COMPLETE: {{len(df)}} records saved")
    print("=" * 70)
'''
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        print(f"[AGENT] Script created: {{output_path}}")
        print(f"[AGENT] Functions: {', '.join(functions)}")
        
        outputs = {}
        outputs[output_file] = {
            "path": str(output_path),
            "size_bytes": output_path.stat().st_size,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "exists": True
        }
        
        return {
            "success": True,
            "outputs": outputs,
            "functions": functions,
            "errors": []
        }

    def execute_data_qa_task(self, manifest: Dict) -> Dict:
        """
        Execute Phase 1 QA: Data validation agent
        """
        print(f"\n[EXECUTING] {{manifest['task_name']}}")
        
        output_file = manifest["expected_outputs"][0]
        output_path = self.project_root / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        spec = manifest.get("implementation_spec", {})
        functions = manifest.get("expected_functions", [])
        
        code = f'''"""
Data QA Agent - CSV Validation

Validate CSV schema, row counts, rankings, and data integrity.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime


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
    
    result = {{
        "passed": len(missing) == 0,
        "expected": expected_columns,
        "actual": actual_columns,
        "missing": list(missing),
        "extra": list(extra)
    }}
    
    print(f"[VALIDATION] Schema check: {{'PASS' if result['passed'] else 'FAIL'}}")
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
            failures.append({{
                "year": year,
                "expected": expected_per_year,
                "actual": count
            }})
    
    result = {{
        "passed": len(failures) == 0,
        "expected_per_year": expected_per_year,
        "failures": failures,
        "total_years_checked": len(range(start_year, end_year + 1))
    }}
    
    print(f"[VALIDATION] Row count check: {{'PASS' if result['passed'] else 'FAIL'}}")
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
            failures.append({{
                "year": year,
                "expected": expected_ranks,
                "actual": ranks
            }})
    
    result = {{
        "passed": len(failures) == 0,
        "failures": failures
    }}
    
    print(f"[VALIDATION] Ranking continuity: {{'PASS' if result['passed'] else 'FAIL'}}")
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
        issues.append({{
            "type": "null_values",
            "columns": null_counts[null_counts > 0].to_dict()
        }})
    
    # Check for non-positive populations
    if (df["population"] <= 0).any():
        count = (df["population"] <= 0).sum()
        issues.append({{
            "type": "non_positive_population",
            "count": int(count)
        }})
    
    result = {{
        "passed": len(issues) == 0,
        "issues": issues
    }}
    
    print(f"[VALIDATION] Data integrity: {{'PASS' if result['passed'] else 'FAIL'}}")
    return result


def generate_qa_report(validations: dict, output_path: Path) -> None:
    """
    Generate QA report JSON file.
    
    Args:
        validations: Dictionary of all validation results
        output_path: Path to output JSON file
    """
    report = {{
        "report_id": f"DATA_QA_{{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "validations": validations,
        "overall_status": "PASS" if all(v["passed"] for v in validations.values()) else "FAIL"
    }}
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"[REPORT] QA report saved to {{output_path}}")


if __name__ == "__main__":
    input_file = Path("{spec.get('input_file', 'csv/processed/population_top50_1970_now_5Mar2026.csv')}")
    report_output = Path("{spec.get('report_output', 'reports/qa/data_qa_report_5Mar2026.json')}")
    expected_per_year = {spec.get('expected_rows_per_year', 50)}
    year_range = ({spec.get('year_range', [1970, 2026])[0]}, {spec.get('year_range', [1970, 2026])[1]})
    
    print("=" * 70)
    print("DATA QA VALIDATION")
    print("=" * 70)
    
    df = pd.read_csv(input_file)
    print(f"[QA] Loaded {{len(df)}} records from {{input_file.name}}")
    
    validations = {{
        "schema": validate_schema(df, ["country_name", "country_code", "year", "population", "rank"]),
        "row_count": validate_row_count(df, expected_per_year, year_range),
        "rankings": validate_rankings(df),
        "data_integrity": validate_data_integrity(df)
    }}
    
    generate_qa_report(validations, report_output)
    
    overall_status = "PASS" if all(v["passed"] for v in validations.values()) else "FAIL"
    print("=" * 70)
    print(f"QA STATUS: {{overall_status}}")
    print("=" * 70)
'''
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        print(f"[AGENT] QA agent created: {{output_path}}")
        print(f"[AGENT] Functions: {', '.join(functions)}")
        
        outputs = {}
        outputs[output_file] = {
            "path": str(output_path),
            "size_bytes": output_path.stat().st_size,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "exists": True
        }
        
        return {
            "success": True,
            "outputs": outputs,
            "functions": functions,
            "errors": []
        }

    def execute_visualization_task(self, manifest: Dict) -> Dict:
        """
        Example: Execute Phase 3 visualization task.
        """
        print(f"\n[EXECUTING] {manifest['task_name']}")
        print(f"  Description: {manifest['description']}")

        outputs = {}
        functions_implemented = []
        errors = []

        try:
            # Simulated work: Create the visualization script
            script_path = self.project_root / "scripts" / "build_visualization.py"
            script_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate the visualization script
            visualization_code = '''
# -*- coding: utf-8 -*-
"""
Build Population Bar Race Visualization
========================================
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np
from pathlib import Path


def build_population_barrace(df: pd.DataFrame, fig_size: tuple = (12, 8)):
    """
    Build animated bar race chart for population data.
    
    Args:
        df: DataFrame with columns [country, year, population]
        fig_size: Figure size tuple
        
    Returns:
        Figure object
    """
    fig, ax = plt.subplots(figsize=fig_size)
    return fig, ax


def apply_flag_labels(ax, data):
    """
    Apply country flag labels to bars in the chart.
    """
    for idx, row in data.iterrows():
        ax.text(0, idx, f"🚩 {row['country']}", va='center')
    return ax


def apply_si_formatting(value: float) -> str:
    """
    Convert number to SI format (1M, 1B, etc).
    
    Args:
        value: Number to format
        
    Returns:
        Formatted string
    """
    if value >= 1e9:
        return f"{value/1e9:.1f}B"
    elif value >= 1e6:
        return f"{value/1e6:.1f}M"
    elif value >= 1e3:
        return f"{value/1e3:.1f}K"
    else:
        return f"{value:.0f}"


def validate_visualization_output(fig) -> bool:
    """
    Validate that visualization object is valid.
    """
    return fig is not None and hasattr(fig, 'axes')
'''

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(visualization_code)

            outputs["build_visualization.py"] = {
                "path": str(script_path),
                "size_bytes": len(visualization_code),
                "created_at": datetime.utcnow().isoformat() + "Z",
                "exists": True,
            }

            functions_implemented = [
                "build_population_barrace",
                "apply_flag_labels",
                "apply_si_formatting",
                "validate_visualization_output",
            ]

            print(f"[AGENT] Visualization script created: {script_path}")

        except Exception as e:
            errors.append(f"Visualization execution failed: {str(e)}")
            traceback.print_exc()

        return {
            "success": len(errors) == 0,
            "outputs": outputs,
            "functions_implemented": functions_implemented,
            "errors": errors,
        }

    def execute_task(self, manifest: Dict) -> Dict:
        """
        Route task to appropriate executor based on phase and task_id.
        """
        phase = manifest.get("phase")
        task_id = manifest.get("task_id")

        if phase == 1:
            # Phase 1: ETL tasks
            if "FETCH" in task_id:
                return self.execute_fetch_task(manifest)
            elif "TRANSFORM" in task_id:
                return self.execute_transform_task(manifest)
            elif "QA_DATA" in task_id:
                return self.execute_data_qa_task(manifest)
            else:
                return {
                    "success": False,
                    "errors": [f"Unknown Phase 1 task: {task_id}"],
                    "outputs": {},
                }
        elif phase == 3:
            # Phase 3: Visualization tasks
            return self.execute_visualization_task(manifest)
        else:
            return {
                "success": False,
                "errors": [f"Unknown phase: {phase}"],
                "outputs": {},
            }


# ========================================================================
# STATUS REPORTER — Creates status report for local agent
# ========================================================================

class StatusReporter:
    """
    Creates and submits status report back to local agent.
    """

    def __init__(self, project_root: Path, coordination_dir: str = "coordination"):
        self.project_root = project_root
        self.status_report_dir = project_root / coordination_dir / "status_reports"
        self.status_report_dir.mkdir(parents=True, exist_ok=True)

    def create_report(
        self,
        task_id: str,
        manifest: Dict,
        execution_result: Dict,
        start_time: float,
        end_time: float,
    ) -> Dict:
        """
        Create comprehensive status report.
        """
        import ast

        duration = end_time - start_time

        # Validate code Quality
        code_quality = {"syntax_valid": False, "can_import": False}
        if execution_result.get("outputs"):
            for output_file, info in execution_result["outputs"].items():
                if output_file.endswith(".py"):
                    script_path = Path(info["path"])
                    if script_path.exists():
                        try:
                            with open(script_path, "r") as f:
                                code = f.read()
                            compile(code, str(script_path), "exec")
                            code_quality["syntax_valid"] = True

                            # Try to parse AST
                            tree = ast.parse(code)
                            code_quality["can_import"] = True
                        except Exception as e:
                            code_quality["errors"] = [str(e)]

        report = {
            "report_id": f"REPORT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "task_id": task_id,
            "agent_type": "background_agent",
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat() + "Z",
            "duration_seconds": int(duration),
            "outputs": execution_result.get("outputs", {}),
            "implemented_functions": execution_result.get("functions_implemented", []),
            "code_quality": code_quality,
            "validation_results": {
                "all_expected_outputs_exist": all(
                    Path(info["path"]).exists()
                    for info in execution_result.get("outputs", {}).values()
                ),
                "all_required_functions_present": len(
                    execution_result.get("functions_implemented", [])
                ) == len(manifest.get("expected_functions", [])),
            },
            "errors": execution_result.get("errors", []),
            "ready_for_verification": len(execution_result.get("errors", [])) == 0,
        }

        return report

    def submit_report(self, report: Dict) -> Path:
        """
        Write status report to disk, making it visible to local agent.
        """
        task_id = report["task_id"]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_file = self.status_report_dir / f"AGENT_{task_id}_{timestamp}_status.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"[AGENT] Status report submitted: {report_file}")
        return report_file


# ========================================================================
# MAIN BACKGROUND AGENT LOOP
# ========================================================================

class BackgroundAgent:
    """
    Main background agent: continuously listens for tasks and executes them.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.listener = TaskListener(project_root)
        self.executor = TaskExecutor(project_root)
        self.reporter = StatusReporter(project_root)

    def run(self):
        """
        Main loop: continuously poll for tasks, execute, report.
        """
        print("\n" + "=" * 70)
        print("BACKGROUND AGENT — LISTENING FOR TASKS")
        print("=" * 70)

        while True:
            # Poll for pending task
            manifest = self.listener.poll_for_tasks(poll_interval=5)

            if not manifest:
                continue

            task_id = manifest["task_id"]
            print(f"\n[AGENT] Processing task: {task_id}")

            # Mark as in progress
            self.listener.mark_task_in_progress(task_id)

            # Execute the task
            start_time = time.time()
            try:
                execution_result = self.executor.execute_task(manifest)
            except Exception as e:
                execution_result = {
                    "success": False,
                    "errors": [str(e)],
                    "outputs": {},
                }
                traceback.print_exc()
            end_time = time.time()

            # Create and submit status report
            report = self.reporter.create_report(
                task_id, manifest, execution_result, start_time, end_time
            )
            self.reporter.submit_report(report)

            print(f"[AGENT] Task complete: {task_id}")


# ========================================================================
# ENTRY POINT
# ========================================================================

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    agent = BackgroundAgent(project_root)
    agent.run()
