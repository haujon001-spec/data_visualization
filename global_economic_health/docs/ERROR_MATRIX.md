# ERROR MATRIX - PROJECT 2 ERROR HANDLING GUIDE
**Project:** Global Economic Health Dashboard  
**Document:** Comprehensive Error Handling & Recovery Matrix  
**Date:** March 7, 2026  
**Version:** 1.0.0  

---

## Overview

This document defines all failure scenarios in Project 2's ETL, visualization, QA, and orchestrator pipeline. For each error:

- **Error Type** — What went wrong
- **Phase** — Which pipeline phase it occurs in
- **Detection Method** — How to detect it
- **Root Causes** — Why it happened
- **Recovery Action** — How to fix it
- **Logging** — How it's recorded
- **Prevention** — How to prevent it

---

## 1. API Failures

### 1.1 World Bank API Timeout (GDP Fetch)

**Phase:** Phase 1 - ETL (Step: Fetch GDP)

**Detection Method:**
```python
# In 01_fetch_gdp.py
if not response within 60 seconds:
    raise TimeoutError("API timeout after 60s")
```
- Orchestrator detects exception
- Logs: `[ERROR] API timeout: requests.Timeout`

**Root Causes:**
- Network connectivity issue
- World Bank API server overloaded
- DNS resolution failure
- Firewall blocking API endpoint

**Recovery Action:**
```
1. Check network connectivity (ping worldbank.org)
2. Verify no firewall blocking
3. Wait 2 seconds (exponential backoff)
4. Retry (max 3 retries configured in settings.yaml)
5. If 3 retries fail → STOP, return FAIL
```

**Logging:**
```
[2026-03-07 14:32:10] [STEP] Fetch GDP
[2026-03-07 14:32:15] [RETRY] API timeout, retrying (attempt 1/3)
[2026-03-07 14:32:17] [RETRY] API timeout, retrying (attempt 2/3)
[2026-03-07 14:32:19] [RETRY] API timeout, retrying (attempt 3/3)
[2026-03-07 14:32:21] [ERROR] API call failed after 3 retries
[2026-03-07 14:32:21] [FAIL] Fetch GDP step failed, stopping pipeline
```

**Prevention:**
- Monitor World Bank API status page before runs
- Run pipeline during off-peak hours (fewer requests)
- Cache recent API responses for testing

---

### 1.2 World Bank API Invalid Response (Population Fetch)

**Phase:** Phase 1 - ETL (Step: Fetch Population)

**Detection Method:**
```python
# In 01_fetch_population.py
response = requests.get(url)
if response.status_code != 200:
    raise ValueError(f"HTTP {response.status_code}")
if not response.json():
    raise ValueError("Empty response")
```

**Root Causes:**
- API endpoint changed
- World Bank API maintenance/downtime
- Invalid API key or permissions
- Response pagination issue

**Recovery Action:**
```
1. Log full API response for debugging
2. Check World Bank API documentation
3. Verify endpoint URL is correct (config/settings.yaml)
4. May need to update indicator code or URL
5. Retry manually after 5 minutes
6. If still failing → need manual investigation
```

**Logging:**
```
[2026-03-07 14:33:20] [VALIDATE] Response validation failed
[2026-03-07 14:33:20] [ERROR] HTTP 400: Invalid request
[2026-03-07 14:33:20] [ERROR] Full response saved to: reports/logs/api_response_error_7Mar2026.json
[2026-03-07 14:33:20] [FAIL] Fetch Population failed, stopping pipeline
```

**Prevention:**
- Periodically validate API response format
- Log sample response structures for comparison
- Set up API monitoring alerts

---

### 1.3 Debt Data Source Unavailable

**Phase:** Phase 1 - ETL (Step: Fetch Debt)

**Detection Method:**
```python
# In 03_fetch_debt.py
if source == "WORLD_BANK":
    try:
        response = requests.get(world_bank_url)
    except Exception as e:
        log("World Bank debt fetch failed, trying IMF backup")
        response = requests.get(imf_url)
```

**Root Causes:**
- Primary source (World Bank) unavailable
- Backup source (IMF) unavailable
- Both sources have incomplete data
- Authentication failure for IMF

