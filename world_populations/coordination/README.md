# Agent Coordination System — Local + Background + Cloud Agents

**Status:** Production-ready implementation  
**Date:** 5 Mar 2026  
**Purpose:** Autonomous 3-tier agent architecture for deterministic, auditable pipeline execution

---

## **Quick Overview**

This system enables **anonymous autonomous agents** to collaborate without human intervention while maintaining **full auditability and control** through a local agent quality gate.

### **The Three Tiers**

```
┌──────────────────────────────────────────────────────────┐
│ LOCAL AGENT (VS Code)                                    │
│ - Chief Quality Officer                                  │
│ - CI/CD Gatekeeper                                       │
│ - Creates task manifests                                 │
│ - Verifies outputs                                       │
│ - Approves (PASS) or rejects (FAIL)                      │
│ - Maintains audit trail                                  │
└──────────────────────────────────────────────────────────┘
         ↑                                   ↓
    STATUS REPORT                   TASK MANIFEST
         ↑                                   ↓
┌──────────────────────────────────────────────────────────┐
│ BACKGROUND AGENT (Autonomous)                            │
│ - Polls for pending tasks                                │
│ - Implements code according to spec                      │
│ - Generates outputs                                      │
│ - Reports completion with outputs                        │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ CLOUD AGENT (Autonomous)                                 │
│ - Receives orchestrator call from local agent            │
│ - Runs full pipeline end-to-end                          │
│ - Collects and verifies outputs                          │
│ - Returns results to local agent                         │
└──────────────────────────────────────────────────────────┘
```

---

## **File Structure**

```
coordination/
├── local_agent_coordinator.py       # Local agent main controller
├── background_agent_worker.py       # Background agent executable
├── cloud_agent_executor.py          # Cloud agent executable
├── task_manifest.json               # Example task spec
├── agent_status_report_schema.json  # Status report schema
│
├── task_queue/                      # Tasks submitted by local agent
│   ├── TASK_03_BUILD_VISUALIZATION_manifest.json
│   └── ...
│
├── status_reports/                  # Reports from agents
│   ├── AGENT_TASK_03_20260305_143000_status.json
│   └── ...
│
├── cloud_results/                   # Cloud agent execution results
│   ├── cloud_result_20260305_143000.json
│   └── ...
│
├── audit_trail/                     # All decisions logged
│   ├── audit_20260305.log
│   └── ...
│
└── pipeline_results.json            # Final pipeline summary
```

---

## **How It Works**

### **1. Local Agent Submits Work** 

The local agent (you in VS Code) creates a task manifest specifying **exactly what** must be implemented:

```python
from pathlib import Path
from coordination.local_agent_coordinator import LocalAgentOrchestrator

project_root = Path(__file__).resolve().parents[1]
orchestrator = LocalAgentOrchestrator(project_root)

result = orchestrator.process_task(
    task_id="TASK_03_BUILD_VISUALIZATION",
    task_name="Build Population Bar Race",
    phase=3,
    description="Implement animated visualization",
    expected_outputs=["scripts/build_visualization.py"],
    expected_functions=["build_population_barrace", "apply_flag_labels"],
    success_criteria={"code_passes_syntax": True, "functions_present": True},
)
```

**What happens:**
1. Local agent creates `TASK_03_BUILD_VISUALIZATION_manifest.json`
2. Manifest is written to `task_queue/`
3. Local agent awaits status report (blocking)

### **2. Background Agent Picks Up Task** 

The background agent (running autonomously) polls the task queue:

```python
from pathlib import Path
from coordination.background_agent_worker import BackgroundAgent

project_root = Path(__file__).resolve().parents[1]
agent = BackgroundAgent(project_root)
agent.run()  # Runs forever, polling for tasks
```

**What happens:**
1. Agent finds `TASK_03_BUILD_VISUALIZATION_manifest.json`
2. Agent marks task as `in_progress`
3. Agent implements the code according to manifest spec
4. Agent generates all expected outputs
5. Agent creates a status report with file paths and validation results
6. Agent writes status report to `status_reports/`

