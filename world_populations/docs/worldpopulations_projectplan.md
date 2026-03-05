Below is a **single, complete, production‑ready Markdown file** you can drop directly into:

```
data_visualization/World_population/docs/Phase0_ProjectPlan_5Mar2026.md
```

It defines:

- The **strict folder structure**  
- The **full 50‑year population dashboard architecture**  
- The **flag‑enhanced visualization design**  
- The **HTML/GIF/MP4 publishing workflow**  
- The **agent QA system**  
- The **end‑to‑end orchestrator**  
- The **Day‑2 OpenClaw/Telegram control plan**  

This file is written so that **VS Code, your agents, and future contributors** can understand exactly what to build.

---

# 🌍 World Population Dashboard — Phase 0 Project Plan  
**Version:** 5 Mar 2026  
**Author:** John  
**Project Root:** `data_visualization/World_population/`  
**Scope:** Build a 50‑year (1970 → present) world population interactive dashboard with polished country flags, timestamped HTML reports, GIF/MP4 previews for LinkedIn, and a full agent‑orchestrated QA + publishing pipeline.

---

## 1. Project Objectives

This project aims to create a **high‑quality, visually appealing, agent‑validated interactive dashboard** showing the **Top 50 most populous countries** from **1970 to the present year**, with:

- Clean ETL pipeline  
- Polished visualization (SVG flags, modern theme, 1M/1B formatting)  
- Automated QA (data + UI)  
- Automated HTML + GIF/MP4 generation  
- Automated publishing workflow  
- Agent orchestrator capable of running the entire pipeline  
- Day‑2 integration with **OpenClaw + Telegram LLM control**  

The final output must be suitable for **LinkedIn publishing**, where users prefer **native video previews** over external links.

---

## 2. Strict Folder Structure

All files must follow this structure for consistency, automation, and agent orchestration.

```
World_population/
├── config/
│     ├── settings.yaml
│     ├── country_code_map.csv
│     └── flag_sources.csv
│
├── csv/
│     ├── raw/
│     │     └── worldbank_population_raw_<YYYYMMDD>.csv
│     └── processed/
│           └── population_top50_1970_now_<YYYYMMDD>.csv
│
├── scripts/
│     ├── 01_fetch_population.py
│     ├── 02_transform_rank_top50.py
│     ├── 03_build_visualization.py
│     ├── 04_generate_html_timestamped.py
│     ├── 05_generate_gif_mp4_preview.py
│     └── orchestrator.py
│
├── qa_agents/
│     ├── agent_data_qa.py
│     ├── agent_ui_qa.py
│     ├── agent_code_review.py
│     └── agent_orchestrator.py
│
├── reports/
│     ├── html/
│     │     └── population_bar_race_<3Mar2026>.html
│     ├── media/
│     │     ├── population_preview_<3Mar2026>.mp4
│     │     └── population_preview_<3Mar2026>.gif
│     ├── qa/
│     │     ├── data_qa_report_<3Mar2026>.json
│     │     └── ui_qa_report_<3Mar2026>.md
│     └── screenshots/
│           └── ui_snapshot_<3Mar2026>.png
│
├── docs/
│     ├── Phase0_ProjectPlan_5Mar2026.md
│     ├── Phase1_ETL_Design_<YYYYMMDD>.md
│     ├── Phase2_Visualization_Design_<YYYYMMDD>.md
│     ├── Phase3_QA_Agents_<YYYYMMDD>.md
│     └── Phase4_Orchestrator_Design_<YYYYMMDD>.md
│
└── README.md
```

---

## 3. Data Source and ETL Requirements

### 3.1 Data Source  
Primary source: **World Bank API**  
Indicator: `SP.POP.TOTL` (Total Population)

API endpoint:  
`https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000`

### 3.2 Time Range  
**1970 → Current Year**

### 3.3 ETL Steps  
1. Fetch raw population data  
2. Filter out aggregate regions (e.g., “World”, “High income”)  
3. Normalize fields:  
   - `country_code`  
   - `country_name`  
   - `year`  
   - `population`  
4. Rank each year by population  
5. Keep **Top 50**  
6. Save processed CSV with timestamp suffix

### 3.4 Output  
`csv/processed/population_top50_1970_now_<3Mar2026>.csv`

---

## 4. Visualization Requirements

### 4.1 Chart Type  
**Horizontal bar‑race animation** (Plotly)

### 4.2 Visual Enhancements  
- **SVG flags** from FlagCDN:  
  `https://flagcdn.com/<country_code>.svg`
