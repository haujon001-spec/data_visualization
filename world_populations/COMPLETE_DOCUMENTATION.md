# 📊 World Population Dashboard - Complete Script & Path Documentation

**Creator**: John Hau  
**Project**: World Population Dashboard v1-v3  
**Date Created**: March 7, 2026  
**Status**: ✅ Complete

---

## 🗂️ Complete Folder Structure

```
c:\Users\haujo\projects\DEV\Data_visualization\world_populations\
├── csv/
│   ├── raw/                                    # ETL Input (World Bank API)
│   │   └── worldbank_population_raw_*.csv    # Raw data from API
│   └── processed/
│       └── population_top50_1970_now_5Mar2026.csv  # Filtered & ranked data
├── reports/
│   └── html/                                  # Final HTML outputs
│       ├── population_bar_race_05Mar2026.html
│       ├── population_trendline_07Mar2026.html
│       └── population_animated_trendline_07Mar2026.html
├── scripts/
│   ├── 01_fetch_population.py                 # ETL: Fetch from World Bank API
│   ├── 02_transform_rank_top50.py             # ETL: Transform & rank top 50
│   ├── 03_build_visualization.py              # v1: Bar race animation
│   ├── 04_build_visualization_v2_with_trendline.py        # v2: Static trendlines
│   └── 05_build_visualization_v3_animated_trendline.py    # v3: Animated trendlines
└── config/
    └── settings.yaml                          # Project configuration
```

---

## 🔄 ETL Pipeline (Data Extraction & Transformation)

### **SCRIPT 1: Data Fetching**
**File**: `scripts/01_fetch_population.py`  
**Creator**: John Hau  
**Purpose**: Fetch world population data from Public World Bank API

```python
# Function: fetch_worldbank_population()
# Indicator: SP.POP.TOTL (Total Population)
# Years: 1960-2024 (using API)
# Source: https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL
```

**Output**:
```
csv/raw/worldbank_population_raw_*.csv
├── country_name (e.g., "China", "India")
├── country_code (e.g., "CHN", "IND")
├── year (1960-2024)
└── population (numeric value)
```

**Execution**:
```bash
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
python scripts/01_fetch_population.py
```

---

### **SCRIPT 2: Data Transformation & Ranking**
**File**: `scripts/02_transform_rank_top50.py`  
**Creator**: John Hau  
**Purpose**: Filter top 50 countries, add ranking, clean data

```python
# Function: filter_top50_per_year()
# Inputs: Raw CSV from World Bank API
# Process:
#   1. Load raw data
#   2. Exclude aggregate regions (using config/aggregate_regions_exclude.csv)
#   3. Filter to top 50 countries per year
#   4. Add rank column (sorted by population descending)
#   5. Validate data quality
```

**Output**:
```
csv/processed/population_top50_1970_now_5Mar2026.csv
├── country_name
├── country_code
├── year
├── population
└── rank (1-50)
```

**Data Shape**: 3,250 records (50 countries × 65 years: 1960-2024)

**Execution**:
```bash
python scripts/02_transform_rank_top50.py
```

---

## 📈 Visualization Pipeline (3 Versions)

### **VERSION 1: Bar Race Animation** 🎬
**File**: `scripts/03_build_visualization.py`  
**Creator**: John Hau  
**Purpose**: Animated bar race showing country rankings over time

**Input**:
```
csv/processed/population_top50_1970_now_5Mar2026.csv
```

**Process**:
1. Load processed population data
2. Load country code mappings
3. Add flag URLs for each country
4. Create animated bar chart (30 countries per frame)
5. Add play/pause controls and year slider
6. Format numbers with SI suffix (M for millions, B for billions)

**Output**:
```
reports/html/population_bar_race_05Mar2026.html
├── Size: ~5-6 MB
├── Frames: 65 (one per year)
├── Countries: 30
└── Animation: 3.3 fps (20 seconds total)
```

**Execution**:
```bash
python scripts/03_build_visualization.py
```

**Key Features**:
- Play/Pause buttons
- Year slider for scrubbing
- Country flag icons
- Hover tooltips with exact populations
- Dark theme with SI number formatting

**Run as Task**:
```
VS Code: Ctrl+Shift+P → "Run Task" → "Python: Run Visualization"
```

---

### **VERSION 2: Static Trendlines** 📊
**File**: `scripts/04_build_visualization_v2_with_trendline.py`  
**Creator**: John Hau (Mar 7, 2026)  
**Purpose**: Show population trends with polynomial trendlines

**Input**:
```
csv/processed/population_top50_1970_now_5Mar2026.csv
```

