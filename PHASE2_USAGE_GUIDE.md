# Phase 2 Example Usage and Sample Output

## Quick Start

### Installation
```bash
cd c:\Users\haujo\projects\DEV\Data_visualization

# Install dependencies (if not already installed)
pip install -r requirements_phase2.txt

# Verify installation
python -c "import pandas, numpy, pyarrow; print('✓ All dependencies installed')"
```

### Run Script (Default Configuration)
```bash
cd c:\Users\haujo\projects\DEV\Data_visualization

# Run with defaults (data/raw/ → data/processed/)
python scripts/02_build_rankings.py

# Output:
# ✓ Saved CSV: data/processed/top20_monthly.csv
# ✓ Saved Parquet: data/processed/top20_monthly.parquet
# ✓ Saved metadata: data/processed/top20_monthly_metadata.json
# ✓ Saved rank transitions: data/processed/rank_transitions.json
```

### Run with Options
```bash
# Filter to 2023 data only
python scripts/02_build_rankings.py \
  --start_date 2023-01-01 \
  --end_date 2023-12-31

# Get top 50 instead of 20
python scripts/02_build_rankings.py --top_n 50

# Use custom directories
python scripts/02_build_rankings.py \
  --input_dir raw_data \
  --output_dir processed_data

# Combined: top 30 for 2024-2026
python scripts/02_build_rankings.py \
  --top_n 30 \
  --start_date 2024-01-01 \
  --end_date 2026-02-24
```

---

## Sample Output: `top20_monthly.csv`

### First 10 rows (2016-01)

```csv
date,rank,asset_id,asset_type,label,market_cap,source,confidence,sector,region,notes
2016-01-29,1,AAPL,company,Apple Inc.,582000000000,yfinance,Medium,Technology,US,
2016-01-29,2,MSFT,company,Microsoft Corporation,456000000000,yfinance,Medium,Technology,US,
2016-01-29,3,XOM,company,Exxon Mobil Corporation,345000000000,yfinance,Medium,Energy,US,
2016-01-29,4,BRK.B,company,Berkshire Hathaway Inc.,325000000000,yfinance,Medium,Financials,US,
2016-01-29,5,JPM,company,JPMorgan Chase & Co.,298000000000,yfinance,Medium,Financials,US,
2016-01-29,6,JNJ,company,Johnson & Johnson,310000000000,yfinance,Medium,Healthcare,US,
2016-01-29,7,WMT,company,Walmart Inc.,285000000000,yfinance,Medium,Consumer,US,
2016-01-29,8,PG,company,Procter & Gamble,210000000000,yfinance,Medium,Consumer,US,
2016-01-29,9,CVX,company,Chevron Corporation,175000000000,yfinance,Medium,Energy,US,
2016-01-29,10,VZ,company,Verizon Communications,234000000000,yfinance,Medium,Telecom,US,
2016-01-29,11,BTC,crypto,Bitcoin,4500000000,coingecko,High,,Global,
2016-01-29,12,ETH,crypto,Ethereum,500000000,coingecko,High,,Global,
2016-01-29,13,XAU,metal,Gold,7800000000,manual/yfinance,Medium,Precious Metals,US,
2016-01-29,14,XAG,metal,Silver,450000000,manual/yfinance,Medium,Precious Metals,US,
2016-01-29,15,GOOGL,company,Alphabet Inc.,521000000000,yfinance,Medium,Technology,US,
2016-01-29,16,FB,company,Meta Platforms Inc.,289000000000,yfinance,Medium,Technology,US,
2016-01-29,17,AMZN,company,Amazon.com Inc.,344000000000,yfinance,Medium,Consumer,US,
2016-01-29,18,INTC,company,Intel Corporation,156000000000,yfinance,Medium,Technology,US,
2016-01-29,19,CSCO,company,Cisco Systems Inc.,145000000000,yfinance,Medium,Technology,US,
2016-01-29,20,IBM,company,International Business Machines,145000000000,yfinance,Medium,Technology,US,
```

### Sample rows with notes (2020 COVID adjustment)

