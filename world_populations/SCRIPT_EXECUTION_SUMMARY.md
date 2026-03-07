# 🎯 Script Execution & Output Summary

**Creator**: John Hau  
**Date**: March 7, 2026

---

## 📊 What Scripts Ran & What They Produced

### **ETL: Data Pipeline**

#### **Step 1: Fetch Population Data**
```
Script: scripts/01_fetch_population.py
Creator: John Hau
Purpose: Extract world population from World Bank API
Input: World Bank API endpoint (SP.POP.TOTL indicator)
Output: csv/raw/worldbank_population_raw_5Mar2026.csv
Data: All countries, years 1960-2024
```

**Run Command**:
```bash
python scripts/01_fetch_population.py
```

---

#### **Step 2: Transform & Rank (Top 50)**
```
Script: scripts/02_transform_rank_top50.py
Creator: John Hau
Purpose: Filter and rank top 50 countries per year
Input: csv/raw/worldbank_population_raw_5Mar2026.csv (from Step 1)
Process:
  ✓ Load raw data
  ✓ Exclude aggregate regions
  ✓ Filter to top 50 countries per year
  ✓ Add rank column (1-50)
  ✓ Validate quality
Output: csv/processed/population_top50_1970_now_5Mar2026.csv
Data: 50 countries × 65 years = 3,250 records
```

**Run Command**:
```bash
python scripts/02_transform_rank_top50.py
```

---

## 📺 Visualization Scripts & HTML Outputs

### **Version 1: Bar Race Animation**

```
Script: scripts/03_build_visualization.py
Creator: John Hau
Purpose: Animated bar race ranking chart
Input: csv/processed/population_top50_1970_now_5Mar2026.csv
Process:
  ✓ Load processed data
  ✓ Load country flag mappings
  ✓ Create 65 animation frames (1 per year)
  ✓ Build bar race with play/pause
  ✓ Add year slider
Output: reports/html/population_bar_race_05Mar2026.html
File Size: ~5-6 MB
Features: Rankings change year by year, 30 countries visible
```

**Run Command**:
```bash
python scripts/03_build_visualization.py
```

**Output Path**:
```
c:\Users\haujo\projects\DEV\Data_visualization\world_populations\reports\html\population_bar_race_05Mar2026.html
```

---

### **Version 2: Static Trendlines**

```
Script: scripts/04_build_visualization_v2_with_trendline.py
Creator: John Hau (Updated: Mar 7, 2026)
Purpose: Population trends with polynomial trendlines
Input: csv/processed/population_top50_1970_now_5Mar2026.csv
Process:
  ✓ Load top 15 countries
  ✓ Calculate YoY growth rates
  ✓ Fit quadratic trendlines
  ✓ Create dual-panel layout:
    Panel 1: Population + Solid trendlines
    Panel 2: Growth rate analysis
  ✓ Format Y-axis: 1B, 1.2B, 1.4B
Output: reports/html/population_trendline_07Mar2026.html
File Size: ~7-8 MB
Features: Solid trendlines, billions format, growth rates
```

**Run Command**:
```bash
python scripts/04_build_visualization_v2_with_trendline.py
```

**Output Path**:
```
c:\Users\haujo\projects\DEV\Data_visualization\world_populations\reports\html\population_trendline_07Mar2026.html
```

---

### **Version 3: Animated Growing Trendlines**

```
Script: scripts/05_build_visualization_v3_animated_trendline.py
Creator: John Hau (Updated: Mar 7, 2026)
Purpose: Watch trendlines grow as years accumulate
Input: csv/processed/population_top50_1970_now_5Mar2026.csv
Process:
  ✓ Load top 15 countries
  ✓ Create 65 animation frames (1 per year, 1960-2024)
  ✓ For each frame:
    - Compile data from 1960 to current year (cumulative)
    - Recalculate polynomial trendline
    - Plot with solid lines (not dashed)
  ✓ Format Y-axis: 1B, 1.2B, 1.4B
  ✓ Add play/pause controls
  ✓ Add year slider
Output: reports/html/population_animated_trendline_07Mar2026.html
File Size: ~9-10 MB
Features: Dynamic trendlines, solid lines, play/pause, billions
```

**Run Command**:
```bash
python scripts/05_build_visualization_v3_animated_trendline.py
```

**Output Path**:
```
c:\Users\haujo\projects\DEV\Data_visualization\world_populations\reports\html\population_animated_trendline_07Mar2026.html
```

---

## 📂 Complete File Paths

