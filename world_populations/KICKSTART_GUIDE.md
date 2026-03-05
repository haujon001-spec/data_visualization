# 🚀 KICKSTART GUIDE — World Population Dashboard
**Date:** 5 Mar 2026  
**Goal:** Get the 3-tier agent coordination system running in 10 minutes

---

## 📋 **What You Currently Have**

✅ **Coordination System** (Complete):
- `coordination/local_agent_coordinator.py` — Local CI/CD gatekeeper
- `coordination/background_agent_worker.py` — Autonomous worker
- `coordination/cloud_agent_executor.py` — Cloud orchestrator
- `coordination/README.md`, `QUICKSTART.md`, `ARCHITECTURE.md`

✅ **Documentation** (Complete):
- All 6 Phase design documents in `docs/`
- Project plan with folder structure
- Implementation verification strategy

✅ **Workflow Script** (Just Fixed):
- `run_full_workflow.py` — Kickstart script (was Markdown, now Python)

---

## ❌ **What You Don'T Have Yet**

Missing folder structure and implementation files (this is intentional — the agents will create them):

```
world_populations/
├── config/          ❌ Not created yet
├── csv/             ❌ Not created yet
├── scripts/         ❌ Not created yet (agents will create this)
├── qa_agents/       ❌ Not created yet
├── reports/         ❌ Not created yet
└── verification/    ❌ Not created yet
```

**This is by design!** The background agent will create `scripts/` and files when you submit tasks.

---

## 🎯 **HOW THE SYSTEM WORKS**

```
┌─────────────────────────────────────────────────┐
│ YOU (Local Agent)                               │
│ - Creates task manifests                        │
│ - Verifies agent outputs                        │
│ - Approves or rejects work                      │
└─────────────────────────────────────────────────┘
         │                                ↑
         │ submits task manifest          │ submits status report
         ↓                                │
┌─────────────────────────────────────────────────┐
│ BACKGROUND AGENT (Autonomous Worker)            │
│ - Polls task_queue/ for pending tasks           │
│ - Implements code according to spec             │
│ - Creates outputs (scripts, CSV, HTML)          │
│ - Reports completion                            │
└─────────────────────────────────────────────────┘
```

---

## 🚦 **STEP-BY-STEP KICKSTART**

### **STEP 1: Start Background Agent** (Terminal 1)

Open **Terminal 1** and run:

```powershell
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
python coordination/background_agent_worker.py
```

**Expected Output:**
```
======================================================================
BACKGROUND AGENT — LISTENING FOR TASKS
======================================================================

[AGENT] No pending tasks, checking again in 5s...
[AGENT] No pending tasks, checking again in 5s...
```

**✅ LEAVE THIS RUNNING.** The agent is now polling for tasks.

---

### **STEP 2: Submit Your First Task** (Terminal 2)

Open **Terminal 2** and run:

```powershell
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
python run_full_workflow.py
```

**What Will Happen:**

1. **Local agent creates task manifest** → `coordination/task_queue/TASK_03_BUILD_VISUALIZATION_manifest.json`
2. **Background agent (Terminal 1) detects it** → Picks up the task
3. **Background agent implements the code** → Creates `scripts/03_build_visualization.py`
4. **Background agent reports completion** → Writes status report to `coordination/status_reports/`
5. **Local agent verifies the output** → Checks syntax, functions, etc.
6. **Local agent approves** → Logs to audit trail

**Expected Terminal 2 Output:**
```
======================================================================
WORLD POPULATION DASHBOARD — AGENT COORDINATION WORKFLOW
======================================================================

This workflow will:
  1. Create task manifests for all phases
  2. Submit to background agent for implementation
  3. Verify all outputs
  4. Run cloud agent for full orchestrator execution

======================================================================

[PHASE 1] Submitting tasks to background agent...

======================================================================
[TASK] TASK_03_BUILD_VISUALIZATION — Build Population Bar Race Visualization
======================================================================

[Step 1/5] Creating task manifest...
[LOCAL] Task submitted: TASK_03_BUILD_VISUALIZATION
  → Manifest: coordination\task_queue\TASK_03_BUILD_VISUALIZATION_manifest.json

[Step 2/5] Waiting for agent status report...
```

**Watch Terminal 1**, you'll see:
```
[AGENT] Found pending task: TASK_03_BUILD_VISUALIZATION
[AGENT] Task marked as in_progress: TASK_03_BUILD_VISUALIZATION
[EXECUTING] Build Population Bar Race Visualization
  Description: Implement animated bar race with flags and SI formatting
[AGENT] Visualization script created: scripts\03_build_visualization.py
[AGENT] Status report submitted: coordination\status_reports\AGENT_TASK_03_...
```

