# Agent Coordination System — Quick Start Guide

**Goal:** Run the 3-tier agent system end-to-end in 5 minutes  
**Time:** ~5 minutes setup + agent execution time

---

## **Step 1: Verify The Structure** (1 min)

The following directories should exist:

```
c:\Users\haujo\projects\DEV\Data_visualization\world_populations\
├── coordination/
│   ├── local_agent_coordinator.py          ✓
│   ├── background_agent_worker.py          ✓
│   ├── cloud_agent_executor.py             ✓
│   ├── task_manifest.json                  ✓
│   ├── agent_status_report_schema.json     ✓
│   ├── README.md                           ✓
│   ├── task_queue/                         (created by system)
│   ├── status_reports/                     (created by system)
│   ├── cloud_results/                      (created by system)
│   ├── audit_trail/                        (created by system)
│   └── pipeline_results.json               (created by system)
│
├── scripts/
│   ├── orchestrator.py
│   ├── 01_fetch_population.py
│   ├── 02_transform_rank_top50.py
│   ├── 03_build_visualization.py
│   ├── 04_generate_html_timestamped.py
│   ├── 05_generate_gif_mp4_preview.py
│   └── ... (other scripts)
│
├── csv/
│   ├── raw/
│   └── processed/
│
└── reports/
    ├── html/
    ├── media/
    ├── qa/
    └── logs/
```

Check that all coordination files exist:

```bash
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
ls coordination/
```

---

## **Step 2: Run the Background Agent** (Terminal 1)

Open **Terminal 1** and start the background agent:

```bash
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
python coordination/background_agent_worker.py
```

**Expected output:**
```
======================================================================
BACKGROUND AGENT — LISTENING FOR TASKS
======================================================================

[AGENT] No pending tasks, checking again in 5s...
[AGENT] No pending tasks, checking again in 5s...
...
```

**Leave this running.** The agent will continuously poll for tasks.

---

## **Step 3: Run the Local Agent** (Terminal 2)

Open **Terminal 2** and run the local agent coordinator:

```bash
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
python coordination/local_agent_coordinator.py
```

**Expected behavior:**

```
======================================================================
LOCAL AGENT ORCHESTRATOR — PROCESSING PIPELINE
======================================================================

[Step 1/5] Creating task manifest...
[LOCAL] Task submitted: TASK_03_BUILD_VISUALIZATION
  → Manifest: .../task_queue/TASK_03_BUILD_VISUALIZATION_manifest.json

[Step 2/5] Waiting for agent status report...
```

**At this moment, watch Terminal 1** — the background agent should detect the task:

```
[AGENT] Found pending task: TASK_03_BUILD_VISUALIZATION
[AGENT] Task marked as in_progress: TASK_03_BUILD_VISUALIZATION
[EXECUTING] Build Population Bar Race Visualization
  Description: Implement animated visualization
[AGENT] Visualization script created: .../scripts/build_visualization.py
[AGENT] Status report submitted: .../status_reports/AGENT_TASK_03_...
```

**Back in Terminal 2**, the local agent receives the report:

```
[LOCAL] Status report received: TASK_03_BUILD_VISUALIZATION

[Step 3/5] Running verification suite...
[Step 4/5] ✅ VERIFICATION PASSED
[Local Agent logs checks passed]

[Step 5/5] ✅ TASK APPROVED
[AUDIT] TASK_APPROVED → APPROVED (TASK_03_BUILD_VISUALIZATION)
```

---

## **What Just Happened?**

1. **Local Agent (Terminal 2):** Created a precise task manifest
2. **Local Agent:** Submitted to `task_queue/`
3. **Background Agent (Terminal 1):** Detected the pending task
4. **Background Agent:** Implemented the code
5. **Background Agent:** Wrote status report to `status_reports/`
6. **Local Agent:** Received and verified the output
7. **Local Agent:** Approved the work and logged to audit trail

**All without any human intervention.**

---

## **Step 4: Check the Results**

### **View Audit Trail**

```bash
cat coordination/audit_trail/audit_*.log | more
```

Output:
```
{"timestamp": "2026-03-05T14:30:00Z", "event_type": "TASK_SUBMITTED", ...}
{"timestamp": "2026-03-05T14:30:05Z", "event_type": "STATUS_RECEIVED", ...}
{"timestamp": "2026-03-05T14:30:06Z", "event_type": "VERIFICATION_PASSED", ...}
{"timestamp": "2026-03-05T14:30:06Z", "event_type": "TASK_APPROVED", ...}
```

### **View Pipeline Results**

```bash
cat coordination/pipeline_results.json
```

Output:
```json
{
  "passed": [
    {
      "task_id": "TASK_03_BUILD_VISUALIZATION",
      "status": "APPROVED"
    }
  ],
  "failed": [],
  "summary": {
    "total_tasks": 1,
    "passed": 1,
    "failed": 0
  }
}
```

### **View Status Report**

```bash
cat coordination/status_reports/AGENT_TASK_03_*_status.json
```

