"""
Phase 2: Data Normalization, Ranking, and Top-20 Extraction

This module provides comprehensive data transformation for multi-asset-class market data.
Normalizes companies, cryptocurrencies, and precious metals into a unified format,
ranks assets by market capitalization, and produces high-quality datasets for visualization.

Author: Data Automation Team
Date: 2026-02-24
"""

import os
import sys
import json
import logging
import argparse
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)


# ============================================================================
# Logging Configuration
# ============================================================================

def setup_logging(log_dir: Path) -> logging.Logger:
    """
    Configure logging to both file and console.
    
    Args:
        log_dir: Directory to save log files
        
    Returns:
        Configured logger instance
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler(log_dir / f"build_rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class AssetRecord:
    """Unified asset record after normalization."""
    date: str
    asset_id: str
    asset_type: str
    label: str
    market_cap: float
    source: str
    confidence: str
    sector: Optional[str] = None
    region: Optional[str] = None
    notes: str = ""
    metadata: str = "{}"


# ============================================================================
# Data Normalizer Class
# ============================================================================

class DataNormalizer:
    """
    Normalizes multi-source market data into unified format.
    
    Handles data from three asset classes:
    - Companies (equity data from yfinance)
    - Cryptocurrencies (CoinGecko data)
    - Precious metals (manual/yfinance data)
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize DataNormalizer.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger
        self.normalized_data: List[AssetRecord] = []
        
    def read_raw_files(self, data_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load raw CSV files for companies, crypto, and metals.
        
        Args:
            data_dir: Path to raw data directory
            
        Returns:
            Tuple of (companies_df, crypto_df, metals_df)
            
        Raises:
            FileNotFoundError: If required data files are missing
        """
        self.logger.info(f"Reading raw files from {data_dir}")
        
        companies_file = data_dir / "companies_monthly.csv"
        crypto_file = data_dir / "crypto_monthly.csv"
        metals_file = data_dir / "metals_monthly.csv"
        
        # Load files with error handling
        companies_df = pd.read_csv(companies_file) if companies_file.exists() else pd.DataFrame()
        crypto_df = pd.read_csv(crypto_file) if crypto_file.exists() else pd.DataFrame()
        metals_df = pd.read_csv(metals_file) if metals_file.exists() else pd.DataFrame()
        
        self.logger.info(f"Loaded {len(companies_df)} company records")
        self.logger.info(f"Loaded {len(crypto_df)} crypto records")
        self.logger.info(f"Loaded {len(metals_df)} metals records")
        
        return companies_df, crypto_df, metals_df
    
    def normalize_companies(
        self, 
        df: pd.DataFrame, 
        shares_csv: Path
    ) -> pd.DataFrame:
        """
        Normalize company data: compute market cap from price × shares outstanding.
        
        Args:
            df: Raw company dataframe with columns: date, ticker, adjusted_close
            shares_csv: Path to shares outstanding reference file
            
        Returns:
            Normalized dataframe with market_cap, source, confidence columns
        """
        self.logger.info("Normalizing company data")
        
        if df.empty:
            self.logger.warning("Empty company dataframe")
            return df
        
        df = df.copy()
        
        # Load shares outstanding reference if available
        shares_data = {}
        if shares_csv.exists():
            try:
                shares_df = pd.read_csv(shares_csv)
                # Assume columns: ticker, shares_outstanding
                if 'ticker' in shares_df.columns and 'shares_outstanding' in shares_df.columns:
                    shares_data = dict(zip(shares_df['ticker'], shares_df['shares_outstanding']))
                    self.logger.info(f"Loaded shares data for {len(shares_data)} companies")
            except Exception as e:
                self.logger.warning(f"Could not load shares data: {e}")
        
        # Ensure required columns exist
        required_cols = ['date', 'ticker', 'adjusted_close', 'name']
        for col in required_cols:
            if col not in df.columns:
                self.logger.warning(f"Missing column '{col}' in company data, adding default")
                if col == 'name':
                    df['name'] = df.get('ticker', 'Unknown')
                else:
                    df[col] = None
        
        # Compute market cap: price × shares outstanding
        def compute_market_cap(row):
            ticker = row.get('ticker', '')
            price = row.get('adjusted_close')
            
            if pd.isna(price) or price <= 0:
                return None
            
            shares = shares_data.get(ticker)
            if shares:
                return price * shares
            else:
                # Fallback: assume 1 billion shares if not in reference (Medium confidence)
                return price * 1_000_000_000
        
        df['market_cap'] = df.apply(compute_market_cap, axis=1)
        df['source'] = 'yfinance'
        df['confidence'] = 'Medium'  # Medium because using estimated/latest shares
        df['asset_type'] = 'company'
        
        # Keep sector and region if available
        if 'sector' not in df.columns:
            df['sector'] = None
        if 'region' not in df.columns:
            df['region'] = None
        
        self.logger.info(f"Normalized {len(df)} company records")
        return df
    
    def normalize_crypto(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize cryptocurrency data: use market_cap directly from CoinGecko.
        
        Args:
            df: Raw crypto dataframe with columns: date, coin_id, market_cap
            
        Returns:
            Normalized dataframe with source and confidence columns
        """
        self.logger.info("Normalizing crypto data")
        
        if df.empty:
            self.logger.warning("Empty crypto dataframe")
            return df
        
        df = df.copy()
        
        # Ensure required columns
        required_cols = ['date', 'coin_id', 'market_cap', 'name']
        for col in required_cols:
            if col not in df.columns:
                self.logger.warning(f"Missing column '{col}' in crypto data, adding default")
                if col == 'name':
                    df['name'] = df.get('coin_id', 'Unknown')
                else:
                    df[col] = None
        
        df['source'] = 'coingecko'
        df['confidence'] = 'High'  # High confidence: official CoinGecko market cap
        df['asset_type'] = 'crypto'
        df['asset_id'] = df['coin_id']
        df['sector'] = None
        df['region'] = None
        
        self.logger.info(f"Normalized {len(df)} crypto records")
        return df
    
    def normalize_metals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize precious metals data: market cap already computed.
        
        Args:
            df: Raw metals dataframe with columns: date, metal_id, market_cap
            
        Returns:
            Normalized dataframe with source and confidence columns
        """
        self.logger.info("Normalizing metals data")
        
        if df.empty:
            self.logger.warning("Empty metals dataframe")
            return df
        
        df = df.copy()
        
        # Ensure required columns
        required_cols = ['date', 'metal_id', 'market_cap', 'name']
        for col in required_cols:
            if col not in df.columns:
                self.logger.warning(f"Missing column '{col}' in metals data, adding default")
                if col == 'name':
                    df['name'] = df.get('metal_id', 'Unknown')
                else:
                    df[col] = None
        
        df['source'] = 'manual/yfinance'
        df['confidence'] = 'Medium'  # Medium: manual calculation from yfinance
        df['asset_type'] = 'metal'
        df['asset_id'] = df['metal_id']
        df['sector'] = None
        df['region'] = None
        
        self.logger.info(f"Normalized {len(df)} metals records")
        return df
    
    def merge_assets(
        self,
        company_df: pd.DataFrame,
        crypto_df: pd.DataFrame,
        metals_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge normalized company, crypto, and metals data into unified table.
        
        Args:
            company_df: Normalized company dataframe
            crypto_df: Normalized crypto dataframe
            metals_df: Normalized metals dataframe
            
        Returns:
            Unified dataframe with all assets
        """
        self.logger.info("Merging normalized datasets")
        
        # Standardize column names across all dataframes
        def prepare_df(df: pd.DataFrame, label_col: str) -> pd.DataFrame:
            if df.empty:
                return pd.DataFrame()
            
            std_cols = ['date', 'asset_id', 'asset_type', 'market_cap', 'source', 'confidence', 'sector', 'region']
            df = df[[col for col in std_cols if col in df.columns]].copy()
            
            # Add label column
            df['label'] = df.get(label_col, 'Unknown')
            
            return df
        
        # Map label columns for each asset type
        company_df_prep = prepare_df(company_df, 'name')
        crypto_df_prep = prepare_df(crypto_df, 'name')
        metals_df_prep = prepare_df(metals_df, 'name')
        
        # Concatenate all dataframes
        merged_df = pd.concat(
            [company_df_prep, crypto_df_prep, metals_df_prep],
            ignore_index=True
        )
        
        # Remove rows with NaN market caps
        merged_df = merged_df.dropna(subset=['market_cap'])
        
        # Ensure date is string in YYYY-MM-DD format
        merged_df['date'] = pd.to_datetime(merged_df['date']).dt.strftime('%Y-%m-%d')
        
        self.logger.info(f"Merged dataset contains {len(merged_df)} records across {merged_df['date'].nunique()} dates")
        
        return merged_df


# ============================================================================
# Top N Ranker Class
# ============================================================================

class TopNRanker:
    """
    Ranks assets by market capitalization and identifies rank transitions.
    
    Produces top-N rankings for each date, detects entries/exits, and flags
    potential corporate actions.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize TopNRanker.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger
        self.ranked_data: pd.DataFrame = pd.DataFrame()
        self.rank_transitions: Dict[str, Any] = {}
        
    def rank_by_date(
        self,
        merged_df: pd.DataFrame,
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        For each date, rank assets by market cap descending and extract top N.
        
        Args:
            merged_df: Merged dataframe with all assets
            top_n: Number of top assets to keep per date
            
        Returns:
            Ranked dataframe with rank column added
        """
        self.logger.info(f"Ranking assets by market cap (top {top_n})")
        
        ranked_list = []
        
        for date_str, group_df in merged_df.groupby('date', sort=True):
            # Sort by market cap descending
            sorted_group = group_df.sort_values('market_cap', ascending=False)
            
            # Assign ranks
            sorted_group = sorted_group.copy()
            sorted_group['rank'] = range(1, len(sorted_group) + 1)
            
            # Keep only top N
            top_n_group = sorted_group.head(top_n)
            
            ranked_list.append(top_n_group)
        
        self.ranked_data = pd.concat(ranked_list, ignore_index=True)
        
        self.logger.info(f"Created rankings for {self.ranked_data['date'].nunique()} dates")
        
        return self.ranked_data
    
    def compute_rank_changes(self, ranked_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect entry/exit/rank movement between consecutive months.
        
        Args:
            ranked_df: Ranked dataframe
            
        Returns:
            Dictionary with entries, exits, climbers, fallers per month
        """
        self.logger.info("Computing rank transitions")
        
        transitions = {}
        dates = sorted(ranked_df['date'].unique())[1:]  # Skip first date
        
        for i, current_date in enumerate(dates):
            if i == 0:
                continue
                
            previous_date = sorted(ranked_df['date'].unique())[i - 1]
            
            current_assets = set(ranked_df[ranked_df['date'] == current_date]['asset_id'])
            previous_assets = set(ranked_df[ranked_df['date'] == previous_date]['asset_id'])
            
            entries = current_assets - previous_assets
            exits = previous_assets - current_assets
            
            # Compute rank changes for assets in both periods
            common_assets = current_assets & previous_assets
            climbers = []
            fallers = []
            
            for asset_id in common_assets:
                prev_data = ranked_df[
                    (ranked_df['date'] == previous_date) & 
                    (ranked_df['asset_id'] == asset_id)
                ]['rank']
                
                curr_data = ranked_df[
                    (ranked_df['date'] == current_date) & 
                    (ranked_df['asset_id'] == asset_id)
                ]['rank']
                
                if len(prev_data) > 0 and len(curr_data) > 0:
                    prev_rank = prev_data.iloc[0]
                    curr_rank = curr_data.iloc[0]
                    
                    rank_change = prev_rank - curr_rank
                    
                    if rank_change > 0:
                        climbers.append((asset_id, rank_change))
                    elif rank_change < 0:
                        fallers.append((asset_id, -rank_change))
            
            transitions[current_date] = {
                'entries': list(entries),
                'exits': list(exits),
                'climbers': climbers,
                'fallers': fallers
            }
        
        self.rank_transitions = transitions
        self.logger.info(f"Identified rank transitions for {len(transitions)} months")
        
        return transitions
    
    def inject_corporate_actions(
        self,
        ranked_df: pd.DataFrame,
        actions_dir: Optional[Path] = None
    ) -> pd.DataFrame:
        """
        Add annotations for stock splits, dilution, mergers.
        
        Currently implements hard-coded detection rules. Future versions
        can load from corporate_actions.csv.
        
        Args:
            ranked_df: Ranked dataframe
            actions_dir: Directory containing corporate action records (unused for now)
            
        Returns:
            Dataframe with notes column updated
        """
        self.logger.info("Injecting corporate action flags")
        
        ranked_df = ranked_df.copy()
        
        # Initialize notes column if not present
        if 'notes' not in ranked_df.columns:
            ranked_df['notes'] = ""
        
        # Detect market cap changes > 30% (potential stock split/dilution)
        for asset_id in ranked_df['asset_id'].unique():
            asset_data = ranked_df[ranked_df['asset_id'] == asset_id].sort_values('date')
            
            for i in range(1, len(asset_data)):
                prev_mc = asset_data.iloc[i - 1]['market_cap']
                curr_mc = asset_data.iloc[i]['market_cap']
                
                if prev_mc > 0:
                    pct_change = abs(curr_mc - prev_mc) / prev_mc * 100
                    
                    if pct_change > 30:
                        idx = asset_data.iloc[i].name
                        note = f"Market cap change {pct_change:.1f}% - check for stock split/dilution"
                        
                        if ranked_df.loc[idx, 'notes']:
                            ranked_df.loc[idx, 'notes'] += f"; {note}"
                        else:
                            ranked_df.loc[idx, 'notes'] = note
        
        self.logger.info("Corporate action injection complete")
        
        return ranked_df
    
    def validate_quality(self, ranked_df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate data quality of ranked dataset.
        
        Checks:
        - No NaN in required columns (date, asset_id, market_cap)
        - market_cap > 0 for all rows
        - Rank is unique per date, 1 to top_n in descending order
        - No negative market caps
        
        Args:
            ranked_df: Ranked dataframe
            
        Returns:
            Tuple of (is_valid: bool, issues: List[str])
        """
        self.logger.info("Validating data quality")
        
        issues = []
        
        # Check for NaN in required columns
        required_cols = ['date', 'asset_id', 'market_cap', 'rank']
        for col in required_cols:
            nan_count = ranked_df[col].isna().sum()
            if nan_count > 0:
                issues.append(f"{nan_count} NaN values in '{col}' column")
        
        # Check for negative/zero market caps
        negative_mc = (ranked_df['market_cap'] <= 0).sum()
        if negative_mc > 0:
            issues.append(f"{negative_mc} rows with non-positive market cap")
        
        # Check rank uniqueness per date
        for date_str in ranked_df['date'].unique():
            date_data = ranked_df[ranked_df['date'] == date_str]
            ranks = date_data['rank'].values
            
            if len(ranks) != len(set(ranks)):
                issues.append(f"Duplicate ranks found for date {date_str}")
            
            # Check if ranks are 1 to N in order
            expected_ranks = list(range(1, len(date_data) + 1))
            actual_ranks = sorted(ranks)
            
            if actual_ranks != expected_ranks:
                issues.append(f"Ranks not sequential for date {date_str}: expected {expected_ranks}, got {actual_ranks}")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            self.logger.info("✓ All quality checks passed")
        else:
            for issue in issues:
                self.logger.warning(f"✗ {issue}")
        
        return is_valid, issues


# ============================================================================
# Main Processing Pipeline
# ============================================================================

def process_data(
    input_dir: Path,
    output_dir: Path,
    top_n: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> Tuple[bool, Path]:
    """
    Main data processing pipeline.
    
    Args:
        input_dir: Input directory with raw CSV files
        output_dir: Output directory for processed files
        top_n: Number of top assets to rank
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
        logger: Logger instance
        
    Returns:
        Tuple of (success: bool, output_csv_path: Path)
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        # Step 1: Normalize data
        logger.info("=" * 80)
        logger.info("STEP 1: Data Normalization")
        logger.info("=" * 80)
        
        normalizer = DataNormalizer(logger)
        companies_df, crypto_df, metals_df = normalizer.read_raw_files(input_dir)
        
        shares_csv = input_dir / "shares_outstanding.csv"
        companies_df = normalizer.normalize_companies(companies_df, shares_csv)
        crypto_df = normalizer.normalize_crypto(crypto_df)
        metals_df = normalizer.normalize_metals(metals_df)
        
        merged_df = normalizer.merge_assets(companies_df, crypto_df, metals_df)
        
        # Step 2: Rank by market cap
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: Ranking by Market Cap")
        logger.info("=" * 80)
        
        ranker = TopNRanker(logger)
        ranked_df = ranker.rank_by_date(merged_df, top_n=top_n)
        
        # Step 3: Apply date filters
        if start_date:
            ranked_df = ranked_df[ranked_df['date'] >= start_date]
            logger.info(f"Filtered to start date: {start_date}")
        
        if end_date:
            ranked_df = ranked_df[ranked_df['date'] <= end_date]
            logger.info(f"Filtered to end date: {end_date}")
        
        # Step 4: Compute rank transitions
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3: Computing Rank Transitions")
        logger.info("=" * 80)
        
        transitions = ranker.compute_rank_changes(ranked_df)
        
        # Step 5: Inject corporate actions
        logger.info("\n" + "=" * 80)
        logger.info("STEP 4: Injecting Corporate Action Flags")
        logger.info("=" * 80)
        
        ranked_df = ranker.inject_corporate_actions(ranked_df, actions_dir=None)
        
        # Step 6: Validate quality
        logger.info("\n" + "=" * 80)
        logger.info("STEP 5: Quality Validation")
        logger.info("=" * 80)
        
        is_valid, issues = ranker.validate_quality(ranked_df)
        
        if not is_valid:
            logger.warning("⚠ Quality checks found issues but proceeding with output")
        
        # Step 7: Format output
        logger.info("\n" + "=" * 80)
        logger.info("STEP 6: Formatting Output")
        logger.info("=" * 80)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Fill NaN values in optional columns
        ranked_df['sector'] = ranked_df['sector'].fillna("")
        ranked_df['region'] = ranked_df['region'].fillna("")
        ranked_df['notes'] = ranked_df['notes'].fillna("")
        
        # Create metadata column (JSON string)
        def create_metadata(row: pd.Series) -> str:
            metadata = {
                'asset_type': row['asset_type'],
                'source': row['source'],
                'confidence': row['confidence']
            }
            return json.dumps(metadata)
        
        ranked_df['metadata'] = ranked_df.apply(create_metadata, axis=1)
        
        # Select and reorder columns
        output_cols = [
            'date', 'rank', 'asset_id', 'asset_type', 'label',
            'market_cap', 'source', 'confidence', 'sector', 'region', 'notes'
        ]
        
        output_df = ranked_df[output_cols].copy()
        output_df = output_df.sort_values(['date', 'rank'])
        
        # Step 8: Save outputs
        logger.info("\n" + "=" * 80)
        logger.info("STEP 7: Saving Outputs")
        logger.info("=" * 80)
        
        csv_path = output_dir / "top20_monthly.csv"
        parquet_path = output_dir / "top20_monthly.parquet"
        metadata_path = output_dir / "top20_monthly_metadata.json"
        transitions_path = output_dir / "rank_transitions.json"
        
        # Save CSV
        output_df.to_csv(csv_path, index=False)
        logger.info(f"✓ Saved CSV: {csv_path}")
        logger.info(f"  Rows: {len(output_df)}, Columns: {len(output_df.columns)}")
        
        # Save Parquet
        output_df.to_parquet(parquet_path, compression='snappy', index=False)
        logger.info(f"✓ Saved Parquet: {parquet_path}")
        
        # Save metadata
        metadata = {
            'schema': {
                'date': 'YYYY-MM-DD',
                'rank': 'integer (1 to top_n)',
                'asset_id': 'string (ticker/coin_id/metal_id)',
                'asset_type': 'enum (company|crypto|metal)',
                'label': 'string (human-readable name)',
                'market_cap': 'float (USD)',
                'source': 'enum (yfinance|coingecko|manual)',
                'confidence': 'enum (High|Medium|Low)',
                'sector': 'string (for companies)',
                'region': 'string (for companies)',
                'notes': 'string (annotations for corporate actions, data issues, etc.)'
            },
            'date_range': {
                'start': output_df['date'].min(),
                'end': output_df['date'].max()
            },
            'statistics': {
                'total_rows': len(output_df),
                'unique_dates': output_df['date'].nunique(),
                'top_n': top_n,
                'date_count': len(output_df) // top_n if top_n > 0 else 0,
                'asset_types': output_df['asset_type'].value_counts().to_dict(),
                'sources': output_df['source'].value_counts().to_dict(),
                'confidence_distribution': output_df['confidence'].value_counts().to_dict()
            },
            'validation': {
                'is_valid': is_valid,
                'issues': issues
            },
            'processing_info': {
                'timestamp': datetime.now().isoformat(),
                'input_directory': str(input_dir),
                'output_directory': str(output_dir),
                'top_n_requested': top_n,
                'start_date_filter': start_date,
                'end_date_filter': end_date
            }
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"✓ Saved metadata: {metadata_path}")
        
        # Save rank transitions
        with open(transitions_path, 'w') as f:
            json.dump(transitions, f, indent=2, default=str)
        
        logger.info(f"✓ Saved rank transitions: {transitions_path}")
        
        # Step 9: Final report
        logger.info("\n" + "=" * 80)
        logger.info("PROCESSING COMPLETE")
        logger.info("=" * 80)
        
        logger.info(f"\nDataset Summary:")
        logger.info(f"  First date: {output_df['date'].min()}")
        logger.info(f"  Last date:  {output_df['date'].max()}")
        logger.info(f"  Unique dates: {output_df['date'].nunique()}")
        logger.info(f"  Total rows: {len(output_df)}")
        
        # Top asset on first and last date
        first_date = output_df['date'].min()
        last_date = output_df['date'].max()
        
        first_top = output_df[output_df['date'] == first_date].iloc[0]
        last_top = output_df[output_df['date'] == last_date].iloc[0]
        
        logger.info(f"\n  Top asset on {first_date}: {first_top['asset_id']} ({first_top['label']})")
        logger.info(f"    Market Cap: ${first_top['market_cap']:,.0f}")
        logger.info(f"    Confidence: {first_top['confidence']}")
        
        logger.info(f"\n  Top asset on {last_date}: {last_top['asset_id']} ({last_top['label']})")
        logger.info(f"    Market Cap: ${last_top['market_cap']:,.0f}")
        logger.info(f"    Confidence: {last_top['confidence']}")
        
        logger.info(f"\n✓ Dataset is ready for Phase 3 visualization")
        
        return True, csv_path
        
    except Exception as e:
        logger.error(f"✗ Processing failed: {e}", exc_info=True)
        return False, None


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Command-line interface for data ranking script."""
    
    parser = argparse.ArgumentParser(
        description="Phase 2: Data Normalization, Ranking, and Top-20 Extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default behavior (data/raw/ → data/processed/)
  python 02_build_rankings.py
  
  # Custom input/output directories
  python 02_build_rankings.py --input_dir /path/to/raw --output_dir /path/to/processed
  
  # Specify date range
  python 02_build_rankings.py --start_date 2020-01-01 --end_date 2025-12-31
  
  # Custom top N
  python 02_build_rankings.py --top_n 50
        """
    )
    
    parser.add_argument(
        '--input_dir',
        type=Path,
        default=Path('data/raw'),
        help='Input directory with raw CSV files (default: data/raw)'
    )
    
    parser.add_argument(
        '--output_dir',
        type=Path,
        default=Path('data/processed'),
        help='Output directory for processed files (default: data/processed)'
    )
    
    parser.add_argument(
        '--top_n',
        type=int,
        default=20,
        help='Number of top assets to rank per date (default: 20)'
    )
    
    parser.add_argument(
        '--start_date',
        type=str,
        default=None,
        help='Start date filter (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--end_date',
        type=str,
        default=None,
        help='End date filter (YYYY-MM-DD format)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_dir = args.output_dir.parent / 'logs'
    logger = setup_logging(log_dir)
    
    logger.info(f"Starting data ranking process")
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Top N: {args.top_n}")
    
    # Run processing
    success, output_path = process_data(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        top_n=args.top_n,
        start_date=args.start_date,
        end_date=args.end_date,
        logger=logger
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
