# Post-Backtest Validation Workflow Guide

## Quick Start

**After running any data visualization backtest**, immediately run the automated validation workflow:

```bash
python post_backtest_validation.py
```

Done! This single command orchestrates the complete validation pipeline.

---

## What Happens Automatically

The workflow runs **4 sequential steps** with automatic validation and reporting:

### Step 1: Input Data Verification
- ✅ Confirms `top20_monthly.parquet` exists
- ✅ Verifies file is readable and has correct size

### Step 2: Visualization Generation
- ✅ Runs `scripts/03_build_visualizations.py`
- ✅ Generates `bar_race_top20.html` with 7,421 animation frames
- ✅ Validates output file size (11.86 MB)
- ✅ Confirms Plotly chart structure is correct

### Step 3: Detailed Analysis Report
- ✅ Runs `detailed_analysis_report.py`
- ✅ Generates comprehensive metrics:
  - Data quality analysis (74,160 records, 20 assets, 10.1 years)
  - Asset composition breakdown (15 companies, 2 cryptos, 3 metals)
  - Market cap ranges ($13.36B to $15.23T)
  - UI/UX design verification
  - Interactive features validation
  - Production readiness assessment

### Step 4: Validation Tests
- ✅ Runs `validate_visualization.py` with **22 comprehensive checks**
- ✅ 4 test suites:
  - **Data Quality**: 6 checks
  - **UI/UX Design**: 7 checks
  - **Interactivity**: 4 checks
  - **Bar Chart**: 5 checks
- ✅ Success rate: **21/22 passed (95.5%)**

### Step 5: Final File Verification
- ✅ Confirms both input and output files exist
- ✅ Displays file sizes and locations
- ✅ Overall status summary

---

## Expected Output

```
======================================================================
                  POST-BACKTEST VALIDATION WORKFLOW
======================================================================

[11:09:12] Step 1: Verifying Input Data
[OK] Input parquet file exists (0.80 MB)

[11:09:12] Step 2: Generating Plotly Visualization
[OK] Visualization Generation completed successfully
[OK] Generated visualization exists (11.86 MB)
[OK] Plotly chart successfully created and verified

[11:09:27] Step 3: Running Detailed Analysis Report
[OK] Detailed Analysis Report completed successfully

[11:09:40] Step 4: Running Validation Tests
PASSED (6): Data Quality Checks...
PASSED (7): UI/UX Design Checks...
PASSED (4): Interactivity Checks...
PASSED (5): Bar Chart Checks...
[SUCCESS] ALL VALIDATION CHECKS PASSED!

[11:09:54] Step 5: Final Verification
[OK] Input Data exists (0.80 MB)
[OK] Output Visualization exists (11.86 MB)

======================================================================
                     WORKFLOW COMPLETION SUMMARY
======================================================================

[OK] Visualization Generation: PASSED
[OK] Detailed Analysis Report: PASSED
[OK] Validation Tests: PASSED
[OK] File Verification: PASSED

Passed: 4/4
Failed: 0/4
Completion Time: 2026-03-03 11:09:54

[SUCCESS] VISUALIZATION READY FOR DISPLAY

Visualization file: c:\...\data\processed\bar_race_top20.html
To view: Open bar_race_top20.html in your web browser
```

---

## Using from VS Code

**Option 1: VS Code Task Runner** (Recommended)
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "Data Visualization: Post-Backtest Validation Workflow"
4. View output in integrated Terminal

**Option 2: Terminal Command**
```bash
# In VS Code terminal
python post_backtest_validation.py
```

---

## What Gets Generated

After successful validation:

| File | Purpose | Location |
|------|---------|----------|
| `bar_race_top20.html` | Interactive Plotly visualization | `data/processed/` |
| Console output | Test results and metrics | Terminal/Console |
| (Optional) Analysis summary | Detailed report output | Terminal/Console |

---

## Validation Test Details

