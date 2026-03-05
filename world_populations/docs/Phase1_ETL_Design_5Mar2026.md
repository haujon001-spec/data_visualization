
---

# Phase 1 — ETL Design (5 Mar 2026)

## 1. Purpose of Phase 1
This phase defines the complete ETL architecture for generating a **clean, validated, agent‑ready dataset** of the **Top 50 most populous countries** from **1970 → present year**. The output of this phase becomes the foundation for:

- Visualization (Phase 2)  
- Data QA (Phase 3)  
- UI QA (Phase 3)  
- GIF/MP4 preview generation (Phase 4)  
- Full orchestrator automation (Phase 5)  
- OpenClaw/Telegram remote control (Day 2)  

The ETL must be deterministic, timestamped, reproducible, and compatible with your strict folder structure.

---

## 2. Data Source Specification

### 2.1 Primary Source  
**World Bank Open Data API**  
Indicator: `SP.POP.TOTL` (Total Population)

API endpoint:  
`https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000`

### 2.2 Data Characteristics  
- Annual population values  
- Coverage from 1960 → present  
- Includes aggregates (must be removed)  
- Uses ISO‑3 country codes  
- Stable and consistent methodology  
- No corporate actions, splits, or dilution  
- Ideal for long‑term ranking animations  

### 2.3 Required Time Range  
**1970 → Current Year**  
The current year is dynamically detected at runtime.

---

## 3. ETL Architecture Overview

### 3.1 Pipeline Stages  
1. **Extract**  
   - Fetch raw JSON from World Bank API  
   - Save raw CSV with timestamp  

2. **Transform**  
   - Normalize fields  
   - Filter out aggregates  
   - Convert population to integers  
   - Filter years 1970 → present  
   - Rank countries per year  
   - Keep Top 50  

3. **Load**  
   - Save processed CSV with timestamp  
   - Store under `csv/processed/`  

### 3.2 Output Files  
- Raw:  
  `csv/raw/worldbank_population_raw_<3Mar2026>.csv`  
- Processed:  
  `csv/processed/population_top50_1970_now_<3Mar2026>.csv`

### 3.3 Timestamp Format  
Human‑friendly, as requested:  
`<3Mar2026>`

---

## 4. Extract Stage Design

### 4.1 Script  
`scripts/01_fetch_population.py`

### 4.2 Responsibilities  
- Call World Bank API  
- Handle pagination  
- Retry on network errors  
- Normalize JSON into tabular rows  
- Save raw CSV with timestamp  

### 4.3 Raw CSV Schema  
| Column | Description |
|--------|-------------|
| country_code | ISO‑3 code from API |
| country_name | Country name |
| year | Year (int) |
| population | Raw population value (may be float or null) |

### 4.4 Required Validations  
- API returns HTTP 200  
- JSON structure matches expected schema  
- At least 50 countries per year  
- No missing `country_code` or `year`  

### 4.5 Failure Handling  
- Log error  
- Save partial file for debugging  
- Orchestrator stops and notifies via Telegram  

---

## 5. Transform Stage Design

### 5.1 Script  
`scripts/02_transform_rank_top50.py`

### 5.2 Responsibilities  
- Load raw CSV  
- Remove aggregate regions (e.g., “World”, “High income”)  
- Filter years 1970 → present  
- Convert population to integer  
- Remove rows with null population  
- Rank each year by population  
- Keep Top 50 per year  
- Save processed CSV with timestamp  

### 5.3 Aggregate Regions to Exclude  
Any country_code in:

- `WLD` (World)  
- `HIC` (High income)  
- `LIC` (Low income)  
- `ECS`, `EAS`, `MEA`, etc.  
- All non‑sovereign aggregates  

### 5.4 Processed CSV Schema  
| Column | Description |
|--------|-------------|
| country_code | ISO‑3 code |
| country_name | Cleaned country name |
| year | Year (int) |
| population | Integer population |
| rank | Rank within that year (1–50) |

### 5.5 Ranking Logic  
For each year:

```
Sort by population descending
Assign rank = 1..50
Keep rows where rank ≤ 50
```

### 5.6 Required Validations  
- Exactly 50 rows per year  
- No duplicate country/year pairs  
- No negative population values  
- No aggregates  
- No missing population values  

---

## 6. File Naming and Storage Rules

### 6.1 Raw Data  
`csv/raw/worldbank_population_raw_<3Mar2026>.csv`

### 6.2 Processed Data  
`csv/processed/population_top50_1970_now_<3Mar2026>.csv`

### 6.3 Naming Requirements  
- Must use human‑friendly timestamp  
- Must never overwrite previous files  
- Must be orchestrator‑friendly  
- Must be QA‑friendly  

---

## 7. Integration with QA Agents

### 7.1 Data QA Agent  
`qa_agents/agent_data_qa.py`

### 7.2 Inputs  
- Processed CSV  
- Metadata: expected years, expected row counts  

### 7.3 Checks  
- 50 rows per year  
- No missing values  
- No aggregates  
- No duplicates  
- Year‑over‑year sanity checks  
- Population > 0  

### 7.4 Output  
`reports/qa/data_qa_report_<3Mar2026>.json`

### 7.5 Orchestrator Behavior  
- If PASS → continue  
- If FAIL → stop + notify via Telegram  

---

## 8. Integration with Later Phases

### 8.1 Phase 2 Visualization  
The processed CSV becomes the input for:

- SVG flag mapping  
- 1M/1B formatting  
- Horizontal bar‑race animation  
- Timestamped HTML generation  

### 8.2 Phase 3 QA  
UI QA agent will validate:

- Flags  
- Number formatting  
- Layout  
- Responsiveness  

### 8.3 Phase 4 GIF/MP4  
The processed CSV drives the animation frames.

### 8.4 Phase 5 Orchestrator  
The orchestrator will:

- Run ETL  
- Run QA  
- Build visualization  
- Generate HTML  
- Generate GIF/MP4  
- Publish  
- Notify via Telegram  

---

## 9. Phase 1 To‑Do List (5 Mar 2026)

- Create `01_fetch_population.py`  
- Create `02_transform_rank_top50.py`  
- Implement timestamp logic  
- Implement aggregate filtering  
- Implement ranking logic  
- Save raw + processed CSVs  
- Validate ETL output manually once  
- Prepare for Data QA agent integration  

---