### **3. Local Agent Verifies Output** 

Upon receiving status report, local agent runs verification:

```python
# Inside local_agent_coordinator.py
verification = self.verifier.run_full_verification(status_report, manifest)

# Checks performed:
# - All expected files exist
# - Code syntax is valid
# - All required functions are present
# - Imports work correctly
# - No undefined references
```

**Possible outcomes:**

- ✅ **PASS**: All checks pass → Task approved, proceeds to next step
- ❌ **FAIL**: Any check fails → Task rejected, sent back to background agent with error details

### **4. Audit Trail Records Everything** 

Every decision is logged:

```json
{
  "timestamp": "2026-03-05T14:30:00Z",
  "event_type": "TASK_SUBMITTED",
  "task_id": "TASK_03_BUILD_VISUALIZATION",
  "result": "OK",
  "details": {...}
}
```

---

## **Running the System**

### **Option 1: Run Full Pipeline (Local Agent Orchestrates Everything)**

```bash
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
python coordination/local_agent_coordinator.py
```

**What happens:**
1. Local agent creates task manifests for all phases
2. Local agent submits them to task queue
3. (Background agent must be running to pick them up)
4. Local agent waits for status reports
5. Local agent verifies outputs
6. Local agent approves/rejects
7. Audit trail is written

---

### **Option 2: Run Background Agent (in separate terminal)**

```bash
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
python coordination/background_agent_worker.py
```

**What happens:**
- Agent continuously polls `task_queue/`
- When a task arrives, agent implements it
- Agent submits status report to `status_reports/`
- Waiting for next task

**Run this in a separate terminal while local agent is running.**

---

### **Option 3: Run Cloud Agent (Orchestrator Execution)**

```bash
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
python coordination/cloud_agent_executor.py
```

**What happens:**
1. Cloud agent executes `orchestrator.py`
2. Collects all outputs (HTML, MP4, GIF, CSV, logs)
3. Verifies critical outputs exist
4. Saves result to `cloud_results/`
5. Local agent will verify the result

---

## **Key Design Principles**

### **1. Deterministic**
Same input → same output, every time. No randomness or side effects.

### **2. Auditable**
Every decision is logged with timestamp, agent type, task ID, and result.

### **3. Verifiable**
Local agent **must verify** before any work is considered complete.

### **4. Autonomous**
Agents work without human intervention. No debugging, no manual fixes.

### **5. Contract-Based**
Tasks are specs (manifests), not descriptions. Agents know exact requirements.

---

## **Task Manifest Structure**

A task manifest defines **everything** an agent must implement:

```json
{
  "task_id": "TASK_03_BUILD_VISUALIZATION",
  "task_name": "Build Population Bar Race Visualization",
  "expected_outputs": ["scripts/build_visualization.py"],
  "expected_functions": [
    "build_population_barrace",
    "apply_flag_labels",
    "apply_si_formatting"
  ],
  "success_criteria": {
    "code_passes_syntax": true,
    "functions_present": true,
    "has_docstrings": true,
    "has_error_handling": true
  }
}
```

---

## **Status Report Structure**

After completing a task, agent submits:

```json
{
  "report_id": "REPORT_20260305_143000",
  "task_id": "TASK_03_BUILD_VISUALIZATION",
  "agent_type": "background_agent",
  "status": "completed",
  "completed_at": "2026-03-05T14:30:00Z",
  "duration_seconds": 45,
  "outputs": {
    "build_visualization.py": {
      "path": "scripts/build_visualization.py",
      "size_bytes": 2048,
      "exists": true
    }
  },
  "implemented_functions": [
    "build_population_barrace",
    "apply_flag_labels",
    "apply_si_formatting",
    "validate_visualization_output"
  ],
  "code_quality": {
    "syntax_valid": true,
    "can_import": true
  },
  "ready_for_verification": true
}
```

