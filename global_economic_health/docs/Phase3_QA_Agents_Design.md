Here is **Phase 3 — QA Agents Design** for **Project 2: `global_economic_health`**, written to match the structure, rigor, and agent‑orchestrated workflow of your world_populations project. It ensures that:

- Data accuracy is enforced  
- Visual correctness is validated  
- Code quality is checked  
- Orchestrator behavior is verified  
- The verification layer integrates cleanly  
- All QA agents work with the heartbeat + audit‑trail model  



---

# Phase 3 — QA Agents Design  
**Project:** Global Economic Health Dashboard  
**Folder:** `data_visualization/global_economic_health/`  
**Phase:** 3 — QA Agents  
**Status:** Ready for agent implementation  
**Dependencies:**  
- Phase 1 ETL outputs  
- Phase 2 visualizations  
- Shared coordination system  
- Verification layer  

---

## 1. Phase Objective

This phase defines the **full QA system** for Project 2. It must match the rigor of Project 1, but expanded for multi‑metric macro‑economic data and multi‑chart visualizations.

The QA system includes:

- **Data QA Agent** — validates GDP, population, and debt  
- **UI QA Agent** — validates bubble map + trendline visuals  
- **Code Review Agent** — validates script quality  
- **Orchestrator QA Agent** — validates pipeline sequencing  
- **Verification Layer** — enforces correctness before approval  

All QA agents must integrate with:

- Local agent (CI/CD gatekeeper)  
- Background agent (worker)  
- Cloud agent (executor)  
- Heartbeat + audit trail  

---

## 2. QA Architecture Overview

### QA Agents Required  
1. `qa_agents/agent_data_qa.py`  
2. `qa_agents/agent_ui_qa.py`  
3. `qa_agents/agent_code_review.py`  
4. `qa_agents/agent_orchestrator.py`  

### Verification Layer  
- `verification/verify_code_structure.py`  
- `verification/verify_outputs.py`  
- `verification/verify_visualization.py`  
- `verification/verify_orchestrator_flow.py`  
- `verification/verify_all.py`  

### Output Locations  
- `reports/qa/*.json`  
- `reports/qa/*.md`  
- `reports/screenshots/*.png`  

---

## 3. Data QA Agent — `agent_data_qa.py`

### Purpose  
Validate the correctness, completeness, and consistency of:

- GDP  
- Population  
- Debt  
- Derived metrics (GDP per capita, debt‑to‑GDP, growth rates)  

### Inputs  
- `macro_final_<timestamp>.csv`  
- `iso_country_codes.csv`  
- `aggregate_regions_exclude.csv`  

### Required Checks  

#### Schema Validation  
- Required columns exist  
- All numeric fields are numeric  
- No unexpected columns  

#### Country Validation  
- All country codes must be valid ISO‑3  
- No aggregates (e.g., “World”, “High income”)  
- No duplicates per country/year  

#### Value Validation  
- GDP > 0  
- Population > 0  
- Debt ≥ 0  
- GDP per capita > 0  
- Debt‑to‑GDP ratio between 0 and 5  
- Growth rates between −50% and +200%  

#### Time‑Series Validation  
- No missing years between 1960–2026  
- No backward population jumps > 10% (flag as anomaly)  
- No GDP drops > 50% (flag as anomaly)  

#### Output  
- `reports/qa/data_qa_report_<timestamp>.json`  
- `reports/qa/data_qa_summary_<timestamp>.md`  

---

## 4. UI QA Agent — `agent_ui_qa.py`

### Purpose  
Validate the correctness of all visualizations:

- Bubble map  
- Population trendline  
- Unified dashboard  

### Inputs  
- HTML files in `reports/html/`  
- Screenshots captured via Playwright  

### Required Checks  

#### Bubble Map  
- Bubble size matches GDP  
- Bubble color matches debt‑to‑GDP  
- Tooltip shows correct values  
- Year slider updates bubble sizes/colors  
- No missing countries  
- No overlapping labels beyond threshold  
- Map loads without JS errors  

#### Population Trendline  
- Trendline matches polynomial fit  
- Growth rates match underlying data  
- Hover tooltips show correct values  
- Animation (if enabled) progresses correctly  

#### Unified Dashboard  
- All charts load  
- Layout responsive on mobile  
- No broken DOM elements  
- No missing Plotly JS  
- No console errors  

#### Output  
- `reports/qa/ui_qa_report_<timestamp>.md`  
- Screenshots in `reports/screenshots/`  

---

## 5. Code Review Agent — `agent_code_review.py`

### Purpose  
Ensure all scripts meet quality, structure, and maintainability standards.

### Inputs  
- All scripts in `scripts/`  

### Required Checks  

#### Structure  
- Required functions exist  
- No hard‑coded paths  
- No unused imports  
- No global variables except constants  

#### Quality  
- Docstrings present  
- Type hints present  
- Logging used instead of print  
- Error handling implemented  

#### Performance  
- No O(n²) operations on large datasets  
- Vectorized Pandas operations preferred  
- No unnecessary loops  

#### Output  
- `reports/qa/code_review_<timestamp>.md`  

---

## 6. Orchestrator QA Agent — `agent_orchestrator.py`

### Purpose  
Validate orchestrator sequencing and behavior.

### Inputs  
- `scripts/orchestrator.py`  
- Orchestrator logs  

### Required Checks  

#### Sequence Validation  
Must run in this exact order:

1. Fetch GDP  
2. Fetch population  
3. Fetch debt  
4. Transform + merge + clean  
5. Data QA  
6. Bubble map  
7. Population trendline  
8. HTML dashboard  
9. UI QA  
10. Previews  
11. Verification layer  
12. Publish (optional)  

#### Error Handling  
- Pipeline must stop on any FAIL  
- Logs must show clear error messages  
- Heartbeat must be present  

#### Output  
- `reports/qa/orchestrator_qa_<timestamp>.md`  

---

## 7. Verification Layer Integration

### verify_code_structure.py  
Checks script existence + required functions.

### verify_outputs.py  
Checks CSV schema + value ranges.

### verify_visualization.py  
Checks HTML structure + DOM elements.

### verify_orchestrator_flow.py  
Checks orchestrator sequence.

### verify_all.py  
Runs all checks and returns PASS/FAIL.

---

## 8. Heartbeat Requirements

- Background agent heartbeat every 5 seconds  
- Cloud agent heartbeat during orchestrator execution  
- Local agent timeout after 60 seconds  
- All events logged to audit trail  

---

## 9. Deliverables for Phase 3

- All QA agents implemented  
- All verification modules implemented  
- QA reports generated  
- Verification summary generated  
- Orchestrator validated  

