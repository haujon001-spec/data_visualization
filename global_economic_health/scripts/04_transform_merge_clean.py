# -*- coding: utf-8 -*-
"""
Transform, Merge, and Clean Global Economic Data

Merges GDP, Population, and Debt datasets into unified macro-economic table.
Applies transformations, cleaning rules, and derives key metrics.

Input CSVs:
  - gdp_raw_<timestamp>.csv
  - population_raw_<timestamp>.csv
  - debt_raw_<timestamp>.csv

Output CSVs:
  - macro_merged_<timestamp>.csv (raw merged)
  - macro_clean_<timestamp>.csv (after cleaning)
  - macro_final_<timestamp>.csv (ready for visualization)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def get_latest_csv(directory: Path, pattern: str, alt_pattern: str = None) -> Path:
    """
    Find latest timestamped CSV file matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Pattern in filename (e.g., 'gdp_raw_')
        alt_pattern: Alternative pattern to try if primary fails
    
    Returns:
        Path to latest matching file
    
    Raises:
        FileNotFoundError: If no matching file found
    """
    matching_files = list(directory.glob(f"{pattern}*.csv"))
    
    # Try alternative pattern if provided and primary didn't match
    if not matching_files and alt_pattern:
        matching_files = list(directory.glob(f"{alt_pattern}*.csv"))
    
    if not matching_files:
        if alt_pattern:
            raise FileNotFoundError(f"No files matching '{pattern}*.csv' or '{alt_pattern}*.csv' in {directory}")
        else:
            raise FileNotFoundError(f"No files matching '{pattern}*.csv' in {directory}")
    
    # Sort by modification time and get latest
    latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"[LOAD] Found latest file: {latest_file.name}")
    return latest_file


def load_raw_csvs(raw_dir: Path) -> tuple:
    """
    Load all three raw CSV files (GDP, Population, Debt).
    
    Args:
        raw_dir: Path to raw CSV directory
    
    Returns:
        Tuple of (gdp_df, population_df, debt_df)
    """
    logger.info("[LOAD] Loading raw CSV files...")
    
    gdp_file = get_latest_csv(raw_dir, 'gdp_raw_')
    gdp_df = pd.read_csv(gdp_file)
    logger.info(f"[LOAD] GDP: {len(gdp_df)} rows, {len(gdp_df['country_code'].unique())} countries")
    
    # Try 'population_raw_' first, then 'worldbank_population_raw_' (from reused Project 1 script)
    pop_file = get_latest_csv(raw_dir, 'population_raw_', alt_pattern='worldbank_population_raw_')
    pop_df = pd.read_csv(pop_file)
    logger.info(f"[LOAD] Population: {len(pop_df)} rows, {len(pop_df['country_code'].unique())} countries")
    
    debt_file = get_latest_csv(raw_dir, 'debt_raw_')
    debt_df = pd.read_csv(debt_file)
    logger.info(f"[LOAD] Debt: {len(debt_df)} rows, {len(debt_df['country_code'].unique())} countries")
    
    return gdp_df, pop_df, debt_df


def merge_datasets(gdp_df: pd.DataFrame, pop_df: pd.DataFrame, debt_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge GDP, population, and debt on country_code and year.
    Uses inner join to keep only complete observations.
    
    Args:
        gdp_df: GDP dataframe
        pop_df: Population dataframe
        debt_df: Debt dataframe
    
    Returns:
        Merged dataframe
    """
    logger.info("[MERGE] Merging datasets...")
    
    # First merge GDP and Population
    merged = gdp_df.merge(
        pop_df,
        on=['country_code', 'year'],
        how='inner',
        suffixes=('', '_pop')
    )
    
    # Rename population columns for clarity
    merged = merged.rename(columns={'country_name': 'country_name'})
    if 'country_name_pop' in merged.columns:
        merged = merged.drop(columns=['country_name_pop'])
    
    logger.info(f"[MERGE] After GDP+Population: {len(merged)} rows")
    
    # Then merge with Debt (using outer join first to detect mismatches)
    merged = merged.merge(
        debt_df,
        on=['country_code', 'year'],
        how='left',
        suffixes=('', '_debt')
    )
    
    # Handle country name conflicts
    if 'country_name_debt' in merged.columns:
        merged = merged.drop(columns=['country_name_debt'])
    
    logger.info(f"[MERGE] After joining Debt: {len(merged)} rows")
    logger.info(f"[MERGE] Countries in final merge: {merged['country_code'].nunique()}")
    
    return merged


