"""
Verify Phase 1 ETL Scripts

Run local agent verification on all Phase 1 tasks
"""

import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / "coordination"))

from local_agent_coordinator import (
    TaskDispatcher,
    StatusMonitor,
    VerificationGateway,
    AuditTrailLogger
)


def verify_phase1_tasks():
    """Verify all Phase 1 ETL tasks"""
    project_root = Path(__file__).parent
    
    dispatcher = TaskDispatcher(project_root)
    monitor = StatusMonitor(project_root)
    gateway = VerificationGateway(project_root)
    logger = AuditTrailLogger(project_root)
    
    task_queue_dir = project_root / "coordination" / "task_queue"
    
    # Get all Phase 1 task manifests
    phase1_tasks = [
        "TASK_01_FETCH_POPULATION",
        "TASK_02_TRANSFORM_RANK",
        "TASK_QA_DATA_VALIDATION"
    ]
    
    print("=" * 70)
    print("PHASE 1 ETL VERIFICATION")
    print("=" * 70)
    print()
    
    results = []
    
    for task_id in phase1_tasks:
        manifest_file = task_queue_dir / f"{task_id}_manifest.json"
        
        if not manifest_file.exists():
            print(f"[WARN] Manifest not found: {task_id}")
            continue
        
        with open(manifest_file, "r") as f:
            manifest = json.load(f)
        
        print(f"[TASK] {task_id}")
        print(f"  Name: {manifest['task_name']}")
        print(f"  Expected Output: {manifest['expected_outputs'][0]}")
        
        # Check if status report exists
        status_report_dir = project_root / "coordination" / "status_reports"
        status_reports = list(status_report_dir.glob(f"*{task_id}*_status.json"))
        
        if not status_reports:
            print(f"  [WARN] No status report found")
            results.append({"task_id": task_id, "status": "NO_REPORT"})
            continue
        
        # Get latest status report
        latest_report = max(status_reports, key=lambda p: p.stat().st_mtime)
        with open(latest_report, "r") as f:
            status_report = json.load(f)
        
        print(f"  Status Report: {latest_report.name}")
        
        # Run verification
        verification_result = gateway.run_full_verification(status_report, manifest)
        
        if verification_result["status"] == "PASS":
            print(f"  [PASS] VERIFICATION PASSED")
            logger.log_event("VERIFICATION_PASSED", task_id, "PASS", verification_result)
            logger.log_event("TASK_APPROVED", task_id, "APPROVED", {})
            results.append({"task_id": task_id, "status": "APPROVED"})
        else:
            print(f"  [FAIL] VERIFICATION FAILED")
            print(f"     Errors: {verification_result['errors']}")
            logger.log_event("VERIFICATION_FAILED", task_id, "FAIL", verification_result["errors"])
            logger.log_event("TASK_REJECTED", task_id, "REJECTED", {
                "reason": "Verification failed",
                "errors": verification_result["errors"]
            })
            results.append({"task_id": task_id, "status": "REJECTED"})
        
        print()
    
    # Save pipeline results
    approved_count = sum(1 for r in results if r["status"] == "APPROVED")
    
    pipeline_results = {
        "pipeline_id": "WORLDPOP_PHASE1",
        "pipeline_name": "World Population Dashboard - Phase 1 ETL",
        "status": "COMPLETE" if approved_count == len(results) else "PARTIAL",
        "completed_at": None,
        "results": results,
        "summary": {
            "total_tasks": len(results),
            "approved": approved_count,
            "rejected": sum(1 for r in results if r["status"] == "REJECTED"),
            "pending": sum(1 for r in results if r["status"] == "NO_REPORT")
        }
    }
    
    pipeline_file = project_root / "coordination" / "pipeline_results.json"
    
    # Read existing results if they exist
    if pipeline_file.exists():
        with open(pipeline_file, "r") as f:
            existing = json.load(f)
        # Merge completed tasks
        if "completed_tasks" not in existing:
            existing["completed_tasks"] = []
        # Add new Phase 1 results
        pipeline_results["completed_tasks"] = existing.get("completed_tasks", [])
    
    with open(pipeline_file, "w") as f:
        json.dump(pipeline_results, f, indent=2)
    
    print("=" * 70)
    print(f"PHASE 1 COMPLETE: {approved_count}/{len(results)} tasks approved")
    print("=" * 70)
    print()
    print(f"Pipeline results saved to: {pipeline_file}")
    
    return pipeline_results


if __name__ == "__main__":
    verify_phase1_tasks()
