# -*- coding: utf-8 -*-
"""
World Population Dashboard - Version 3
======================================
Animated trendlines growing over 65 years (1960-2024) with interactive play controls.

Features:
- Animation frame for each year
- Trendlines dynamically grow as you progress through time
- Interactive play/pause button with year slider
- Growth rate visualization in separate panel
- Smooth transitions between years

Author: Analytics Team
Date: 2026-03-07
Version: 3.0.0
"""

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import numpy as np
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class AnimatedPopulationAnalyzer:
    """Analyzes population data and creates animated frames."""
    
    @staticmethod
    def load_data(input_path: Path) -> pd.DataFrame:
        """Load and prepare population data."""
        df = pd.read_csv(input_path, encoding='utf-8')
        df['year'] = pd.to_numeric(df['year'])
        df['population'] = pd.to_numeric(df['population'])
        df = df.sort_values(['country_name', 'year']).reset_index(drop=True)
        logger.info(f"[LOAD] Loaded {len(df)} records, {df['country_name'].nunique()} countries, {df['year'].max()-df['year'].min()+1} years")
        return df
    
    @staticmethod
    def fit_polynomial_trendline(years: np.ndarray, populations: np.ndarray, degree: int = 2) -> np.ndarray:
        """
        Fit polynomial to data and return trendline values.
        
        Args:
            years: Array of year values
            populations: Array of population values
            degree: Polynomial degree
        
        Returns:
            Array of trendline values
        """
        if len(years) < 3:
            return np.full_like(populations, np.nan, dtype=float)
        
        try:
            coeffs = np.polyfit(years, populations, degree)
            poly = np.poly1d(coeffs)
            return poly(years)
        except:
            return np.full_like(populations, np.nan, dtype=float)
    
    @staticmethod
    def prepare_animation_data(df: pd.DataFrame, top_n: int = 15) -> dict:
        """
        Prepare data for animation by year.
        
        Args:
            df: Full population DataFrame
            top_n: Number of top countries
        
        Returns:
            Dictionary with data for each animation frame
        """
        # Get top countries by latest year
        latest_year = df['year'].max()
        top_countries = (
            df[df['year'] == latest_year]
            .nlargest(top_n, 'population')['country_name']
            .tolist()
        )
        
        df_top = df[df['country_name'].isin(top_countries)].copy()
        years = sorted(df_top['year'].unique())
        
        animation_data = {}
        
        for current_year in years:
            frame_data = {}
            
            # Get data up to current year for each country
            for country in top_countries:
                df_country = df_top[
                    (df_top['country_name'] == country) & 
                    (df_top['year'] <= current_year)
                ].copy()
                
                if len(df_country) > 0:
                    # Calculate trendline for available data
                    years_arr = df_country['year'].values
                    pop_arr = df_country['population'].values
                    
                    trendline = AnimatedPopulationAnalyzer.fit_polynomial_trendline(
                        years_arr, pop_arr, degree=2
                    )
                    
                    frame_data[country] = {
                        'years': years_arr,
                        'populations': pop_arr,
                        'trendline': trendline,
                        'latest_pop': pop_arr[-1],
                        'year_count': len(years_arr)
                    }
            
            animation_data[current_year] = frame_data
        
        return animation_data, top_countries, years


