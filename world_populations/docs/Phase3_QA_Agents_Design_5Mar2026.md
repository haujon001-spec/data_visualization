Below is your complete **Phase 3 QA Agents Design** Markdown file, ready to save as:

```
data_visualization/World_population/docs/Phase3_QA_Agents_Design_5Mar2026.md
```

It follows your strict structure, timestamping, and agent‑oriented workflow. It is written so **VS Code, your orchestrator, and future OpenClaw/Telegram agents** can execute the QA pipeline reliably.

---

# Phase 3 — QA Agents Design (5 Mar 2026)

## 1. Purpose of Phase 3
This phase defines the **full quality‑assurance architecture** for the world‑population dashboard. The QA system must validate:

- Data correctness  
- Visualization correctness  
- HTML/UI rendering  
- Code quality and maintainability  

The QA agents operate independently but are orchestrated in sequence to ensure **no garbage in, no garbage out**, and to guarantee that the final dashboard is **accurate, readable, mobile‑friendly, and visually polished**.

The outputs of this phase feed directly into Phase 4 (GIF/MP4 preview) and Phase 5 (orchestrator automation).

---

## 2. QA Architecture Overview

The QA system consists of **three specialized agents**:

- **Data QA Agent** — validates processed CSV  
- **UI QA Agent** — validates HTML visualization  
- **Code Review Agent** — validates ETL + visualization scripts  

These agents are coordinated by the **Orchestrator Agent** in Phase 5.

Each agent must:

- Produce timestamped QA reports  
- Follow strict folder structure  
- Provide actionable feedback  
- Integrate cleanly with VS Code and OpenClaw  

---

## 3. Data QA Agent

### 3.1 Script Location
```
qa_agents/agent_data_qa.py
```

### 3.2 Purpose
Validate the processed population dataset before visualization. This ensures the bar‑race animation is built only from **clean, complete, and logically consistent data**.

### 3.3 Input
```
csv/processed/population_top50_1970_now_<3Mar2026>.csv
```

### 3.4 Validation Rules

- **Completeness**  
  - Exactly 50 rows per year  
  - No missing `country_code`, `country_name`, `year`, or `population`  

- **Sanity Checks**  
  - Population > 0  
  - Year‑over‑year change within reasonable bounds  
  - No negative or null values  

- **Consistency**  
  - No duplicate country/year pairs  
  - No aggregate regions (e.g., “World”, “High income”)  
  - All country codes must be valid ISO‑3  

- **Ranking Integrity**  
  - Rank must be 1–50  
  - Rank must match sorted population order  

### 3.5 Output
```
reports/qa/data_qa_report_<3Mar2026>.json
```

### 3.6 Failure Behavior
If any rule fails:

- The agent marks the dataset as **FAIL**  
- The orchestrator stops the pipeline  
- A Telegram notification is sent (Day‑2 integration)  
- The HTML/UI steps are skipped  

---

## 4. UI QA Agent

### 4.1 Script Location
```
qa_agents/agent_ui_qa.py
```

### 4.2 Purpose
Validate the **HTML visualization** to ensure it is visually correct, readable, mobile‑friendly, and suitable for publishing.

### 4.3 Input
```
reports/html/population_bar_race_<3Mar2026>.html
```

### 4.4 Rendering Method
The agent must load the HTML using a **headless browser** (Playwright or Puppeteer‑Python equivalent).

### 4.5 Validation Rules

- **Flag Rendering**  
  - All SVG flags load correctly  
  - No broken image links  

- **Number Formatting**  
  - All population values use SI suffixes (1M, 1B)  
  - No raw numbers like 1,000,000  

- **Layout & Readability**  
  - Bars fully visible  
  - Labels readable  
  - No overlapping text  
  - No clipped bars  
  - Title and data source visible  

- **Mobile Responsiveness**  
  - Render at 375px width  
  - Bars remain readable  
  - Flags remain visible  
  - Controls accessible  

- **Theme & Styling**  
  - Modern theme applied  
  - Colors distinct  
  - No default Plotly grey theme  

### 4.6 Output
```
reports/qa/ui_qa_report_<3Mar2026>.md
reports/screenshots/ui_snapshot_<3Mar2026>.png
```

### 4.7 Failure Behavior
If any rule fails:

- The agent marks the HTML as **FAIL**  
- The orchestrator stops before GIF/MP4 generation  
- A Telegram notification is sent  
- Developer must fix visualization script  

---

## 5. Code Review Agent

### 5.1 Script Location
```
qa_agents/agent_code_review.py
```

### 5.2 Purpose
Review ETL and visualization scripts for:

- Maintainability  
- Performance  
- Readability  
- Error handling  
- Agent‑orchestrator compatibility  

### 5.3 Input Files
- `scripts/01_fetch_population.py`  
- `scripts/02_transform_rank_top50.py`  
- `scripts/03_build_visualization.py`  
- `scripts/04_generate_html_timestamped.py`  
- `scripts/05_generate_gif_mp4_preview.py`  

### 5.4 Review Criteria

- **Code Quality**  
  - Clear naming conventions  
  - Modular functions  
  - No duplicated logic  
  - Proper comments  

- **Performance**  
  - Vectorized operations where possible  
  - Efficient sorting and ranking  
  - Avoid unnecessary loops  

- **Error Handling**  
  - API retry logic  
  - File existence checks  
  - Graceful failure modes  

- **Orchestrator Compatibility**  
  - Functions return predictable outputs  
  - No hard‑coded paths  
  - Timestamp logic consistent  

### 5.5 Output
```
reports/qa/code_review_<3Mar2026>.md
```

### 5.6 Failure Behavior
If major issues are found:

- The agent marks the code as **FAIL**  
- Orchestrator halts  
- Developer must apply recommended patches  

---

## 6. QA Output Folder Structure

All QA outputs must follow this strict structure:

```
reports/
   ├── qa/
   │     ├── data_qa_report_<3Mar2026>.json
   │     ├── ui_qa_report_<3Mar2026>.md
   │     └── code_review_<3Mar2026>.md
   └── screenshots/
         └── ui_snapshot_<3Mar2026>.png
```

This ensures:

- Traceability  
- Versioning  
- Agent‑friendly parsing  
- Clean publishing workflow  

---

## 7. Integration with Orchestrator (Phase 5)

The orchestrator must run QA agents in this order:

1. **Data QA Agent**  
2. **UI QA Agent**  
3. **Code Review Agent**  

The orchestrator must:

- Stop immediately on any FAIL  
- Log all results  
- Notify via Telegram (Day‑2)  
- Only proceed to GIF/MP4 generation if all QA passes  

---

## 8. Integration with OpenClaw/Telegram (Day‑2)

The orchestrator will expose commands:

```
/check_data
/check_ui
/check_code
/check_all
```

Each command triggers the corresponding QA agent and returns:

- PASS/FAIL  
- QA report  
- Screenshot (UI QA only)  
- Next recommended action  

---

## 9. Phase 3 To‑Do List (5 Mar 2026)

- Implement Data QA agent  
- Implement UI QA agent with headless browser  
- Implement Code Review agent  
- Add timestamp logic to all QA outputs  
- Add screenshot capture for UI QA  
- Validate QA outputs manually once  
- Prepare for orchestrator integration  

---