**Recovery Action:**
```
1. Priority 1: Try World Bank IDS API
2. Priority 2: Fall back to IMF Global Debt Database
3. Priority 3: Use cached historical debt data
4. Priority 4: Continue without debt data (log warning)

If only debt partially available:
- Flag affected countries in QA report
- Forward-fill missing debt values for stable countries
- Continue pipeline with warnings
```

**Logging:**
```
[2026-03-07 14:34:00] [FETCH] Debt from World Bank IDS
[2026-03-07 14:34:15] [ERROR] World Bank IDS timeout
[2026-03-07 14:34:15] [FALLBACK] Trying IMF Global Debt Database
[2026-03-07 14:34:30] [WARNING] IMF response incomplete (150/180 countries)
[2026-03-07 14:34:30] [FORWARD_FILL] Using last-known debt value for 30 countries
[2026-03-07 14:34:30] [CONTINUE] Proceeding with partial debt data
```

**Prevention:**
- Monitor both data sources regularly
- Cache debt data locally (update weekly)
- Have manual debt CSV as fallback

---

## 2. Data Merge Conflicts

### 2.1 Missing GDP Data After Merge

**Phase:** Phase 1 - ETL (Step: Transform + Merge + Clean)

**Detection Method:**
```python
# In 04_transform_merge_clean.py
merged = gdp.merge(population, on=['country_code', 'year'], how='inner')
null_gdp = merged[merged['gdp_usd'].isnull()]

if len(null_gdp) > 0:
    log(f"WARNING: {len(null_gdp)} rows with missing GDP after merge")
    
if len(merged) < 100:  # Sanity check
    raise ValueError("Too few rows after merge (data integrity issue)")
```

**Root Causes:**
- GDP API incomplete (missing countries or years)
- Country code mismatch between datasets
- Date range mismatch
- One dataset has fewer countries than expected

**Recovery Action:**
```
1. Analyze which countries/years have missing GDP
2. Decision tree:
   a) If < 10% missing → Continue with warning
   b) If 10-30% missing → Log warning, re-fetch GDP
   c) If > 30% missing → FAIL, investigate API

3. For missing years:
   - Forward-fill: Use last known GDP value
   - Interpolate: Linear interpolation between years
   - Drop: Remove countries with too much missing data

4. For missing countries:
   - Re-run GDP fetch with expanded date range
   - Check country code mappings
```

**Logging:**
```
[2026-03-07 14:35:10] [MERGE] Merging GDP + Population + Debt
[2026-03-07 14:35:15] [WARNING] Missing GDP data
[2026-03-07 14:35:15] [ANALYSIS] 5 countries with missing GDP
[2026-03-07 14:35:15] [ANALYSIS] Affected countries: ZWE, SSD, AND, FSM, MHL
[2026-03-07 14:35:15] [ACTION] Forward-filling GDP for these countries
[2026-03-07 14:35:15] [RESULT] Merged {len(merged)} rows
```

**Prevention:**
- Pre-validate each data source before merge
- Log row counts after each fetch step
- Use sanity checks (min countries, min years)

---

### 2.2 Country Code Mismatch

**Phase:** Phase 1 - ETL (Step: Transform + Merge + Clean)

**Detection Method:**
```python
# In 04_transform_merge_clean.py
gdp_codes = set(gdp['country_code'].unique())
pop_codes = set(population['country_code'].unique())

mismatched = gdp_codes.symmetric_difference(pop_codes)

if len(mismatched) > 10:
    log(f"WARNING: {len(mismatched)} unmatched country codes")
    log(f"Mismatched codes: {mismatched}")
```

**Root Causes:**
- Inconsistent country code standards (ISO-2 vs ISO-3 vs numeric)
- Data source uses proprietary country codes
- Name spelling variations (e.g., "Czech Republic" vs "Czechia")
- Regional/temporal code changes

**Recovery Action:**
```
1. Create country code mapping CSV:
   old_code, new_code, country_name, notes
   
2. Use mapping to standardize codes:
   df['country_code'] = df['country_code'].map(code_mapping)
   
3. Re-attempt merge with standardized codes
4. Log any remaining unmatched items
5. If still > 5% unmatched → investigate manually
```

