Project 1 = world population located in folder "C:\Users\haujo\projects\DEV\Data_visualization\world_populations"
---

# Phase 0 — Project Definition  
**Project Name:** Global Economic Health Dashboard  
**Folder Path:** `data_visualization/global_economic_health/`  
**Status:** Phase 0 Complete  
**Agent Model:** Local Agent → Background Agent → Cloud Agent (same as world_populations)

---

## 1. Purpose

This project builds a **multi‑metric global macro‑economic dashboard** combining:

- GDP (World Bank)
- Population (reuse from Project 1)
- Global debt (IMF Global Debt Database or World Bank IDS)
- Bubble‑map visualization (crypto‑bubble style)
- Population trendline visualization (reuse from Project 1)
- Multi‑chart HTML dashboard
- Automated ETL, QA, previews, orchestrator, cloud execution

The project must follow the **same agent‑orchestrated architecture** as `world_populations`, including:

- task manifests  
- background agent implementation  
- local agent verification  
- cloud agent execution  
- heartbeat monitoring  
- audit trail logging  
- verification layer enforcement  

---

## 2. Folder Structure

```
global_economic_health/
├── config/
│   ├── settings.yaml
│   ├── iso_country_codes.csv
│   ├── bubble_scaling.yaml
│   └── map_geojson.json
├── coordination/        ← shared with world_populations
├── csv/
│   ├── raw/
│   └── processed/
├── scripts/
│   ├── 01_fetch_gdp.py
│   ├── 02_fetch_population.py        ← reused from Project 1
│   ├── 03_fetch_debt.py
│   ├── 04_transform_merge_clean.py
│   ├── 05_build_bubble_map.py
│   ├── 06_build_population_trendline.py  ← reused from Project 1 (v2 or v3)
│   ├── 07_generate_html_dashboard.py
│   ├── 08_generate_previews.py
│   └── orchestrator.py
├── qa_agents/
│   ├── agent_data_qa.py
│   ├── agent_ui_qa.py
│   ├── agent_code_review.py
│   └── agent_orchestrator.py
├── reports/
│   ├── html/
│   ├── media/
│   ├── qa/
│   └── screenshots/
└── verification/
    ├── verify_code_structure.py
    ├── verify_outputs.py
    ├── verify_visualization.py
    ├── verify_orchestrator_flow.py
    └── verify_all.py
```

Project 2 is **fully separate** from Project 1, but allowed to reuse scripts.

---

## 3. Data Sources

### GDP (World Bank)
- Indicator: `NY.GDP.MKTP.CD`
- Annual, globally complete
- Used for bubble size, GDP growth, GDP per capita

### Population (World Bank)
- Indicator: `SP.POP.TOTL`
- **Reuse Project 1’s ETL scripts**:
  - `01_fetch_population.py`
  - `02_transform_rank_top50.py`
- Used for population trendline and per‑capita metrics

### Global Debt
- IMF Global Debt Database (preferred)
- World Bank IDS (alternative)
- Used for debt‑to‑GDP ratio and bubble color encoding

---

## 4. Visualizations

### Bubble Map (Crypto‑Bubble Style)
- Bubble size = GDP  
- Bubble color = debt‑to‑GDP ratio or GDP growth  
- Tooltip = GDP, population, debt, growth  
- Year slider = 1970 → present  
- Global map base layer  

### Population Trendline (Reused from Project 1)
- Use `05_build_visualization_v3_animated_trendline.py`  
- Or use v2 static trendline version  
- Integrated into the multi‑chart dashboard  

### Optional Additional Charts
- GDP growth bar‑race  
- Debt‑to‑GDP choropleth  
- Country profile panel  

---

## 5. Agent Responsibilities

### Local Agent (CI/CD Gatekeeper)
- Creates task manifests  
- Verifies ETL, visualization, QA scripts  
- Runs verification layer  
- Approves or rejects tasks  
- Ensures heartbeat from background/cloud agents  

### Background Agent (Worker)
- Implements GDP ETL  
- Implements debt ETL  
- Reuses population ETL from Project 1  
- Implements bubble map + trendline visualizations  
- Implements QA agents  
- Implements orchestrator  

### Cloud Agent (Executor)
- Runs orchestrator end‑to‑end  
- Generates HTML, MP4, GIF  
- Sends results back to local agent  
- Provides heartbeat signals  

---

## 6. Orchestrator Workflow

1. Fetch GDP  
2. Fetch population (reuse script)  
3. Fetch debt  
4. Transform + merge + clean  
5. Data QA  
6. Build bubble map  
7. Build population trendline (reuse script)  
8. Generate HTML dashboard  
9. UI QA  
10. Preview generation  
11. Verification layer  
12. Publish (optional)  
13. Cloud agent notification  

Pipeline must stop immediately on any FAIL.

---

## 7. Heartbeat Requirements

- Background agent polls every 5 seconds  
- Cloud agent sends orchestrator heartbeat  
- Local agent times out after 60 seconds  
- All events logged to audit trail  

This ensures no task is left incomplete.

---

## 8. Reuse from Project 1 = "C:\Users\haujo\projects\DEV\Data_visualization\world_populations"

The following scripts may be reused directly:

- `01_fetch_population.py`  
- `02_transform_rank_top50.py`  
- `05_build_visualization_v3_animated_trendline.py`  
- Data QA logic (adapted for GDP/debt)  
- UI QA logic (extended for bubble maps)  
- Verification layer modules  

This accelerates Project 2 significantly.

---

## 9. Output Requirements

- Timestamped CSVs  
- Multi‑chart HTML dashboard  
- MP4 + GIF previews  
- QA reports  
- Verification summary  
- Orchestrator logs  

---

## 10. Notes

Project 2 must maintain full compatibility with the agent orchestration system used in Project 1 = "C:\Users\haujo\projects\DEV\Data_visualization\world_populations" .  
All scripts must be generated via task manifests and verified by the local agent.

---

If you'd like, I can now generate **Phase 1 — ETL Design** for Project 2, including:

- GDP fetch  
- Debt fetch  
- Population reuse  
- Merge + clean  
- Data QA rules  
- Verification rules  

This will give your agents the next layer of instructions to begin implementation.
