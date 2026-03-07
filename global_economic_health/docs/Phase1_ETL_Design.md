Here is a complete **Phase 1 — ETL Design** for **Project 2: `global_economic_health`**, written in the same structure, tone, and level of detail as the Phase documents in your `world_populations` project. It is designed so that:

- VS Code’s **local agent** can interpret it as a specification  
- The **background agent** can implement scripts directly from it  
- The **cloud agent** can run the orchestrator using these outputs  
- The **verification layer** can validate correctness  
- The **heartbeat model** ensures no ETL task is left incomplete  
- **Population ETL is reused** from Project 1 to save time  

Project 1  = C:\Users\haujo\projects\DEV\Data_visualization\world_populations

---

# Phase 1 — ETL Design  
**Project:** Global Economic Health Dashboard  
**Folder:** `data_visualization/global_economic_health/`  
**Phase:** 1 — Extract, Transform, Load  
**Status:** Ready for agent implementation  
**Dependencies:** Reuse population ETL from Project 1 (`world_populations`)  

---

## 1. Phase Objective

This phase builds the **complete ETL foundation** for the Global Economic Health Dashboard by:

- Fetching **GDP**, **Population**, and **Debt** data  
- Reusing population ETL scripts from Project 1  
- Merging all three datasets into a unified macro‑economic table  
- Producing clean, validated, timestamped CSV outputs  
- Ensuring all ETL steps pass **Data QA** and **Verification Layer** checks  

This phase must follow the same agent‑orchestrated workflow as Project 1:

- Local agent creates task manifests  
- Background agent implements ETL scripts  
- Local agent verifies outputs  
- Cloud agent executes orchestrator  
- Heartbeat ensures no task stalls  

---

## 2. ETL Architecture Overview

### Data Sources  
| Metric | Source | Indicator | Notes |
|--------|--------|-----------|-------|
| **GDP** | World Bank | `NY.GDP.MKTP.CD` | Nominal GDP in USD |
| **Population** | World Bank | `SP.POP.TOTL` | Reuse Project 1 scripts |
| **Debt** | IMF Global Debt Database | Public + private debt | CSV download |

### Output Tables  
1. **Raw tables**  
   - `gdp_raw_<timestamp>.csv`  
   - `population_raw_<timestamp>.csv` (reused)  
   - `debt_raw_<timestamp>.csv`  

2. **Processed tables**  
   - `macro_merged_<timestamp>.csv`  
   - `macro_clean_<timestamp>.csv`  

3. **Final table for visualization**  
   - `macro_final_<timestamp>.csv`  

---

## 3. Script Requirements

### 3.1 Script: `01_fetch_gdp.py`  
**Purpose:** Fetch GDP data from World Bank API.

**Inputs:**  
- World Bank API endpoint  
- Indicator: `NY.GDP.MKTP.CD`  
- Years: 1960–2026  

**Outputs:**  
- `csv/raw/gdp_raw_<timestamp>.csv`  
  Columns:  
  - `country_name`  
  - `country_code` (ISO‑3)  
  - `year`  
  - `gdp_usd`  

**Key Requirements:**  
- Must retry on API failure  
- Must validate JSON structure  
- Must exclude aggregates (same list as Project 1)  
- Must log fetch count and missing values  

---

### 3.2 Script: `02_fetch_population.py` (REUSED)  
**Purpose:** Reuse Project 1’s population fetch script.

**Implementation:**  
Copy or reference:

```
world_populations/scripts/01_fetch_population.py
```

**Output:**  
- `csv/raw/population_raw_<timestamp>.csv`

**Notes:**  
- No modification needed  
- Local agent must verify script integrity  
- Background agent should not regenerate this script  

---

### 3.3 Script: `03_fetch_debt.py`  
**Purpose:** Fetch global debt data from IMF GDD.

**Inputs:**  
- IMF Global Debt Database CSV  
- Columns vary by year; must normalize  

**Outputs:**  
- `csv/raw/debt_raw_<timestamp>.csv`  
  Columns:  
  - `country_name`  
  - `country_code`  
  - `year`  
  - `debt_total_usd`  
  - `debt_public_usd`  
  - `debt_private_usd`  

**Key Requirements:**  
- Must normalize country names to ISO‑3  
- Must convert debt values to USD if needed  
- Must handle missing years gracefully  
- Must log coverage per country  

---

### 3.4 Script: `04_transform_merge_clean.py`  
**Purpose:** Merge GDP + Population + Debt into a unified dataset.

**Inputs:**  
- `gdp_raw_<timestamp>.csv`  
- `population_raw_<timestamp>.csv`  
- `debt_raw_<timestamp>.csv`  

**Outputs:**  
- `csv/processed/macro_merged_<timestamp>.csv`  
- `csv/processed/macro_clean_<timestamp>.csv`  
- `csv/processed/macro_final_<timestamp>.csv`  

**Transformations:**  
- Inner join on `country_code` + `year`  
- Remove aggregates  
- Remove rows with missing GDP or population  
- Compute derived metrics:  
  - `gdp_per_capita = gdp_usd / population`  
  - `debt_to_gdp = debt_total_usd / gdp_usd`  
  - `population_growth = pct_change(population)`  
  - `gdp_growth = pct_change(gdp_usd)`  
  - `debt_growth = pct_change(debt_total_usd)`  

**Cleaning Rules:**  
- Drop rows where `debt_to_gdp > 10` (likely data error)  
- Drop rows where `population < 10,000`  
- Forward‑fill missing debt values for stable countries  
- Ensure all numeric columns are numeric  

---

## 4. Data QA Requirements

### 4.1 Data QA Agent (`agent_data_qa.py`)  
Must validate:

- Schema correctness  
- No missing ISO‑3 codes  
- No missing years between 1960–2026  
- GDP > 0  
- Population > 0  
- Debt >= 0  
- `debt_to_gdp` between 0 and 5  
- Growth rates between −50% and +200%  
- No duplicate rows  

### 4.2 QA Output  
- `reports/qa/data_qa_report_<timestamp>.json`  
- `reports/qa/data_qa_summary_<timestamp>.md`  

---

## 5. Verification Layer Requirements

### 5.1 `verify_outputs.py`  
Must check:

- All required CSVs exist  
- All required columns exist  
- Row counts match expected ranges  
- No NaN in critical fields  
- No invalid country codes  
- No impossible values (negative GDP, negative population)  

### 5.2 `verify_code_structure.py`  
Must check:

- Scripts exist:  
  - `01_fetch_gdp.py`  
  - `02_fetch_population.py` (reused)  
  - `03_fetch_debt.py`  
  - `04_transform_merge_clean.py`  
- Required functions exist  
- No missing imports  
- No hard‑coded paths  

---

## 6. Orchestrator Integration

The orchestrator must run ETL in this order:

1. `01_fetch_gdp.py`  
2. `02_fetch_population.py` (reused)  
3. `03_fetch_debt.py`  
4. `04_transform_merge_clean.py`  
5. Data QA  
6. Verification layer  

If any step fails, orchestrator must stop immediately.

---

## 7. Heartbeat Requirements

- Background agent must send heartbeat every 5 seconds  
- Local agent must timeout after 60 seconds  
- Cloud agent must send orchestrator heartbeat  
- All events logged to `audit_trail/`  

---

## 8. Deliverables for Phase 1

- All ETL scripts implemented  
- All raw and processed CSVs generated  
- Data QA report  
- Verification summary  
- Orchestrator ETL section validated  

---

