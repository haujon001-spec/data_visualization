#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WORLD POPULATION DASHBOARD — FULL WORKFLOW KICKSTARTER
========================================================

This script demonstrates the 3-tier agent coordination system:
- Local Agent (this script) — Creates task manifests and verifies outputs
- Background Agent — Autonomous worker that implements code
- Cloud Agent — Runs full orchestrator pipeline

Author: OpenClaw Coordination System
Date: 5 Mar 2026
"""

import sys
from pathlib import Path

# Add coordination to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from coordination.local_agent_coordinator import LocalAgentOrchestrator


def main():
    """
    Kickstart the full workflow using local > background > cloud orchestration.
    """
    print("=" * 70)
    print("WORLD POPULATION DASHBOARD — AGENT COORDINATION WORKFLOW")
    print("=" * 70)
    print()
    print("This workflow will:")
    print("  1. Create task manifests for all phases")
    print("  2. Submit to background agent for implementation")
    print("  3. Verify all outputs")
    print("  4. Run cloud agent for full orchestrator execution")
    print()
    print("=" * 70)
    print()

    # Initialize local agent orchestrator
    orchestrator = LocalAgentOrchestrator(project_root)

    # =====================================================================
    # PHASE 1: Submit tasks to background agent
    # =====================================================================
    
    print("[PHASE 1] Submitting tasks to background agent...")
    print()

    # Task 1: Build Visualization
    result_viz = orchestrator.process_task(
        task_id="TASK_03_BUILD_VISUALIZATION",
        task_name="Build Population Bar Race Visualization",
        phase=3,
        description="Implement animated bar race with flags and SI formatting",
        expected_outputs=["scripts/03_build_visualization.py"],
        expected_functions=[
            "build_population_barrace",
            "apply_flag_labels",
            "apply_si_formatting",
            "validate_visualization_output"
        ],
        success_criteria={
            "code_passes_syntax": True,
            "functions_present": True,
            "has_docstrings": True,
            "has_error_handling": True,
        },
    )

    if result_viz["status"] == "APPROVED":
        print("Task 03: Visualization — APPROVED")
    else:
        print("Task 03: Visualization — REJECTED")
        print(f"   Reason: {result_viz.get('errors', [])}")
        return

    print()
    print("-" * 70)
    print()

    # =====================================================================
    # PHASE 2: View results
    # =====================================================================
    
    print("[PHASE 2] Checking generated outputs...")
    print()
    
    # Check if script was created
    script_path = project_root / "scripts" / "03_build_visualization.py"
    if script_path.exists():
        print(f"Script created: {script_path}")
        print(f"   Size: {script_path.stat().st_size} bytes")
    else:
        print(f"Script not found: {script_path}")

    print()
    print("-" * 70)
    print()

    # =====================================================================
    # PHASE 3: Show next steps
    # =====================================================================
    
    print("[NEXT STEPS]")
    print()
    print("1. View audit trail:")
    print("   cat coordination/audit_trail/audit_*.log")
    print()
    print("2. View pipeline results:")
    print("   cat coordination/pipeline_results.json")
    print()
    print("3. View generated script:")
    print("   cat scripts/03_build_visualization.py")
    print()
    print("4. Add more tasks by modifying this script")
    print()
    print("5. Run background agent in separate terminal:")
    print("   python coordination/background_agent_worker.py")
    print()
    print("6. Run cloud agent for full orchestrator:")
    print("   python coordination/cloud_agent_executor.py")
    print()
    print("=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
