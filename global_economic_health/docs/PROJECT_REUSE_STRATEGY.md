# PROJECT REUSE STRATEGY
**Project:** Global Economic Health Dashboard  
**Document:** Project 1 Script Reuse Plan  
**Date:** March 7, 2026  
**Status:** Active  

---

## 1. Overview

Project 2 (`global_economic_health`) reuses **three proven scripts** from Project 1 (`world_populations`) to accelerate development and ensure consistency. This document specifies:

- Which scripts are reused
- Why they are reusable
- How to copy and maintain them
- Version control strategy
- Migration/update procedures

---

## 2. Reusable Scripts

### 2.1 `01_fetch_population.py`

**Location in Project 1:**  
`world_populations/scripts/01_fetch_population.py`

**Location in Project 2:**  
`global_economic_health/scripts/01_fetch_population.py`

**Purpose:**  
Fetch population data from World Bank API (`SP.POP.TOTL` indicator) for years 1960–2026.

**Why Reusable:**
- Uses parameterized API calls (indicator, date range can be changed)
- Returns standardized DataFrame with columns: `country_name`, `country_code`, `year`, `population`
- No hard-coded paths (uses relative `Path` objects)
- Includes error handling and retry logic
- No dependency on Project 1-specific code

**Interface Contract:**
```python
def fetch_worldbank_population(
    indicator: str = "SP.POP.TOTL",
    start_year: int = 1960,
    end_year: int = 2026,
    per_page: int = 20000
) -> pd.DataFrame:
    """Returns DataFrame with columns: country_name, country_code, year, population"""
```

**Usage in Project 2:**
- Copy file as-is to `global_economic_health/scripts/`
- Add comment header noting reuse from Project 1
- No modifications needed
- Output path: `csv/raw/population_raw_<timestamp>.csv`

---

### 2.2 `02_transform_rank_top50.py`

**Location in Project 1:**  
`world_populations/scripts/02_transform_rank_top50.py`

**Location in Project 2:**  
`global_economic_health/scripts/02_transform_rank_top50.py`

**Purpose:**  
Filter top N countries per year by population, add ranking column.

**Why Reusable:**
- Generic transformation logic (top-N filtering + ranking)
- Works with any metric (not population-specific)
- Takes exclusion list as config parameter
- Returns standardized DataFrame with added `rank` column
- Uses config CSV for aggregate exclusions

**Interface Contract:**
```python
def filter_top50_per_year(
    df: pd.DataFrame, 
    top_n: int = 50, 
    exclude_csv: Path = None
) -> pd.DataFrame:
    """Returns DataFrame with top N countries per year"""

def add_ranking_column(df: pd.DataFrame) -> pd.DataFrame:
    """Adds rank column based on metric"""
```

**Usage in Project 2:**
- Copy file as-is to `global_economic_health/scripts/`
- Add comment header noting reuse from Project 1
- No modifications needed
- Input: `csv/raw/population_raw_<timestamp>.csv`
- Output: `csv/processed/population_top50_1970_now_<timestamp>.csv`
- Config: `config/aggregate_regions_exclude.csv` (same as Project 1)

---

### 2.3 `05_build_visualization_v3_animated_trendline.py`

**Location in Project 1:**  
`world_populations/scripts/05_build_visualization_v3_animated_trendline.py`

**Location in Project 2:**  
`global_economic_health/scripts/05_build_visualization_v3_animated_trendline.py`

**Purpose:**  
Build animated Plotly dashboard with growing trendlines and interactive controls.

**Why Reusable:**
- Generic animation engine (not population-specific)
- Takes input CSV with columns: `country_name`, `year`, `population`
- Parameterized number of top countries (default 15)
- Produces interactive HTML with play/pause and year slider
- Dark theme, responsive design
- Polynomial trendline fitting (configurable degree)

**Interface Contract:**
```python
class AnimatedPopulationDashboardV3:
    def create_animated_dashboard(self, output_path: Path) -> go.Figure:
        """Creates animated Plotly dashboard HTML output"""
```

**Usage in Project 2:**
- Copy file as-is to `global_economic_health/scripts/`
- Add comment header noting reuse from Project 1
- No modifications needed (unless title needs updating)
- Input: `csv/processed/population_top50_1970_now_<timestamp>.csv`
- Output: `reports/html/population_animated_trendline_<timestamp>.html`

---

## 3. Reuse Implementation Strategy

### 3.1 Copy vs. Symlink vs. Module Import

**Decision: COPY (recommended)**

**Rationale:**
- Easier version control (each project has independent history)
- Simplifies debugging (no cross-project dependencies)
- Allows independent modification if needed
- No path complexity (no symlink resolution)
- Ensures reproducibility

**Alternative: Symlink**
- Would work but harder to track
- Not recommended for multi-agent systems

**Alternative: Module Import**
- Could import from Project 1 package
- Not recommended (couples projects)

### 3.2 Implementation Steps