**Logging:**
```
[2026-03-07 14:35:20] [VALIDATE] Country code consistency
[2026-03-07 14:35:20] [WARNING] 12 mismatched country codes
[2026-03-07 14:35:20] [LOAD] Loading country code mapping: config/country_code_mapping.csv
[2026-03-07 14:35:20] [STANDARDIZE] Applying code mapping
[2026-03-07 14:35:20] [RETRY] Re-merging with standardized codes
[2026-03-07 14:35:20] [RESULT] 0 remaining mismatches
```

**Prevention:**
- Pre-validate country codes before merge
- Maintain updated country code mapping file
- Use World Bank ISO-3 code standard consistently

---

### 2.3 Year Range Mismatch

**Phase:** Phase 1 - ETL (Step: Transform + Merge + Clean)

**Detection Method:**
```python
# In 04_transform_merge_clean.py
gdp_years = set(gdp['year'].unique())
pop_years = set(population['year'].unique())

if len(gdp_years) != len(pop_years):
    missing_in_gdp = pop_years - gdp_years
    missing_in_pop = gdp_years - pop_years
    log(f"Year range mismatch: {missing_in_gdp}, {missing_in_pop}")
```

**Root Causes:**
- Data sources have different historical coverage
- API returns different date ranges
- Year filter parameter set incorrectly

**Recovery Action:**
```
1. Identify overlapping year range
2. Trim all datasets to overlapping years
3. Log original vs. trimmed year ranges
4. If overlapping period < 30 years → FLAG WARNING
5. Continue with trimmed data range
```

**Logging:**
```
[2026-03-07 14:35:30] [YEAR_RANGE] GDP: 1960-2026 (67 years)
[2026-03-07 14:35:30] [YEAR_RANGE] Population: 1960-2026 (67 years)
[2026-03-07 14:35:30] [YEAR_RANGE] Debt: 1990-2024 (35 years)
[2026-03-07 14:35:30] [TRIM] Using overlapping range: 1990-2024 (35 years)
[2026-03-07 14:35:30] [WARNING] Limited debt coverage may affect debt_to_gdp metrics
```

**Prevention:**
- Review and document expected year ranges per source
- Add year range validation in settings.yaml
- Log source-specific year coverages

---

## 3. Data Validation Failures

### 3.1 Impossible Value: Negative GDP

**Phase:** Phase 1 - ETL (Step: Data QA)

**Detection Method:**
```python
# In qa_agents/agent_data_qa.py
negative_gdp = df[df['gdp_usd'] < 0]

if len(negative_gdp) > 0:
    log(f"ERROR: {len(negative_gdp)} rows with negative GDP")
    raise DataQAError("Negative GDP values detected")
```

**Root Causes:**
- Data entry error in source
- Incorrect currency conversion
- Parsing error (negative sign misinterpreted)

**Recovery Action:**
```
1. Identify affected rows: country, year, gdp value
2. Re-fetch data for affected countries
3. Check if parsing/conversion error
4. If truly invalid → remove row and log
5. Verify no cascade (other metrics affected)
```

**Logging:**
```
[2026-03-07 14:36:00] [QA_DATA] Validating GDP values
[2026-03-07 14:36:00] [ERROR] Negative GDP found
[2026-03-07 14:36:00] [ERROR] Affected: ZWE (2009): -1.2M USD
[2026-03-07 14:36:00] [ACTION] Re-fetching ZWE GDP for 2009
[2026-03-07 14:36:05] [RESULT] Corrected value: 7.8B USD
[2026-03-07 14:36:05] [UPDATE] Updated ZWE 2009 GDP in dataset
```

**Prevention:**
- Validate value ranges immediately after fetch
- Log anomalies for review before processing
- Use data profiling on new sources

---

### 3.2 Impossible Value: Debt-to-GDP Ratio > 10

**Phase:** Phase 1 - ETL (Step: Data QA)

**Detection Method:**
```python
# In qa_agents/agent_data_qa.py
debt_ratio = df['debt_total_usd'] / df['gdp_usd']
impossible = df[debt_ratio > 10]

if len(impossible) > 0:
    log(f"ERROR: {len(impossible)} rows with debt_ratio > 10")
    raise DataQAError("Impossible debt-to-GDP ratio")
```