```csv
date,rank,asset_id,asset_type,label,market_cap,source,confidence,sector,region,notes
2020-02-28,1,AAPL,company,Apple Inc.,1289000000000,yfinance,Medium,Technology,US,
2020-02-28,2,MSFT,company,Microsoft Corporation,1456000000000,yfinance,Medium,Technology,US,
2020-02-28,3,XOM,company,Exxon Mobil Corporation,285000000000,yfinance,Medium,Energy,US,Market cap change 34.5% - check for stock split/dilution
2020-02-28,4,BRK.B,company,Berkshire Hathaway Inc.,425000000000,yfinance,Medium,Financials,US,
2020-02-28,22,BTC,crypto,Bitcoin,185000000000,coingecko,High,,Global,
```

### Last rows (2026-02)

```csv
date,rank,asset_id,asset_type,label,market_cap,source,confidence,sector,region,notes
2026-02-24,1,AAPL,company,Apple Inc.,2850000000000,yfinance,Medium,Technology,US,
2026-02-24,2,MSFT,company,Microsoft Corporation,2645000000000,yfinance,Medium,Technology,US,
2026-02-24,3,GOOGL,company,Alphabet Inc.,1890000000000,yfinance,Medium,Technology,US,
2026-02-24,4,AMZN,company,Amazon.com Inc.,1756000000000,yfinance,Medium,Consumer,US,
2026-02-24,5,BRK.B,company,Berkshire Hathaway Inc.,1234000000000,yfinance,Medium,Financials,US,
2026-02-24,6,TSLA,company,Tesla Inc.,856000000000,yfinance,Medium,Automotive,US,
2026-02-24,7,META,company,Meta Platforms Inc.,745000000000,yfinance,Medium,Technology,US,
2026-02-24,8,NVDA,company,NVIDIA Corporation,987000000000,yfinance,Medium,Technology,US,
2026-02-24,9,JPM,company,JPMorgan Chase & Co.,534000000000,yfinance,Medium,Financials,US,
2026-02-24,10,JNJ,company,Johnson & Johnson,589000000000,yfinance,Medium,Healthcare,US,
2026-02-24,11,V,company,Visa Inc.,678000000000,yfinance,Medium,Financials,US,
2026-02-24,12,MA,company,Mastercard Inc.,423000000000,yfinance,Medium,Financials,US,
2026-02-24,13,BTC,crypto,Bitcoin,78500000000,coingecko,High,,Global,
2026-02-24,14,ETH,crypto,Ethereum,34200000000,coingecko,High,,Global,
2026-02-24,15,XAU,metal,Gold,12500000000,manual/yfinance,Medium,Precious Metals,US,
2026-02-24,16,INTC,company,Intel Corporation,198000000000,yfinance,Medium,Technology,US,
2026-02-24,17,AMD,company,Advanced Micro Devices,145000000000,yfinance,Medium,Technology,US,
2026-02-24,18,XAG,metal,Silver,785000000,manual/yfinance,Medium,Precious Metals,US,
2026-02-24,19,WMT,company,Walmart Inc.,412000000000,yfinance,Medium,Consumer,US,
2026-02-24,20,PG,company,Procter & Gamble,398000000000,yfinance,Medium,Consumer,US,
```

---

## Sample Output: `top20_monthly_metadata.json`

```json
{
  "schema": {
    "date": "YYYY-MM-DD",
    "rank": "integer (1 to top_n)",
    "asset_id": "string (ticker/coin_id/metal_id)",
    "asset_type": "enum (company|crypto|metal)",
    "label": "string (human-readable name)",
    "market_cap": "float (USD)",
    "source": "enum (yfinance|coingecko|manual)",
    "confidence": "enum (High|Medium|Low)",
    "sector": "string (for companies)",
    "region": "string (for companies)",
    "notes": "string (annotations for corporate actions, data issues, etc.)"
  },
  "date_range": {
    "start": "2016-01-29",
    "end": "2026-02-24"
  },
  "statistics": {
    "total_rows": 2220,
    "unique_dates": 111,
    "top_n": 20,
    "date_count": 111,
    "asset_types": {
      "company": 1652,
      "crypto": 364,
      "metal": 204
    },
    "sources": {
      "yfinance": 1652,
      "coingecko": 364,
      "manual/yfinance": 204
    },
    "confidence_distribution": {
      "High": 364,
      "Medium": 1856
    }
  },
  "validation": {
    "is_valid": true,
    "issues": []
  },
  "processing_info": {
    "timestamp": "2026-02-24T14:32:45.123456",
    "input_directory": "c:\\Users\\haujo\\projects\\DEV\\Data_visualization\\data\\raw",
    "output_directory": "c:\\Users\\haujo\\projects\\DEV\\Data_visualization\\data\\processed",
    "top_n_requested": 20,
    "start_date_filter": null,
    "end_date_filter": null
  }
}
```

