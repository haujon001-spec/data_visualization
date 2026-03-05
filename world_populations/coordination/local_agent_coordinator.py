# -*- coding: utf-8 -*-
"""
LOCAL AGENT COORDINATOR
=======================

Purpose:
    Orchestrates autonomous background and cloud agents.
    - Submits task manifests to agents
    - Monitors task status
    - Runs verification layer on outputs
    - Approves (PASS) or rejects (FAIL) work
    - Maintains audit trail

Role: Chief Quality Officer + CI/CD Gatekeeper

Author: OpenClaw Coordination System
Date: 5 Mar 2026
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import traceback

# ========================================================================
# TASK DISPATCHER — Local agent submits work to background agents
# ========================================================================

class TaskDispatcher:
    """
    Creates and dispatches task manifests to autonomous agents.
    """

    def __init__(self, project_root: Path, coordination_dir: str = "coordination"):
        self.project_root = project_root
        self.coordination_dir = project_root / coordination_dir
        self.task_queue_dir = self.coordination_dir / "task_queue"
        self.task_queue_dir.mkdir(parents=True, exist_ok=True)

    def create_task_manifest(
        self,
        task_id: str,
        task_name: str,
        phase: int,
        description: str,
        expected_outputs: List[str],
        expected_functions: List[str],
        success_criteria: Dict[str, Any],
        assigned_to: str = "background_agent",
    ) -> Dict:
        """
        Create a task manifest that specifies exactly what agents must do.

        Returns:
            Task manifest dict.
        """
        manifest = {
            "task_id": task_id,
            "task_name": task_name,
            "phase": phase,
            "description": description,
            "created_by": "local_agent",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "pending",
            "assigned_to": assigned_to,
            "priority": "high",
            "expected_outputs": expected_outputs,
            "expected_functions": expected_functions,
            "success_criteria": success_criteria,
        }
        return manifest

    def submit_task(self, manifest: Dict) -> Path:
        """
        Write task manifest to disk, making it visible to background agent.

        Returns:
            Path to submitted manifest.
        """
        task_id = manifest["task_id"]
        manifest_file = self.task_queue_dir / f"{task_id}_manifest.json"

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        print(f"[LOCAL] Task submitted: {task_id}")
        print(f"  → Manifest: {manifest_file}")
        return manifest_file

    def list_pending_tasks(self) -> List[Dict]:
        """List all pending tasks in the queue."""
        pending = []
        for manifest_file in self.task_queue_dir.glob("*_manifest.json"):
            with open(manifest_file, "r") as f:
                manifest = json.load(f)
                if manifest["status"] == "pending":
                    pending.append(manifest)
        return pending


# ========================================================================
# STATUS MONITOR — Local agent waits for agent status reports
# ========================================================================

class StatusMonitor:
    """
    Monitors status reports from background/cloud agents.
    Waits for agents to complete work and report back.
    """

    def __init__(self, project_root: Path, coordination_dir: str = "coordination"):
        self.project_root = project_root
        self.coordination_dir = project_root / coordination_dir
        self.status_report_dir = self.coordination_dir / "status_reports"
        self.status_report_dir.mkdir(parents=True, exist_ok=True)

    def wait_for_report(
        self, task_id: str, timeout_seconds: int = 300
    ) -> Dict | None:
        """
        Wait for background agent to submit a status report for this task.
        Returns status report dict or None if timeout.
        """
        import time

        start = time.time()
        while time.time() - start < timeout_seconds:
            # Look for status report matching this task
            for report_file in self.status_report_dir.glob(f"**/*_{task_id}_*_status.json"):
                with open(report_file, "r") as f:
                    report = json.load(f)
                    if report.get("task_id") == task_id:
                        print(f"[LOCAL] Status report received for {task_id}")
                        return report

            time.sleep(2)  # Poll every 2 seconds

        print(f"[LOCAL] TIMEOUT: No status report for {task_id} after {timeout_seconds}s")
        return None

    def save_report(self, report: Dict) -> Path:
        """Save incoming status report to disk."""
        task_id = report["task_id"]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_file = (
            self.status_report_dir / f"AGENT_{task_id}_{timestamp}_status.json"
        )

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"[LOCAL] Report saved: {report_file}")
        return report_file


# ========================================================================
# VERIFICATION GATEWAY — Local agent verifies outputs
# ========================================================================

class VerificationGateway:
    """
    Runs verification suite on agent outputs.
    - Code structure   - File outputs
    - Function presence & correctness
    - Syntax & import validity
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def verify_code_structure(self, script_path: Path) -> Dict:
        """Verify Python code structure and syntax."""
        results = {"passed": True, "errors": []}

        if not script_path.exists():
            results["passed"] = False
            results["errors"].append(f"Script not found: {script_path}")
            return results

        # Check syntax
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                code = f.read()
            compile(code, str(script_path), "exec")
        except SyntaxError as e:
            results["passed"] = False
            results["errors"].append(f"Syntax error at line {e.lineno}: {e.msg}")
            return results

        # Check imports
        import ast
        try:
            tree = ast.parse(code)
            # Extract all function definitions
            functions = [
                node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
            ]
            results["functions_found"] = functions
        except Exception as e:
            results["passed"] = False
            results["errors"].append(f"AST parsing failed: {str(e)}")
            return results

        return results

    def verify_outputs_exist(self, expected_outputs: List[str]) -> Dict:
        """Verify all expected output files exist."""
        results = {"passed": True, "missing": [], "found": []}

        for output_path in expected_outputs:
            full_path = self.project_root / output_path
            if full_path.exists():
                results["found"].append(output_path)
            else:
                results["passed"] = False
                results["missing"].append(output_path)

        return results

    def verify_functions(self, script_path: Path, required_functions: List[str]) -> Dict:
        """Verify all required functions are present."""
        results = {"passed": True, "missing": [], "found": []}

        if not script_path.exists():
            results["passed"] = False
            results["missing"] = required_functions
            return results

        import ast
        with open(script_path, "r", encoding="utf-8") as f:
            code = f.read()

        try:
            tree = ast.parse(code)
            defined_functions = {
                node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
            }

            for fn in required_functions:
                if fn in defined_functions:
                    results["found"].append(fn)
                else:
                    results["passed"] = False
                    results["missing"].append(fn)
        except Exception as e:
            results["passed"] = False
            results["errors"] = [str(e)]

        return results

    def run_full_verification(
        self, status_report: Dict, manifest: Dict
    ) -> Dict:
        """
        Run complete verification against manifest requirements.
        Returns PASS or FAIL with detailed report.
        """
        verification_result = {
            "status": "PASS",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {},
            "errors": [],
        }

        # Check 1: Outputs exist
        if "outputs" in status_report:
            output_paths = list(status_report["outputs"].keys())
            outputs_check = self.verify_outputs_exist(output_paths)
            verification_result["checks"]["outputs_exist"] = outputs_check
            if not outputs_check["passed"]:
                verification_result["status"] = "FAIL"
                verification_result["errors"].append("Some outputs missing")

        # Check 2: Code syntax
        if "outputs" in status_report and "scripts" in str(status_report["outputs"]):
            for output_name in status_report["outputs"]:
                if output_name.endswith(".py"):
                    script_path = self.project_root / status_report["outputs"][output_name][
                        "path"
                    ]
                    syntax_check = self.verify_code_structure(script_path)
                    verification_result["checks"][f"syntax_{output_name}"] = syntax_check
                    if not syntax_check["passed"]:
                        verification_result["status"] = "FAIL"
                        verification_result["errors"].extend(syntax_check.get("errors", []))

        # Check 3: Required functions
        if "expected_functions" in manifest:
            for output in manifest.get("expected_outputs", []):
                if output.endswith(".py"):
                    script_path = self.project_root / output
                    func_check = self.verify_functions(
                        script_path, manifest["expected_functions"]
                    )
                    verification_result["checks"]["functions"] = func_check
                    if not func_check["passed"]:
                        verification_result["status"] = "FAIL"
                        verification_result["errors"].extend(func_check.get("missing", []))

        return verification_result