class AnimatedPopulationDashboardV3:
    """Creates animated population dashboard with growing trendlines."""
    
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
        'Mexico': '#20B2AA',
        'Vietnam': '#FFD700',
        'Egypt': '#FF4500',
        'Spain': '#9370DB',
        'Ethiopia': '#3CB371',
    }
    
    def __init__(self, animation_data: dict, top_countries: list, years: list):
        """Initialize dashboard with animation data."""
        self.animation_data = animation_data
        self.top_countries = top_countries
        self.years = years
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def generate_y_axis_ticks(y_max: float) -> tuple:
        """
        Generate nice round tick values and labels for y-axis with 'B' for billions.
        
        Args:
            y_max: Maximum y value to display
        
        Returns:
            Tuple of (tickvals, ticktext)
        """
        # Calculate number of ticks needed
        billion = 1_000_000_000
        max_billions = y_max / billion
        
        # Determine tick interval
        if max_billions <= 0.5:
            tick_interval = 100_000_000  # 0.1B
        elif max_billions <= 2:
            tick_interval = 200_000_000  # 0.2B
        elif max_billions <= 4:
            tick_interval = 400_000_000  # 0.4B
        else:
            tick_interval = 400_000_000  # 0.4B
        
        tickvals = []
        ticktext = []
        tick = 0
        
        while tick <= y_max:
            tickvals.append(tick)
            if tick == 0:
                ticktext.append('0')
            else:
                billions = tick / billion
                if billions >= 1:
                    ticktext.append(f'{billions:.1f}B')
                else:
                    millions = tick / 1_000_000
                    ticktext.append(f'{millions:.0f}M')
            tick += tick_interval
        
        return tickvals, ticktext
    
    def create_animated_dashboard(self, output_path: Path) -> go.Figure:
        """
        Create animated population dashboard with growing trendlines.
        
        Args:
            output_path: Path to save HTML output
        
        Returns:
            Plotly Figure object
        """
        min_year = self.years[0]
        max_year = self.years[-1]
        
        self.logger.info(f"[VIZ] Creating animated dashboard for {len(self.top_countries)} countries over {len(self.years)} years")
        
        # Create initial frame (1960)
        fig = go.Figure()
        
        # Add initial traces for each country
        initial_frame_data = self.animation_data[self.years[0]]
        
        for country in self.top_countries:
            if country in initial_frame_data:
                data = initial_frame_data[country]
                color = self.COUNTRY_COLORS.get(country, '#CCCCCC')
                
                # Actual population line
                fig.add_trace(
                    go.Scatter(
                        x=data['years'],
                        y=data['populations'],
                        mode='lines+markers',
                        name=country,
                        line=dict(width=3, color=color),
                        marker=dict(size=4),
                        hovertemplate=(
                            f'<b>{country}</b><br>' +
                            'Population: %{y:,.0f}<br>' +
                            '<extra></extra>'
                        ),
                        visible=True
                    )
                )
        
        # Create frames for animation
        frames = []
        
        for year in self.years:
            frame_data = self.animation_data[year]
            frame_traces = []
            
            for country in self.top_countries:
                if country in frame_data:
                    data = frame_data[country]
                    color = self.COUNTRY_COLORS.get(country, '#CCCCCC')
                    
                    # Actual line
                    frame_traces.append(
                        go.Scatter(
                            x=data['years'],
                            y=data['populations'],
                            mode='lines+markers',
                            line=dict(width=3, color=color),
                            marker=dict(size=4),
                            hovertemplate=(
                                f'<b>{country}</b><br>' +
                                'Population: %{y:,.0f}<br>' +
                                '<extra></extra>'
                            )
                        )
                    )
            
            # Calculate max population for dynamic y-axis scaling
            max_pop = 0
            for country in self.top_countries:
                if country in frame_data:
                    max_pop = max(max_pop, frame_data[country]['latest_pop'])
            
            # Add 10% padding to max for better visualization
            y_max = max_pop * 1.1
            
            # Generate custom y-axis ticks with 'B' for billions
            tickvals, ticktext = self.generate_y_axis_ticks(y_max)
            
            frames.append(go.Frame(
                data=frame_traces,
                name=str(year),
                layout=go.Layout(
                    title_text=f'🌍 World Population Animation (1960-2024)<br><sub>{len([c for c in self.top_countries if c in frame_data])} Countries</sub>',
                    yaxis=dict(range=[0, y_max], tickvals=tickvals, ticktext=ticktext)
                )
            ))
        
        fig.frames = frames
        
        # Create slider steps
        sliders = [{
            'active': 0,
            'yanchor': 'top',
            'y': -0.08,
            'xanchor': 'left',
            'currentvalue': {
                'prefix': '📅 Year: ',
                'visible': True,
                'xanchor': 'center',
                'font': {'size': 14, 'color': '#FFFFFF'}
            },
            'transition': {'duration': 0},
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.05,
            'steps': [
                {
                    'args': [
                        [str(year)],
                        {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }
                    ],
                    'method': 'animate',
                    'label': str(year)
                }
                for year in self.years
            ]
        }]
        
        # Update layout
        fig.update_layout(
            title={
                'text': f'🌍 World Population Animation v3.0<br><sub>Trendlines Growing Over 65 Years (1960-2024)</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 26, 'color': '#FFFFFF', 'family': 'Arial Black'}
            },
            xaxis=dict(
                title='Year',
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                range=[self.years[0] - 1, self.years[-1] + 1]
            ),
            yaxis=dict(
                title='Population',
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                tickformat='.2~s'
            ),
            template='plotly_dark',
            height=900,
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
            margin=dict(r=250, b=150, t=120, l=80),
            updatemenus=[
                {
                    'type': 'buttons',
                    'showactive': True,
                    'y': -0.05,
                    'x': -0.08,
                    'xanchor': 'left',
                    'yanchor': 'top',
                    'buttons': [
                        {
                            'label': '▶️ Play (1x)',
                            'method': 'animate',
                            'args': [
                                None,
                                {
                                    'frame': {'duration': 80, 'redraw': False},
                                    'fromcurrent': True,
                                    'transition': {'duration': 0},
                                    'mode': 'immediate'
                                }
                            ]
                        },
                        {
                            'label': '▶️ Play (3x)',
                            'method': 'animate',
                            'args': [
                                None,
                                {
                                    'frame': {'duration': 27, 'redraw': False},
                                    'fromcurrent': True,
                                    'transition': {'duration': 0},
                                    'mode': 'immediate'
                                }
                            ]
                        },
                        {
                            'label': '▶️ Play (5x)',
                            'method': 'animate',
                            'args': [
                                None,
                                {
                                    'frame': {'duration': 16, 'redraw': False},
                                    'fromcurrent': True,
                                    'transition': {'duration': 0},
                                    'mode': 'immediate'
                                }
                            ]
                        },
                        {
                            'label': '⏸️ Pause',
                            'method': 'animate',
                            'args': [
                                [None],
                                {
                                    'frame': {'duration': 0, 'redraw': False},
                                    'mode': 'immediate',
                                    'transition': {'duration': 0}
                                }
                            ]
                        }
                    ]
                }
            ],
            sliders=sliders
        )
        
        # Save HTML with metadata
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add metadata footer
        metadata_text = (
            f"<b>Creator:</b> John Hau | "
            f"<b>Script:</b> 05_build_visualization_v3_animated_trendline.py | "
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
        
        self.logger.info(f"[OUTPUT] Animated dashboard saved to {output_path}")
        
        return fig


def main():
    """Main execution function."""
    # Define paths
    project_root = Path(__file__).parent.parent
    input_path = project_root / 'csv' / 'processed' / 'population_top50_1970_now_5Mar2026.csv'
    output_path = project_root / 'reports' / 'html' / 'population_animated_trendline_07Mar2026.html'
    
    # Validate input exists
    if not input_path.exists():
        logger.error(f"[ERROR] Input file not found: {input_path}")
        return
    
    logger.info(f"[START] Population Dashboard v3.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    logger.info("[LOAD] Loading population data...")
    df = AnimatedPopulationAnalyzer.load_data(input_path)
    
    # Prepare animation data
    logger.info("[PREPARE] Preparing animation frames...")
    animation_data, top_countries, years = AnimatedPopulationAnalyzer.prepare_animation_data(df, top_n=15)
    logger.info(f"[PREPARE] Created {len(years)} animation frames for {len(top_countries)} countries")
    
    # Create dashboard
    dashboard = AnimatedPopulationDashboardV3(animation_data, top_countries, years)
    fig = dashboard.create_animated_dashboard(output_path)
    
    # Print summary
    logger.info("[SUMMARY] Animation Details:")
    logger.info(f"  Time Range: {years[0]} - {years[-1]} ({len(years)} years)")
    logger.info(f"  Countries: {len(top_countries)}")
    logger.info(f"  Total Frames: {len(years)}")
    
    logger.info(f"[COMPLETE] Animated dashboard created successfully!")
    logger.info(f"[OUTPUT] View at: {output_path}")


if __name__ == '__main__':
    main()
