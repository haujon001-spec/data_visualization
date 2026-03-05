#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST AGENT COORDINATION SYSTEM
================================

This script helps you test the 3-tier agent coordination in one command.
It will show you what the background agent would create.

Usage:
  python test_coordination.py

This runs a simplified test to verify the system works.
"""

import sys
from pathlib import Path

# Add coordination to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from coordination.local_agent_coordinator import LocalAgentOrchestrator


def main():
    print("=" * 70)
    print("TESTING AGENT COORDINATION SYSTEM")
    print("=" * 70)
    print()
    print("This test will:")
    print("  1. Create a task manifest")
    print("  2. Show you how to run the background agent")
    print("  3. Demonstrate the full workflow")
    print()
    
    orchestrator = LocalAgentOrchestrator(project_root)
    
    # Create task manifest
    print("[STEP 1] Creating task manifest...")
    manifest = orchestrator.dispatcher.create_task_manifest(
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
        },
    )
    
    manifest_path = orchestrator.dispatcher.submit_task(manifest)
    print(f"Task manifest created: {manifest_path}")
    print()
    
    print("=" * 70)
    print("NEXT: RUN THE BACKGROUND AGENT")
    print("=" * 70)
    print()
    print("Open a NEW terminal and run:")
    print()
    print("  cd c:\\Users\\haujo\\projects\\DEV\\Data_visualization\\world_populations")
    print("  python coordination/background_agent_worker.py")
    print()
    print("The background agent will:")
    print("  - Detect the task manifest")
    print("  - Implement the code")
    print("  - Create scripts/03_build_visualization.py")
    print("  - Report back with status")
    print()
    print("Then check the results:")
    print("  - ls scripts/")
    print("  - cat coordination/audit_trail/audit_*.log")
    print("  - cat coordination/pipeline_results.json")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