Output:
```json
{
  "report_id": "REPORT_20260305_143000",
  "task_id": "TASK_03_BUILD_VISUALIZATION",
  "agent_type": "background_agent",
  "status": "completed",
  "duration_seconds": 5,
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

### **Check Generated Script**

```bash
cat scripts/build_visualization.py
```

The script was automatically created by the background agent!

---

## **Step 5: Add More Tasks**

To process multiple tasks, modify the coordinator to include all phases:

Edit `coordination/local_agent_coordinator.py` and replace the task list:

```python
tasks = [
    {
        "task_id": "TASK_03_BUILD_VISUALIZATION",
        "task_name": "Build Population Bar Race Visualization",
        ...
        "critical": True,
    },
    {
        "task_id": "TASK_04_GENERATE_HTML",
        "task_name": "Generate Timestamped HTML Report",
        ...
        "critical": True,
    },
    {
        "task_id": "TASK_05_GENERATE_PREVIEW",
        "task_name": "Generate MP4 and GIF Preview",
        ...
        "critical": False,
    },
]
```

Then run again:

```bash
python coordination/local_agent_coordinator.py
```

The system will process all tasks in sequence, stopping at any critical failure.

---

## **Step 6: Run Cloud Agent (Full Pipeline)**

Once background agent tasks are complete, run the cloud agent:

```bash
python coordination/cloud_agent_executor.py
```

**Expected output:**
```
======================================================================
CLOUD AGENT — EXECUTING ORCHESTRATOR
======================================================================

[Step 1/4] Running orchestrator.py...
[Step 2/4] Collecting outputs...
[Step 3/4] Verifying critical outputs...
[Step 4/4] Formatting results...

[COMPLETE] Cloud agent execution finished
  Status: success
  Ready for verification: true
```

Result saved to `coordination/cloud_results/cloud_result_*.json`

The local agent can then verify these results:

```python
orchestrator.verify_cloud_results(cloud_result)
```

---

## **Troubleshooting**

### **Background Agent Never Picks Up Tasks**

**Problem:** Terminal 1 keeps saying "No pending tasks"

**Solution:** 
1. Check that `task_queue/` directory exists
2. Check that Terminal 2 is actually submitting tasks
3. Verify manifest file was created: `ls coordination/task_queue/`

### **Local Agent Timeout**

**Problem:** Terminal 2 says "TIMEOUT: No status report received"

**Solution:**
1. Check that background agent (Terminal 1) is running
2. Check that status report was created: `ls coordination/status_reports/`
3. Increase timeout: change `timeout=300` to `timeout=600` in orchestrator call

### **Verification Fails**

**Problem:** Local agent rejects work with "Verification FAILED"

**Solution:**
1. Check audit trail: `cat coordination/audit_trail/audit_*.log`
2. Check status report: `cat coordination/status_reports/AGENT_*.json`
3. Look for specific errors in the `errors` field
4. Background agent will automatically retry

### **Permission Denied**

**Problem:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
```bash
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## **Performance**

Typical execution times:

| Task | Time |
|------|------|
| Task submission | < 1s |
| Status report wait | 1-5s |
| Verification suite | 1-2s |
| Full pipeline (5 tasks) | 30-60s |
| Cloud orchestrator | 60-300s |

**Total for full workflow:** ~5-10 minutes

---

## **Understanding the Flow**

```
┌────────────────────────────────────────────────────────────┐
│ LOCAL AGENT (Terminal 2)                                   │
│                                                            │
│ 1. Creates manifest for TASK_03                           │
│ 2. Writes to task_queue/                                  │
│ 3. Waits for status_reports/                              │
│    ↓                                                       │
│    (waiting...)                                            │
│    ↓                                                       │
│ 5. Receives status report                                 │
│ 6. Runs verification                                      │
│ 7. Logs to audit_trail/                                   │
│ 8. Returns APPROVED or REJECTED                           │
└────────────────────────────────────────────────────────────┘
         ↑ writes manifest             writes status report ↑
         │                                                   │
┌────────┴────────────────────────────────────────────────────┐
│ BACKGROUND AGENT (Terminal 1)                              │
│                                                            │
│ 1. Polls task_queue/ every 5s                             │
│ 2. Detects TASK_03 manifest                               │
│ 3. Reads manifest (specifications)                         │
│ 4. Implements code according to spec                       │
│ 5. Generates outputs (scripts/)                            │
│ 6. Creates status report                                   │
│ 7. Writes to status_reports/                              │
│ 8. Loops back to step 1                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## **Key Takeaways**

- ✅ **Deterministic:** Same input → same output
- ✅ **Autonomous:** No human intervention needed
- ✅ **Auditable:** Every decision logged
- ✅ **Verifiable:** Local agent approves all work
- ✅ **Traceable:** Full audit trail available
- ✅ **Scalable:** Works with multiple agents simultaneously
- ✅ **Resilient:** Handles errors gracefully

---

**Ready to try it? Start with Step 1!**
