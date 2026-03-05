# 🎯 NEXT STEPS — World Population Dashboard

**Status:** Phase 0 Complete ✅  
**Date:** 5 Mar 2026  
**Current State:** Ready to test agent coordination

---

## ✅ What You've Completed

### **1. Folder Structure** ✓
- `config/` — 4 configuration files created
- `csv/raw/` — Ready for ETL outputs
- `csv/processed/` — Ready for transformed data
- `scripts/` — Ready for agent-generated code
- `qa_agents/` — Ready for QA agents
- `reports/` — Ready for HTML, MP4, GIF outputs
- `verification/` — Ready for verification layer

### **2. Configuration Files** ✓
- `settings.yaml` — Project settings
- `country_code_map.csv` — 50 countries mapped
- `validation_reference_data_5Mar2026.csv` — QA reference data
- `aggregate_regions_exclude.csv` — Regions to filter

### **3. Coordination System** ✓
- Local agent coordinator (quality gate)
- Background agent worker (autonomous implementer)
- Cloud agent executor (orchestrator runner)
- Task manifest system
- Audit trail logging
- Verification gateway

### **4. Test Scripts** ✓
- `run_full_workflow.py` — Full workflow orchestrator
- `test_coordination.py` — Quick coordination test

### **5. Pending Task** ✓
- `TASK_03_BUILD_VISUALIZATION_manifest.json` — Waiting for background agent

---

## 🚀 IMMEDIATE NEXT STEP: Test the Agent System

You have a task waiting in the queue! Let's test the full coordination flow.

### **Option A: Manual Test (Recommended First Time)**

**Terminal 1 — Background Agent:**
```powershell
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
python coordination/background_agent_worker.py
```

**What you'll see:**
```
======================================================================
BACKGROUND AGENT — LISTENING FOR TASKS
======================================================================

[AGENT] Found pending task: TASK_03_BUILD_VISUALIZATION
[AGENT] Task marked as in_progress: TASK_03_BUILD_VISUALIZATION
[EXECUTING] Build Population Bar Race Visualization
[AGENT] Visualization script created: scripts\03_build_visualization.py
[AGENT] Status report submitted
```

**Then check the results:**
```powershell
# Terminal 2
ls scripts/
cat scripts/03_build_visualization.py
cat coordination/pipeline_results.json
```

---

### **Option B: Full Workflow Test**

Keep Terminal 1 running with background agent, then in Terminal 2:

```powershell
python run_full_workflow.py
```

This will:
1. Submit the task
2. Background agent picks it up
3. Implements the code
4. Local agent verifies it
5. Approves or rejects
6. Logs everything to audit trail

**Expected Result:**
- ✅ `scripts/03_build_visualization.py` created
- ✅ Audit trail logged
- ✅ Pipeline results saved
- ✅ Status report generated

---

## 📋 After Testing: Next Implementation Phases

### **Phase 1: ETL Implementation** (1-2 days)

Create task manifests for:

1. **01_fetch_population.py**
   - Fetch from World Bank API
   - Save to `csv/raw/worldbank_population_raw_5Mar2026.csv`

2. **02_transform_rank_top50.py**
   - Filter top 50 countries
   - Rank by population
   - Save to `csv/processed/population_top50_1970_now_5Mar2026.csv`

3. **agent_data_qa.py**
   - Validate CSV schema
   - Check 50 rows/year
   - Verify rankings

**How to run:**
```powershell
# Create a run_phase1_tasks.py script
# Submit all 3 tasks to background agent
# Local agent verifies each one
```

---

### **Phase 2: Visualization** (1-2 days)

4. **03_build_visualization.py** ← ALREADY IN QUEUE!
   - Plotly bar race animation
   - SVG flag integration
   - SI number formatting

5. **04_generate_html_timestamped.py**
   - Export self-contained HTML
   - Timestamped filename