**Root Causes:**
- Data entry error (units wrong)
- Currency mismatch (debt in local, GDP in USD without conversion)
- Data from different years merged incorrectly
- Incomplete GDP or debt data

**Recovery Action:**
```
1. Flag affected country-years
2. Options:
   a) Re-fetch both GDP and debt for that country-year
   b) Verify units and conversion rates
   c) Check if data from same year
   d) If still > 10 → likely data error → REMOVE

3. Continue pipeline without affected rows
4. Log reason for removal
```

**Logging:**
```
[2026-03-07 14:36:15] [QA_DATA] Validating debt-to-GDP ratio
[2026-03-07 14:36:15] [ERROR] Impossible debt_ratio > 10
[2026-03-07 14:36:15] [ERROR] VEN 2016: debt_ratio = 23.4 (debt=450B, gdp=19.3B)
[2026-03-07 14:36:15] [INVESTIGATE] Re-checking Venezuela 2016 data
[2026-03-07 14:36:20] [RESULT] Confirmed error: GDP from 2015 accidentally used
[2026-03-07 14:36:20] [FIX] Re-fetching correct 2016 GDP
[2026-03-07 14:36:25] [REMOVE] Removing VEN 2016 from dataset due to data integrity issue
```

**Prevention:**
- Validate debt-to-GDP ratio immediately after calculation
- Add logic to detect unit mismatches
- Cross-check year alignment

---

### 3.3 QA Validation Failure: Missing Critical Fields

**Phase:** Phase 1 - ETL (Step: Data QA)

**Detection Method:**
```python
# In qa_agents/agent_data_qa.py
required_fields = ['country_code', 'year', 'gdp_usd', 'population', 'debt_total_usd']

for field in required_fields:
    if field not in df.columns:
        raise DataQAError(f"Missing required field: {field}")
    
    if df[field].isnull().sum() > len(df) * 0.15:  # 15% threshold
        raise DataQAError(f"Too many nulls in {field}: {pct}%")
```

**Root Causes:**
- CSV schema changed
- Data transformation step failed
- File corruption or incomplete write

**Recovery Action:**
```
1. Examine CSV header and first rows
2. Verify all transformation scripts ran successfully
3. Check orchestrator logs for failures
4. Re-run transformation step
5. Verify output CSVs created correctly
```

**Logging:**
```
[2026-03-07 14:36:30] [QA_DATA] Validating schema
[2026-03-07 14:36:30] [ERROR] Missing field: gdp_growth
[2026-03-07 14:36:30] [ERROR] Expected from: 04_transform_merge_clean.py
[2026-03-07 14:36:30] [ACTION] Checking orchestrator logs
[2026-03-07 14:36:35] [RESULT] Found error: Division by zero in gdp_growth calculation
[2026-03-07 14:36:35] [FIX] Fixed division by zero handling in 04_transform_merge_clean.py
[2026-03-07 14:36:35] [RETRY] Re-running transformation step
```

**Prevention:**
- Validate schema after each transformation
- Unit tests for derived metric calculations
- Pre-execution schema validation

---

## 4. Visualization Rendering Failures

### 4.1 Bubble Map Rendering Error

**Phase:** Phase 2 - Visualization (Step: Build Bubble Map)

**Detection Method:**
```python
# In 05_build_bubble_map.py
try:
    fig.write_html(output_path)
except Exception as e:
    log(f"ERROR: Failed to render bubble map: {e}")
    raise
```

**Root Causes:**
- Missing geojson file (map data)
- Corrupted CSV data preventing Plotly processing
- Memory exhaustion (large dataset)
- Plotly dependency issue

**Recovery Action:**
```
1. Check if GeoJSON file exists: config/map_geojson.json
2. Validate CSV data types (numeric columns must be numeric)
3. Check if dataset too large (>100K rows → subsample)
4. Verify Plotly version compatibility
5. Reduce bubble count or combine countries if needed
```

**Logging:**
```
[2026-03-07 14:37:00] [VIZ] Building bubble map
[2026-03-07 14:37:15] [ERROR] Rendering failed
[2026-03-07 14:37:15] [ERROR] Plotly error: column 'gdp_usd' not numeric
[2026-03-07 14:37:15] [ACTION] Checking data types in CSV
[2026-03-07 14:37:20] [RESULT] Found: gdp_usd is string, not float
[2026-03-07 14:37:20] [FIX] Re-ran 04_transform_merge_clean.py with type conversion
[2026-03-07 14:37:25] [RETRY] Re-building bubble map with corrected data
```

