### Project Overview

**Project name**: Global Top‑20 Market Cap Evolution Dashboard  
**Goal**: Build an interactive, animated dashboard that shows how the top 20 global market‑cap assets evolve over a 10‑year period, including **public companies**, **top cryptocurrencies**, and **precious metals**.  
**Stack**: Python • Pandas • yfinance • CoinGecko • Plotly • VS Code • DigitalOcean VPS (optional cloud workers).  

**What this file contains**  
- A phase‑by‑phase implementation plan you can follow in VS Code.  
- Clear handling rules for stock splits, dilution, and consolidated shares.  
- UX rules and annotations to make accuracy and assumptions visible in the interactive chart.  
- Success criteria, acceptance tests, and don'ts.

---

### Phase Plan

#### Phase 0 Preflight
- **Deliverables**: `config/*.csv` templates, `requirements.txt`, `README.md`.  
- **Actions**: Populate `config/universe_companies.csv`, `config/crypto_list.csv`, `config/precious_metals_supply.csv`, `config/vps_list.csv`.  
- **Validation**: Run `scripts/00_validate_sources.py` and `scripts/00_validate_vps.py` to confirm API connectivity and VPS SSH/HTTP readiness.  
- **Outcome**: Clean baseline; all sources reachable and VPS accessible.

#### Phase 1 Data Ingest
- **Deliverables**: Raw files in `data/raw/` for companies, crypto, and metals.  
- **Actions**:
  - Use `yfinance` multi‑ticker monthly downloads for equities and metals (`interval="1mo"`).  
  - Use CoinGecko `/market_chart` or `/market_chart/range` to fetch crypto `market_caps`.  
  - Cache `sharesOutstanding` once per ticker to `config/shares_outstanding.csv`.  
  - Save raw outputs as CSV or Parquet.  
- **Outcome**: Complete raw dataset covering the target 10‑year window.

#### Phase 2 Transform and Ranking
- **Deliverables**: `data/processed/top20_monthly.parquet` and CSV.  
- **Actions**:
  - Normalize timestamps to monthly period.  
  - Compute market cap per asset type:
    - **Company**: `adjusted_close × shares_outstanding` (note approximation if shares history missing).  
    - **Crypto**: use CoinGecko `market_caps` or `price × circulating_supply`.  
    - **Metal**: `spot_price_per_ounce × ounces_supply` from `precious_metals_supply.csv`.  
  - Concatenate assets into unified table: `date, asset_id, asset_type, label, market_cap, source, confidence`.  
  - Rank per date and extract top 20.  
- **Outcome**: Reproducible ranked dataset ready for visualization.

#### Phase 3 Visualization and UX
- **Deliverables**: `data/processed/bar_race_top20.html`, optional Streamlit wrapper.  
- **Actions**:
  - Build animated bar chart race with Plotly using `animation_frame="date"` and `animation_group="label"`.  
  - Add interactive controls: date slider, asset filter, asset type toggle, sector filter, currency selector.  
  - Implement annotations and tooltips for corporate actions and data confidence (see next section).  
- **Outcome**: Smooth, explorable animation with clear provenance and notes.

#### Phase 4 Cloud Acceleration and Deployment
- **Deliverables**: Cloud job templates and deployment instructions.  
- **Actions**:
  - Use your two DigitalOcean VPS: one for ingestion (parallel downloads), one for transforms and HTML generation.  
  - Orchestrate with simple shell scripts or a lightweight job runner; use `rsync`/`scp` to move artifacts.  
  - Schedule periodic refreshes with `cron` or CI.  
- **Outcome**: Faster ETL runs and reproducible artifact generation.

#### Phase 5 Polish Monitoring and Documentation
- **Deliverables**: README, troubleshooting, data lineage logs, monitoring alerts.  
- **Actions**:
  - Add logging for missing shares, API failures, and large month‑over‑month jumps.  
  - Create a small dashboard page with data source attributions and a changelog.  
  - Add acceptance tests and a short runbook for re‑runs and recovery.  
- **Outcome**: Production‑ready repo and clear operational guidance.

---

### Data Accuracy and Dilution Handling

**Core principle**  
Be explicit about assumptions and show confidence levels in the UI. Market cap for each asset must be accompanied by a **source** and a **confidence tag** (High, Medium, Low).

**Stock splits**
- **Effect**: No change to market cap.  
- **Implementation**: Use split‑adjusted prices (`auto_adjust=True` or adjusted close). No special annotation required beyond normal tooltips.