6. **agent_ui_qa.py** (Enhanced 7-Layer)
   - Layer 1: DOM data extraction
   - Layer 2: Known facts validation
   - Layer 3: Temporal consistency
   - Layer 4: OCR spot checks
   - Layer 5: Statistical sanity
   - Layer 6: Gold standard comparison
   - Layer 7: Visual rendering

---

### **Phase 3: Preview Generation** (1 day)

7. **05_generate_gif_mp4_preview.py**
   - Frame interpolation
   - MP4 encoding (H.264, 30 FPS)
   - GIF optimization (<10 MB)

---

### **Phase 4: Orchestrator** (1 day)

8. **orchestrator.py**
   - Run all 10 steps in sequence
   - Validation gates between each step
   - Comprehensive logging
   - Error handling

---

### **Phase 5: Verification Layer** (1 day)

Create verification modules:
- `verify_code_structure.py`
- `verify_outputs.py`
- `verify_visualization.py`
- `verify_orchestrator_flow.py`
- `verify_all.py`

---

### **Phase 6: Cloud + Telegram** (Day 2 feature)

- Run cloud agent executor
- Telegram bot integration
- Remote execution
- Notification system

---

## 💡 Understanding the Workflow

```
┌─────────────────────────────────────────────┐
│ YOU RUN: python run_full_workflow.py       │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ LOCAL AGENT:                                │
│ - Creates task manifest                     │
│ - Writes to task_queue/                     │
│ - Waits for status report                   │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ BACKGROUND AGENT (separate terminal):       │
│ - Polls task_queue/ every 5s                │
│ - Finds TASK_03_BUILD_VISUALIZATION         │
│ - Reads spec from manifest                  │
│ - Implements code exactly as specified      │
│ - Creates scripts/03_build_visualization.py │
│ - Writes status report                      │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ LOCAL AGENT:                                │
│ - Receives status report                    │
│ - Runs verification:                        │
│   ✓ Code syntax valid                       │
│   ✓ All functions present                   │
│   ✓ Docstrings exist                        │
│ - APPROVE or REJECT                         │
│ - Log to audit trail                        │
└─────────────────────────────────────────────┘
              ↓
         ✅ DONE!
```

---

## 🎯 Your Immediate Action Plan

**RIGHT NOW:**

1. **Open Terminal 1:**
   ```powershell
   cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
   python coordination/background_agent_worker.py
   ```
   *(Leave this running)*

2. **Watch Terminal 1:**
   - Within 5 seconds, it should detect `TASK_03_BUILD_VISUALIZATION`
   - It will create `scripts/03_build_visualization.py`
   - It will report completion

3. **Check Results (Terminal 2):**
   ```powershell
   ls scripts/
   cat scripts/03_build_visualization.py
   cat coordination/audit_trail/audit_*.log
   cat coordination/pipeline_results.json
   ```

4. **If it works:**
   - ✅ System is validated
   - ✅ Ready for Phase 1 implementation
   - ✅ Proceed to create Phase 1 task manifests

5. **If it doesn't work:**
   - Check Terminal 1 for errors
   - Check that `coordination/task_queue/` has the manifest file
   - Check Python path issues

---

## 📊 Success Criteria

After running the background agent, you should have:

- ✅ `scripts/03_build_visualization.py` exists
- ✅ File contains 4 functions:
  - `build_population_barrace()`
  - `apply_flag_labels()`
  - `apply_si_formatting()`
  - `validate_visualization_output()`
- ✅ Audit trail shows `TASK_APPROVED`
- ✅ Pipeline results shows `"passed": 1`

---

## 📞 Resources

- **Quick Test:** `python test_coordination.py`
- **Full Workflow:** `python run_full_workflow.py`
- **Background Agent:** `python coordination/background_agent_worker.py`
- **Detailed Guide:** `KICKSTART_GUIDE.md`
- **Project Overview:** `README.md`

---

**Ready? Open Terminal 1 and run the background agent NOW!** 🚀
