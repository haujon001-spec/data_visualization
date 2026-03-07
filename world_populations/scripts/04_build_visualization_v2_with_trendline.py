# -*- coding: utf-8 -*-
"""
World Population Dashboard - Version 2
======================================
Interactive population trends dashboard with trendlines and growth analysis.

Features:
- Line chart showing population trends over 1960-2024
- Polynomial trendline overlay for each country
- Growth rate calculations and trend indicators
- Interactive country selection and filtering
- Responsive design with dark theme
- Growth acceleration/deceleration analysis

Author: Analytics Team
Date: 2026-03-07
Version: 2.0.0
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import numpy as np
from datetime import datetime
from scipy import stats
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class PopulationTrendAnalyzer:
    """Analyzes population trends and calculates growth metrics."""
    
    @staticmethod
    def load_data(input_path: Path) -> pd.DataFrame:
        """Load processed population data."""
        df = pd.read_csv(input_path, encoding='utf-8')
        df['year'] = pd.to_numeric(df['year'])
        df['population'] = pd.to_numeric(df['population'])
        logger.info(f"[LOAD] Loaded {len(df)} records, {df['country_name'].nunique()} countries, {df['year'].max()-df['year'].min()+1} years")
        return df
    
    @staticmethod
    def analyze_all_trends(df: pd.DataFrame) -> pd.DataFrame:
        """Apply trend analysis to all countries."""
        logger.info("[ANALYZE] Fitting trendlines for all countries...")
        
        # Process each country separately
        processed_dfs = []
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            df_country = df_country.sort_values('year').reset_index(drop=True)
            
            # Fit trendline
            if len(df_country) >= 3:
                try:
                    coeffs = np.polyfit(df_country['year'], df_country['population'], 2)
                    poly = np.poly1d(coeffs)
                    df_country['trendline'] = poly(df_country['year'])
                except:
                    df_country['trendline'] = np.nan
            else:
                df_country['trendline'] = np.nan
            
            # Calculate growth rate
            df_country['growth_rate'] = df_country['population'].pct_change() * 100
            
            processed_dfs.append(df_country)
        
        df = pd.concat(processed_dfs, ignore_index=True)
        return df


class PopulationDashboardV2:
    """Creates interactive population dashboard with trendlines."""
    
    # Define color palette for top countries
    COUNTRY_COLORS = {
        'China': '#FF6B6B',
        'India': '#4ECDC4',
        'United States': '#45B7D1',
        'Russian Federation': '#FFA07A',
        'Japan': '#98D8C8',
        'Indonesia': '#F7DC6F',
        'Germany': '#BB8FCE',
        'Brazil': '#85C1E9',
        'United Kingdom': '#F8B88B',
        'Bangladesh': '#87CEEB',
        'Italy': '#DDA0DD',
        'France': '#90EE90',
        'Pakistan': '#FFB6C1',
        'Nigeria': '#FFA500',
        'Ukraine': '#87CEEB',
    }
    
    def __init__(self, df: pd.DataFrame):
        """Initialize dashboard with data."""
        self.df = df
        self.countries = df['country_name'].unique()
        self.logger = logging.getLogger(__name__)
    
    def create_dashboard(self, output_path: Path, top_n: int = 15) -> go.Figure:
        """
        Create interactive population trends dashboard.
        
        Args:
            output_path: Path to save HTML output
            top_n: Number of top countries to display
        
        Returns:
            Plotly Figure object
        """
        # Get top countries by latest population
        latest_year = self.df['year'].max()
        top_countries = (
            self.df[self.df['year'] == latest_year]
            .nlargest(top_n, 'population')['country_name']
            .tolist()
        )
        
        df_display = self.df[self.df['country_name'].isin(top_countries)].copy()
        
        self.logger.info(f"[VIZ] Creating dashboard for {len(top_countries)} countries")
        
        # Create figure with secondary y-axis for growth rate
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(
                '📈 Population Trends & Trendlines (1960-2024)',
                '📊 Year-over-Year Growth Rate (%)'
            ),
            specs=[
                [{'secondary_y': False}],
                [{'secondary_y': False}]
            ],
            vertical_spacing=0.15,
            row_heights=[0.7, 0.3]
        )
        
        # Add traces for each country
        for country in top_countries:
            df_country = df_display[df_display['country_name'] == country]
            color = self.COUNTRY_COLORS.get(country, None)
            
            # Add actual population line
            fig.add_trace(
                go.Scatter(
                    x=df_country['year'],
                    y=df_country['population'],
                    mode='lines',
                    name=country,
                    line=dict(width=2.5, color=color),
                    hovertemplate=(
                        f'<b>{country}</b><br>' +
                        'Year: %{x}<br>' +
                        'Population: %{y:,.0f}<br>' +
                        '<extra></extra>'
                    ),
                    visible=True
                ),
                row=1, col=1
            )
            
            # Add trendline
            df_trendline = df_country[df_country['trendline'].notna()]
            if len(df_trendline) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=df_trendline['year'],
                        y=df_trendline['trendline'],
                        mode='lines',
                        name=f'{country} (Trend)',
                        line=dict(width=2, color=color),
                        opacity=0.7,
                        hovertemplate=(
                            f'<b>{country} - Trend</b><br>' +
                            'Year: %{x}<br>' +
                            'Trendline: %{y:,.0f}<br>' +
                            '<extra></extra>'
                        ),
                        visible=True,
                        showlegend=False
                    ),
                    row=1, col=1
                )
            
            # Add growth rate line (only to countries with valid data)
            df_growth = df_country[df_country['growth_rate'].notna()]
            if len(df_growth) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=df_growth['year'],
                        y=df_growth['growth_rate'],
                        mode='lines',
                        name=f'{country} GR%',
                        line=dict(width=2, color=color),
                        hovertemplate=(
                            f'<b>{country}</b><br>' +
                            'Year: %{x}<br>' +
                            'Growth Rate: %{y:.2f}%<br>' +
                            '<extra></extra>'
                        ),
                        visible=True,
                        showlegend=False
                    ),
                    row=2, col=1
                )
        
        # Add zero line for growth rate
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="rgba(255,255,255,0.3)",
            row=2, col=1,
            showlegend=False
        )
        
        # Update layout with dark theme
        fig.update_layout(
            title={
                'text': (
                    '🌍 World Population Dashboard v2.0<br>' +
                    '<sub>Interactive Trends with Trendlines & Growth Analysis</sub>'
                ),
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 26, 'color': '#FFFFFF', 'family': 'Arial Black'}
            },
            template='plotly_dark',
            height=1000,
            hovermode='x unified',
            font=dict(family='Arial, sans-serif', size=12, color='#E0E0E0'),
            showlegend=True,
            legend=dict(
                x=1.02,
                y=0.95,
                bgcolor='rgba(30,30,40,0.8)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1,
                font=dict(size=11)
            ),
            plot_bgcolor='rgba(25,25,35,0.8)',
            paper_bgcolor='rgba(15,15,25,1)',
            margin=dict(r=250, b=100, t=120, l=80)
        )
        
        # Update x-axes
        fig.update_xaxes(
            title_text='Year',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            row=1, col=1
        )
        fig.update_xaxes(
            title_text='Year',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            row=2, col=1
        )
        
        # Update y-axes
        fig.update_yaxes(
            title_text='Population',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            tickformat='.2~s',
            ticksuffix='',
            ticktext=['0', '200M', '400M', '600M', '800M', '1B', '1.2B', '1.4B'],
            tickvals=[0, 200000000, 400000000, 600000000, 800000000, 1000000000, 1200000000, 1400000000],
            row=1, col=1
        )
        fig.update_yaxes(
            title_text='YoY Growth Rate (%)',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            row=2, col=1
        )
        
        # Save HTML with metadata
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add metadata footer
        metadata_text = (
            f"<b>Creator:</b> John Hau | "
            f"<b>Script:</b> 04_build_visualization_v2_with_trendline.py | "
            f"<b>Output:</b> {output_path.name} | "
            f"<b>Data Path:</b> csv/processed/population_top50_1970_now_5Mar2026.csv"
        )
        
        fig.add_annotation(
            text=metadata_text,
            xref="paper", yref="paper",
            x=0.5, y=-0.12,
            showarrow=False,
            font=dict(size=9, color='#AAAAAA'),
            xanchor='center',
            yanchor='top'
        )
        
        fig.write_html(
            str(output_path),
            config=dict(
                responsive=True,
                displayModeBar=True,
                displaylogo=False,
                modeBarButtonsToRemove=['select2d', 'lasso2d']
            )
        )
        
        self.logger.info(f"[OUTPUT] Dashboard saved to {output_path}")
        
        return fig


def main():
    """Main execution function."""
    # Define paths
    project_root = Path(__file__).parent.parent
    input_path = project_root / 'csv' / 'processed' / 'population_top50_1970_now_5Mar2026.csv'
    output_path = project_root / 'reports' / 'html' / 'population_trendline_07Mar2026.html'
    
    # Validate input exists
    if not input_path.exists():
        logger.error(f"[ERROR] Input file not found: {input_path}")
        return
    
    logger.info(f"[START] Population Dashboard v2.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load and analyze data
    logger.info("[LOAD] Loading population data...")
    df = PopulationTrendAnalyzer.load_data(input_path)
    
    logger.info("[ANALYZE] Analyzing trends and growth rates...")
    df = PopulationTrendAnalyzer.analyze_all_trends(df)
    
    # Create dashboard
    dashboard = PopulationDashboardV2(df)
    fig = dashboard.create_dashboard(output_path, top_n=15)
    
    # Print summary statistics
    logger.info("[SUMMARY] Population Statistics:")
    latest_year = df['year'].max()
    df_latest = df[df['year'] == latest_year].nlargest(5, 'population')
    for idx, row in df_latest.iterrows():
        logger.info(f"  {row['country_name']}: {row['population']:,.0f} ({row['rank']})")
    
    logger.info(f"[COMPLETE] Dashboard created successfully!")
    logger.info(f"[OUTPUT] View at: {output_path}")


if __name__ == '__main__':
    main()