**Prevention:**
- Validate CSV data types before visualization
- Unit test bubble map with small sample
- Check GeoJSON file at pipeline start

---

### 4.2 Bubble Map Missing Countries

**Phase:** Phase 2 - Visualization (Step: Build Bubble Map)

**Detection Method:**
```python
# In ui_qa/agent_ui_qa.py
expected_countries = set(df['country_name'].unique())
rendered_countries = extract_countries_from_html(html)

missing = expected_countries - rendered_countries
if len(missing) > 0:
    log(f"WARNING: {len(missing)} countries missing from map")
    log(f"Missing: {missing}")
```

**Root Causes:**
- Country not in GeoJSON file (no coordinates)
- Country code not matching GeoJSON
- Continent/region aggregates excluded
- Map library doesn't support certain countries

**Recovery Action:**
```
1. Identify which countries missing
2. For each missing country:
   a) Check if in GeoJSON file
   b) If not → add to manual location mapping
   c) If yes → check country code match
3. Update GeoJSON or country mapping
4. Re-build bubble map
5. Continue if most countries (>95%) are shown
```

**Logging:**
```
[2026-03-07 14:37:30] [UI_QA] Validating bubble map countries
[2026-03-07 14:37:30] [WARNING] 8 countries missing from map
[2026-03-07 14:37:30] [WARNING] Missing: ATF, GGY, JEY, KOS, PSE, SJM, TLS, WBK
[2026-03-07 14:37:30] [INFO] These are small territories/disputed regions
[2026-03-07 14:37:30] [ACTION] Continuing with 172/180 countries (95.6%)
```

**Prevention:**
- Pre-check GeoJSON coverage for all countries
- Map territorial/disputed regions manually if needed
- Document excluded countries

---

### 4.3 Trendline Animation Performance Issue

**Phase:** Phase 2 - Visualization (Step: Build Population Trendline)

**Detection Method:**
```python
# In 06_build_population_trendline.py / monitoring
html_file_size = output_path.stat().st_size
if html_file_size > 50 * 1024 * 1024:  # 50 MB threshold
    log(f"WARNING: HTML file very large: {html_file_size / 1024 / 1024}MB")
    
# Browser performance test
animation_frames = count_frames(html_output)
if animation_frames > 200:  # Too many frames
    log(f"WARNING: {animation_frames} animation frames (may be slow)")
```

**Root Causes:**
- Too many animation frames (yearly for 100+ years)
- Too many countries in trendline (memory issue)
- Embedded data duplicated unnecessarily
- Plotly config not optimized

**Recovery Action:**
```
1. Reduce top-N countries (from 15 to 10)
2. Reduce animation granularity (every 2 years instead of 1)
3. Optimize Plotly config (reduce hover data)
4. Check if HTML needs gzip compression
5. Load test in browser with performance monitor
```

**Logging:**
```
[2026-03-07 14:37:45] [VIZ] Building population trendline
[2026-03-07 14:37:50] [WARNING] HTML output size: 65 MB (threshold: 50 MB)
[2026-03-07 14:37:50] [ANALYSIS] Animation frames: 67 (reasonable)
[2026-03-07 14:37:50] [ANALYSIS] Hover data is large
[2026-03-07 14:37:50] [ACTION] Reducing hover data precision
[2026-03-07 14:37:55] [RETRY] Rebuilding trendline with optimized config
[2026-03-07 14:38:00] [RESULT] Output size: 38 MB
```

**Prevention:**
- Profile HTML performance before scaling
- Set file size limits in pre-execution checks
- Test animation in browser with dev tools

---

## 5. Orchestrator Step Failures

### 5.1 Step Timeout

**Phase:** Any phase

**Detection Method:**
```python
# In orchestrator.py
import signal

def timeout_handler(signum, frame):
    raise TimeoutError(f"Step exceeded {timeout}s limit")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(step_timeout_seconds)

try:
    run_step()
except TimeoutError:
    log(f"Step timed out after {timeout}s")
    raise
```

