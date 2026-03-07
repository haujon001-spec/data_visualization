Here is **Phase 5 — Orchestrator Design** for **Project 2: `global_economic_health`**, written to match the structure, rigor, and agent‑orchestrated workflow of your world_populations project. It defines the full pipeline, sequencing, heartbeat, error handling, logging, and verification integration. It also ensures population ETL + trendline visualization can be reused from Project 1 without duplication.



---

# Phase 5 — Orchestrator Design  
**Project:** Global Economic Health Dashboard  
**Folder:** `data_visualization/global_economic_health/`  
**Phase:** 5 — Orchestrator  
**Status:** Ready for agent implementation  
**Dependencies:**  
- Phase 1 ETL  
- Phase 2 Visualizations  
- Phase 3 QA Agents  
- Phase 4 Preview Generation  
- Shared coordination system  
- Verification layer  

---

## 1. Phase Objective

This phase defines the **full orchestrator pipeline** for Project 2. The orchestrator must:

- Run all ETL, QA, visualization, preview, and verification steps  
- Enforce strict sequencing  
- Stop immediately on any failure  
- Log every step  
- Emit heartbeat signals for cloud execution  
- Produce timestamped outputs  
- Return a structured result object for the cloud agent  
- Integrate with the verification layer  
- Reuse population ETL + trendline visualization from Project 1  

The orchestrator is the **single source of truth** for the entire pipeline.

---

## 2. Orchestrator Responsibilities

### Core Responsibilities  
- Execute all scripts in correct order  
- Validate outputs after each step  
- Run QA agents  
- Run verification layer  
- Generate final dashboard + previews  
- Produce logs and structured results  
- Support cloud agent execution  
- Provide heartbeat signals  

### Failure Handling  
- Any FAIL stops the pipeline  
- Orchestrator returns a structured error object  
- Local agent logs failure in audit trail  
- Cloud agent sends failure notification  

---

## 3. Orchestrator Sequence (Strict Order)

The orchestrator must run in this exact order:

### **ETL Phase**
1. **Fetch GDP**  
2. **Fetch Population** (reuse Project 1 script)  
3. **Fetch Debt**  
4. **Transform + Merge + Clean**  
5. **Run Data QA Agent**  
   - If FAIL → stop  

### **Visualization Phase**
6. **Build Bubble Map**  
7. **Build Population Trendline** (reuse Project 1 script)  
8. **Generate Unified HTML Dashboard**  
9. **Run UI QA Agent**  
   - If FAIL → stop  

### **Preview Phase**
10. **Generate Bubble Map Frames**  
11. **Generate Trendline Frames**  
12. **Generate GIF Preview**  
13. **Generate MP4 Preview**  
14. **Run Preview QA**  
   - If FAIL → stop  

### **Verification Phase**
15. **Run Verification Layer (`verify_all.py`)**  
   - Code structure  
   - Outputs  
   - Visualizations  
   - Orchestrator flow  
   - If FAIL → stop  

### **Publishing Phase (Optional)**
16. **Publish to GitHub Pages or VPS**  
17. **Send Cloud Agent Notification**  

---

## 4. Orchestrator File Requirements

### File: `scripts/orchestrator.py`

### Required Functions

#### `generate_timestamp()`
- Returns human‑friendly timestamp (e.g., `7Mar2026`)

#### `orchestrator_log(message, log_file)`
- Appends message to orchestrator log  
- Prints message to console  

#### `run_pipeline()`
- Main orchestrator function  
- Executes all steps  
- Returns structured result object  

#### `if __name__ == "__main__":`
- Runs `run_pipeline()`  
- Prints result  

---

## 5. Logging Requirements

### Log File Location  
```
reports/logs/orchestrator_log_<timestamp>.txt
```

### Log Must Include  
- Start time  
- Each step name  
- Success/failure messages  
- File paths of outputs  
- QA results  
- Verification results  
- End time  

### Log Format  
- Plain text  
- Timestamped entries  
- Human‑readable  

---

## 6. Heartbeat Requirements

### Background Agent  
- Sends heartbeat every 5 seconds  
- Logs heartbeat to audit trail  

### Cloud Agent  
- Sends heartbeat during orchestrator execution  
- Local agent must timeout after 60 seconds of silence  

### Orchestrator  
- Writes heartbeat entries to log  
- Cloud agent reads log to confirm progress  

---

## 7. Error Handling Requirements

### On Any Failure  
- Stop pipeline immediately  
- Write error to log  
- Return structured error object:  
  ```
  {
      "status": "FAIL",
      "stage": "UI QA",
      "timestamp": "7Mar2026",
      "error": "Missing bubble map HTML"
  }
  ```
- Cloud agent sends failure notification  
- Local agent logs failure in audit trail  

---

## 8. Output Requirements

### Final Output Object  
The orchestrator must return:

```
{
  "status": "PASS",
  "timestamp": "<timestamp>",
  "html": "<path>",
  "gif": "<path>",
  "mp4": "<path>",
  "verification": {...}
}
```

### Required Output Files  
- `macro_final_<timestamp>.csv`  
- `bubble_map_<timestamp>.html`  
- `population_trendline_<timestamp>.html`  
- `global_economic_health_dashboard_<timestamp>.html`  
- `global_economic_health_preview_<timestamp>.gif`  
- `global_economic_health_preview_<timestamp>.mp4`  
- QA reports  
- Verification summary  
- Orchestrator log  

---

## 9. Verification Layer Integration

### verify_all.py must check:
- All required scripts exist  
- All required outputs exist  
- All visualizations load correctly  
- All CSVs have valid schema  
- Orchestrator sequence is correct  
- No missing timestamps  
- No missing logs  

### Orchestrator must call:
```
verification_result = verify_all(project_root, timestamp)
```

### If FAIL:
- Stop pipeline  
- Return structured error  

---

## 10. Reuse from Project 1

The orchestrator must reuse:

- `01_fetch_population.py`  
- `02_transform_rank_top50.py`  
- `05_build_visualization_v3_animated_trendline.py`  
- Data QA logic (adapted)  
- UI QA logic (extended)  
- Preview generation logic (adapted)  
- Verification layer structure  

This ensures consistency and saves development time.

---

## 11. Deliverables for Phase 5

- `scripts/orchestrator.py` implemented  
- Full pipeline executable  
- Logs generated  
- QA agents integrated  
- Verification layer integrated  
- Cloud agent execution validated  

---

If you want, I can now generate **Phase 6 — Cloud Integration Design**, which defines:

- Cloud agent execution  
- Remote orchestrator control  
- Telegram/OpenClaw notifications  
- Remote heartbeat monitoring  
- Remote preview delivery
