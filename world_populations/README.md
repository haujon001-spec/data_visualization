# World Population Dashboard

**Status:** Phase 0 Complete — Ready for Agent Implementation  
**Date:** 5 Mar 2026

## 🎯 Project Goal

Build a 50-year (1970–2026) world population dashboard with:
- Automated ETL from World Bank API
- Animated bar race visualization with country flags
- 7-layer QA validation system
- GIF/MP4 previews for LinkedIn
- Full agent orchestration

---

## ✅ What's Ready

### **Folder Structure** ✓
```
world_populations/
├── config/               ✓ Settings + country mappings
├── coordination/         ✓ 3-tier agent system
├── csv/raw/             ✓ Ready for ETL outputs
├── csv/processed/       ✓ Ready for cleaned data
├── scripts/             ✓ Ready for implementation
├── qa_agents/           ✓ Ready for QA agents
├── reports/             ✓ Ready for outputs
└── verification/        ✓ Ready for verification layer
```

### **Configuration Files** ✓
- `config/settings.yaml` — Project settings
- `config/country_code_map.csv` — ISO-3 to ISO-2 mapping (50 countries)
- `config/validation_reference_data_5Mar2026.csv` — QA validation reference
- `config/aggregate_regions_exclude.csv` — Regions to filter out

### **Coordination System** ✓
- Local Agent — Creates tasks, verifies outputs
- Background Agent — Autonomous code implementation
- Cloud Agent — Full orchestrator execution
- Full audit trail + verification gateway

---

## 🚀 Next Steps

### **STEP 1: Test Agent Coordination** (5 minutes)

**Terminal 1 — Start Background Agent:**
```powershell
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
python coordination/background_agent_worker.py
```

**Terminal 2 — Run Test:**
```powershell
python test_coordination.py
```

This will create a task manifest and show you how the system works.

---

### **STEP 2: Install Dependencies** (5 minutes)

```powershell
pip install -r requirements.txt
playwright install chromium
```

---

### **STEP 3: Implement Phase 1 — ETL** (Day 1)

The background agent will create these scripts when you submit tasks:

**Task 1: Data Fetching**
- Input: World Bank API
- Output: `scripts/01_fetch_population.py`
- CSV: `csv/raw/worldbank_population_raw_5Mar2026.csv`

**Task 2: Data Transformation**
- Input: Raw CSV
- Output: `scripts/02_transform_rank_top50.py`
- CSV: `csv/processed/population_top50_1970_now_5Mar2026.csv`

**Task 3: Data QA Agent**
- Output: `qa_agents/agent_data_qa.py`
- Report: `reports/qa/data_qa_report_5Mar2026.json`

**How to Run:**
```powershell
# Terminal 1: Background agent (keep running)
python coordination/background_agent_worker.py

# Terminal 2: Submit Phase 1 tasks
python run_phase1_tasks.py
```

---

### **STEP 4: Implement Phase 2 — Visualization** (Day 2)

**Task 4: Build Visualization**
- Output: `scripts/03_build_visualization.py`
- Features: SVG flags, SI formatting, bar race animation

**Task 5: Generate HTML**
- Output: `scripts/04_generate_html_timestamped.py`
- HTML: `reports/html/population_bar_race_5Mar2026.html`

**Task 6: UI QA Agent** (7-Layer Validation)
- Output: `qa_agents/agent_ui_qa.py`
- Report: `reports/qa/ui_qa_report_5Mar2026.md`
- Screenshots: `reports/screenshots/`

---

### **STEP 5: Implement Phase 3 — Previews** (Day 3)

**Task 7: Preview Generation**
- Output: `scripts/05_generate_gif_mp4_preview.py`
- MP4: `reports/media/population_preview_5Mar2026.mp4`
- GIF: `reports/media/population_preview_5Mar2026.gif`

---

### **STEP 6: Implement Orchestrator** (Day 4)

**Task 8: Orchestrator**
- Output: `scripts/orchestrator.py`
- Runs full pipeline: ETL → QA → Viz → HTML → Preview
- Logs: `reports/logs/orchestrator_log_5Mar2026.txt`

---

### **STEP 7: Run Cloud Agent** (Day 5)

```powershell
python coordination/cloud_agent_executor.py
```

This executes the full orchestrator and returns results to local agent for verification.

---

## 📊 Architecture Summary

```
YOU (Local Agent)
   ↓ creates task manifest
BACKGROUND AGENT
   ↓ implements code
LOCAL AGENT VERIFIES
   ↓ approves/rejects
CLOUD AGENT EXECUTES
   ↓ runs orchestrator
LOCAL AGENT VERIFIES FINAL OUTPUT
   ↓ publishes
COMPLETE!
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `run_full_workflow.py` | Main workflow entry point |
| `test_coordination.py` | Test agent coordination |
| `coordination/local_agent_coordinator.py` | Local agent (you) |
| `coordination/background_agent_worker.py` | Worker agent |
| `coordination/cloud_agent_executor.py` | Cloud orchestrator |
| `KICKSTART_GUIDE.md` | Detailed walkthrough |

---

## 🎓 Understanding the System

**Traditional Approach:**
- You write all code manually
- Hope it works
- Debug when it fails

**Agent Orchestration Approach:**
- You define task specifications
- Agents implement according to spec
- Local agent verifies before approval
- Only correct code proceeds
- Full audit trail maintained

**This is how GitHub Actions, AWS CodePipeline, and Google Borg work.**

---

## ⚡ Quick Commands

```powershell
# Test coordination system
python test_coordination.py

# Run background agent
python coordination/background_agent_worker.py

# Run full workflow
python run_full_workflow.py

# Check results
cat coordination/audit_trail/audit_*.log
cat coordination/pipeline_results.json
ls scripts/

# Install dependencies
pip install -r requirements.txt
```

---

## 📞 Support

- Detailed guide: `KICKSTART_GUIDE.md`
- Architecture: `coordination/ARCHITECTURE.md`
- Quick start: `coordination/QUICKSTART.md`
- Phase designs: `docs/Phase*_*.md`

---

**Ready to start? Run `python test_coordination.py` to test the system!**
