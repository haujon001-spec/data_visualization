# -*- coding: utf-8 -*-
"""
Transform and Rank Top 50 Countries

Filter top 50 countries by population for each year, add ranking column.
"""

import pandas as pd
from pathlib import Path


def load_raw_csv(input_path: Path) -> pd.DataFrame:
    """
    Load raw CSV data from World Bank API fetch.
    
    Args:
        input_path: Path to raw CSV file
    
    Returns:
        DataFrame with raw population data
    """
    df = pd.read_csv(input_path)
    print(f"[LOAD] Loaded {len(df)} records from {input_path.name}")
    return df


def filter_top50_per_year(df: pd.DataFrame, top_n: int = 50, exclude_csv: Path = None) -> pd.DataFrame:
    """
    Filter top N countries by population for each year.
    
    Args:
        df: Raw population DataFrame
        top_n: Number of top countries to keep
        exclude_csv: Path to CSV with aggregate regions to exclude
    
    Returns:
        Filtered DataFrame with only top N countries per year
    """
    # Load exclusion list
    exclude_codes = []
    if exclude_csv and exclude_csv.exists():
        exclude_df = pd.read_csv(exclude_csv)
        # Use 'code' column from config CSV
        exclude_codes = exclude_df["code"].tolist()
        print(f"[FILTER] Excluding {len(exclude_codes)} aggregate regions")
    
    # Filter out aggregates and rows with missing country codes
    df_filtered = df[
        ~df["country_code"].isin(exclude_codes) & 
        df["country_code"].notna()
    ].copy()
    
    # Get top N per year
    top_df = (
        df_filtered
        .sort_values(["year", "population"], ascending=[True, False])
        .groupby("year")
        .head(top_n)
        .reset_index(drop=True)
    )
    
    print(f"[FILTER] Top {top_n} countries per year: {len(top_df)} records")
    return top_df


def add_ranking_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add rank column based on population per year.
    
    Args:
        df: DataFrame with population data
    
    Returns:
        DataFrame with added rank column
    """
    df["rank"] = (
        df.groupby("year")["population"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )
    print(f"[RANK] Added ranking column")
    return df


def save_processed_csv(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save processed DataFrame to CSV.
    
    Args:
        df: Processed DataFrame
        output_path: Path to output CSV file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SAVE] Processed data saved to {output_path}")
    print(f"[SAVE] File size: {output_path.stat().st_size} bytes")


if __name__ == "__main__":
    input_file = Path("csv/raw/worldbank_population_raw_5Mar2026.csv")
    output_file = Path("csv/processed/population_top50_1970_now_5Mar2026.csv")
    exclude_file = Path("config/aggregate_regions_exclude.csv")
    top_n = 50
    
    print("=" * 70)
    print("TRANSFORMING AND RANKING POPULATION DATA")
    print("=" * 70)
    
    df = load_raw_csv(input_file)
    df = filter_top50_per_year(df, top_n, exclude_file)
    df = add_ranking_column(df)
    save_processed_csv(df, output_file)
    
    print("=" * 70)
    print(f"COMPLETE: {len(df)} records saved")
    print("=" * 70)
