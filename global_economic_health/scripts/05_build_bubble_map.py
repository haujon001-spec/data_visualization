# -*- coding: utf-8 -*-
"""
Phase 2: Build Bubble Map Visualization

Creates interactive Plotly bubble map showing:
- X-axis: GDP per capita (USD, logarithmic scale)
- Y-axis: Population (logarithmic scale)
- Size: Total GDP (larger bubble = higher GDP)
- Color: Debt-to-GDP ratio (red = high debt burden, green = low)
- Year slider to animate through time

Output: reports/html/bubble_map_<timestamp>.html
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime
import logging
import json
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class BubbleMapBuilder:
    """Builds interactive bubble map from macro-economic data."""
    
    def __init__(self, project_root: Path = None):
        """Initialize builder."""
        self.project_root = project_root or Path(__file__).parent.parent
    
    def load_data(self) -> pd.DataFrame:
        """Load latest macro_final dataset."""
        import glob
        
        logger.info("[LOAD] Searching for macro_final data...")
        pattern = str(self.project_root / 'csv' / 'processed' / 'macro_final_*.csv')
        files = glob.glob(pattern)
        
        if not files:
            raise ValueError(f"No macro_final CSV found in {self.project_root / 'csv' / 'processed'}")
        
        latest_file = max(files, key=lambda p: Path(p).stat().st_mtime)
        logger.info(f"[LOAD] Using: {Path(latest_file).name}")
        
        df = pd.read_csv(latest_file)
        logger.info(f"[LOAD] {len(df)} rows loaded")
        
        return df
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validate dataset has required columns."""
        required = ['country_name', 'country_code', 'year', 'gdp_usd', 'population', 'gdp_per_capita']
        
        missing = set(required) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        logger.info("[VALIDATE] Schema OK")
        return True
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for visualization with dynamic scaling and country colors."""
        logger.info("[PREPARE] Processing data...")
        
        # Ensure required columns exist
        if 'debt_to_gdp' not in df.columns:
            logger.warning("[PREPARE] debt_to_gdp not found, setting to null")
            df['debt_to_gdp'] = None
        
        # Filter out null/invalid values
        df = df.dropna(subset=['gdp_per_capita', 'population', 'gdp_usd'])
        
        # Ensure positive values for log scale
        df = df[(df['gdp_per_capita'] > 0) & (df['population'] > 0) & (df['gdp_usd'] > 0)]
        
        # Assign unique colors to each country (like crypto bubbles)
        # Use a diverse color palette
        colors_palette = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8B88B', '#76D7C4',
            '#FF85A2', '#A8D8EA', '#FFB347', '#C39BD3', '#82E0AA',
            '#F5B041', '#85C1E9', '#F5B7B1', '#D7BDE2', '#90EE90',
            '#FFB6C1', '#87CEEB', '#F0E68C', '#DDA0DD', '#20B2AA',
            '#FF69B4', '#6495ED', '#FFFFE0', '#EE82EE', '#32CD32'
        ]
        
        unique_countries = df['country_name'].unique()
        country_colors = {
            country: colors_palette[i % len(colors_palette)] 
            for i, country in enumerate(sorted(unique_countries))
        }
        df['country_color'] = df['country_name'].map(country_colors)
        
        # Dynamic bubble size scaling per year
        # Normalize bubble sizes within each year so they scale proportionally
        def scale_bubbles_by_year(year_group):
            """Scale bubbles dynamically for each year independently."""
            gdp_values = year_group['gdp_usd']
            min_gdp = gdp_values.min()
            max_gdp = gdp_values.max()
            
            # Map to bubble sizes 5-60 (like crypto bubbles)
            if max_gdp > min_gdp:
                normalized = (gdp_values - min_gdp) / (max_gdp - min_gdp)
                year_group['bubble_size'] = 5 + (normalized * 55)
            else:
                year_group['bubble_size'] = 20
            
            return year_group
        
        df = df.groupby('year', group_keys=False).apply(scale_bubbles_by_year)
        
        # Format text for hover with more details
        df['hover_text'] = (
            df.apply(
                lambda row: (
                    f"<b>{row['country_name']}</b><br>"
                    f"GDP: ${row['gdp_usd']/1e12:.2f}T<br>"
                    f"Population: {row['population']/1e6:.1f}M<br>"
                    f"GDP/Capita: ${row['gdp_per_capita']:,.0f}<br>"
                    f"Debt/GDP: {row['debt_to_gdp']:.2f}x<br>"
                    f"Year: {int(row['year'])}"
                ),
                axis=1
            )
        )
        
        logger.info(f"[PREPARE] {len(df)} valid records ready")
        logger.info(f"[PREPARE] {len(unique_countries)} unique countries with assigned colors")
        
        return df
    
    def build_figure(self, df: pd.DataFrame) -> go.Figure:
        """Build interactive Plotly bubble map."""
        logger.info("[BUILD] Creating figure...")
        
        # Get unique years for slider
        years = sorted(df['year'].unique())
        
        # Create figure with Plotly
        fig = go.Figure()
        
        # Add traces for each year (initially hidden, shown via slider)
        for year in years:
            year_data = df[df['year'] == year].copy()
            
            fig.add_trace(
                go.Scatter(
                    x=year_data['gdp_per_capita'],
                    y=year_data['population'],
                    mode='markers',
                    marker=dict(
                        size=year_data['bubble_size'],
                        color=year_data['debt_to_gdp'],
                        colorscale='RdYlGn_r',  # Red=high debt, Green=low debt
                        showscale=bool(year == years[0]),  # Only show once (convert numpy.bool to bool)
                        colorbar=dict(
                            title="Debt/GDP<br>Ratio",
                            thickness=15,
                            len=0.7,
                            x=1.02
                        ),
                        opacity=0.7,
                        line=dict(width=1, color='white')
                    ),
                    text=year_data['hover_text'],
                    hovertemplate='%{text}<extra></extra>',
                    name=str(int(year)),
                    visible=(year == years[0])  # Only first year visible initially
                )
            )
        
        # Create slider steps
        steps = []
        for i, year in enumerate(years):
            step = dict(
                method='update',
                args=[{'visible': [j == i for j in range(len(years))]},
                      {'title.text': f'Global Economic Health - {int(year)}<br><sub>Bubble size = GDP, Color = Debt/GDP ratio</sub>'}],
                label=str(int(year))
            )
            steps.append(step)
        
        # Add slider
        sliders = [dict(
            active=0,
            yanchor='top',
            y=0,
            xanchor='left',
            x=0.1,
            len=0.8,
            transition={'duration': 300},
            pad={'b': 10, 't': 50},
            currentvalue=dict(
                prefix='Year: ',
                visible=True,
                xanchor='center',
                font=dict(size=16, color='#000')
            ),
            steps=steps
        )]
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f'Global Economic Health - {int(years[0])}<br><sub>Bubble size = GDP, Color = Debt/GDP ratio</sub>',
                font=dict(size=20)
            ),
            xaxis=dict(
                title='GDP per Capita (USD, log scale)',
                type='log',
                gridcolor='#eee',
                showgrid=True,
                zeroline=False
            ),
            yaxis=dict(
                title='Population (log scale)',
                type='log',
                gridcolor='#eee',
                showgrid=True,
                zeroline=False
            ),
            sliders=sliders,
            hovermode='closest',
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=12, color='#333'),
            width=1400,
            height=800,
            margin=dict(l=80, r=150, t=120, b=100),
            showlegend=False
        )
        
        logger.info(f"[BUILD] Figure created with {len(years)} years of data")
        
        return fig
    
    def save_figure(self, fig: go.Figure) -> Path:
        """Save figure to HTML."""
        timestamp = datetime.now().strftime("%d%b%Y_%H%M%S").upper()
        output_dir = self.project_root / 'reports' / 'html'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f'bubble_map_{timestamp}.html'
        
        fig.write_html(
            str(output_file),
            config=dict(
                responsive=True,
                displayModeBar=True,
                displaylogo=False,
                modeBarButtonsToRemove=['lasso2d', 'select2d']
            )
        )
        
        logger.info(f"[SAVE] Bubble map saved to {output_file.relative_to(self.project_root)}")
        logger.info(f"[SIZE] {output_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        return output_file


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent
    
    builder = BubbleMapBuilder(project_root)
    
    try:
        # Load and prepare data
        df = builder.load_data()
        builder.validate_data(df)
        df = builder.prepare_data(df)
        
        # Build and save figure
        fig = builder.build_figure(df)
        output_path = builder.save_figure(fig)
        
        logger.info("\n✅ Bubble map generation complete")
        return 0
    
    except Exception as e:
        logger.error(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