**Process**:
1. Load population data for top 15 countries
2. Calculate year-over-year growth rates
3. Fit polynomial trendlines (degree 2 / quadratic)
4. Create dual-panel visualization:
   - Panel 1: Population trends + trendlines (solid lines)
   - Panel 2: Year-over-year growth rates
5. Format Y-axis in billions (1B, 1.2B, 1.4B)

**Output**:
```
reports/html/population_trendline_07Mar2026.html
├── Size: ~7-8 MB
├── Countries: 15
├── Time Range: 1960-2024
└── Panels: 2 (population + growth rate)
```

**Execution**:
```bash
python scripts/04_build_visualization_v2_with_trendline.py
```

**Key Features**:
- Solid trendlines (not dashed)
- Y-axis shows billions: 1B, 1.2B, 1.4B
- Growth rate analysis panel
- Interactive hover with exact values
- Legend toggling by country
- Zoom/pan capabilities

**Run as Task**:
```
VS Code: Ctrl+Shift+P → "Run Task" → "Population: Dashboard v2 with Trendlines"
```

---

### **VERSION 3: Animated Growing Trendlines** 🎬📈
**File**: `scripts/05_build_visualization_v3_animated_trendline.py`  
**Creator**: John Hau (Mar 7, 2026)  
**Purpose**: Watch trendlines grow as years accumulate (65-year animation)

**Input**:
```
csv/processed/population_top50_1970_now_5Mar2026.csv
```

**Process**:
1. Load population data
2. Create 65 animation frames (one per year)
3. For each frame:
   - Collect data from year 1 through current year
   - Recalculate polynomial trendline (cumulative)
   - Plot actual + trend with solid lines
4. Format Y-axis in billions
5. Add play/pause controls and year slider

**Output**:
```
reports/html/population_animated_trendline_07Mar2026.html
├── Size: ~9-10 MB
├── Frames: 65 (one per year)
├── Countries: 15
├── Animation: 5 fps (13 seconds total)
└── Trendlines: Recalculated each frame
```

**Execution**:
```bash
python scripts/05_build_visualization_v3_animated_trendline.py
```

**Key Features**:
- Trendlines grow dynamically as more data accumulates
- Solid trendlines (not dashed)
- Y-axis in billions: 1B, 1.2B, 1.4B
- Play/Pause & Year Slider controls
- Interactive legend
- Smooth 5 fps animation

**Run as Task**:
```
VS Code: Ctrl+Shift+P → "Run Task" → "Population: Dashboard v3 Animated Growing Trendlines"
```

---

## 📊 Data Flow Diagram

```
┌──────────────────────────────┐
│  World Bank API              │
│  (SP.POP.TOTL indicator)     │
│  Years: 1960-2024            │
└──────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ Script 01: fetch_population.py       │
│ Input: World Bank API endpoint       │
│ Output: csv/raw/worldbank_*.csv      │
│ - country_code, country_name         │
│ - year, population                   │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ Script 02: transform_rank_top50.py   │
│ Input: csv/raw/worldbank_*.csv       │
│ Process:                             │
│   - Filter top 50 countries          │
│   - Add rank per year                │
│   - Validate data                    │
│ Output: csv/processed/*.csv          │
│ - 3,250 records (50 × 65 years)      │
└──────────────────────────────────────┘
              ↓
    ┌─────────┴─────────┬──────────────┐
    ↓                   ↓              ↓
    │                   │              │
┌───────────┐  ┌──────────────┐  ┌──────────────┐
│ Script 03 │  │ Script 04    │  │ Script 05    │
│ Bar Race  │  │ Trendlines   │  │ Animated     │
│ v1        │  │ v2 (Static)  │  │ v3 (Dynamic) │
└───────────┘  └──────────────┘  └──────────────┘
    ↓                   ↓              ↓
┌───────────────────────────────────────────┐
│     reports/html/                         │
├───────────────────────────────────────────┤
│ population_bar_race_05Mar2026.html        │
│ population_trendline_07Mar2026.html       │
│ population_animated_trendline_07Mar2026.html │
└───────────────────────────────────────────┘
```

---

## 🔧 Script Execution Commands

### **Run ETL Pipeline**
```bash
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations

# Step 1: Fetch data
python scripts/01_fetch_population.py

# Step 2: Transform & rank
python scripts/02_transform_rank_top50.py
```

### **Run All Visualizations**
```bash
# v1: Bar race
python scripts/03_build_visualization.py

# v2: Static trendlines
python scripts/04_build_visualization_v2_with_trendline.py

# v3: Animated trendlines
python scripts/05_build_visualization_v3_animated_trendline.py
```

### **Run Specific Visualization**
```bash
# Just v3 (animated)
python scripts/05_build_visualization_v3_animated_trendline.py
```