**Root Causes:**
- Dataset larger than expected
- Network latency causing API delays
- Insufficient compute resources
- Step has algorithmic inefficiency

**Recovery Action:**
```
1. Log which step timed out
2. Log duration and expected duration
3. Increase timeout in config/settings.yaml (if reasonable)
4. Profile step to identify bottleneck
5. Optimize or parallelize if possible
6. Retry with increased timeout
```

**Logging:**
```
[2026-03-07 14:38:15] [STEP] Transform + Merge + Clean (timeout: 120s)
[2026-03-07 14:39:15] [TIMEOUT] Step exceeded 120s limit
[2026-03-07 14:39:15] [ERROR] Step failed due to timeout
[2026-03-07 14:39:15] [ANALYSIS] Processing 500K+ rows took 125s
[2026-03-07 14:39:15] [ACTION] Increasing timeout to 180s in settings.yaml
[2026-03-07 14:39:15] [RETRY] Re-running orchestrator with new timeout
```

**Prevention:**
- Profile each step with real data before production
- Set initial timeouts conservatively (1.5x expected)
- Monitor resource usage (CPU, memory, disk I/O)

---

### 5.2 Orchestrator Step Process Killed

**Phase:** Any phase

**Detection Method:**
```python
# In orchestrator.py
# Check if subprocess exit code indicates kill signal
if return_code < 0:  # Negative code = killed by signal
    signal_num = abs(return_code)
    log(f"Process killed by signal {signal_num}")
    raise ProcessKilledError(f"Killed by signal {signal_num}")
```

**Root Causes:**
- Out of memory (OOM killer)
- System resource exhaustion
- External process termination
- User manual kill

**Recovery Action:**
```
1. Check system resource usage at time of failure
2. If OOM:
   - Reduce batch size in processing steps
   - Subsample data for testing
   - Add swap space (temporary)
   - Use 64-bit Python (if not already)

3. If other signals:
   - Check system logs
   - Investigate other processes
   - Rerun after resources freed

4. Increase available memory/resources
5. Retry orchestrator
```

**Logging:**
```
[2026-03-07 14:39:30] [STEP] Data QA (running in subprocess)
[2026-03-07 14:39:45] [ERROR] Subprocess killed by signal 9 (SIGKILL - OOM)
[2026-03-07 14:39:45] [SYSTEM] Memory at time: 95% of {total_mem}GB
[2026-03-07 14:39:45] [ACTION] Will subsample data to 250K rows
[2026-03-07 14:39:45] [NOTE] Full data QA deferred to cloud execution
```

**Prevention:**
- Monitor memory usage per step
- Set memory limits per subprocess
- Test with large data beforehand
- Use CloudShell with more resources

---

### 5.3 Missing Step Output File

**Phase:** Any phase

**Detection Method:**
```python
# In orchestrator.py (after each step)
expected_output = Path(step_config['expected_output'])

if not expected_output.exists():
    raise FileNotFoundError(
        f"Expected output not found: {expected_output}"
    )
```

**Root Causes:**
- Step failed silently (exception not caught)
- Wrong output path configuration
- Output directory permissions issue
- Disk space exhausted

**Recovery Action:**
```
1. Check orchestrator logs for step errors
2. Verify output path in configuration
3. Check directory permissions:
   - Can orchestrator process write to reports/ ?
   - Are parent directories created?
4. Check disk space: df -h
5. Re-run failed step with debugging
6. Verify step produces output with sample data first
```

**Logging:**
```
[2026-03-07 14:39:50] [VERIFY] Checking outputs from Data QA step
[2026-03-07 14:39:50] [ERROR] Missing output: reports/qa/data_qa_report_7Mar2026.json
[2026-03-07 14:39:50] [ACTION] Checking orchestrator logs
[2026-03-07 14:39:55] [RESULT] Step logged: "File write failed: Permission denied"
[2026-03-07 14:39:55] [FIX] reports/qa/ directory has read-only permissions
[2026-03-07 14:39:55] [ACTION] Fixing permissions: chmod -R 755 reports/
[2026-03-07 14:40:00] [RETRY] Re-running Data QA step
```

**Prevention:**
- Create all output directories at pipeline start
- Verify write permissions at startup
- Sub-step logging to detect silent failures

---

## 6. Verification Layer Failures