---

## **Verification Checks**

Local agent runs these checks on every output:

| Check | Purpose |
|-------|---------|
| `outputs_exist` | All expected files exist |
| `syntax_valid` | Python code compiles |
| `can_import` | Module can be imported |
| `functions_present` | All required functions defined |
| `no_undefined_refs` | No missing imports |
| `docstrings_present` | Functions documented |
| `error_handling` | Proper exception handling |

**If any check fails → Task is REJECTED**

---

## **Approval Logic**

```
┌─────────────────────┐
│  Status Report      │
│  from Agent         │
└──────────┬──────────┘
           ↓
┌─────────────────────────────┐
│  Run Verification Suite     │
│  - Code structure           │
│  - Outputs exist            │
│  - Functions present        │
│  - Syntax valid             │
└──────────┬──────────────────┘
           ↓
       ┌───────────┐
       │ All Pass? │
       └──┬──────┬─┘
          │ YES  │ NO
          ↓      ↓
       [PASS]  [FAIL]
          ↓      ↓
        [APPROVED] [REJECTED]
```

---

## **Audit Trail Example**

```
[2026-03-05 14:30:00] TASK_SUBMITTED → OK (TASK_03_BUILD_VISUALIZATION)
[2026-03-05 14:30:05] STATUS_RECEIVED → OK (TASK_03_BUILD_VISUALIZATION)
[2026-03-05 14:30:06] VERIFICATION_PASSED → PASS (all checks)
[2026-03-05 14:30:06] TASK_APPROVED → APPROVED (TASK_03_BUILD_VISUALIZATION)

[2026-03-05 14:35:00] TASK_SUBMITTED → OK (TASK_04_GENERATE_HTML)
[2026-03-05 14:35:10] STATUS_RECEIVED → OK (TASK_04_GENERATE_HTML)
[2026-03-05 14:35:11] VERIFICATION_FAILED → FAIL (missing function: apply_si_formatting)
[2026-03-05 14:35:11] TASK_REJECTED → REJECTED (TASK_04_GENERATE_HTML)
```

---

## **Error Handling**

When a task fails verification:

1. **Local agent logs the error** to audit trail
2. **Status marked as REJECTED** with detailed error list
3. **Feedback sent back to background agent** (via manifest update)
4. **Background agent retries** with corrected code
5. **Process repeats until PASS**

---

## **Integration with Orchestrator**

When cloud agent is ready:

```python
from coordination.local_agent_coordinator import LocalAgentOrchestrator

orchestrator = LocalAgentOrchestrator(project_root)

# Invoke cloud agent
result = orchestrator.invoke_cloud_orchestrator()

# Local agent verifies cloud results
verification = orchestrator.verify_cloud_results(result)

if verification["status"] == "PASS":
    # Publish outputs
    orchestrator.approve_cloud_results()
else:
    # Reject and handle errors
    orchestrator.reject_cloud_results(verification["errors"])
```

---

## **Next Steps**

1. **Start background agent**: `python coordination/background_agent_worker.py` (in separate terminal)
2. **Run local agent**: `python coordination/local_agent_coordinator.py`
3. **Check audit trail**: `coordination/audit_trail/audit_*.log`
4. **Review pipeline results**: `coordination/pipeline_results.json`

---

## **Summary**

You now have a **fully autonomous, deterministic, auditable 3-tier agent system** that:

- ✅ Creates precise task specifications (manifests)
- ✅ Dispatches work to autonomous agents
- ✅ Verifies all outputs before approval
- ✅ Rejects invalid work immediately
- ✅ Logs every decision forever
- ✅ Requires NO human intervention once started
- ✅ Can be audited end-to-end at any time
- ✅ Handles errors deterministically
- ✅ Scales from 1 task to 100+ tasks
- ✅ Works with background + cloud agents simultaneously

This is the **same architecture used by** GitHub Actions, Google Borg, and AWS CodePipeline — adapted for AI agents.
