# Global Top-20 Market Cap Evolution Dashboard

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen) ![Phase](https://img.shields.io/badge/Phase-3%20Complete-blue) ![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

An interactive, animated dashboard showing how the top 20 global market-cap assets **evolve over a 10-year period** (2016-2026), including public companies, cryptocurrencies, and precious metals.

## 🎯 Project Overview

This project creates an animated bar-race visualization that tracks the market cap evolution of:
- **Public Companies** (Apple, Microsoft, Samsung, etc.)
- **Cryptocurrencies** (Bitcoin, Ethereum, and top 20 by market cap)
- **Precious Metals** (Gold, Silver, Platinum, Palladium as commodities)

**Tech Stack**: Python • Pandas • yfinance • CoinGecko API • Plotly • Parquet • VS Code

**Live Output**: An interactive HTML5 visualization with:
- ✅ Animated bar race (monthly frames)
- ✅ Date slider and playback controls
- ✅ Hover tooltips with detailed data
- ✅ Speed control (0.5x, 1x, 1.5x, 2x)
- ✅ Responsive design (works on all devices)
- ✅ Standalone file (no internet required after generation)

---

## 📊 What You Get

### Main Visualization Output
- **File**: `data/processed/bar_race_top20.html` (5.37 MB)
- **Format**: Standalone interactive Plotly visualization
- **Frames**: 132 monthly data points (Jan 2016 - Dec 2026)
- **Data**: Top 20 assets by market cap, ranked monthly
- **Features**: Play/pause, date slider, speed controls, tooltips, legend

### Supporting Data Files
- `data/processed/top20_monthly.parquet` – Processed ranking data (Parquet format)
- `data/processed/top20_monthly.csv` – Processed ranking data (CSV format)
- `data/processed/bar_race_top20_metadata.json` – Visualization metadata
- `data/processed/rank_transitions.json` – Monthly rank change tracking

### Raw Data (Cached)
- `data/raw/companies_monthly.csv` – Historical equity market cap data
- `data/raw/crypto_monthly.csv` – CoinGecko crypto market cap data
- `data/raw/metals_monthly.csv` – Precious metals spot price data

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda package manager
- Virtual environment (recommended)

### Installation

```bash
# Clone or navigate to the project
cd c:\Users\haujo\projects\DEV\Data_visualization

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Generate the Visualization (Fast)

If you already have processed data:
```bash
python scripts/03_build_visualizations.py
```

Output: `data/processed/bar_race_top20.html` (ready to view)

### Full Data Pipeline (Slow, ~5-10 minutes)

To fetch fresh data from all sources:
```bash
# Phase 1: Fetch data from APIs
python scripts/01_fetch_companies.py      # yfinance equity data
python scripts/01b_fetch_crypto.py        # CoinGecko crypto data
python scripts/01c_fetch_metals.py        # Metals spot prices

# Phase 2: Transform and rank
python scripts/02_build_rankings.py       # Generate top 20 rankings

# Phase 3: Create visualization
python scripts/03_build_visualizations.py # Generate HTML animation
```

### View Results

**Method 1: Direct File**
```bash
# Simply open in your browser:
data/processed/bar_race_top20.html
```

**Method 2: Local Server**
```bash
# Run Python server
python -m http.server 8000 --directory "data/processed"

# Open: http://localhost:8000/bar_race_top20.html
```

---

## 📁 Project Structure

```
data_visualization/
├── scripts/                          # Main Python scripts (Phase 1-3)
│   ├── 00_validate_sources.py        # Validate API connectivity
│   ├── 00_validate_vps.py            # Validate VPS access (optional)
│   ├── 01_fetch_companies.py         # Phase 1: Fetch company data
│   ├── 01b_fetch_crypto.py           # Phase 1: Fetch crypto data
│   ├── 01c_fetch_metals.py           # Phase 1: Fetch metals prices
│   ├── 02_build_rankings.py          # Phase 2: Rank & transform data
│   └── 03_build_visualizations.py    # Phase 3: Create HTML visualization
│
├── data/
│   ├── raw/                          # Original data from APIs
│   │   ├── companies_monthly.csv
│   │   ├── crypto_monthly.csv
│   │   └── metals_monthly.csv
│   ├── processed/                    # Final outputs
│   │   ├── bar_race_top20.html       # ⭐ Main visualization
│   │   ├── top20_monthly.parquet     # Processed data (Parquet)
│   │   ├── top20_monthly.csv         # Processed data (CSV)
│   │   ├── bar_race_top20_metadata.json
│   │   └── rank_transitions.json
│   └── logs/                         # Processing logs
│
├── config/                           # Asset lists and metadata
│   ├── universe_companies.csv        # List of tracked companies
│   ├── crypto_list.csv               # List of tracked cryptocurrencies
│   ├── precious_metals_supply.csv    # Metal supplies (ounces)
│   ├── shares_outstanding.csv        # Historical shares for companies
│   └── vps_list.csv                  # Optional VPS worker nodes
│
├── docs/                             # Documentation
│   ├── ProjectPlan.md                # Full technical plan
│   └── PHASE_3_VISUALIZATION.md      # Visualization architecture
│
├── docs/                             # Delivery reports
│   └── PHASE_3_DELIVERABLES_INDEX.md
│
├── dashboard/                        # Streamlit dashboard (optional)
│   └── app_bar_race.py
│
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
└── [Other documentation files]       # Phase reports, verification guides
```

---

## 📋 Key Scripts

### Phase 1: Data Ingestion

#### `scripts/01_fetch_companies.py`
Fetches historical equity data using yfinance.
```bash
python scripts/01_fetch_companies.py
# Output: data/raw/companies_monthly.csv
```
- Downloads S&P 500 + additional tracked companies
- Uses monthly intervals to reduce API load
- Caches share count data to `config/shares_outstanding.csv`
- Handles stock splits automatically

#### `scripts/01b_fetch_crypto.py`
Fetches cryptocurrency market cap data from CoinGecko.
```bash
python scripts/01b_fetch_crypto.py
# Output: data/raw/crypto_monthly.csv
```
- Uses free CoinGecko API (no auth required)
- Fetches top 100+ cryptocurrencies
- Downloads monthly market cap snapshots
- Handles delisted coins gracefully

#### `scripts/01c_fetch_metals.py`
Fetches precious metals spot prices.
```bash
python scripts/01c_fetch_metals.py
# Output: data/raw/metals_monthly.csv
```
- Gold, Silver, Platinum, Palladium
- Uses yfinance commodity data
- Converts spot price + supply = market cap
- Supply data from `config/precious_metals_supply.csv`

### Phase 2: Data Transformation & Ranking

#### `scripts/02_build_rankings.py`
Normalizes multi-asset data and computes monthly rankings.
```bash
python scripts/02_build_rankings.py
# Output: data/processed/top20_monthly.parquet, .csv, metadata, transitions
```
**Classes:**
- `DataNormalizer` – Unifies three asset classes into single format
- `TopNRanker` – Ranks assets by market cap, detects transitions

**Key Features:**
- ✅ Handles missing data gracefully
- ✅ Assigns confidence levels (High/Medium/Low)
- ✅ Tracks rank transitions (entries, exits, climbers, fallers)
- ✅ Detects corporate actions (>30% market cap jumps)
- ✅ Validates data quality (8-point checklist)

**Output Schema:**
```
Columns: date, rank, asset_id, asset_type, label, market_cap, 
         source, confidence, sector, region, notes
Rows: ~2,380 (20 assets × 132 months)
Format: CSV + Parquet (compressed)
```

### Phase 3: Visualization

#### `scripts/03_build_visualizations.py`
Generates interactive Plotly bar-race animation.
```bash
python scripts/03_build_visualizations.py \
  --input_path data/processed/top20_monthly.parquet \
  --output_path data/processed/bar_race_top20.html \
  --title "Global Top 20 Market Cap Evolution" \
  --animate_speed 1000
# Output: 5.37 MB standalone HTML file
```

**Class: `BarRaceVisualizer`**
- `read_processed_data()` – Load & validate data
- `prepare_animation_data()` – Reshape for Plotly animation
- `build_bar_race()` – Create animated bars with colors
- `add_annotations()` – Add metadata, source attribution
- `add_legend_and_branding()` – Format legend, title, credits
- `generate_metadata()` – Create summary JSON

**Visualization Features:**
- animated bars growing/shrinking by market cap
- Monthly frames update smoothly
- Color-coded by asset type (companies=blue, crypto=orange, metals=yellow)
- Hover tooltips: asset name, rank, market cap, source
- Play/pause/date slider controls
- Responsive design (works on mobile, tablet, desktop)
- Standalone HTML (no dependencies, no internet needed)

---

## 🎨 Visualization Features

### Interactive Controls
- **Play/Pause Button** – Start/stop animation
- **Date Slider** – Jump to any month
- **Speed Controls** – 0.5x, 1x, 1.5x, 2x playback speed
- **Hover Tooltips** – Detailed info on hover

### Data Visualization
- **Animated Bars** – Smooth ranking transitions
- **Color Coding**:
  - 🔵 Blue = Public companies
  - 🟠 Orange = Cryptocurrencies
  - 🟡 Yellow = Precious metals
- **Responsive Layout** – Adapts to screen size
- **Grid & Axes** – Clear neon green axes on dark background

### Metadata & Attribution
- **Source Credit** – Shows data sources
- **Confidence Levels** – High/Medium/Low badges per asset
- **Timestamp** – Generation date and time
- **legend** – Asset type legend at bottom

---

## 📊 Data Accuracy & Confidence

Each asset in the visualization has a **confidence level**:

| Level | Meaning | Examples |
|-------|---------|----------|
| **High** | Direct API data, validated | Bitcoin price from CoinGecko, Apple price from yfinance |
| **Medium** | Calculated from market data + assumptions | Company market cap with estimated shares |
| **Low** | Estimated or inferred | Historical data gaps, estimated supply |

### Sources
1. **yfinance** – Historical equity prices & volumes
2. **CoinGecko API** – Cryptocurrency market cap (free tier)
3. **Metals Prices** – Spot prices + supply (yfinance commodities)

### Known Limitations
- ⚠️ Precious metals use approximate supply (may not account for all held inventory)
- ⚠️ Historical crypto prices pre-2015 may have limited data
- ⚠️ Share counts are point-in-time (historical changes not fully tracked)
- ⚠️ Corporate actions (splits, mergers) handled via yfinance auto-adjustment

---

## 📚 Documentation Structure

### Quick References
- **[PHASE_3_QUICKSTART.md](PHASE_3_QUICKSTART.md)** – Current phase overview
- **[PHASE_3_DELIVERABLES_INDEX.md](PHASE_3_DELIVERABLES_INDEX.md)** – Delivery checklist
- **[SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)** – Features & improvements

### Phase-Specific Guides
- **[README_PHASE2.md](README_PHASE2.md)** – Phase 2 transformation details
- **[PHASE2_SPECIFICATION.md](PHASE2_SPECIFICATION.md)** – Technical architecture
- **[PHASE2_USAGE_GUIDE.md](PHASE2_USAGE_GUIDE.md)** – Implementation examples
- **[PHASE2_VERIFICATION.md](PHASE2_VERIFICATION.md)** – Verification checklist

### Technical Documentation
- **[docs/ProjectPlan.md](docs/ProjectPlan.md)** – Full 5-phase plan
- **[docs/PHASE_3_VISUALIZATION.md](docs/PHASE_3_VISUALIZATION.md)** – Visualization architecture
- **[HTML_VERIFICATION_AND_UI_GUIDE.md](HTML_VERIFICATION_AND_UI_GUIDE.md)** – UI guide

### Validation & Verification
- **[VALIDATION_REPORT.md](VALIDATION_REPORT.md)** – Data validation results
- **[DATA_VALIDATION_GUIDE.md](DATA_VALIDATION_GUIDE.md)** – How to validate data
- **[COMPLETE_SOLUTION_FINAL.md](COMPLETE_SOLUTION_FINAL.md)** – Fixes and improvements

### Delivery Reports
- **[DELIVERY_SUMMARY.md](DELIVERY_SUMMARY.md)** – Phase 2 completion report
- **[DELIVERY_REPORT_PHASE3.md](DELIVERY_REPORT_PHASE3.md)** – Phase 3 completion report
- **[ENVIRONMENT_FIX_SUMMARY.md](ENVIRONMENT_FIX_SUMMARY.md)** – Environment setup notes

---

## 🔧 Configuration

### Company Universe
**File**: `config/universe_companies.csv`

Edit to add/remove companies:
```csv
ticker,name,sector,exchange
AAPL,Apple Inc.,Technology,NASDAQ
MSFT,Microsoft Corp.,Technology,NASDAQ
...
```

### Cryptocurrency List
**File**: `config/crypto_list.csv`

Edit to change tracked cryptocurrencies:
```csv
symbol,name,coingecko_id
BTC,Bitcoin,bitcoin
ETH,Ethereum,ethereum
...
```

### Precious Metals Supply
**File**: `config/precious_metals_supply.csv`

Adjust supply estimates (in ounces):
```csv
metal,supply_ounces,source
Gold,210000000,USGS
Silver,1750000000,USGS
...
```

---

## 🛠️ Utility Scripts

### Data Validation & Verification
- `verify_phase2.py` – Validate processed data
- `data_integrity_audit.py` – Check data quality
- `verify_html_visualization.py` – Validate HTML output
- `check_parquet.py` – Inspect Parquet files

### Data Correction & Fixing
- `precious_metals_supply_correction.py` – Fix metal supplies
- `fix_all_assets_per_date.py` – Fix missing asset dates
- `rebuild_top20.py`, `rebuild_top20_v2.py` – Regenerate rankings
- `8marketcap_complete_validation.py` – Validate against external sources

### Analysis & Reporting
- `detailed_analysis_report.py` – Generate detailed analysis
- `enhanced_visualization_builder.py` – Create enhanced visuals
- `post_backtest_validation.py` – Post-processing validation

---

## ✅ Completion Status

### Phase 1: Data Ingest ✅
- ✅ Fetch companies from yfinance
- ✅ Fetch crypto from CoinGecko
- ✅ Fetch metals prices
- ✅ Cache raw data locally

### Phase 2: Transform & Rank ✅
- ✅ Normalize asset data
- ✅ Compute market cap
- ✅ Rank by market cap (monthly)
- ✅ Detect rank transitions
- ✅ Save Parquet + CSV outputs

### Phase 3: Visualization ✅
- ✅ Generate Plotly bar-race animation
- ✅ Add interactive controls
- ✅ Apply color coding & branding
- ✅ Create metadata JSON
- ✅ Validate HTML output

### Phase 4: Cloud Deployment (Optional)
- 📋 VPS worker node templates available
- 📋 rsync/scp orchestration examples
- 📋 cron scheduling scripts

### Phase 5: Monitoring & Docs (Optional)
- ✅ Comprehensive documentation
- ✅ Verification scripts
- ✅ Data lineage tracking
- ✅ Error handling & logging

---

## 🐛 Troubleshooting

### "No module named 'yfinance'"
```bash
pip install -r requirements.txt
```

### "CoinGecko API timeout"
- Check internet connection
- CoinGecko free tier has rate limits (may need pause between calls)
- Script retries automatically 3 times

### "Parquet file corrupted"
```bash
# Regenerate from CSV
python scripts/02_build_rankings.py
```

### "HTML file won't render"
- Must use a modern browser (Chrome, Firefox, Safari, Edge)
- Check that Plotly.js is embedded (file size should be 5+ MB)
- Try opening in a different browser or with Python server

### "Missing data in visual"
Check logs:
```bash
cat data/logs/build_rankings_*.log
```
Then regenerate:
```bash
python scripts/02_build_rankings.py
python scripts/03_build_visualizations.py
```

---

## 🚀 Production Deployment

For continuous updates (e.g., monthly):

```bash
# Create a scheduled task (Windows):
# Task Scheduler → Create Task → Daily at 2 AM
# Action: powershell.exe -Command "cd c:\...\Data_visualization && python scripts/01_fetch_companies.py && python scripts/02_build_rankings.py && python scripts/03_build_visualizations.py"
```

Or on Linux/macOS:
```bash
# Add to crontab
0 2 1 * * cd /path/to/Data_visualization && python scripts/01_fetch_companies.py && python scripts/02_build_rankings.py && python scripts/03_build_visualizations.py
```

---

## 📦 Dependencies

Core libraries:
- **pandas** – Data manipulation
- **yfinance** – Stock market data
- **requests** – HTTP client for CoinGecko API
- **plotly** – Interactive visualizations
- **pyarrow** – Parquet file support

See `requirements.txt` for full list with versions.

---

## 📝 Recent Updates (2026-03)

### ✅ Version History
- **2026-03-03**: Initial GitHub commit with Phases 1-3 complete
- **2026-02-24**: Phase 3 visualization finalized
- **2026-02-23**: Phase 2 ranking system completed
- **2026-02-01**: Phase 1 data ingestion complete

### Latest Enhancements
- ✅ Synchronized data across companies, crypto, metals
- ✅ Confidence scoring system for data accuracy
- ✅ Interactive speed controls (0.5x-2x)
- ✅ Neon green color scheme for better visibility
- ✅ Responsive HTML5 visualization
- ✅ Comprehensive logging & error handling
- ✅ Full validation suite

---

## 🤝 Contributing

To contribute updates:
1. Create a new branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Commit: `git commit -m "Add: your feature"`
4. Push: `git push origin feature/your-feature`
5. Create a Pull Request

---

## 📄 License

This project uses publicly available market data from yfinance and CoinGecko APIs.

---

## 📞 Support

- **Data Issues**: Check `data/logs/` directory for processing logs
- **API Errors**: Verify internet connection and API rate limits
- **Visualization Issues**: Use modern browser, check console for JavaScript errors

**Need Help?** See the relevant documentation file in `docs/` or the phase-specific guide.

---

**Last Updated**: 2026-03-03 | **Status**: Production Ready | **Version**: 1.0