### 6.1 Verification: Code Structure Check Failed

**Phase:** Verification

**Detection Method:**
```python
# In verification/verify_code_structure.py
required_scripts = [
    'scripts/01_fetch_gdp.py',
    'scripts/02_fetch_population.py',
    # ... etc
]

for script in required_scripts:
    if not Path(script).exists():
        raise VerificationError(f"Missing script: {script}")
```

**Root Causes:**
- Script not created yet
- Script file deleted
- Script path in wrong location
- Wrong file extension

**Recovery Action:**
```
1. Identify which script(s) missing
2. Verify against task manifests
3. Re-create missing scripts (background agent)
4. Re-verify
5. Continue only if all scripts present
```

**Logging:**
```
[2026-03-07 14:40:10] [VERIFY] Code structure check
[2026-03-07 14:40:10] [ERROR] Missing script: scripts/01_fetch_gdp.py
[2026-03-07 14:40:10] [ACTION] Re-requesting script creation from background agent
[2026-03-07 14:40:30] [RESULT] Script created
[2026-03-07 14:40:30] [PASS] Code structure verification passed
```

**Prevention:**
- Create scripts before orchestrator runs
- Use pre-execution task manifest checks

---

### 6.2 Verification: Output Schema Check Failed

**Phase:** Verification

**Detection Method:**
```python
# In verification/verify_outputs.py
expected_schema = {
    'country_code': 'object',
    'year': 'int64',
    'gdp_usd': 'float64',
    'population': 'int64',
    'debt_total_usd': 'float64'
}

df = pd.read_csv(csv_file)
for col, dtype in expected_schema.items():
    if col not in df.columns:
        raise VerificationError(f"Missing column: {col}")
    if str(df[col].dtype) != dtype:
        raise VerificationError(
            f"Wrong dtype for {col}: {df[col].dtype} vs {dtype}"
        )
```

**Root Causes:**
- Transformation script modified schema
- CSV written with wrong encoding
- Data type conversion failed
- Column naming inconsistency

**Recovery Action:**
```
1. Examine actual CSV headers and types
2. Compare with expected schema in Phase 1 docs
3. Find which transformation step changed schema
4. Fix transformation logic
5. Re-run transformation
6. Re-verify
```

**Logging:**
```
[2026-03-07 14:40:20] [VERIFY] Output schema check
[2026-03-07 14:40:20] [ERROR] Wrong dtype for gdp_usd: object (expected float64)
[2026-03-07 14:40:20] [ACTION] Checking 04_transform_merge_clean.py
[2026-03-07 14:40:25] [RESULT] Missing .astype(float) conversion
[2026-03-07 14:40:25] [FIX] Added type conversion in transform script
[2026-03-07 14:40:25] [RETRY] Re-running transformation step
```

**Prevention:**
- Add schema assertion to each ETL step
- Log data types after each transformation
- Unit tests for schema preservation

---

## 7. Cloud Agent Communication Failures

### 7.1 Heartbeat Timeout

**Phase:** Orchestrator execution (Cloud Agent monitoring)

**Detection Method:**
```python
# In cloud_agent monitoring loop
last_heartbeat = get_last_heartbeat_timestamp(log_file)
elapsed = now() - last_heartbeat

if elapsed > 60:  # 60 second timeout
    log(f"Heartbeat timeout: {elapsed}s elapsed")
    terminate_orchestrator()
    return "TIMEOUT"
```

**Root Causes:**
- Orchestrator hung or deadlocked
- Log file not being written
- File system issue preventing writes
- Network issue (even on localhost)

**Recovery Action:**
```
1. Check if orchestrator process still running
2. Check orchestrator logs for errors
3. Check disk space
4. Check file descriptor limits
5. Kill hung process
6. Retry orchestrator with debugging enabled
```

**Logging:**
```
[Cloud Agent] [2026-03-07 14:41:00] Heartbeat timeout (60s)
[Cloud Agent] [2026-03-07 14:41:00] Terminating orchestrator PID 12345
[Cloud Agent] [2026-03-07 14:41:05] Checking orchestrator logs...
[Cloud Agent] [2026-03-07 14:41:05] Last log entry: 14:40:45 - "Processing 500K rows..."
[Cloud Agent] [2026-03-07 14:41:05] Orchestrator appears hung
[Cloud Agent] [2026-03-07 14:41:05] Retrying with max_retries=1
```

