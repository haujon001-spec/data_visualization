"""
Submit Phase 1 ETL Tasks to Background Agent

This script creates task manifests for:
1. Fetch population data from World Bank API
2. Transform and rank top 50 countries
3. QA agent for CSV validation
"""

import json
from pathlib import Path
from datetime import datetime


def create_fetch_task():
    """Task 01: Fetch population data from World Bank API"""
    task = {
        "task_id": "TASK_01_FETCH_POPULATION",
        "task_name": "Fetch Population Data from World Bank API",
        "phase": 1,
        "description": "Fetch total population (SP.POP.TOTL) from World Bank API for all countries, 1970-2026",
        "created_by": "local_agent",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "status": "pending",
        "assigned_to": "background_agent",
        "priority": "high",
        "expected_outputs": [
            "scripts/01_fetch_population.py"
        ],
        "expected_functions": [
            "fetch_worldbank_population",
            "save_to_csv",
            "validate_response"
        ],
        "success_criteria": {
            "code_passes_syntax": True,
            "functions_present": True,
            "has_docstrings": True,
            "has_error_handling": True
        },
        "implementation_spec": {
            "api_endpoint": "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL",
            "date_range": "1970:2026",
            "format": "json",
            "per_page": 20000,
            "output_file": "csv/raw/worldbank_population_raw_5Mar2026.csv",
            "required_columns": ["country_name", "country_code", "year", "population"],
            "error_handling": "retry_on_failure",
            "timeout": 60
        }
    }
    return task


def create_transform_task():
    """Task 02: Transform and rank top 50 countries"""
    task = {
        "task_id": "TASK_02_TRANSFORM_RANK",
        "task_name": "Transform and Rank Top 50 Countries",
        "phase": 1,
        "description": "Filter top 50 countries by population, add ranking column, save processed CSV",
        "created_by": "local_agent",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "status": "pending",
        "assigned_to": "background_agent",
        "priority": "high",
        "expected_outputs": [
            "scripts/02_transform_rank_top50.py"
        ],
        "expected_functions": [
            "load_raw_csv",
            "filter_top50_per_year",
            "add_ranking_column",
            "save_processed_csv"
        ],
        "success_criteria": {
            "code_passes_syntax": True,
            "functions_present": True,
            "has_docstrings": True,
            "has_error_handling": True
        },
        "implementation_spec": {
            "input_file": "csv/raw/worldbank_population_raw_5Mar2026.csv",
            "output_file": "csv/processed/population_top50_1970_now_5Mar2026.csv",
            "ranking_method": "per_year_descending",
            "top_n": 50,
            "required_columns": ["country_name", "country_code", "year", "population", "rank"],
            "exclude_aggregates": "config/aggregate_regions_exclude.csv"
        }
    }
    return task


def create_data_qa_task():
    """Task QA: Data QA Agent for CSV validation"""
    task = {
        "task_id": "TASK_QA_DATA_VALIDATION",
        "task_name": "Data QA Agent - CSV Validation",
        "phase": 1,
        "description": "Validate CSV schema, row counts, rankings, and data integrity",
        "created_by": "local_agent",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "status": "pending",
        "assigned_to": "background_agent",
        "priority": "high",
        "expected_outputs": [
            "qa_agents/agent_data_qa.py"
        ],
        "expected_functions": [
            "validate_schema",
            "validate_row_count",
            "validate_rankings",
            "validate_data_integrity",
            "generate_qa_report"
        ],
        "success_criteria": {
            "code_passes_syntax": True,
            "functions_present": True,
            "has_docstrings": True,
            "has_error_handling": True
        },
        "implementation_spec": {
            "input_file": "csv/processed/population_top50_1970_now_5Mar2026.csv",
            "expected_rows_per_year": 50,
            "year_range": [1970, 2026],
            "validations": [
                "schema_check",
                "null_check",
                "ranking_continuity",
                "population_positive",
                "year_coverage"
            ],
            "report_output": "reports/qa/data_qa_report_5Mar2026.json"
        }
    }
    return task


def submit_tasks():
    """Submit all Phase 1 tasks to background agent"""
    project_root = Path(__file__).parent
    task_queue_dir = project_root / "coordination" / "task_queue"
    task_queue_dir.mkdir(parents=True, exist_ok=True)
    
    tasks = [
        create_fetch_task(),
        create_transform_task(),
        create_data_qa_task()
    ]
    
    print("=" * 70)
    print("SUBMITTING PHASE 1 ETL TASKS TO BACKGROUND AGENT")
    print("=" * 70)
    print()
    
    for task in tasks:
        manifest_file = task_queue_dir / f"{task['task_id']}_manifest.json"
        
        with open(manifest_file, "w") as f:
            json.dump(task, f, indent=2)
        
        print(f"✅ Task Submitted: {task['task_id']}")
        print(f"   Name: {task['task_name']}")
        print(f"   Output: {task['expected_outputs'][0]}")
        print(f"   Manifest: {manifest_file}")
        print()
    
    print("=" * 70)
    print(f"Total Tasks Submitted: {len(tasks)}")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("1. Ensure background agent is running:")
    print("   python coordination/background_agent_worker.py")
    print()
    print("2. Monitor task_queue/ folder for task completion")
    print()
    print("3. Check status_reports/ for agent feedback")
    print()


if __name__ == "__main__":
    submit_tasks()
