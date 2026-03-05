Here is your complete **Phase 5 Orchestrator Design** Markdown file, ready to save as:

```
data_visualization/World_population/docs/Phase5_Orchestrator_Design_5Mar2026.md
```

It is written to be fully compatible with your strict folder structure, timestamping rules, agent workflow, and your Day‑2 plan to trigger everything through **OpenClaw + Telegram**.

---

# Phase 5 — Orchestrator Design (5 Mar 2026)

## 1. Purpose of Phase 5
This phase defines the **full automation architecture** for the world‑population dashboard pipeline. The orchestrator coordinates all scripts and QA agents to produce:

- Clean ETL output  
- Validated processed data  
- Polished visualization  
- Timestamped HTML report  
- GIF/MP4 preview  
- QA reports  
- Optional publishing  
- Telegram notifications (Day‑2)  

The orchestrator must be deterministic, fault‑tolerant, timestamp‑aware, and fully compatible with VS Code and OpenClaw.

---

## 2. Orchestrator Responsibilities

The orchestrator must run the entire pipeline **end‑to‑end**, in the correct order, with strict validation gates:

1. Fetch raw population data  
2. Transform + rank top 50  
3. Run Data QA agent  
4. Build visualization  
5. Generate timestamped HTML  
6. Run UI QA agent  
7. Generate MP4 preview  
8. Generate GIF preview  
9. Publish HTML (optional)  
10. Send Telegram notification (Day‑2)  
11. Log all outputs  

If any step fails, the orchestrator must stop immediately and notify the user.

---

## 3. Orchestrator Script Location

```
scripts/orchestrator.py
```

This script is the **single entry point** for the entire project.

---

## 4. Orchestrator Workflow

### 4.1 High‑Level Flow

```
[Start]
   ↓
Run ETL (fetch + transform)
   ↓
Run Data QA
   ↓ PASS
Build visualization
   ↓
Generate timestamped HTML
   ↓
Run UI QA
   ↓ PASS
Generate MP4 preview
   ↓
Generate GIF preview
   ↓
Publish HTML (optional)
   ↓
Send Telegram notification (Day‑2)
   ↓
[Done]
```

### 4.2 Failure Handling

If any step fails:

- Stop pipeline  
- Log failure  
- Save partial outputs  
- Send Telegram alert (Day‑2)  
- Do not generate previews  
- Do not publish  

---

## 5. Timestamp Management

### 5.1 Human‑Friendly Timestamp Format

```
3Mar2026
```

### 5.2 Orchestrator Must Generate a Single Timestamp Per Run

This timestamp is used for:

- Raw CSV  
- Processed CSV  
- HTML report  
- GIF preview  
- MP4 preview  
- QA reports  
- Screenshots  
- Logs  

This ensures perfect traceability.

---

## 6. Orchestrator Inputs and Outputs

### 6.1 Inputs

- `config/settings.yaml`  
- `csv/raw/` (optional previous runs)  
- `csv/processed/` (optional previous runs)  
- All scripts in `scripts/`  
- All agents in `qa_agents/`  

### 6.2 Outputs

Stored under:

```
reports/
   ├── html/
   ├── media/
   ├── qa/
   └── screenshots/
```

Outputs include:

- Timestamped HTML  
- MP4 preview  
- GIF preview  
- Data QA report  
- UI QA report  
- Code review report  
- UI screenshot  
- Orchestrator log  

---

## 7. Orchestrator Step‑by‑Step Design

### 7.1 Step 1 — Fetch Population Data

Call:

```
scripts/01_fetch_population.py
```

Output:

```
csv/raw/worldbank_population_raw_<3Mar2026>.csv
```

### 7.2 Step 2 — Transform + Rank Top 50

Call:

```
scripts/02_transform_rank_top50.py
```

Output:

```
csv/processed/population_top50_1970_now_<3Mar2026>.csv
```

### 7.3 Step 3 — Data QA Agent

Call:

```
qa_agents/agent_data_qa.py
```

Output:

```
reports/qa/data_qa_report_<3Mar2026>.json
```

If FAIL → stop pipeline.

### 7.4 Step 4 — Build Visualization

Call:

```
scripts/03_build_visualization.py
```

This script must:

- Load processed CSV  
- Apply color palette  
- Embed SVG flags  
- Format numbers as 1M/1B  
- Build bar‑race figure  

### 7.5 Step 5 — Generate Timestamped HTML

Call:

```
scripts/04_generate_html_timestamped.py
```

Output:

```
reports/html/population_bar_race_<3Mar2026>.html
```

### 7.6 Step 6 — UI QA Agent

Call:

```
qa_agents/agent_ui_qa.py
```

Outputs:

```
reports/qa/ui_qa_report_<3Mar2026>.md
reports/screenshots/ui_snapshot_<3Mar2026>.png
```

If FAIL → stop pipeline.

### 7.7 Step 7 — Generate MP4 Preview

Call:

```
scripts/05_generate_gif_mp4_preview.py
```

Output:

```
reports/media/population_preview_<3Mar2026>.mp4
```

### 7.8 Step 8 — Generate GIF Preview

Output:

```
reports/media/population_preview_<3Mar2026>.gif
```

### 7.9 Step 9 — Publish HTML (Optional)

Two supported methods:

- GitHub Pages  
- VPS (Nginx)  

Orchestrator must support both.

### 7.10 Step 10 — Telegram Notification (Day‑2)

Send:

- PASS/FAIL summary  
- HTML link  
- MP4 preview  
- GIF preview  
- QA reports  

---

## 8. Orchestrator Logging

### 8.1 Log File Location

```
reports/logs/orchestrator_log_<3Mar2026>.txt
```

### 8.2 Log Contents

- Start time  
- End time  
- Timestamp used  
- Each step status  
- QA results  
- File paths generated  
- Errors (if any)  

---

## 9. Orchestrator Error Handling

### 9.1 Hard Failures

- API unreachable  
- Missing CSV columns  
- Data QA FAIL  
- UI QA FAIL  
- MP4 encoding failure  
- GIF encoding failure  

Pipeline stops immediately.

### 9.2 Soft Failures

- Minor warnings  
- Non‑critical layout issues  
- Missing optional metadata  

Pipeline continues but logs warnings.

---

## 10. Orchestrator Configuration

### 10.1 Config File

```
config/settings.yaml
```

Contains:

- Start year  
- End year  
- Top N  
- Output resolution  
- MP4 FPS  
- GIF FPS  
- Publishing mode  
- Telegram bot token (Day‑2)  
- Telegram chat ID (Day‑2)  

---

## 11. OpenClaw + Telegram Integration (Day‑2)

### 11.1 Supported Commands

```
/run_population_dashboard
/get_latest_preview
/get_latest_html
/check_data
/check_ui
/check_code
```

### 11.2 Telegram Output

- PASS/FAIL summary  
- HTML link  
- Attached MP4 preview  
- Attached GIF preview  
- QA reports  
- Timestamp  

### 11.3 Remote Execution

OpenClaw triggers:

```
python3 scripts/orchestrator.py
```

---

## 12. Phase 5 To‑Do List (5 Mar 2026)

- Implement orchestrator script  
- Add timestamp generator  
- Add step‑by‑step execution  
- Add error handling  
- Add logging  
- Integrate Data QA agent  
- Integrate UI QA agent  
- Integrate Code Review agent  
- Integrate preview generator  
- Integrate publishing logic  
- Prepare for Telegram integration  