---

## Sample Output: `rank_transitions.json` (excerpt)

```json
{
  "2016-02-29": {
    "entries": ["AMZN"],
    "exits": ["XAG"],
    "climbers": [
      ["AAPL", 2],
      ["BTC", 5]
    ],
    "fallers": [
      ["JPM", 1],
      ["XOM", 3]
    ]
  },
  "2016-03-31": {
    "entries": ["FB"],
    "exits": ["INTC"],
    "climbers": [
      ["MSFT", 1],
      ["AMZN", 3]
    ],
    "fallers": [
      ["BRK.B", 2]
    ]
  },
  "2020-02-28": {
    "entries": ["NFLX", "ZOOM"],
    "exits": ["GE", "IBM"],
    "climbers": [
      ["AAPL", 2],
      ["MSFT", 1]
    ],
    "fallers": [
      ["XOM", 8],
      ["CVX", 6]
    ]
  },
  "2026-02-24": {
    "entries": [],
    "exits": [],
    "climbers": [],
    "fallers": []
  }
}
```

---

## Expected Console Output

```
2026-02-24 14:32:45 - __main__ - INFO - Starting data ranking process
2026-02-24 14:32:45 - __main__ - INFO - Input directory: data/raw
2026-02-24 14:32:45 - __main__ - INFO - Output directory: data/processed
2026-02-24 14:32:45 - __main__ - INFO - Top N: 20
2026-02-24 14:32:45 - __main__ - INFO - ================================================================================
2026-02-24 14:32:45 - __main__ - INFO - STEP 1: Data Normalization
2026-02-24 14:32:45 - __main__ - INFO - ================================================================================
2026-02-24 14:32:46 - __main__ - INFO - Reading raw files from data/raw
2026-02-24 14:32:46 - __main__ - INFO - Loaded 2145 company records
2026-02-24 14:32:46 - __main__ - INFO - Loaded 389 crypto records
2026-02-24 14:32:46 - __main__ - INFO - Loaded 204 metals records
2026-02-24 14:32:46 - __main__ - INFO - Normalizing company data
2026-02-24 14:32:47 - __main__ - INFO - Loaded shares data for 45 companies
2026-02-24 14:32:47 - __main__ - INFO - Normalized 2145 company records
2026-02-24 14:32:47 - __main__ - INFO - Normalizing crypto data
2026-02-24 14:32:47 - __main__ - INFO - Normalized 389 crypto records
2026-02-24 14:32:47 - __main__ - INFO - Normalizing metals data
2026-02-24 14:32:47 - __main__ - INFO - Normalized 204 metals records
2026-02-24 14:32:47 - __main__ - INFO - Merging normalized datasets
2026-02-24 14:32:47 - __main__ - INFO - Merged dataset contains 2738 records across 111 dates

2026-02-24 14:32:47 - __main__ - INFO - ================================================================================
2026-02-24 14:32:47 - __main__ - INFO - STEP 2: Ranking by Market Cap
2026-02-24 14:32:47 - __main__ - INFO - ================================================================================
2026-02-24 14:32:47 - __main__ - INFO - Ranking assets by market cap (top 20)
2026-02-24 14:32:48 - __main__ - INFO - Created rankings for 111 dates

2026-02-24 14:32:48 - __main__ - INFO - ================================================================================
2026-02-24 14:32:48 - __main__ - INFO - STEP 3: Computing Rank Transitions
2026-02-24 14:32:48 - __main__ - INFO - ================================================================================
2026-02-24 14:32:48 - __main__ - INFO - Computing rank transitions
2026-02-24 14:32:48 - __main__ - INFO - Identified rank transitions for 110 months

2026-02-24 14:32:48 - __main__ - INFO - ================================================================================
2026-02-24 14:32:48 - __main__ - INFO - STEP 4: Injecting Corporate Action Flags
2026-02-24 14:32:48 - __main__ - INFO - ================================================================================
2026-02-24 14:32:48 - __main__ - INFO - Injecting corporate action flags
2026-02-24 14:32:48 - __main__ - INFO - Corporate action injection complete

2026-02-24 14:32:48 - __main__ - INFO - ================================================================================
2026-02-24 14:32:48 - __main__ - INFO - STEP 5: Quality Validation
2026-02-24 14:32:48 - __main__ - INFO - ================================================================================
2026-02-24 14:32:48 - __main__ - INFO - Validating data quality
2026-02-24 14:32:48 - __main__ - INFO - ✓ All quality checks passed

2026-02-24 14:32:48 - __main__ - INFO - ================================================================================
2026-02-24 14:32:48 - __main__ - INFO - STEP 6: Formatting Output
2026-02-24 14:32:48 - __main__ - INFO - ================================================================================

2026-02-24 14:32:48 - __main__ - INFO - ================================================================================
2026-02-24 14:32:48 - __main__ - INFO - STEP 7: Saving Outputs
2026-02-24 14:32:48 - __main__ - INFO - ================================================================================
2026-02-24 14:32:48 - __main__ - INFO - ✓ Saved CSV: data/processed/top20_monthly.csv
2026-02-24 14:32:48 - __main__ - INFO -   Rows: 2220, Columns: 11
2026-02-24 14:32:48 - __main__ - INFO - ✓ Saved Parquet: data/processed/top20_monthly.parquet
2026-02-24 14:32:48 - __main__ - INFO - ✓ Saved metadata: data/processed/top20_monthly_metadata.json
2026-02-24 14:32:49 - __main__ - INFO - ✓ Saved rank transitions: data/processed/rank_transitions.json

2026-02-24 14:32:49 - __main__ - INFO - ================================================================================
2026-02-24 14:32:49 - __main__ - INFO - PROCESSING COMPLETE
2026-02-24 14:32:49 - __main__ - INFO - ================================================================================
2026-02-24 14:32:49 - __main__ - INFO - 
Dataset Summary:
  First date: 2016-01-29
  Last date:  2026-02-24
  Unique dates: 111
  Total rows: 2220

  Top asset on 2016-01-29: AAPL (Apple Inc.)
    Market Cap: $582,000,000,000
    Confidence: Medium

  Top asset on 2026-02-24: AAPL (Apple Inc.)
    Market Cap: $2,850,000,000,000
    Confidence: Medium

✓ Dataset is ready for Phase 3 visualization
```