### **Input Data (ETL Output)**
```
c:\Users\haujo\projects\DEV\Data_visualization\world_populations\csv\processed\population_top50_1970_now_5Mar2026.csv
```

### **HTML Chart Outputs** (All in same folder)
```
c:\Users\haujo\projects\DEV\Data_visualization\world_populations\reports\html\

📄 population_bar_race_05Mar2026.html (v1) ← 5-6 MB
📄 population_trendline_07Mar2026.html (v2) ← 7-8 MB
📄 population_animated_trendline_07Mar2026.html (v3) ← 9-10 MB
```

### **Script Locations**
```
c:\Users\haujo\projects\DEV\Data_visualization\world_populations\scripts\

🐍 01_fetch_population.py (ETL - Fetch)
🐍 02_transform_rank_top50.py (ETL - Transform)
🐍 03_build_visualization.py (v1 - Bar race)
🐍 04_build_visualization_v2_with_trendline.py (v2 - Static trends)
🐍 05_build_visualization_v3_animated_trendline.py (v3 - Animated trends)
```

---

## 🔄 Complete Data Flow

```
1️⃣  World Bank API
    ↓
    scripts/01_fetch_population.py (John Hau)
    ↓
    csv/raw/worldbank_population_raw_5Mar2026.csv

2️⃣  Transform & Rank
    ↓
    scripts/02_transform_rank_top50.py (John Hau)
    ↓
    csv/processed/population_top50_1970_now_5Mar2026.csv
    
3️⃣  Visualizations (3 versions)
    ├─ scripts/03_build_visualization.py
    │  ↓
    │  reports/html/population_bar_race_05Mar2026.html
    │
    ├─ scripts/04_build_visualization_v2_with_trendline.py
    │  ↓
    │  reports/html/population_trendline_07Mar2026.html
    │
    └─ scripts/05_build_visualization_v3_animated_trendline.py
       ↓
       reports/html/population_animated_trendline_07Mar2026.html
```

---

## 📋 Script Execution Summary

| Script | Phase | Type | Input | Output | Date |
|--------|-------|------|-------|--------|------|
| 01_fetch_population.py | ETL | Data fetch | World Bank API | CSV (raw) | Original |
| 02_transform_rank_top50.py | ETL | Transform | CSV (raw) | CSV (processed) | Original |
| 03_build_visualization.py | Viz | Bar race | CSV (processed) | HTML (v1) | 05Mar2026 |
| 04_build_visualization_v2_with_trendline.py | Viz | Trends | CSV (processed) | HTML (v2) | 07Mar2026 |
| 05_build_visualization_v3_animated_trendline.py | Viz | Animated | CSV (processed) | HTML (v3) | 07Mar2026 |

---

## 🎯 Key Updates (March 7, 2026)

**Changes made by John Hau**:

1. ✅ **Y-Axis Formatting**: Changed all visualizations to show billions (1B, 1.2B, 1.4B)
2. ✅ **Trendlines**: Changed from dashed to solid lines in v2 and v3
3. ✅ **Output Paths**: Moved all HTML files to `reports/html/` with date suffix
4. ✅ **File Naming**: Applied consistent naming convention `{description}_{DDMmmYYYY}.html`

---

## 🚀 Quick Run Instructions

### **Run Latest (v3 - Animated Trendlines)**
```bash
cd c:\Users\haujo\projects\DEV\Data_visualization\world_populations
python scripts/05_build_visualization_v3_animated_trendline.py
```

### **Run All Three Visualizations**
```bash
python scripts/03_build_visualization.py
python scripts/04_build_visualization_v2_with_trendline.py
python scripts/05_build_visualization_v3_animated_trendline.py
```

### **Run via VS Code Tasks**
```
Ctrl+Shift+P → "Run Task" → Select one:
- Python: Run Visualization
- Population: Dashboard v2 with Trendlines
- Population: Dashboard v3 Animated Growing Trendlines
```

---

## 📊 Generated Files Summary

**All outputs created in**:
```
c:\Users\haujo\projects\DEV\Data_visualization\world_populations\reports\html\
```

| File | Size | Frames | Countries | Type |
|------|------|--------|-----------|------|
| population_bar_race_05Mar2026.html | 5-6 MB | 65 | 30 | Animated bar chart |
| population_trendline_07Mar2026.html | 7-8 MB | 1 | 15 | Static trendlines |
| population_animated_trendline_07Mar2026.html | 9-10 MB | 65 | 15 | Animated trendlines |

---

**Created By**: John Hau  
**Date**: March 7, 2026  
**Status**: ✅ Complete
