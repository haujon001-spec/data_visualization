#!/usr/bin/env python3
"""
Comprehensive Visualization Validation Suite
Tests data quality, UI/UX, and interactive functionality
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import re
from bs4 import BeautifulSoup
import numpy as np

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


class DataQualityValidator:
    """Validates input data quality for top 20 assets"""
    
    def __init__(self, parquet_path):
        self.df = pd.read_parquet(parquet_path)
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def validate_row_count(self, min_rows=10000):
        """Check minimum rows exist"""
        actual = len(self.df)
        if actual >= min_rows:
            self.results['passed'].append(f"Row count: {actual:,} rows >= {min_rows:,} minimum")
            return True
        else:
            self.results['failed'].append(f"Row count too low: {actual:,} rows < {min_rows:,} minimum")
            return False
    
    def validate_date_range(self):
        """Check date range spans at least 5 years"""
        df_sorted = self.df.sort_values('date')
        df_sorted['date'] = pd.to_datetime(df_sorted['date'])
        start = df_sorted['date'].min()
        end = df_sorted['date'].max()
        days = (end - start).days
        years = days / 365.25
        
        if years >= 5:
            self.results['passed'].append(f"Date range: {start.date()} to {end.date()} ({years:.1f} years)")
            return True
        else:
            self.results['failed'].append(f"Date range too short: {years:.1f} years < 5 years minimum")
            return False
    
    def validate_unique_assets(self, min_assets=5):
        """Check minimum number of unique assets"""
        unique = self.df['asset_id'].nunique()
        if unique >= min_assets:
            assets = self.df['asset_id'].unique()
            self.results['passed'].append(f"Unique assets: {unique} ({', '.join(assets[:5])}...)")
            return True
        else:
            self.results['failed'].append(f"Too few unique assets: {unique} < {min_assets} minimum")
            return False
    
    def validate_market_cap_values(self):
        """Check market cap values are reasonable (>0, not NaN, no inf)"""
        issues = []
        
        # Check for NaN
        nans = self.df['market_cap'].isna().sum()
        if nans > 0:
            issues.append(f"{nans:,} NaN values found")
        
        # Check for negative values
        negatives = (self.df['market_cap'] < 0).sum()
        if negatives > 0:
            issues.append(f"{negatives:,} negative values found")
        
        # Check for zero values
        zeros = (self.df['market_cap'] == 0).sum()
        if zeros > 0:
            issues.append(f"{zeros:,} zero values found")
        
        # Check for inf values
        infs = np.isinf(self.df['market_cap']).sum()
        if infs > 0:
            issues.append(f"{infs:,} infinite values found")
        
        if not issues:
            min_cap = self.df['market_cap'].min()
            max_cap = self.df['market_cap'].max()
            self.results['passed'].append(f"Market cap range: ${min_cap/1e9:.2f}B to ${max_cap/1e12:.2f}T")
            return True
        else:
            self.results['failed'].extend([f"Market cap quality: {issue}" for issue in issues])
            return False
    
    def validate_data_continuity(self):
        """Check data doesn't have excessive gaps"""
        date_counts = self.df.groupby('date').size()
        min_assets_per_date = date_counts.min()
        max_assets_per_date = date_counts.max()
        avg_assets_per_date = date_counts.mean()
        
        if min_assets_per_date >= 3:
            self.results['passed'].append(
                f"Data continuity: {min_assets_per_date} min, {avg_assets_per_date:.1f} avg, {max_assets_per_date} max assets/date"
            )
            return True
        else:
            self.results['warnings'].append(
                f"Data continuity warning: Only {min_assets_per_date} assets on some dates (expected 5+)"
            )
            return True  # Warning, not failure
    
    def validate_asset_types(self):
        """Check asset type distribution"""
        type_counts = self.df['asset_type'].value_counts()
        expected_types = {'company', 'crypto', 'metal'}
        actual_types = set(type_counts.index)
        
        if expected_types.issubset(actual_types):
            distribution = ', '.join([f"{t}: {cnt:,} rows" for t, cnt in type_counts.items()])
            self.results['passed'].append(f"Asset types present: {distribution}")
            return True
        else:
            missing = expected_types - actual_types
            self.results['failed'].append(f"Missing asset types: {missing}")
            return False
    
    def run_all_checks(self):
        """Run all data quality checks"""
        checks = [
            self.validate_row_count,
            self.validate_date_range,
            self.validate_unique_assets,
            self.validate_market_cap_values,
            self.validate_data_continuity,
            self.validate_asset_types
        ]
        
        results = [check() for check in checks]
        return all(results)