**Back in Terminal 2:**
```
[LOCAL] Status report received for TASK_03_BUILD_VISUALIZATION

[Step 3/5] Running verification suite...

[Step 4/5] ✅ VERIFICATION PASSED

[Step 5/5] ✅ TASK APPROVED
[AUDIT] TASK_APPROVED → APPROVED (TASK_03_BUILD_VISUALIZATION)

----------------------------------------------------------------------

[PHASE 2] Checking generated outputs...

✅ Script created: scripts\03_build_visualization.py
   Size: 1847 bytes

----------------------------------------------------------------------

[NEXT STEPS]

1. View audit trail:
   cat coordination/audit_trail/audit_*.log

2. View pipeline results:
   cat coordination/pipeline_results.json

3. View generated script:
   cat scripts/03_build_visualization.py
...
```

---

### **STEP 3: Check the Results**

#### **View the Generated Script:**

```powershell
cat scripts/03_build_visualization.py
```

You'll see the background agent created a complete Python script with all required functions!

#### **View Audit Trail:**

```powershell
cat coordination/audit_trail/audit_*.log
```

Output (JSON logs):
```json
{"timestamp": "2026-03-05T...", "event_type": "TASK_SUBMITTED", "task_id": "TASK_03_BUILD_VISUALIZATION", ...}
{"timestamp": "2026-03-05T...", "event_type": "STATUS_RECEIVED", "task_id": "TASK_03_BUILD_VISUALIZATION", ...}
{"timestamp": "2026-03-05T...", "event_type": "VERIFICATION_PASSED", "task_id": "TASK_03_BUILD_VISUALIZATION", ...}
{"timestamp": "2026-03-05T...", "event_type": "TASK_APPROVED", "task_id": "TASK_03_BUILD_VISUALIZATION", ...}
```

#### **View Pipeline Results:**

```powershell
cat coordination/pipeline_results.json
```

Output:
```json
{
  "passed": [
    {
      "task_id": "TASK_03_BUILD_VISUALIZATION",
      "status": "APPROVED",
      "verification": {...},
      "outputs": {...}
    }
  ],
  "failed": [],
  "summary": {
    "total_tasks": 1,
    "passed": 1,
    "failed": 0,
    "timestamp": "2026-03-05T..."
  }
}
```

---

### **STEP 4: Alternative — Run Local Agent Directly**

Instead of `run_full_workflow.py`, you can also run:

```powershell
python coordination/local_agent_coordinator.py
```

This runs the same task from the coordinator's main() function.

---

## 🔧 **TROUBLESHOOTING**

### **Issue: Background Agent Not Running**

**Symptom:** Terminal 2 says "TIMEOUT: Agent did not report back"

**Solution:** 
1. Check Terminal 1 is still running
2. Restart background agent:
   ```powershell
   python coordination/background_agent_worker.py
   ```

### **Issue: Task Queue Empty**

**Symptom:** Terminal 1 says "No pending tasks" even after submitting

**Solution:**
1. Check if manifest was created:
   ```powershell
   ls coordination/task_queue/
   ```
2. If empty, run `run_full_workflow.py` again

### **Issue: Scripts Folder Doesn't Exist**

**Symptom:** Background agent can't write to `scripts/`

**Solution:**
```powershell
mkdir scripts
```

The agent will now be able to create files there.

### **Issue: Verification Fails**

**Symptom:** Local agent rejects work with "VERIFICATION FAILED"

**Solution:**
1. Check the audit trail to see specific errors:
   ```powershell
   cat coordination/audit_trail/audit_*.log | Select-String "VERIFICATION_FAILED"
   ```
2. The background agent will automatically retry with corrections

---

## 📊 **WHAT HAPPENS NEXT?**

After verifying this system works, you can:

1. **Add More Tasks** — Edit `run_full_workflow.py` to include Phase 1, 2, 4, 5, 6
2. **Create Config Files** — Add `config/settings.yaml`, country mappings, etc.
3. **Implement QA Agents** — Background agent will create `qa_agents/` when you submit those tasks
4. **Run Cloud Agent** — Execute full orchestrator pipeline

---

## 🎯 **KEY DESIGN INSIGHTS**

✅ **No guessing** — Background agent implements exactly what manifest specifies  
✅ **No partial work** — Local agent verifies before approval  
✅ **Full audit trail** — Every decision logged  
✅ **Agent coordination** — Local agent = quality gate, background agent = worker  
✅ **Scalable** — Can run multiple background agents in parallel  

This is how **GitHub Actions, AWS CodePipeline, and Google Borg** work.

---

## 📝 **NEXT STEPS AFTER KICKSTART**

Once you've verified the system works:

1. ✅ **Phase 0:** Create folder structure
2. ✅ **Phase 1:** Submit ETL tasks (fetch + transform)
3. ✅ **Phase 2:** Submit visualization tasks
4. ✅ **Phase 3:** Submit QA agent tasks
5. ✅ **Phase 4:** Submit preview generation tasks
6. ✅ **Phase 5:** Submit orchestrator tasks
7. ✅ **Phase 6:** Integrate Telegram/OpenClaw

**Estimated Time:**
- Kickstart test: **5-10 minutes**
- Full Phase 1-6 implementation: **2-3 days** (agents do the work!)

---

**🚀 Ready? Run Terminal 1 and Terminal 2 now!**