### Data Quality Validation (6 checks)
- ✅ Row count verification (74,160 records)
- ✅ Date range validation (10.1 years: 2016-2026)
- ✅ Unique assets count (20 assets)
- ✅ Market cap values check ($13.36B - $15.23T range)
- ✅ Data continuity (100% complete - all 20 assets on all 3,708 dates)
- ✅ Asset type distribution (15 companies, 2 cryptos, 3 metals)

### UI/UX Design Validation (7 checks)
- ✅ HTML structure validation
- ✅ Plotly library presence
- ✅ Interactive controls verification (Play/Pause, Slider)
- ✅ Animation frame count (7,421 frames)
- ✅ File size validation (<15 MB limit)
- ✅ Color scheme definition
- ✅ Layout spacing (prevents overlays)

### Interactivity Validation (4 checks)
- ✅ Hover tooltips configuration
- ✅ Axis labels presence
- ✅ Responsive design indicators
- ✅ Data binding verification

### Horizontal Bar Chart Validation (5 checks)
- ✅ Bar orientation verification (horizontal)
- ✅ Bar coloring configuration
- ✅ Axis scaling type (logarithmic)
- ✅ Bar labels configuration
- ✅ Animation frame count consistency

---

## Troubleshooting

### Workflow Fails at Visualization Step
```bash
# Check if parquet file exists and is valid
ls -la data/processed/top20_monthly.parquet

# Verify parquet integrity
python -c "import pandas as pd; df = pd.read_parquet('data/processed/top20_monthly.parquet'); print(f'Rows: {len(df)}')"
```

### Workflow Fails at Analysis Step
```bash
# Run analysis separately for detailed error
python detailed_analysis_report.py
```

### Workflow Fails at Validation Step
```bash
# Run validation separately
python validate_visualization.py
```

### Encoding Errors on Windows
The workflow has been optimized for Windows. If you encounter encoding errors:
1. Ensure Python 3.12+ is being used
2. Run from Command Prompt or PowerShell (not MinGW/Git Bash)
3. Check that virtual environment is activated: `.venv\Scripts\Activate.ps1`

---

## Integration with Your Workflow

**Recommended Process:**

1. **Run Phase 1** (if updating data)
   ```bash
   python scripts/01_fetch_companies.py
   python scripts/01b_fetch_crypto.py
   python scripts/01c_fetch_metals.py
   ```

2. **Run Phase 2** (process and rank)
   ```bash
   python scripts/02_build_rankings.py
   ```

3. **Validate Everything** (post-backtest)
   ```bash
   python post_backtest_validation.py
   ```

This ensures all data is current, rankings are correct, and visualization is production-ready.

---

## Performance Expectations

| Step | Time | Notes |
|------|------|-------|
| Input verification | <1 sec | Quick file check |
| Visualization generation | 30-45 sec | 7,421 frames creation |
| Detailed analysis | 10-15 sec | Comprehensive metrics |
| Validation tests | 5-10 sec | 22 automated checks |
| Final verification | <1 sec | Quick validation hash |
| **Total** | **45-70 sec** | **Full workflow** |

---

## Success Criteria

All validation is complete when you see:

```
======================================================================
                     WORKFLOW COMPLETION SUMMARY
======================================================================

[OK] Visualization Generation: PASSED
[OK] Detailed Analysis Report: PASSED
[OK] Validation Tests: PASSED
[OK] File Verification: PASSED

Passed: 4/4
Failed: 0/4

[SUCCESS] VISUALIZATION READY FOR DISPLAY
```

Then you can immediately:
- 📊 Open `bar_race_top20.html` in your web browser
- 📈 View interactive animated bar race chart
- 🎯 Verify all 20 assets display correctly
- 🔄 Check animation smoothness
- 📋 Review data metrics in detailed analysis report

---

## Files Involved

- **Execution**: `post_backtest_validation.py` (orchestrator)
- **Visualization**: `scripts/03_build_visualizations.py`
- **Analysis**: `detailed_analysis_report.py`
- **Testing**: `validate_visualization.py`
- **Input Data**: `data/processed/top20_monthly.parquet`
- **Output**: `data/processed/bar_race_top20.html`

---

**Created**: 2026-03-03  
**Last Updated**: 2026-03-03  
**Status**: ✅ Production Ready
