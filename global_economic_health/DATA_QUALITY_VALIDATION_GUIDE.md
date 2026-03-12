# Data Quality Validation System

## Quick Start

Before running any visualizations, validate your data quality:

```powershell
python global_economic_health\scripts\data_quality_validator.py
```

## What It Checks

### 1. **Debt/GDP Ratio Consistency**
- ✓ Detects mixed formats (decimal vs percentage)
- ✓ Recalculates from source and compares with stored values
- ✗ **Issue Found**: China/India/Brazil stored as decimals (0.80 vs 80%)

### 2. **Missing Data Analysis**
- ✓ Checks for missing GDP, population, debt values
- ✗ **Issue Found**: 43.9% of recent records missing debt data

### 3. **Outlier Detection**
- ✓ Identifies extreme statistical outliers
- ℹ️ **Note**: Some outliers are legitimate (e.g., Japan 237% is accurate)

### 4. **Currency Unit Consistency**
- ✓ Validates GDP per capita calculations
- ✓ Ensures consistent units across all records

## Example Output

```
[CHECK 1] Debt/GDP Ratio Consistency
✗ Found 3 debt/GDP inconsistencies:
  Brazil: Stored=0.82, Calculated=82.35% - Stored as decimal
  China: Stored=0.80, Calculated=80.03% - Stored as decimal
  India: Stored=0.77, Calculated=76.73% - Stored as decimal

DATA QUALITY VALIDATION REPORT
======================================================================
✗ FOUND 3 ISSUES:
  - Debt/GDP Format: 3 problems
  - Missing debt_total_usd: 534 problems
  - Debt/GDP Outliers: 3 problems

⚠ RECOMMENDATION: Fix these issues before running visualizations
```

## How The Dashboard Handles This

The dashboard **automatically recalculates** debt/GDP ratios from source data:

```python
# Instead of trusting the stored column:
debt_to_gdp_calculated = (debt_total_usd / gdp_usd) * 100
```

This ensures:
- ✓ **China**: Now shows 80.03% (was 0.8%)
- ✓ **India**: Now shows 76.73% (was 0.77%)
- ✓ **Brazil**: Now shows 82.35% (was 0.82%)
- ✓ **USA**: Still shows 124% (unchanged, was already correct)

## Human-Readable Formatting

All currency values now display in B/T format:

```
Debt: $15.00T (instead of $15,000,000,000,000)
GDP: $18.74T
Debt/GDP: 80.0%
```

## Integration Workflow

**Recommended workflow:**

1. **Run validator** before visualization:
   ```powershell
   python global_economic_health\scripts\data_quality_validator.py
   ```

2. **Review issues** - decide if they need fixing or are acceptable

3. **Run dashboard** - it auto-corrects known issues:
   ```powershell
   cd global_economic_health
   python viz\dashboard_four_panel_animated_12Mar2026.py
   ```

4. **Verify results** in browser - hover over bars to check values

## Adding New Checks

To add custom validation checks, edit `data_quality_validator.py`:

```python
def check_custom_rule(self):
    """Your custom validation logic."""
    logger.info("\n[CHECK X] Your Check Name")
    
    # Your validation code here
    issues_found = []
    
    if issues_found:
        logger.warning(f"✗ Found {len(issues_found)} issues")
        self.issues.append(('Your Check', issues_found))
    else:
        logger.info("✓ Check passed")
    
    return len(issues_found) == 0
```

Then add it to `run_all_checks()`:

```python
checks = [
    self.check_debt_to_gdp_consistency,
    self.check_missing_data,
    self.check_outliers,
    self.check_data_currency_units,
    self.check_custom_rule  # ← Add your check
]
```

## Exit Codes

- `0` = All checks passed ✓
- `1` = Issues found ⚠

Use in CI/CD pipelines:

```powershell
python data_quality_validator.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Data quality validation failed!"
    exit 1
}
```