---

## Verifying the Output

### Check file creation
```bash
# Verify all output files exist
ls -lh data/processed/top20_monthly.*
ls -lh data/processed/rank_transitions.json
ls -lh data/processed/top20_monthly_metadata.json
```

### Check CSV structure
```bash
# View first 5 rows
head -n 5 data/processed/top20_monthly.csv

# Count rows
wc -l data/processed/top20_monthly.csv

# Check for duplicates
cut -d, -f1,2,3 data/processed/top20_monthly.csv | sort | uniq -d | wc -l
# Should output: 0 (no duplicates)
```

### Check JSON validity
```bash
# Using Python
python -c "
import json
with open('data/processed/top20_monthly_metadata.json') as f:
    data = json.load(f)
    print('✓ Metadata JSON is valid')
    print(f\"  Date range: {data['date_range']['start']} to {data['date_range']['end']}\")
    print(f\"  Total rows: {data['statistics']['total_rows']}\")
"
```

### Check Parquet file
```bash
# Using Python
python -c "
import pandas as pd
df = pd.read_parquet('data/processed/top20_monthly.parquet')
print('✓ Parquet file is valid')
print(f'  Shape: {df.shape}')
print(f'  Columns: {list(df.columns)}')
"
```

---

## Integration with Phase 3

The Phase 2 outputs are fully compatible with Phase 3 visualization:

### CSV Usage
- Load directly into pandas: `pd.read_csv('data/processed/top20_monthly.csv')`
- Filter by date range: `df[df['date'] == '2026-02-24']`
- Sort by rank: `df.sort_values('rank')`
- Group by asset_type: `df.groupby('asset_type')`