### **Via PowerShell**
```powershell
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
c:\Users\haujo\projects\DEV\Data_visualization\.venv\Scripts\python.exe scripts/05_build_visualization_v3_animated_trendline.py
```

---

## 📁 Input & Output Paths Summary

| Component | Path | Format | Description |
|-----------|------|--------|-------------|
| **Input CSV** | `csv/processed/population_top50_1970_now_5Mar2026.csv` | CSV | Processed data (3,250 rows) |
| **Output v1** | `reports/html/population_bar_race_05Mar2026.html` | HTML | Bar race animation |
| **Output v2** | `reports/html/population_trendline_07Mar2026.html` | HTML | Static trendlines |
| **Output v3** | `reports/html/population_animated_trendline_07Mar2026.html` | HTML | Animated growing trendlines |
| **Config** | `config/settings.yaml` | YAML | Project settings |

---

## 📊 Data Specifications

### **Input Data**: `population_top50_1970_now_5Mar2026.csv`
```
country_name,country_code,year,population,rank
China,CHN,1960,667070000,1
India,IND,1960,435990338,2
...
```

**Columns**:
- `country_name`: Full country name
- `country_code`: ISO-3 country code (CHN, IND, USA, etc.)
- `year`: Year (1960-2024)
- `population`: Total population (numeric)
- `rank`: Ranking by population (1-50)

**Rows**: 3,250 (50 countries × 65 years)  
**Date Range**: 1960-2024 (65 years)

---

## 🎨 Visualization Specifications

### **Version 1: Bar Race**
- Type: Animated horizontal bar chart
- Countries: Top 30
- Frames: 65 (annual)
- Frame Rate: 3.3 fps
- Duration: ~20 seconds
- Key Feature: Rankings change dynamically

### **Version 2: Trendlines (Static)**
- Type: Dual-panel line chart
- Countries: Top 15
- Panels: 2 (Population + Growth Rate)
- Time Range: Full (1960-2024)
- Key Feature: Solid trendlines, billions Y-axis

### **Version 3: Trendlines (Animated)**
- Type: Animated line chart with growing trendlines
- Countries: Top 15
- Frames: 65 (annual)
- Frame Rate: 5 fps
- Duration: ~13 seconds
- Key Feature: Trendlines recalculated each frame

---

## 🔍 File Naming Convention

**Pattern**: `{description}_{DDMmmYYYY}.html`

Examples:
- `population_bar_race_05Mar2026.html` (Created: March 5, 2026)
- `population_trendline_07Mar2026.html` (Created: March 7, 2026)
- `population_animated_trendline_07Mar2026.html` (Created: March 7, 2026)

**Date Format**: DDMmmYYYY
- DD: Day (05, 07, etc.)
- Mmm: Month (Mar, Apr, etc.)
- YYYY: Year (2026)

---

## 👤 Creator Information

**Name**: John Hau  
**Email**: (As configured in project)  
**Team**: Analytics & Data Visualization  
**Date**: March 7, 2026

**Scripts Created**:
1. ✅ `01_fetch_population.py` - ETL: Data fetching
2. ✅ `02_transform_rank_top50.py` - ETL: Data transformation
3. ✅ `03_build_visualization.py` - v1: Bar race animation
4. ✅ `04_build_visualization_v2_with_trendline.py` - v2: Trendlines (Mar 7, 2026)
5. ✅ `05_build_visualization_v3_animated_trendline.py` - v3: Animated (Mar 7, 2026)

---

## 📋 Version Comparison

| Feature | v1 (Bar Race) | v2 (Trendlines) | v3 (Animated) |
|---------|:---:|:---:|:---:|
| Animation | ✅ | ❌ | ✅ |
| Trendlines | ❌ | ✅ Solid | ✅ Solid |
| Growth Rates | ❌ | ✅ Panel | 🔄 Implicit |
| Y-axis Billions | ✅ | ✅ | ✅ |
| Countries | 30 | 15 | 15 |
| Time Range | Full | Full | Full |
| Best For | Rankings | Analysis | Learning |

---

## 🚀 Quick Start

1. **View v3 (Latest - Animated)**:
   ```
   Open: reports/html/population_animated_trendline_07Mar2026.html
   ```

2. **Regenerate All**:
   ```bash
   cd world_populations
   python scripts/05_build_visualization_v3_animated_trendline.py
   ```

3. **Run via VS Code Task**:
   - Press: `Ctrl+Shift+P`
   - Type: `Run Task`
   - Select: `Population: Dashboard v3 Animated Growing Trendlines`

---

**Status**: ✅ Complete & Documented  
**Last Updated**: March 7, 2026  
**Creator**: John Hau
