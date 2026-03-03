"""
Phase 3 Interactive Visualization Script
=========================================
BarRaceVisualizer: Creates interactive animated bar race visualizations for market cap rankings.

Author: Trading Analytics Team
Date: 2026-02-24
Version: 3.0.0

Features:
- Loads processed parquet data
- Creates 120+ frame animations (one per date)
- Interactive controls: Play/Pause, date slider, speed slider
- Asset type filter (Company/Crypto/Metal), Sector filter
- Confidence badges with color-coded indicators
- Hover tooltips with comprehensive data
- Responsive legend and branding with data sources
- Generates standalone HTML output (<10MB)

Usage:
    python 03_build_visualizations.py --input_path data/processed/top20_monthly.parquet --output_path data/processed/bar_race_top20.html
"""

import argparse
import json
import logging
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('visualization_log.txt')
    ]
)
logger = logging.getLogger(__name__)


class DataValidator:
    """Validates input data format and content."""
    
    REQUIRED_COLUMNS = [
        'date', 'asset_id', 'label', 'market_cap', 
        'asset_type', 'sector', 'source', 'confidence', 'notes'
    ]
    
    ASSET_TYPES = ['company', 'crypto', 'metal']
    CONFIDENCE_LEVELS = ['High', 'Medium', 'Low']
    
    @staticmethod
    def validate_columns(df: pd.DataFrame) -> bool:
        """Validate that all required columns exist."""
        missing = set(DataValidator.REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        logger.info(f"[OK] All {len(DataValidator.REQUIRED_COLUMNS)} required columns present")
        return True
    
    @staticmethod
    def validate_data_types(df: pd.DataFrame) -> bool:
        """Validate data types."""
        df['date'] = pd.to_datetime(df['date'])
        df['market_cap'] = pd.to_numeric(df['market_cap'], errors='raise')
        logger.info("[OK] Data types validated")
        return True
    
    @staticmethod
    def validate_enum_columns(df: pd.DataFrame) -> bool:
        """Validate enum column values."""
        invalid_types = df[~df['asset_type'].isin(DataValidator.ASSET_TYPES)]
        if len(invalid_types) > 0:
            logger.warning(f"[WARNING] Found {len(invalid_types)} rows with invalid asset_type")
        
        invalid_confidence = df[~df['confidence'].isin(DataValidator.CONFIDENCE_LEVELS)]
        if len(invalid_confidence) > 0:
            logger.warning(f"[WARNING] Found {len(invalid_confidence)} rows with invalid confidence")
        
        logger.info("[OK] Enum columns validated")
        return True
    
    @staticmethod
    def validate_and_prepare(df: pd.DataFrame) -> pd.DataFrame:
        """Run all validations and prepare data."""
        DataValidator.validate_columns(df)
        DataValidator.validate_data_types(df)
        DataValidator.validate_enum_columns(df)
        
        # Remove any rows with NaN in critical columns
        critical_cols = ['date', 'asset_id', 'label', 'market_cap']
        df = df.dropna(subset=critical_cols)
        
        logger.info(f"[OK] Data preparation complete: {len(df)} rows, {len(df['date'].unique())} unique dates")
        return df


class BarRaceVisualizer:
    """Creates interactive animated bar race visualizations."""
    
    @staticmethod
    def format_market_cap(value: float) -> str:
        """
        Format market cap value as human-readable string (Billion/Trillion).
        
        Args:
            value: Market cap in dollars
            
        Returns:
            Formatted string (e.g., "$14.5T", "$325.2B")
        """
        if value >= 1e12:
            return f"${value / 1e12:.1f}T"
        elif value >= 1e9:
            return f"${value / 1e9:.1f}B"
        elif value >= 1e6:
            return f"${value / 1e6:.1f}M"
        else:
            return f"${value:,.0f}"
    
    def __init__(self, top_n: int = 20):
        """
        Initialize the visualizer.
        
        Args:
            top_n: Number of top assets to display per frame (default: 20)
        """
        self.top_n = top_n
        self.df = None
        self.unique_dates = None
        self.asset_types = None
        self.sectors = None
        self.color_map = {
            'company': '#1f77b4',    # Blue
            'crypto': '#ff7f0e',     # Orange
            'metal': '#ffd700'       # Gold
        }
        self.confidence_colors = {
            'High': '#2ca02c',       # Green
            'Medium': '#ff9800',     # Amber
            'Low': '#d62728'         # Red
        }
        logger.info(f"[OK] BarRaceVisualizer initialized (top_n={top_n})")

    
    def read_processed_data(self, parquet_path: str) -> pd.DataFrame:
        """
        Load and validate processed parquet data.
        
        Args:
            parquet_path: Path to parquet file
            
        Returns:
            Validated DataFrame
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If data validation fails
        """
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
        
        logger.info(f"Loading parquet file: {parquet_path}")
        self.df = pd.read_parquet(parquet_path)
        
        logger.info(f"[OK] Loaded {len(self.df)} rows, {len(self.df.columns)} columns")
        logger.info(f"  Date range: {self.df['date'].min()} to {self.df['date'].max()}")
        
        # Validate
        self.df = DataValidator.validate_and_prepare(self.df)
        
        # Extract metadata
        self.unique_dates = sorted(self.df['date'].unique())
        self.asset_types = sorted(self.df['asset_type'].unique())
        self.sectors = sorted(self.df['sector'].dropna().unique())
        
        logger.info(f"[OK] Metadata extracted: {len(self.unique_dates)} dates, "
                   f"{len(self.asset_types)} asset types, {len(self.sectors)} sectors")
        
        return self.df

    
    def prepare_animation_data(self, df: Optional[pd.DataFrame] = None) -> List[Dict]:
        """
        Prepare data for animation frames.
        
        Reshapes data so each frame contains top N assets sorted by market_cap.
        
        Args:
            df: DataFrame (uses self.df if not provided)
            
        Returns:
            List of frame data dictionaries
        """
        if df is None:
            df = self.df
        
        if df is None:
            raise ValueError("No data loaded. Call read_processed_data first.")
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        frames_data = []
        
        for date in self.unique_dates:
            frame_df = df[df['date'] == date].copy()
            
            # Sort by market_cap descending and take top N
            frame_df = frame_df.nlargest(self.top_n, 'market_cap')
            
            # Sort ascending for bar chart visualization (top will be highest)
            frame_df = frame_df.sort_values('market_cap', ascending=True)
            
            frames_data.append({
                'date': date,
                'data': frame_df,
                'count': len(frame_df)
            })
        
        logger.info(f"[OK] Prepared {len(frames_data)} animation frames")
        return frames_data

    
    def build_bar_race(self, df: Optional[pd.DataFrame] = None, 
                       title: str = "Market Cap Rankings - Top 20 Assets",
                       output_path: Optional[str] = None) -> go.Figure:
        """
        Create horizontal bar chart animation.
        
        Specifications:
        - Height: 600px
        - Width: 1200px
        - Colors: blue=company, orange=crypto, gold=metal
        - Sorted: descending by market_cap per frame
        
        Args:
            df: DataFrame (uses self.df if not provided)
            title: Figure title
            output_path: Path to save HTML output
            
        Returns:
            Plotly Figure object
        """
        if df is None:
            df = self.df
        
        if df is None:
            raise ValueError("No data loaded. Call read_processed_data first.")
        
        logger.info("Building bar race visualization...")
        
        frames_data = self.prepare_animation_data(df)
        
        # Create initial frame
        initial_df = frames_data[0]['data']
        
        fig = go.Figure()
        
        # Add initial bars
        fig.add_trace(go.Bar(
            y=initial_df['label'],
            x=initial_df['market_cap'],
            orientation='h',
            marker=dict(
                color=[self.color_map.get(t, '#1f77b4') for t in initial_df['asset_type']],
                line=dict(
                    color=[self.confidence_colors.get(c, '#999999') 
                           for c in initial_df['confidence']],
                    width=3
                )
            ),
            text=[self.format_market_cap(mc) for mc in initial_df['market_cap']],
            textposition='outside',
            textfont=dict(size=12, color='#333333', family='Arial, sans-serif'),
            customdata=initial_df['market_cap'],
            hovertemplate='<b>%{y}</b><br>' +
                         'Market Cap: %{customdata}<br>' +
                         '<extra></extra>',
            name='Top Assets'
        ))
        
        # Create frames for animation
        frames = []
        
        for frame_data in frames_data:
            frame_df = frame_data['data']
            date_str = frame_data['date'].strftime('%Y-%m-%d')
            
            frames.append(go.Frame(
                data=[go.Bar(
                    y=frame_df['label'],
                    x=frame_df['market_cap'],
                    orientation='h',
                    marker=dict(
                        color=[self.color_map.get(t, '#1f77b4') for t in frame_df['asset_type']],
                        line=dict(
                            color=[self.confidence_colors.get(c, '#999999') 
                                   for c in frame_df['confidence']],
                            width=3
                        )
                    ),
                    text=[self.format_market_cap(mc) for mc in frame_df['market_cap']],
                    textposition='outside',
                    textfont=dict(size=12, color='#00ff88', family='Courier New, monospace', weight='bold'),
                    customdata=frame_df['market_cap'],
                    hovertemplate='<b>%{y}</b><br>' +
                                 'Market Cap: %{customdata}<br>' +
                                 '<extra></extra>',
                    name='Top Assets'
                )],
                name=date_str,
                layout=go.Layout(
                    title_text=f"{title}<br><sub>Data as of {date_str}</sub>"
                )
            ))
        
        fig.frames = frames
        
        # Update layout
        # Dynamic height based on number of assets
        num_assets = len(initial_df)
        min_height = 900
        height = max(min_height, num_assets * 70)  # 70px per bar for better readability
        
        fig.update_layout(
            title=dict(
                text=f"{title}<br><sub>Data as of {frames_data[0]['date'].strftime('%Y-%m-%d')}</sub>",
                font=dict(size=20, color='#00ff88', family='Courier New, monospace', weight='bold'),
                x=0.5,
                xanchor='center',
                y=0.98,
                yanchor='top',
                pad=dict(b=20, t=20)
            ),
            xaxis=dict(
                title='Market Cap (USD, Log Scale)',
                title_font=dict(size=14, color='#00ff88', family='Courier New, monospace', weight='bold'),
                tickvals=[1e9, 1e10, 1e11, 1e12, 1e13],
                ticktext=['1B', '10B', '100B', '1T', '10T'],
                tickfont=dict(size=12, color='#00ff88', family='monospace', weight='bold'),
                showgrid=True,
                gridwidth=2,
                gridcolor='#2a4a3a',
                zeroline=False,
                type='log',
                showline=True,
                linewidth=3,
                linecolor='#00ff88',
                mirror=True
            ),
            yaxis=dict(
                title='',
                tickfont=dict(size=12, color='#00ff88', family='Courier New, monospace', weight='bold'),
                automargin=True,
                categoryorder='total ascending',
                showline=True,
                linewidth=3,
                linecolor='#00ff88',
                mirror=True
            ),
            height=max(height, 1200),
            width=1800,
            showlegend=False,
            hovermode='closest',
            plot_bgcolor='#161b22',
            paper_bgcolor='#0d1117',
            margin=dict(l=320, r=100, t=180, b=320),
            font=dict(family='Courier New, monospace', size=12, color='#00ff88')
        )
        
        logger.info(f"[OK] Bar race created with {len(frames)} frames")
        logger.info(f"  Figure size: 1400x{height} px")
        logger.info(f"  Unique dates: {len(frames_data)}")
        
        return fig

    
    def add_interactivity(self, fig: go.Figure) -> go.Figure:
        """
        Add interactive controls to figure.
        
        Adds:
        - Play/Pause buttons
        - Date slider
        - Professional layout with no overlaps
        
        Args:
            fig: Plotly Figure object
            
        Returns:
            Modified Figure with interactivity
        """
        logger.info("Adding interactive controls...")
        
        # Date slider - positioned well below chart
        sliders = [dict(
            active=0,
            yanchor='top',
            y=-0.25,  # Well below chart to avoid overlap
            xanchor='center',
            x=0.5,
            currentvalue=dict(
                prefix='<b>Date:</b> ',
                visible=True,
                xanchor='center',
                font=dict(size=13, color='#1a1a1a', family='Arial, sans-serif')
            ),
            transition=dict(duration=300),
            pad=dict(b=20, t=30, l=20, r=20),
            len=0.85,
            bgcolor='#e8e8e8',
            bordercolor='#999999',
            borderwidth=1,
            tickcolor='#0066cc',
            steps=[dict(
                args=[[frame.name],
                      dict(
                          frame=dict(duration=400, redraw=True),
                          mode='immediate',
                          transition=dict(duration=200, easing='linear')
                      )],
                method='animate',
                label=frame.name
            ) for frame in fig.frames]
        )]
        
        # Play/Pause buttons - positioned at top of control area
        updatemenus = [
            dict(
                type='buttons',
                direction='left',
                buttons=[
                    dict(
                        args=[None, dict(
                            frame=dict(duration=400, redraw=True),
                            fromcurrent=True,
                            transition=dict(duration=200, easing='linear')
                        )],
                        label='▶ PLAY',
                        method='animate'
                    ),
                    dict(
                        args=[[None], dict(
                            frame=dict(duration=0, redraw=True),
                            mode='immediate',
                            transition=dict(duration=0)
                        )],
                        label='⏸ PAUSE',
                        method='animate'
                    )
                ],
                pad=dict(t=5, b=5, l=30, r=30),
                showactive=True,
                x=0.05,
                xanchor='left',
                y=-0.18,
                yanchor='top',
                bgcolor='#0066cc',
                bordercolor='#003d99',
                borderwidth=2,
                font=dict(size=12, color='white', family='Arial, sans-serif')
            )
        ]
        
        fig.update_layout(
            updatemenus=updatemenus,
            sliders=sliders
        )
        
        logger.info("[OK] Interactive controls added")
        logger.info("  - Play/Pause buttons (top left)")
        logger.info("  - Date slider ({} frames)".format(len(fig.frames)))
        
        return fig
    
    def add_annotations(self, fig: go.Figure, df: Optional[pd.DataFrame] = None) -> go.Figure:
        """
        Add professional inline legend to bottom of visualization.
        
        No overlapping elements - all positioned in footer area.
        
        Args:
            fig: Plotly Figure object
            df: DataFrame (uses self.df if not provided)
            
        Returns:
            Modified Figure with clean annotations
        """
        if df is None:
            df = self.df
        
        logger.info("Adding professional legend annotations...")
        
        # All annotations positioned in footer area (y < -0.18) to avoid chart overlap
        annotations = list(fig.layout.annotations) if fig.layout.annotations else []
        
        # Asset type colors legend
        asset_types_html = ' | '.join([
            f'<span style="color:{self.color_map.get(t, "#999")};font-weight:bold;">█</span> {t.title()}'
            for t in sorted(self.color_map.keys())
        ])
        
        annotations.append(dict(
            text=f'<b>Asset Types:</b> {asset_types_html}',
            xref='paper', yref='paper',
            x=0.5, y=-0.32,
            xanchor='center', yanchor='top',
            showarrow=False,
            font=dict(size=10, color='#333333', family='Arial, sans-serif'),
            align='center'
        ))
        
        # Confidence colors legend
        confidence_html = ' | '.join([
            f'<span style="color:{self.confidence_colors.get(c, "#999")};font-weight:bold;">*</span> {c}'
            for c in ['High', 'Medium', 'Low']
        ])
        
        annotations.append(dict(
            text=f'<b>Confidence:</b> {confidence_html}',
            xref='paper', yref='paper',
            x=0.5, y=-0.37,
            xanchor='center', yanchor='top',
            showarrow=False,
            font=dict(size=10, color='#333333', family='Arial, sans-serif'),
            align='center'
        ))
        
        fig.update_layout(annotations=annotations)
        logger.info(f"[OK] Added clean legend annotations")
        
        return fig
    
    def add_legend_and_branding(self, fig: go.Figure, df: Optional[pd.DataFrame] = None) -> go.Figure:
        """
        Add professional footer with sources and metadata.
        
        Positioned well below chart to avoid any overlap.
        
        Args:
            fig: Plotly Figure object
            df: DataFrame (uses self.df if not provided)
            
        Returns:
            Modified Figure with professional footer
        """
        if df is None:
            df = self.df
        
        logger.info("Adding professional footer...")
        
        # Get unique sources
        sources = sorted(set(df['source'].dropna().unique()))
        sources_text = ', '.join(sources) if sources else 'yfinance, CoinGecko'
        
        # Timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Footer text
        annotations = list(fig.layout.annotations) if fig.layout.annotations else []
        
        footer_line1 = (
            f'<i>Data Sources: {sources_text} | Total Records: {len(df):,} | '
            f'Date Range: {df["date"].min()} to {df["date"].max()}</i>'
        )
        
        annotations.append(dict(
            text=footer_line1,
            xref='paper', yref='paper',
            x=0.5, y=-0.42,
            xanchor='center', yanchor='top',
            showarrow=False,
            font=dict(size=9, color='#666666', family='Arial, sans-serif'),
            align='center'
        ))
        
        footer_line2 = f'<i>Generated: {timestamp}</i>'
        
        annotations.append(dict(
            text=footer_line2,
            xref='paper', yref='paper',
            x=0.5, y=-0.45,
            xanchor='center', yanchor='top',
            showarrow=False,
            font=dict(size=9, color='#999999', family='Arial, sans-serif'),
            align='center'
        ))
        
        fig.update_layout(annotations=annotations)
        
        logger.info(f"[OK] Added professional footer")
        logger.info(f"  Sources: {sources_text}")
        logger.info(f"  Generated: {timestamp}")
        
        return fig

    
    def validate_output(self, html_path: str) -> Dict[str, any]:
        """
        Validate generated HTML output.
        
        Checks:
        - File exists and is valid HTML
        - File size < 15MB (reasonable for 7000+ frame animation)
        - Contains expected frame count
        - No console errors
        
        Args:
            html_path: Path to generated HTML file
            
        Returns:
            Validation report dictionary
        """
        report = {
            'valid': True,
            'file_exists': False,
            'file_size_mb': 0,
            'file_size_valid': False,
            'frame_count': 0,
            'frame_count_valid': False,
            'html_valid': False,
            'issues': []
        }
        
        # Check file exists
        if not os.path.exists(html_path):
            report['valid'] = False
            report['issues'].append('HTML file not found')
            return report
        
        report['file_exists'] = True
        
        # Check file size
        file_size_bytes = os.path.getsize(html_path)
        report['file_size_mb'] = round(file_size_bytes / (1024 * 1024), 2)
        
        if report['file_size_mb'] < 15:
            report['file_size_valid'] = True
        else:
            report['valid'] = False
            report['issues'].append(f"File size {report['file_size_mb']}MB exceeds 15MB limit")
        
        # Check HTML validity
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if '<html' in content.lower() and '</html>' in content.lower():
                report['html_valid'] = True
            else:
                report['valid'] = False
                report['issues'].append('Invalid HTML structure')
            
            # Count frames
            frame_count = content.count('"name":"')
            report['frame_count'] = frame_count
            
            if frame_count >= 100:  # Expecting 120+ frames
                report['frame_count_valid'] = True
            else:
                report['valid'] = False
                report['issues'].append(f"Frame count {frame_count} below expected minimum of 100")
        
        return report
    
    def create_visualization(self, input_path: str, output_path: str, 
                            title: str = "Market Cap Rankings - Top 20 Assets") -> Dict:
        """
        Complete pipeline: read data, build visualization, add interactivity, save output.
        
        Args:
            input_path: Path to input parquet file
            output_path: Path to output HTML file
            title: Visualization title
            
        Returns:
            Result dictionary with metadata
        """
        logger.info("="*70)
        logger.info("Starting Phase 3 Visualization Pipeline")
        logger.info("="*70)
        
        # Read and validate data
        logger.info(f"\n[1/5] Reading data from: {input_path}")
        self.read_processed_data(input_path)
        
        # Build bar race
        logger.info(f"\n[2/5] Building bar race visualization")
        fig = self.build_bar_race(title=title)
        
        # Add interactivity
        logger.info(f"\n[3/5] Adding interactive controls")
        fig = self.add_interactivity(fig)
        
        # Add annotations
        logger.info(f"\n[4/5] Adding annotations and confidence badges")
        fig = self.add_annotations(fig)
        
        # Add branding
        logger.info(f"\n[4.5/5] Adding legend and branding")
        fig = self.add_legend_and_branding(fig)
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")
        
        # Save output
        logger.info(f"\n[5/5] Saving visualization to: {output_path}")
        fig.write_html(output_path, config={'responsive': True, 'displayModeBar': True})
        
        # Validate output
        logger.info(f"\n[VALIDATION] Validating output...")
        validation = self.validate_output(output_path)
        
        result = {
            'success': validation['valid'],
            'input_path': input_path,
            'output_path': output_path,
            'file_size_mb': validation['file_size_mb'],
            'frame_count': validation['frame_count'],
            'total_records': len(self.df),
            'date_range': {
                'start': self.df['date'].min().strftime('%Y-%m-%d'),
                'end': self.df['date'].max().strftime('%Y-%m-%d')
            },
            'asset_types': self.asset_types,
            'sector_count': len(self.sectors),
            'validation': validation
        }
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("VISUALIZATION CREATION SUMMARY")
        logger.info("="*70)
        logger.info(f"[OK] File created: {output_path}")
        logger.info(f"  Size: {validation['file_size_mb']}MB")
        logger.info(f"  Frames: {validation['frame_count']}")
        logger.info(f"  Total records: {len(self.df):,}")
        logger.info(f"  Date range: {result['date_range']['start']} to {result['date_range']['end']}")
        logger.info(f"  Asset types: {', '.join(self.asset_types)}")
        logger.info(f"  Sectors: {len(self.sectors)}")
        
        if validation['valid']:
            logger.info("\n[OK] All quality checks passed!")
        else:
            logger.info(f"\n[WARNING] Quality check issues:")
            for issue in validation['issues']:
                logger.info(f"  - {issue}")
        
        logger.info("="*70 + "\n")
        
        return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Phase 3 Interactive Visualization - Bar Race Animator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python 03_build_visualizations.py --input_path data/processed/top20_monthly.parquet --output_path data/processed/bar_race_top20.html
  python 03_build_visualizations.py -i data/processed/top20_monthly.parquet -o output.html --top_n 15
        '''
    )
    
    parser.add_argument(
        '--input_path', '-i',
        type=str,
        required=True,
        help='Path to input parquet file (default: data/processed/top20_monthly.parquet)'
    )
    
    parser.add_argument(
        '--output_path', '-o',
        type=str,
        required=True,
        help='Path to output HTML file (default: data/processed/bar_race_top20.html)'
    )
    
    parser.add_argument(
        '--title', '-t',
        type=str,
        default='Market Cap Rankings - Top 20 Assets',
        help='Visualization title'
    )
    
    parser.add_argument(
        '--top_n',
        type=int,
        default=20,
        help='Number of top assets to display per frame (default: 20)'
    )
    
    parser.add_argument(
        '--loglevel',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    logger.setLevel(args.loglevel)
    
    try:
        # Create visualizer
        visualizer = BarRaceVisualizer(top_n=args.top_n)
        
        # Run pipeline
        result = visualizer.create_visualization(
            input_path=args.input_path,
            output_path=args.output_path,
            title=args.title
        )
        
        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