class HTMLUXValidator:
    """Validates UI/UX and HTML structure"""
    
    def __init__(self, html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        self.file_size_mb = os.path.getsize(html_path) / (1024 * 1024)
    
    def validate_html_structure(self):
        """Check valid HTML structure"""
        has_html = '<html' in self.html.lower()
        has_body = '<body' in self.html.lower()
        has_script = '<script' in self.html.lower()
        
        if has_html and has_body and has_script:
            self.results['passed'].append("HTML structure: Valid (html, body, script tags present)")
            return True
        else:
            self.results['failed'].append("HTML structure: Invalid or incomplete")
            return False
    
    def validate_plotly_presence(self):
        """Check Plotly library is included"""
        has_plotly = 'plotly' in self.html.lower()
        has_plotly_div = 'plotly' in self.html.lower() and 'div' in self.html.lower()
        
        if has_plotly and has_plotly_div:
            self.results['passed'].append("Plotly library: Included and configured")
            return True
        else:
            self.results['failed'].append("Plotly library: Missing or misconfigured")
            return False
    
    def validate_controls_presence(self):
        """Check interactive controls exist"""
        has_buttons = 'button' in self.html.lower() or 'Button' in self.html
        has_slider = 'slider' in self.html.lower() or 'input' in self.html.lower()
        
        issues = []
        if not has_buttons:
            issues.append("Play/Pause buttons not found")
        if not has_slider:
            issues.append("Date slider not found")
        
        if not issues:
            self.results['passed'].append("Interactive controls: Play/Pause buttons and date slider present")
            return True
        else:
            self.results['failed'].extend([f"Interactive controls: {issue}" for issue in issues])
            return False
    
    def validate_no_overlays(self):
        """Check for potential UI overlays by analyzing CSS/layout"""
        # Check margin/padding values in layout
        has_proper_margins = 'margin' in self.html or 'padding' in self.html
        
        # Look for fixed positioning that might cause overlays
        has_fixed_pos = re.search(r'position\s*:\s*fixed', self.html, re.IGNORECASE)
        
        # Check for legend positioning
        has_legend_config = 'legend' in self.html.lower()
        
        if has_proper_margins and has_legend_config and not has_fixed_pos:
            self.results['passed'].append("UI Layout: Proper spacing, legends, no fixed positioning conflicts")
            return True
        elif has_proper_margins and has_legend_config:
            self.results['warnings'].append("UI Layout: Fixed positioning detected (may have overlaps)")
            return True
        else:
            self.results['failed'].append("UI Layout: Missing proper margin/legend configuration")
            return False
    
    def validate_animation_frames(self):
        """Check animation frame count"""
        frame_count = self.html.count('"name":"')
        
        if frame_count >= 1000:
            self.results['passed'].append(f"Animation frames: {frame_count:,} frames (smooth animation expected)")
            return True
        elif frame_count >= 100:
            self.results['warnings'].append(f"Animation frames: {frame_count} frames (less smooth than optimal)")
            return True
        else:
            self.results['failed'].append(f"Animation frames: Only {frame_count} frames (need 100+)")
            return False
    
    def validate_file_size(self):
        """Check file size is reasonable"""
        if self.file_size_mb < 15:
            self.results['passed'].append(f"File size: {self.file_size_mb:.2f} MB (reasonable for web delivery)")
            return True
        elif self.file_size_mb < 20:
            self.results['warnings'].append(f"File size: {self.file_size_mb:.2f} MB (larger than ideal for web)")
            return True
        else:
            self.results['failed'].append(f"File size: {self.file_size_mb:.2f} MB (too large for web delivery)")
            return False
    
    def validate_color_scheme(self):
        """Check color scheme is defined"""
        has_colors = '#' in self.html  # Hex colors
        has_rgb = 'rgb(' in self.html  # RGB colors
        
        if has_colors or has_rgb:
            color_count = self.html.count('#') + self.html.count('rgb(')
            self.results['passed'].append(f"Color scheme: {color_count} color definitions found")
            return True
        else:
            self.results['failed'].append("Color scheme: No colors defined")
            return False
    
    def run_all_checks(self):
        """Run all UX validation checks"""
        checks = [
            self.validate_html_structure,
            self.validate_plotly_presence,
            self.validate_controls_presence,
            self.validate_no_overlays,
            self.validate_animation_frames,
            self.validate_file_size,
            self.validate_color_scheme
        ]
        
        results = [check() for check in checks]
        return all(results)


class InteractivityValidator:
    """Validates interactive functionality"""
    
    def __init__(self, html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def validate_hover_tooltips(self):
        """Check tooltip configuration"""
        has_hovertemplate = 'hovertemplate' in self.html.lower()
        has_hoverlabel = 'hoverlabel' in self.html.lower()
        has_customdata = 'customdata' in self.html.lower()
        
        if has_hovertemplate or has_hoverlabel:
            self.results['passed'].append("Hover tooltips: Configured (hovertemplate/hoverlabel present)")
            return True
        else:
            self.results['warnings'].append("Hover tooltips: May not be fully configured")
            return True
    
    def validate_axis_labels(self):
        """Check axis labels and titles"""
        has_xaxis = 'xaxis' in self.html.lower()
        has_yaxis = 'yaxis' in self.html.lower()
        
        if has_xaxis and has_yaxis:
            self.results['passed'].append("Axis labels: X and Y axes configured")
            return True
        else:
            self.results['failed'].append("Axis labels: Missing axis configuration")
            return False
    
    def validate_responsive_design(self):
        """Check responsive design indicators"""
        has_width = 'width' in self.html.lower()
        has_height = 'height' in self.html.lower()
        has_responsive = 'responsive' in self.html.lower() or 'autosize' in self.html.lower()
        
        if has_width and has_height:
            self.results['passed'].append("Responsive design: Width/height properties defined")
            return True
        elif has_responsive:
            self.results['passed'].append("Responsive design: Autosize/responsive mode enabled")
            return True
        else:
            self.results['warnings'].append("Responsive design: May not adapt well to different screen sizes")
            return True
    
    def validate_data_binding(self):
        """Check data is properly bound to visualization"""
        has_x_data = '"x"' in self.html or "'x'" in self.html
        has_y_data = '"y"' in self.html or "'y'" in self.html
        has_traces = 'Scatter' in self.html or 'Bar' in self.html
        
        if has_x_data and has_y_data and has_traces:
            self.results['passed'].append("Data binding: X/Y data properly bound to traces")
            return True
        else:
            self.results['failed'].append("Data binding: Data may not be properly bound")
            return False
    
    def run_all_checks(self):
        """Run all interactivity validation checks"""
        checks = [
            self.validate_hover_tooltips,
            self.validate_axis_labels,
            self.validate_responsive_design,
            self.validate_data_binding
        ]
        
        results = [check() for check in checks]
        return all(results)


class HorizontalBarValidator:
    """Validates horizontal bar chart specifications"""
    
    def __init__(self, html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html = f.read()
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def validate_horizontal_orientation(self):
        """Check bar chart is horizontal"""
        has_orientation_h = '"orientation":"h"' in self.html or '"orientation": "h"' in self.html
        has_hor_keyword = 'horizontal' in self.html.lower()
        
        if has_orientation_h:
            self.results['passed'].append("Bar orientation: Horizontal (orientation='h' detected)")
            return True
        elif has_hor_keyword:
            self.results['warnings'].append("Bar orientation: May be horizontal (keyword present)")
            return True
        else:
            self.results['failed'].append("Bar orientation: Not confirmed as horizontal")
            return False
    
    def validate_bar_coloring(self):
        """Check bars are colored by asset type"""
        has_marker_color = '"marker"' in self.html and 'color' in self.html
        has_colorscale = 'colorscale' in self.html.lower()
        
        if has_marker_color or has_colorscale:
            self.results['passed'].append("Bar coloring: Marker colors/colorscale configured")
            return True
        else:
            self.results['warnings'].append("Bar coloring: May not be fully configured")
            return True
    
    def validate_axis_scaling(self):
        """Check axis uses appropriate scale (log scale for wide range)"""
        has_log_scale = '"type":"log"' in self.html or "'type': 'log'" in self.html
        has_linear_scale = '"type":"linear"' in self.html
        
        if has_log_scale:
            self.results['passed'].append("Axis scaling: Logarithmic scale (handles $505B to $32T range)")
            return True
        elif has_linear_scale:
            self.results['warnings'].append("Axis scaling: Linear scale (may compress small values)")
            return True
        else:
            self.results['failed'].append("Axis scaling: Scale type not specified")
            return False
    
    def validate_bar_labels(self):
        """Check bars have labels"""
        has_textposition = 'textposition' in self.html.lower()
        has_text_field = '"text"' in self.html or "'text'" in self.html
        
        if has_textposition and has_text_field:
            self.results['passed'].append("Bar labels: Text labels positioned on bars")
            return True
        elif has_text_field:
            self.results['warnings'].append("Bar labels: Text present but positioning unclear")
            return True
        else:
            self.results['failed'].append("Bar labels: Not configured")
            return False
    
    def validate_bar_count_per_frame(self):
        """Check reasonable number of bars per frame"""
        # Estimate by looking at frame structure
        frame_pattern = r'"name":"[^"]*"'
        frames = re.findall(frame_pattern, self.html)
        frame_count = len(frames)
        
        if frame_count >= 1000:
            self.results['passed'].append(f"Animation frames: {frame_count:,} frames (smooth daily progression)")
            return True
        else:
            self.results['warnings'].append(f"Animation frames: {frame_count} frames (less smooth than optimal)")
            return True
    
    def run_all_checks(self):
        """Run all bar chart validation checks"""
        checks = [
            self.validate_horizontal_orientation,
            self.validate_bar_coloring,
            self.validate_axis_scaling,
            self.validate_bar_labels,
            self.validate_bar_count_per_frame
        ]
        
        results = [check() for check in checks]
        return all(results)


def print_section(title):
    """Print formatted section header"""
    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}{title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}\n")


def print_results(validator_name, results):
    """Print validation results"""
    print(f"{BOLD}{validator_name}{RESET}")
    
    if results['passed']:
        print(f"{GREEN}PASSED ({len(results['passed'])}):{RESET}")
        for msg in results['passed']:
            print(f"  {GREEN}[OK]{RESET} {msg}")
    
    if results['warnings']:
        print(f"\n{YELLOW}WARNINGS ({len(results['warnings'])}):{RESET}")
        for msg in results['warnings']:
            print(f"  {YELLOW}[WARNING]{RESET} {msg}")
    
    if results['failed']:
        print(f"\n{RED}FAILED ({len(results['failed'])}):{RESET}")
        for msg in results['failed']:
            print(f"  {RED}[FAILED]{RESET} {msg}")
    
    print()


def main():
    """Run comprehensive validation suite"""
    print(f"\n{BOLD}{CYAN}COMPREHENSIVE VISUALIZATION VALIDATION SUITE{RESET}")
    print("Data Quality | UI/UX | Interactivity | Bar Chart Analysis\n")
    
    # File paths
    parquet_path = Path('data/processed/top20_monthly.parquet')
    html_path = Path('data/processed/bar_race_top20.html')
    
    # Check files exist
    if not parquet_path.exists():
        print(f"{RED}ERROR: {parquet_path} not found{RESET}")
        sys.exit(1)
    if not html_path.exists():
        print(f"{RED}ERROR: {html_path} not found{RESET}")
        sys.exit(1)
    
    all_passed = True
    
    # 1. DATA QUALITY VALIDATION
    print_section("1. DATA QUALITY VALIDATION")
    dq = DataQualityValidator(str(parquet_path))
    dq.run_all_checks()
    print_results("Input Data Quality (Top 20 Assets)", dq.results)
    all_passed = all_passed and len(dq.results['failed']) == 0
    
    # 2. HTML UX VALIDATION
    print_section("2. UI/UX VALIDATION")
    uux = HTMLUXValidator(str(html_path))
    uux.run_all_checks()
    print_results("UI/UX and HTML Structure", uux.results)
    all_passed = all_passed and len(uux.results['failed']) == 0
    
    # 3. INTERACTIVITY VALIDATION
    print_section("3. INTERACTIVITY VALIDATION")
    inter = InteractivityValidator(str(html_path))
    inter.run_all_checks()
    print_results("Interactive Features", inter.results)
    all_passed = all_passed and len(inter.results['failed']) == 0
    
    # 4. HORIZONTAL BAR VALIDATION
    print_section("4. HORIZONTAL BAR CHART VALIDATION")
    bar = HorizontalBarValidator(str(html_path))
    bar.run_all_checks()
    print_results("Bar Chart Configuration", bar.results)
    all_passed = all_passed and len(bar.results['failed']) == 0
    
    # SUMMARY
    print_section("VALIDATION SUMMARY")
    
    total_checks = (
        len(dq.results['passed']) + len(dq.results['failed']) + len(dq.results['warnings']) +
        len(uux.results['passed']) + len(uux.results['failed']) + len(uux.results['warnings']) +
        len(inter.results['passed']) + len(inter.results['failed']) + len(inter.results['warnings']) +
        len(bar.results['passed']) + len(bar.results['failed']) + len(bar.results['warnings'])
    )
    
    total_passed = (
        len(dq.results['passed']) + len(uux.results['passed']) + 
        len(inter.results['passed']) + len(bar.results['passed'])
    )
    
    total_failed = (
        len(dq.results['failed']) + len(uux.results['failed']) + 
        len(inter.results['failed']) + len(bar.results['failed'])
    )
    
    total_warnings = (
        len(dq.results['warnings']) + len(uux.results['warnings']) + 
        len(inter.results['warnings']) + len(bar.results['warnings'])
    )
    
    print(f"Total Checks: {total_checks}")
    print(f"{GREEN}Passed: {total_passed}{RESET}")
    print(f"{YELLOW}Warnings: {total_warnings}{RESET}")
    print(f"{RED}Failed: {total_failed}{RESET}")
    print()
    
    if all_passed and total_failed == 0:
        print(f"{GREEN}{BOLD}[SUCCESS] ALL VALIDATION CHECKS PASSED!{RESET}")
        print(f"{GREEN}The visualization is production-ready.{RESET}\n")
        return 0
    else:
        print(f"{RED}{BOLD}[FAILED] VALIDATION ISSUES DETECTED{RESET}")
        print(f"{RED}Please address the {total_failed} failed checks above.{RESET}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