**Dilution and share issuance**
- **Effect**: Changes shares outstanding; market cap can increase or decrease depending on price reaction and capital raised.  
- **Implementation**:
  - **Primary approach**: If historical `sharesOutstanding` is unavailable, compute market cap using **adjusted price × latest sharesOutstanding** and mark **confidence = Medium**.  
  - **Better approach**: If you can obtain quarterly historical shares outstanding (paid sources or company filings), compute exact historical market cap and mark **confidence = High**.
- **Visualization note**: When a large dilution event is detected (e.g., shares outstanding increases by >10% quarter‑over‑quarter), add a **visible marker** on the timeline and a tooltip explaining the event and its source.

**Share buybacks**
- **Effect**: Reduces shares outstanding; can increase per‑share price.  
- **Implementation**: Same as dilution — detect large decreases in shares outstanding and annotate.

**Consolidated shares and corporate actions**
- **Mergers, spin‑offs, reverse splits, delistings**: treat as lifecycle events.  
- **Implementation**:
  - Add **lifecycle annotations** (entered, merged, delisted) to the asset row.  
  - If a company changes ticker or is replaced by a consolidated entity, show a **link icon** in the tooltip and explain the mapping.

**ADRs and dual class shares**
- **Effect**: ADR ratios and multiple classes can distort naive calculations.  
- **Implementation**: Prefer the most liquid class; document the choice in `config/universe_companies.csv` and show it in the tooltip.

**Confidence and provenance**
- **Field**: `confidence` with values **High**, **Medium**, **Low**.  
- **Rule**: Show `source` (yfinance, CoinGecko, World Gold Council, manual) and `confidence` in every tooltip and in a persistent legend.

---

### Visualization Annotations and UX Rules

**Annotations to include on the interactive chart**
- **Corporate action markers**: visible dot on the date with hover text: `Action: Stock split 10‑for‑1; Source: company filing; Effect: price adjusted`.  
- **Dilution markers**: flag when shares outstanding changes by a threshold (e.g., ±10%) with explanation and link to source.  
- **Data confidence badge**: small colored badge next to asset label (green = High, amber = Medium, red = Low).  
- **Source attribution**: footer or info panel listing data sources and last refresh timestamp.  
- **Asset type icon**: company, crypto, metal icons to visually separate asset classes.

**UX behavior**
- **Default view**: monthly frames for 10 years (~120 frames) with autoplay and manual slider.  
- **Performance**: limit unique colors; group by sector or asset type when many assets are visible.  
- **Interactivity**: clicking an asset pins it and shows a side panel with detailed time series, corporate actions, and data confidence.  
- **Export**: allow exporting the current frame as PNG (client side) but do not auto‑generate files server side.

**Remarkable notes to display prominently**
- **Market cap approximations**: a short banner: **"Market cap values are computed using adjusted prices and available shares outstanding. Historical shares outstanding may be approximated; see tooltip for confidence and source."**  
- **Private companies excluded**: a note explaining why private firms are not in the ranking.

---

### Acceptance Criteria and Tests

**Success criteria**
- **ETL**: `data/processed/top20_monthly.csv` exists with ≥120 monthly frames and includes companies, top 5 cryptos, and metals where applicable.  
- **Visualization**: `bar_race_top20.html` animates smoothly in modern browsers and shows entries/exits.  
- **Data quality**: no negative market caps; major anomalies logged and annotated.  
- **Performance**: full pipeline for ~300 tickers + crypto + metals completes within target time on VPS (ingest + transform < 2 hours for recommended VPS specs).

**Automated acceptance tests**
- **Connectivity**: `00_validate_sources.py` and `00_validate_vps.py` return exit code 0.  
- **Completeness**: raw files exist for ≥90% of tickers.  
- **Ranking sanity**: top 20 market caps are non‑negative and sorted descending per date.  
- **Annotation coverage**: corporate actions with large share changes are annotated in processed data.

**Don'ts**
- **Do not** treat private companies as market cap entries.  
- **Do not** rely on yfinance for perfect historical shares outstanding without marking confidence.  
- **Do not** scrape sites that disallow scraping; use APIs or licensed data.

---

### Next Steps and Follow up

**Immediate next step**  
- Run Phase 0 validation scripts to confirm API and VPS connectivity.

**What happens next**  
- Phase 1: Execute data ingest scripts to populate `data/raw/` with company, crypto, and metal data.
- Phase 2: Build ranking logic and produce `data/processed/top20_monthly.csv`.  
- Phase 3: Generate interactive HTML visualization.