### Parquet Usage
- More efficient for large datasets
- Supports column projection: Load only needed columns
- Better compression: Smaller file size
- Faster queries: Columnar organization

### Metadata Usage
- Validate schema before loading
- Check date range: `metadata['date_range']`
- Review statistics: `metadata['statistics']`
- Verify validation: `metadata['validation']['is_valid']`

### Rank Transitions Usage
- Animate rank changes: `transitions[date]['climbers']`
- Highlight entries: `transitions[date]['entries']`
- Track exits: `transitions[date]['exits']`
- Generate narratives: Use transitions data as context

---

## Troubleshooting

### Script fails to run
**Error**: `ModuleNotFoundError: No module named 'pandas'`  
**Solution**: Install dependencies: `pip install -r requirements_phase2.txt`

### Input files not found
**Error**: `Loaded 0 company records`  
**Solution**: Ensure files exist in `data/raw/`:
```bash
ls data/raw/companies_monthly.csv
ls data/raw/crypto_monthly.csv
ls data/raw/metals_monthly.csv
```

### Output files not created
**Error**: `No such file or directory: 'data/processed'`  
**Solution**: Script creates directory automatically, or create manually:
```bash
mkdir -p data/processed
```

### Quality validation warnings
**Issue**: Output shows validation warnings  
**Action**: Check logs for details: `cat data/logs/build_rankings_*.log`

---

## Post-Backtest Validation Workflow

### Automated Validation After Running Backtests

After running data visualization backtests, use the **Post-Backtest Validation Orchestrator** to automatically:
1. Generate the Plotly visualization
2. Run detailed analysis report
3. Execute validation tests
4. Verify everything displays properly

### Quick Start: Automated Workflow

```bash
cd c:\Users\haujo\projects\DEV\Data_visualization

# Run complete post-backtest validation workflow
python post_backtest_validation.py
```

This single command will:
- ✅ Generate Plotly bar race visualization (scripts/03_build_visualizations.py)
- ✅ Run detailed analysis report (detailed_analysis_report.py)
- ✅ Execute validation tests (validate_visualization.py)
- ✅ Verify all output files and display status
- ✅ Display workflow completion summary

### Expected Output

```
======================================================================
          POST-BACKTEST VALIDATION WORKFLOW
======================================================================

[14:32:15] Step 1: Verifying Input Data
----------------------------------------------------------------------
[OK] Input parquet file exists (28.45 MB)

[14:32:15] Step 2: Generating Plotly Visualization
----------------------------------------------------------------------
[OK] Visualization Generation (03_build_visualizations.py) completed successfully
[OK] Generated visualization exists (11.86 MB)
[OK] Plotly chart successfully created and verified

[14:32:45] Step 3: Running Detailed Analysis Report
----------------------------------------------------------------------
[OK] Detailed Analysis Report (detailed_analysis_report.py) completed successfully

[14:33:00] Step 4: Running Validation Tests
----------------------------------------------------------------------
[OK] Validation Tests (validate_visualization.py) completed successfully

[14:33:15] Step 5: Final Verification
----------------------------------------------------------------------
[OK] Input Data (top20_monthly.parquet) exists (28.45 MB)
[OK] Output Visualization (bar_race_top20.html) exists (11.86 MB)

======================================================================
                WORKFLOW COMPLETION SUMMARY
======================================================================

[OK] Visualization Generation: PASSED
[OK] Detailed Analysis Report: PASSED
[OK] Validation Tests: PASSED
[OK] File Verification: PASSED

Passed: 4/4
Failed: 0/4
Completion Time: 2026-03-03 14:33:15

======================================================================

✅ VISUALIZATION READY FOR DISPLAY

Visualization file: c:\Users\haujo\projects\DEV\Data_visualization\data\processed\bar_race_top20.html
To view: Open bar_race_top20.html in your web browser
```

### Detailed Validation Information

The workflow provides comprehensive validation across 4 test suites:

**Test Suite 1: Data Quality Validation (6 checks)**
- Row count verification (should be ≥10,000)
- Date range validation (should span years)
- Unique assets count (should be 20+)
- Market cap values check (should be valid range)
- Data continuity verification (should be 100% complete)
- Asset type distribution check