1. **Copy Script:**
   ```bash
   cp world_populations/scripts/01_fetch_population.py \
      global_economic_health/scripts/01_fetch_population.py
   ```

2. **Add Reuse Header:**
   At the top of each copied script, add:
   ```python
   """
   REUSED FROM: world_populations/scripts/01_fetch_population.py
   PROJECT 2: global_economic_health
   Copied: March 7, 2026
   Status: Active
   """
   ```

3. **Version Control:**
   - Track reused scripts in Project 2 repo
   - Document source and copy timestamp in Git commit message
   - No special handling in `.gitignore`

4. **Testing:**
   - Run each copied script against Project 2 data
   - Verify outputs match expected schema
   - Log test results in `reports/qa/reuse_verification.md`

---

## 4. Version Control Strategy

### 4.1 Tracking Reused Code

Each reused script includes:
- Source project and path
- Copy timestamp
- Status ("Active", "Deprecated", "Modified")
- Link to original for reference

**Example Git Commit Message:**
```
feat: Add reused scripts from Project 1 (world_populations)

- Copy 01_fetch_population.py from world_populations
- Copy 02_transform_rank_top50.py from world_populations
- Copy 05_build_visualization_v3_animated_trendline.py from world_populations

Source: world_populations at commit abc123d
Date copied: March 7, 2026
Status: Active (no modifications needed)
```

### 4.2 Maintenance Policy

**If Project 1 Changes:**
1. Project 1 owner updates script
2. Notify Project 2 team of changes
3. Review change impact on Project 2
4. Decide: Propagate or Keep Local Version
5. If propagate: Re-copy and re-test

**If Project 2 Modifies a Reused Script:**
1. Change status header to "Modified"
2. Document modifications in comments
3. Notify Project 1 team if relevant
4. Don't propagate back to Project 1 (separate projects)

---

## 5. Compatibility Guarantees

All three reused scripts guarantee:

✅ **Input Schema Compatibility:**
- Scripts expect specific CSV columns
- Column order doesn't matter
- Extra columns are ignored
- Missing columns raise clear errors

✅ **Output Schema Stability:**
- Output columns never change without notification
- Output CSV format (UTF-8, standard pandas format)
- File naming convention consistent (with timestamps)

✅ **Error Handling:**
- API failures raise informative exceptions
- Data validation errors logged clearly
- No silent failures
- Timeout behavior documented

✅ **Performance:**
- Process 100K+ records without significant slowdown
- Population dataset (200K records) processes in < 1 minute
- Memory usage scales linearly

---

## 6. Migration and Update Procedures

### 6.1 Migrating to New Version

**Scenario: Project 1 releases improved version of 01_fetch_population.py**

**Process:**
1. Project 1 bumps version (e.g., v1.1)
2. Project 2 team reviews changelog
3. Decision: Adopt new version or maintain local version?
4. If adopting:
   - Back up current version (Git handles this)
   - Re-copy script
   - Update reuse header with new version number
   - Run QA tests
   - Commit with message referencing Project 1 commit

### 6.2 Testing After Update

Run the verification suite:
```bash
python verification/verify_code_structure.py
python verification/verify_outputs.py
```

Verify outputs match expected:
- Schema correctness
- Row counts (within tolerance)
- No new errors

---

## 7. Reuse Summary

| Script | Size | Purpose | Dependencies | Status |
|--------|------|---------|--------------|--------|
| `01_fetch_population.py` | ~200 lines | World Bank API fetch | `requests`, `pandas` | ✅ Active |
| `02_transform_rank_top50.py` | ~150 lines | Top-N filtering + ranking | `pandas` | ✅ Active |
| `05_build_visualization_v3_animated_trendline.py` | ~900 lines | Animated dashboard | `plotly`, `pandas`, `numpy` | ✅ Active |

**Total Reused Code:** ~1,250 lines (20% of Project 2 implementation)

**Development Time Saved:** ~2-3 days of development and testing

---

## 8. Verification Steps

To verify reused scripts work correctly in Project 2:

1. **Code Structure Check:**
   ```bash
   python verification/verify_code_structure.py
   ```
   - Confirms scripts exist
   - Confirms required functions exist
   - Confirms no missing imports

2. **Integration Test:**
   ```bash
   # Run each reused script against Project 2 data
   python scripts/01_fetch_population.py
   python scripts/02_transform_rank_top50.py  # Requires output of 01
   python scripts/05_build_visualization_v3_animated_trendline.py  # Requires output of 02
   ```

3. **Output Validation:**
   ```bash
   python verification/verify_outputs.py
   ```
   - Confirms CSV schemas match
   - Confirms row counts reasonable
   - Confirms no data errors

---

## 9. Contact and Questions

**Project 1 Owner:** [Contact info]  
**Project 2 Owner:** [Contact info]  
**Last Updated:** March 7, 2026  
**Next Review:** June 7, 2026