# ========================================================================
# AUDIT TRAIL LOGGER — Records all decisions for accountability
# ========================================================================

class AuditTrailLogger:
    """
    Maintains comprehensive audit trail of all agent interactions.
    """

    def __init__(self, project_root: Path, coordination_dir: str = "coordination"):
        self.project_root = project_root
        self.audit_dir = project_root / coordination_dir / "audit_trail"
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.audit_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"

    def log_event(self, event_type: str, task_id: str, result: str, details: Dict | str):
        """
        Log an event to audit trail.
        Event types: TASK_SUBMITTED, STATUS_RECEIVED, VERIFICATION_PASSED, VERIFICATION_FAILED, TASK_APPROVED, TASK_REJECTED
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "task_id": task_id,
            "result": result,
            "details": details,
        }

        # Write to audit file
        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        print(f"[AUDIT] {event_type} → {result} ({task_id})")

    def generate_audit_summary(self) -> Dict:
        """Generate summary of all logged events."""
        events = []
        if self.audit_file.exists():
            with open(self.audit_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))

        return {"total_events": len(events), "events": events}


# ========================================================================
# MAIN ORCHESTRATOR — Coordinates the full workflow
# ========================================================================

class LocalAgentOrchestrator:
    """
    Main orchestrator: coordinates dispatching, monitoring, verification, and approval.

    Workflow:
    1. Create task manifest
    2. Submit to background agent
    3. Wait for status report
    4. Run verification
    5. PASS → approve and log
    6. FAIL → reject, send feedback, and log
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dispatcher = TaskDispatcher(project_root)
        self.monitor = StatusMonitor(project_root)
        self.verifier = VerificationGateway(project_root)
        self.audit = AuditTrailLogger(project_root)

    def process_task(
        self,
        task_id: str,
        task_name: str,
        phase: int,
        description: str,
        expected_outputs: List[str],
        expected_functions: List[str],
        success_criteria: Dict,
        timeout: int = 300,
    ) -> Dict:
        """
        Complete workflow for one task:
        dispatch → wait → verify → approve/reject
        """
        print("\n" + "=" * 70)
        print(f"[TASK] {task_id} — {task_name}")
        print("=" * 70)

        # Step 1: Create and submit task manifest
        print("\n[Step 1/5] Creating task manifest...")
        manifest = self.dispatcher.create_task_manifest(
            task_id=task_id,
            task_name=task_name,
            phase=phase,
            description=description,
            expected_outputs=expected_outputs,
            expected_functions=expected_functions,
            success_criteria=success_criteria,
        )
        manifest_path = self.dispatcher.submit_task(manifest)
        self.audit.log_event("TASK_SUBMITTED", task_id, "OK", {"manifest": str(manifest_path)})

        # Step 2: Wait for status report from agent
        print("\n[Step 2/5] Waiting for agent status report...")
        status_report = self.monitor.wait_for_report(task_id, timeout_seconds=timeout)
        if not status_report:
            self.audit.log_event("STATUS_RECEIVED", task_id, "TIMEOUT", {})
            return {
                "task_id": task_id,
                "status": "REJECTED",
                "reason": "Agent did not report back within timeout",
            }

        self.audit.log_event("STATUS_RECEIVED", task_id, "OK", status_report)

        # Step 3: Run verification
        print("\n[Step 3/5] Running verification suite...")
        verification = self.verifier.run_full_verification(status_report, manifest)

        # Step 4 & 5: Decide approval
        if verification["status"] == "PASS":
            print("\n[Step 4/5] ✅ VERIFICATION PASSED")
            self.audit.log_event(
                "VERIFICATION_PASSED", task_id, "PASS", verification["checks"]
            )
            print("\n[Step 5/5] ✅ TASK APPROVED")
            self.audit.log_event("TASK_APPROVED", task_id, "APPROVED", {})
            return {
                "task_id": task_id,
                "status": "APPROVED",
                "verification": verification,
                "outputs": status_report.get("outputs", {}),
            }
        else:
            print("\n[Step 4/5] ❌ VERIFICATION FAILED")
            print(f"  Errors: {verification['errors']}")
            self.audit.log_event(
                "VERIFICATION_FAILED", task_id, "FAIL", verification["errors"]
            )
            print("\n[Step 5/5] ❌ TASK REJECTED")
            feedback = {
                "reason": "Verification failed",
                "errors": verification["errors"],
                "checks": verification["checks"],
            }
            self.audit.log_event("TASK_REJECTED", task_id, "REJECTED", feedback)
            return {"task_id": task_id, "status": "REJECTED", "feedback": feedback}

    def process_pipeline(self, tasks: List[Dict]) -> Dict:
        """
        Process multiple tasks in sequence.
        Each task is approved before next begins.
        """
        print("\n" + "=" * 70)
        print("LOCAL AGENT ORCHESTRATOR — PROCESSING PIPELINE")
        print("=" * 70)

        results = {"passed": [], "failed": [], "summary": {}}

        for task_config in tasks:
            result = self.process_task(**task_config)

            if result["status"] == "APPROVED":
                results["passed"].append(result)
            else:
                results["failed"].append(result)

            # If critical task fails, abort
            if result["status"] == "REJECTED" and task_config.get("critical", True):
                print(f"\n[ABORT] Critical task failed: {task_config['task_id']}")
                break

        results["summary"] = {
            "total_tasks": len(tasks),
            "passed": len(results["passed"]),
            "failed": len(results["failed"]),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Save results
        results_file = self.project_root / "coordination" / "pipeline_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n[COMPLETE] Pipeline summary: {results['summary']}")
        return results


# ========================================================================
# MAIN ENTRY POINT
# ========================================================================

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]

    orchestrator = LocalAgentOrchestrator(project_root)

    # Example: Process Phase 3 (Visualization)
    tasks = [
        {
            "task_id": "TASK_03_BUILD_VISUALIZATION",
            "task_name": "Build Population Bar Race Visualization",
            "phase": 3,
            "description": "Implement animated bar race visualization",
            "expected_outputs": ["scripts/build_visualization.py"],
            "expected_functions": [
                "build_population_barrace",
                "apply_flag_labels",
                "apply_si_formatting",
            ],
            "success_criteria": {
                "code_passes_syntax": True,
                "functions_present": True,
                "has_error_handling": True,
            },
            "critical": True,
        },
    ]

    results = orchestrator.process_pipeline(tasks)
    print(json.dumps(results, indent=2))