**Test Suite 2: UI/UX Design Validation (7 checks)**
- HTML structure validation
- Plotly library presence check
- Interactive controls verification
- Animation frame count check
- File size validation (should be <15 MB)
- Color scheme definition check
- UI Layout overlap detection

**Test Suite 3: Interactivity Validation (4 checks)**
- Hover tooltips configuration
- Axis labels presence
- Responsive design indicators
- Data binding verification

**Test Suite 4: Horizontal Bar Chart Validation (5 checks)**
- Bar orientation verification (should be horizontal)
- Bar coloring configuration
- Axis scaling type (should be logarithmic)
- Bar labels configuration
- Animation frame count (should be ≥1000)

### VS Code Task Integration

Run the validation from VS Code Task Runner:

1. Open Command Palette: `Ctrl+Shift+P`
2. Select "Tasks: Run Task"
3. Choose "Data Visualization: Post-Backtest Validation"
4. View output in Terminal

Or run from terminal:
```bash
# In VS Code Terminal
python post_backtest_validation.py
```

### Troubleshooting Validation

**Issue**: Visualization generation fails
```bash
# Check input file exists
ls -la data/processed/top20_monthly.parquet

# Verify parquet file integrity
python -c "import pandas as pd; df = pd.read_parquet('data/processed/top20_monthly.parquet'); print(f'Rows: {len(df)}')"
```

**Issue**: Analysis report fails
```bash
# Ensure visualization was generated
ls -la data/processed/bar_race_top20.html

# Run analysis separately for detailed error
python detailed_analysis_report.py
```

**Issue**: Validation tests show failures
```bash
# Run validation separately for detailed output
python validate_visualization.py

# Check specific test details
python -c "from validate_visualization import HTMLUXValidator; v = HTMLUXValidator(); v.run_all_checks()"
```

### What Each Step Validates

| Step | Component | Validates |
|------|-----------|-----------|
| Visualization Generation | Plotly chart creation | 7,421 animation frames, log scale axis, proper styling |
| Detailed Analysis | Data metrics | 74,160 records, 20 assets, 10.1 years, data quality |
| Validation Tests | Quality checks | 22 comprehensive tests across 4 suites |
| File Verification | Output artifacts | HTML file exists, size is optimal, no corruption |

### Success Criteria

All steps should show:
- ✅ **Visualization Generation**: PASSED
- ✅ **Detailed Analysis Report**: PASSED
- ✅ **Validation Tests**: PASSED (21/22 minimum, 95.5% success rate acceptable)
- ✅ **File Verification**: PASSED

Final status should be: **✅ VISUALIZATION READY FOR DISPLAY**

### Viewing Your Visualization

After successful validation:

1. Open HTML file in browser:
   ```
   c:\Users\haujo\projects\DEV\Data_visualization\data\processed\bar_race_top20.html
   ```

2. Interact with visualization:
   - Click **Play** to start animation
   - Use **Date Slider** to jump to specific dates
   - Hover over bars to see market cap details
   - View **Legend** to understand asset categories

3. Verify proper display:
   - All 20 assets visible
   - Bars animate smoothly day-by-day
   - Market cap values in USD Billions format
   - No overlapping UI elements
   - Color coding: Blue (Companies), Orange (Crypto), Green (Metals)

---

## Next Steps

After Phase 2 completes successfully:

1. **Verify output files**
   - Check `data/processed/top20_monthly.csv` exists
   - Spot-check data: `head -20 data/processed/top20_monthly.csv`

2. **Review metadata**
   - Open `data/processed/top20_monthly_metadata.json`
   - Check validation status and date range

3. **Run Post-Backtest Validation**
   - Run: `python post_backtest_validation.py`
   - This is the recommended workflow after any backtest
   - Ensures visualization is correct and all data is valid

4. **Proceed to Phase 3 (if needed)**
   - Run: `python scripts/03_build_visualizations.py`
   - Use CSV/Parquet as input
   - Reference rank transitions for animations

---

## Contact & Support

For issues or questions:
- Check logs: `data/logs/build_rankings_*.log`
- Review specification: `PHASE2_SPECIFICATION.md`
- Inspect sample outputs in this file
