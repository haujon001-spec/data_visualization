Project1 = C:\Users\haujo\projects\DEV\Data_visualization\world_populations
```

---

# Phase 2 — Visualization Design  
**Project:** Global Economic Health Dashboard  
**Folder:** `data_visualization/global_economic_health/`  
**Phase:** 2 — Visualization  
**Status:** Ready for agent implementation  
**Dependencies:**  
- Phase 1 ETL outputs  
- Reuse population trendline visualization from Project 1  
- New bubble‑map visualization for GDP + Debt  

---

## 1. Phase Objective

This phase produces all visual components for the Global Economic Health Dashboard. It must follow the same architecture as Project 1:

- Background agent implements visualization scripts  
- Local agent verifies correctness  
- Cloud agent renders heavy visualizations  
- QA agents validate chart accuracy  
- Verification layer enforces compliance  

The dashboard will combine **bubble‑map visuals**, **population trendlines**, and **macro‑economic indicators** into a unified HTML output.

---

## 2. Visualization Architecture Overview

### Required Visual Components  
1. **Global Bubble Map (Crypto‑Bubble Style)**  
   - Bubble size = GDP  
   - Bubble color = debt‑to‑GDP ratio or GDP growth  
   - Tooltip = GDP, population, debt, growth  
   - Year slider = 1970 → present  
   - Interactive hover, zoom, pan  

2. **Population Trendline Visualization (Reused)**  
   - Reuse Project 1’s v2 or v3 trendline visualization  
   - Top 15 countries  
   - Trendlines + growth rates  
   - Optional animation  

3. **Optional Panels**  
   - GDP growth bar‑race  
   - Debt‑to‑GDP choropleth  
   - Country profile panel  

4. **Unified HTML Dashboard**  
   - Multi‑chart layout  
   - Dark theme  
   - Responsive design  
   - Timestamped filename  

---

## 3. Script Requirements

### 3.1 Script: `05_build_bubble_map.py`  
**Purpose:** Create an interactive global bubble map.

**Inputs:**  
- `macro_final_<timestamp>.csv`  
- `map_geojson.json`  
- `iso_country_codes.csv`  

**Outputs:**  
- Plotly figure object  
- Saved HTML snippet or full HTML  

**Visualization Rules:**  
- Bubble size = GDP (scaled using bubble_scaling.yaml)  
- Bubble color = debt‑to‑GDP ratio  
- Tooltip must show:  
  - Country  
  - GDP (formatted)  
  - Population (formatted)  
  - Debt (formatted)  
  - Debt‑to‑GDP ratio  
  - GDP growth  
- Year slider must update bubble sizes and colors  
- Map must use a neutral dark theme  
- Bubbles must not overlap excessively (use jitter or scaling)  

**Scaling Rules:**  
- Use logarithmic scaling for GDP  
- Use diverging color scale for debt‑to‑GDP  
- Use consistent bubble sizes across years  

---

### 3.2 Script: `06_build_population_trendline.py`  
**Purpose:** Reuse population trendline visualization from Project 1.

**Implementation:**  
Copy or reference:

```
world_populations/scripts/05_build_visualization_v3_animated_trendline.py
```

**Modifications:**  
- Input path must point to Project 2 population CSV  
- Output path must point to Project 2 reports/html  
- Title updated to reflect Project 2 context  
- Optional: remove animation if needed  

**Outputs:**  
- `population_trendline_<timestamp>.html`  
- Plotly figure object  

---

### 3.3 Script: `07_generate_html_dashboard.py`  
**Purpose:** Combine all visual components into a single HTML dashboard.

**Inputs:**  
- Bubble map figure  
- Population trendline figure  
- Optional additional charts  

**Outputs:**  
- `reports/html/global_economic_health_dashboard_<timestamp>.html`  

**Layout Requirements:**  
- Two‑column layout on desktop  
- Single‑column layout on mobile  
- Sticky header with year slider  
- Dark theme  
- Embedded Plotly JS  
- No external dependencies  

**Sections:**  
- Header (title, timestamp, description)  
- Bubble map  
- Population trendline  
- Optional panels  
- Footer (data sources, version, timestamp)  

---

### 3.4 Script: `08_generate_previews.py`  
**Purpose:** Generate MP4 + GIF previews for social media.

**Inputs:**  
- Bubble map frames  
- Trendline frames  

**Outputs:**  
- `reports/media/global_economic_health_preview_<timestamp>.gif`  
- `reports/media/global_economic_health_preview_<timestamp>.mp4`  

**Rules:**  
- 720p resolution  
- 10–15 seconds  
- 10–24 FPS  
- Optimized palette for GIF  
- Must pass preview QA  

---

## 4. Visualization QA Requirements

### 4.1 UI QA Agent (`agent_ui_qa.py`)  
Must validate:

- Bubble sizes match GDP values  
- Bubble colors match debt‑to‑GDP ratio  
- Year slider updates correctly  
- Trendlines match underlying data  
- No missing countries  
- No overlapping labels  
- No broken tooltips  
- HTML loads without errors  
- Mobile responsiveness  

### 4.2 QA Output  
- `reports/qa/ui_qa_report_<timestamp>.md`  
- Screenshots in `reports/screenshots/`  

---

## 5. Verification Layer Requirements

### 5.1 `verify_visualization.py`  
Must check:

- Bubble map HTML exists  
- Trendline HTML exists  
- All required DOM elements present  
- Year slider present  
- Plotly JS embedded  
- No missing data in tooltips  
- Bubble sizes and colors match expected ranges  

### 5.2 `verify_code_structure.py`  
Must check:

- Scripts exist:  
  - `05_build_bubble_map.py`  
  - `06_build_population_trendline.py`  
  - `07_generate_html_dashboard.py`  
  - `08_generate_previews.py`  
- Required functions exist  
- No hard‑coded paths  

---

## 6. Orchestrator Integration

Visualization steps must run in this order:

1. Build bubble map  
2. Build population trendline (reused)  
3. Generate unified HTML dashboard  
4. Run UI QA  
5. Generate previews  
6. Verification layer  

If any step fails, orchestrator must stop immediately.

---

## 7. Heartbeat Requirements

- Background agent must send heartbeat every 5 seconds  
- Cloud agent must send orchestrator heartbeat  
- Local agent must timeout after 60 seconds  
- All events logged to audit trail  

---

## 8. Deliverables for Phase 2

- All visualization scripts implemented  
- Bubble map HTML  
- Population trendline HTML  
- Unified dashboard HTML  
- MP4 + GIF previews  
- UI QA report  
- Verification summary  

---

If you want, I can now generate **Phase 3 — QA Agents Design**, covering:

- Data QA  
- UI QA  
- Code Review QA  
- Orchestrator QA  
- Verification layer integration