**Prevention:**
- Add frequent heartbeat entries in long-running steps
- Monitor resource usage to detect bottlenecks
- Use subprocess timeouts as safety

---

### 7.2 Task Result Retrieval Failure

**Phase:** After orchestrator completion

**Detection Method:**
```python
# In cloud agent result handling
result_file = Path(project_root) / "reports" / f"orchestrator_result_{timestamp}.json"

if not result_file.exists():
    raise FileNotFoundError(
        f"Orchestrator result file not found: {result_file}"
    )

result = json.load(result_file)
if result['status'] not in ['PASS', 'FAIL']:
    raise ValueError(f"Invalid status: {result['status']}")
```

**Root Causes:**
- Orchestrator didn't write result file
- Result file corrupted
- Wrong timestamp in filename
- Orchestrator failed before writing result

**Recovery Action:**
```
1. Check orchestrator logs for final status
2. Manually inspect orchestrator_log_*.txt for [COMPLETE] or [FAILED]
3. Parse final log line to extract result
4. If result found in logs → create result JSON manually
5. If not found → orchestrator failed, check errors
6. If errors found → fix and retry
```

**Logging:**
```
[Cloud Agent] [2026-03-07 14:42:00] Retrieving orchestrator result
[Cloud Agent] [2026-03-07 14:42:00] ERROR: Result file not found
[Cloud Agent] [2026-03-07 14:42:00] Checking orchestrator logs...
[Cloud Agent] [2026-03-07 14:42:05] Found final entry: "[COMPLETE] status=PASS"
[Cloud Agent] [2026-03-07 14:42:05] Parsing result from log entry
[Cloud Agent] [2026-03-07 14:42:05] SUCCESS: Extracted result from logs
```

**Prevention:**
- Write result JSON at multiple points in orchestrator
- Always write final status to both log and JSON
- Verify result file created before returning success

---

## 8. Summary Table

| Error Type | Phase | Severity | Recovery Time | Prevention |
|------------|-------|----------|----------------|------------|
| API Timeout | ETL | Medium | 2-5 min | Retry logic, monitor endpoints |
| API Invalid Response | ETL | High | 10+ min | Response validation, schema checks |
| Data Merge Conflict | ETL | High | 30+ min | Pre-merge validation, code mapping |
| Negative GDP | QA | High | 5-10 min | Value validation, unit tests |
| Impossible Ratio | QA | Medium | 10-20 min | Range validation, data profiling |
| Visualization Render | VIZ | Medium | 10-15 min | Data type validation, unit tests |
| Missing Countries | VIZ | Low | N/A (warning) | GeoJSON validation |
| Performance Issue | VIZ | Low | 5-10 min | Profiling, optimization |
| Step Timeout | ORCH | High | 5-10 min | Profiling, increase timeout |
| Process Killed | ORCH | High | 15-30 min | Memory monitoring, resource mgmt |
| Missing Output | ORCH | High | 10-20 min | Output verification, permissions |
| Code Check Failed | VERIFY | High | 5 min | Pre-execution checks |
| Schema Check Failed | VERIFY | Medium | 10-15 min | Schema assertions, unit tests |
| Heartbeat Timeout | CLOUD | High | 10-15 min | Frequent heartbeats, monitoring |
| Result Not Found | CLOUD | Medium | 10 min | Multiple result writes, validation |

---

## 9. Recommended Actions by Severity

**CRITICAL (Stop Immediately):**
- Negative GDP or impossible data values
- Missing required fields
- Code structure failure
- Orchestrator process killed

**HIGH (Investigate):**
- API failures after 3 retries
- Severe data merge conflicts (>30% missing)
- Missing step outputs
- Visualization schema errors

**MEDIUM (Log and Continue):**
- Partial data missing (< 15%)
- API invalid response (fallback available)
- Minor visualization issues
- Heartbeat warnings

**LOW (Warning Only):**
- Missing some countries from map
- Performance not ideal but acceptable
- Extra data beyond required

---

**Last Updated:** March 7, 2026  
**Owner:** Project 2 Team  
**Review Schedule:** Quarterly