- **1M/1B formatting** using Plotly SI formatter  
- **Modern theme** (dark or light)  
- **Responsive layout** for desktop + mobile  
- **Readable labels** with no overlap  
- **Smooth animation** with play/pause controls  

### 4.3 Output  
`reports/html/population_bar_race_<3Mar2026>.html`

---

## 5. GIF/MP4 Preview for LinkedIn

### 5.1 Purpose  
LinkedIn users avoid unknown URLs.  
Native video previews dramatically increase engagement.

### 5.2 Requirements  
- 10–15 second animation  
- 1080p or 720p resolution  
- Smooth transitions  
- Clean color palette  
- Country flags visible  
- 1M/1B formatting  
- Timestamped filename

### 5.3 Output  
- `reports/media/population_preview_<3Mar2026>.mp4`  
- `reports/media/population_preview_<3Mar2026>.gif`

---

## 6. QA Agents

### 6.1 Data QA Agent  
Validates processed CSV:

- 50 rows per year  
- No missing values  
- No negative population  
- No duplicate country/year  
- No aggregate regions  
- Year‑over‑year sanity checks  

Output:  
`reports/qa/data_qa_report_<3Mar2026>.json`

---

### 6.2 UI QA Agent  
Loads HTML in headless browser and checks:

- Flags load correctly  
- Numbers show as 1M/1B  
- Bars readable on desktop + mobile  
- No label overlap  
- Animation controls visible  
- Title + data source visible  
- Modern theme applied  

Output:  
`reports/qa/ui_qa_report_<3Mar2026>.md`  
Screenshot:  
`reports/screenshots/ui_snapshot_<3Mar2026>.png`

---

### 6.3 Code Review Agent  
Reviews:

- ETL scripts  
- Visualization scripts  
- QA scripts  
- Orchestrator  

Checks for:

- Clarity  
- Performance  
- Error handling  
- Naming conventions  
- Vectorization  
- Caching  
- Retry logic  

---

## 7. Orchestrator Agent (End‑to‑End Pipeline)

### 7.1 Responsibilities  
Runs the entire workflow:

1. Fetch population data  
2. Transform + rank  
3. Run Data QA  
4. Build visualization  
5. Generate timestamped HTML  
6. Run UI QA  
7. Generate GIF/MP4 preview  
8. Publish HTML (GitHub Pages or VPS)  
9. Notify via Telegram (OpenClaw)

### 7.2 Trigger Methods  
- VS Code task  
- Cron job  
- Telegram command  
- GitHub Action  

### 7.3 Telegram Commands  
```
/run_population_dashboard
/get_latest_preview
/get_latest_html
/check_data
/check_ui
```

---

## 8. Publishing Workflow (LinkedIn‑Optimized)

### 8.1 Steps  
1. Upload **MP4 preview** directly to LinkedIn  
2. Add screenshot thumbnail  
3. Add caption  
4. Put HTML link in comments (not main post)  
5. Optionally include GIF for messaging apps  

### 8.2 Why this works  
- Native video auto‑plays  
- Higher engagement  
- No fear of unknown URLs  
- HTML link still available for deeper exploration  

---

## 9. Phase‑Based To‑Do List (with timestamps)

### Phase 1 — ETL (5 Mar 2026)
- Implement `01_fetch_population.py`  
- Implement `02_transform_rank_top50.py`  
- Save processed CSV with timestamp  

### Phase 2 — Visualization (5 Mar 2026)
- Build Plotly bar‑race  
- Add SVG flags  
- Add 1M/1B formatting  
- Add responsive layout  
- Generate timestamped HTML  

### Phase 3 — QA Agents (6 Mar 2026)
- Implement Data QA agent  
- Implement UI QA agent  
- Implement Code Review agent  

### Phase 4 — GIF/MP4 Preview (6 Mar 2026)
- Implement preview generator  
- Export MP4 + GIF  

### Phase 5 — Orchestrator (7 Mar 2026)
- Implement orchestrator agent  
- Integrate all scripts  
- Integrate QA agents  
- Integrate publishing logic  

### Phase 6 — OpenClaw/Telegram (Day‑2)
- Add Telegram command triggers  
- Add notification pipeline  
- Add remote execution  

---

## 10. Final Notes

- All filenames must use **human‑friendly timestamps** (e.g., `3Mar2026`).  
- All scripts must be modular and agent‑friendly.  
- All QA outputs must be timestamped for traceability.  
- All HTML/GIF/MP4 outputs must be stored under `reports/`.  