def apply_cleaning_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply data cleaning rules per Phase 1 specification.
    
    Rules:
    - Remove rows with missing GDP or population (critical fields)
    - Remove countries with population < 10,000
    - Remove impossible debt_to_gdp ratios (> 10)
    - Handle missing debt values (forward-fill for stable countries)
    
    Args:
        df: Merged dataframe
    
    Returns:
        Cleaned dataframe
    """
    logger.info("[CLEAN] Applying cleaning rules...")
    
    initial_rows = len(df)
    
    # Rule 1: Remove rows with missing GDP or population
    logger.info("[CLEAN] Rule 1: Removing rows with missing GDP or population")
    df = df.dropna(subset=['gdp_usd', 'population'])
    logger.info(f"[CLEAN]   Removed {initial_rows - len(df)} rows (missing GDP/population)")
    
    # Rule 2: Remove countries with population < 10,000
    before = len(df)
    df = df[df['population'] >= 10000]
    logger.info(f"[CLEAN] Rule 2: Removed {before - len(df)} rows (population < 10K)")
    
    # Rule 3: Forward-fill missing debt values (per country)
    logger.info("[CLEAN] Rule 3: Forward-filling missing debt values")
    debt_columns = [col for col in df.columns if 'debt' in col.lower()]
    
    for col in debt_columns:
        df[col] = df.groupby('country_code')[col].fillna(method='ffill')
    
    null_debt_before = df[debt_columns].isnull().sum().sum()
    if null_debt_before > 0:
        logger.warning(f"[CLEAN]   {null_debt_before} null debt values remain (countries with no debt data)")
    
    logger.info(f"[CLEAN] Rows after cleaning: {len(df)}")
    
    return df


def derive_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive key economic metrics per Phase 1 specification.
    
    Derived Metrics:
    - gdp_per_capita = gdp_usd / population
    - debt_to_gdp = debt_total_usd / gdp_usd (if debt available)
    - population_growth = pct_change(population) by country
    - gdp_growth = pct_change(gdp_usd) by country
    - debt_growth = pct_change(debt_total_usd) by country (if debt available)
    
    Args:
        df: DataFrame with base metrics
    
    Returns:
        DataFrame with derived metrics
    """
    logger.info("[DERIVE] Deriving metrics...")
    
    # GDP per capita
    df['gdp_per_capita'] = df['gdp_usd'] / df['population']
    logger.info("[DERIVE] Computed: gdp_per_capita")
    
    # Debt-to-GDP ratio (if debt available)
    if 'debt_total_usd' in df.columns:
        df['debt_to_gdp'] = df['debt_total_usd'] / df['gdp_usd']
        
        # Flag impossible debt_to_gdp > 10 for investigation
        impossible = df[df['debt_to_gdp'] > 10]
        if len(impossible) > 0:
            logger.warning(f"[DERIVE] Found {len(impossible)} rows with debt_to_gdp > 10 (data errors)")
            for idx, row in impossible.iterrows():
                logger.warning(f"         {row['country_name']} {int(row['year'])}: {row['debt_to_gdp']:.1f}")
        
        df.loc[df['debt_to_gdp'] > 10, 'debt_to_gdp'] = np.nan
        logger.info("[DERIVE] Computed: debt_to_gdp (flagged impossible values)")
    
    # Growth rates (by country)
    df_growth = df.sort_values(['country_code', 'year']).copy()
    
    df_growth['population_growth'] = (
        df_growth.groupby('country_code')['population']
        .pct_change()
    )
    
    df_growth['gdp_growth'] = (
        df_growth.groupby('country_code')['gdp_usd']
        .pct_change()
    )
    
    if 'debt_total_usd' in df_growth.columns:
        df_growth['debt_growth'] = (
            df_growth.groupby('country_code')['debt_total_usd']
            .pct_change()
        )
        logger.info("[DERIVE] Computed: population_growth, gdp_growth, debt_growth")
    else:
        logger.info("[DERIVE] Computed: population_growth, gdp_growth")
    
    return df_growth


def save_outputs(merged_df: pd.DataFrame, cleaned_df: pd.DataFrame, final_df: pd.DataFrame, output_dir: Path) -> None:
    """
    Save three versions of processed data.
    
    Args:
        merged_df: Raw merged dataframe
        cleaned_df: After cleaning rules applied
        final_df: Final with derived metrics
        output_dir: Output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%d%b%Y").upper()
    
    files = {
        f'macro_merged_{timestamp}.csv': merged_df,
        f'macro_clean_{timestamp}.csv': cleaned_df,
        f'macro_final_{timestamp}.csv': final_df
    }
    
    logger.info("[SAVE] Saving outputs...")
    
    for filename, df in files.items():
        filepath = output_dir / filename
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        file_size_kb = filepath.stat().st_size / 1024
        logger.info(f"[SAVE] {filename}: {len(df)} rows, {file_size_kb:.1f} KB")
    
    logger.info(f"[SAVE] All outputs saved to {output_dir}")


def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("TRANSFORMING, MERGING, AND CLEANING GLOBAL ECONOMIC DATA")
    logger.info("=" * 70)
    
    try:
        # Define paths
        project_root = Path(__file__).parent.parent
        raw_dir = project_root / 'csv' / 'raw'
        processed_dir = project_root / 'csv' / 'processed'
        
        # Load raw CSVs
        gdp_df, pop_df, debt_df = load_raw_csvs(raw_dir)
        
        # Merge datasets
        merged_df = merge_datasets(gdp_df, pop_df, debt_df)
        
        # Apply cleaning rules
        cleaned_df = apply_cleaning_rules(merged_df.copy())
        
        # Derive metrics
        final_df = derive_metrics(cleaned_df.copy())
        
        # Save outputs
        save_outputs(merged_df, cleaned_df, final_df, processed_dir)
        
        logger.info("=" * 70)
        logger.info(f"✅ COMPLETE: Transformation pipeline finished successfully")
        logger.info(f"   Final dataset: {len(final_df)} rows, {final_df['country_code'].nunique()} countries")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"❌ FAILED: {str(e)}")
        logger.error("=" * 70)
        raise


if __name__ == "__main__":
    main()
