
# -*- coding: utf-8 -*-
"""
Phase 2 - Visualization Builder
Build interactive bar race visualization with flags and formatting.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime


def load_processed_data(input_path: Path) -> pd.DataFrame:
    """
    Load processed population data.
    
    Args:
        input_path: Path to processed CSV
    
    Returns:
        DataFrame with population data
    """
    df = pd.read_csv(input_path, encoding='utf-8')
    print(f"[LOAD] Loaded {len(df)} records from {input_path.name}")
    return df


def load_country_mapping(mapping_path: Path) -> dict:
    """
    Load ISO-3 to ISO-2 country code mapping.
    
    Args:
        mapping_path: Path to country_code_map.csv
    
    Returns:
        Dictionary mapping ISO-3 to ISO-2 codes
    """
    df = pd.read_csv(mapping_path, encoding='utf-8')
    mapping = dict(zip(df['iso3'], df['iso2']))
    print(f"[MAPPING] Loaded {len(mapping)} country code mappings")
    return mapping


def add_flag_urls(df: pd.DataFrame, code_mapping: dict) -> pd.DataFrame:
    """
    Add flag URL column to DataFrame.
    
    Args:
        df: DataFrame with country_code column
        code_mapping: ISO-3 to ISO-2 mapping
    
    Returns:
        DataFrame with flag_url column
    """
    def get_flag_url(iso3_code):
        iso2_code = code_mapping.get(iso3_code, '').lower()
        if iso2_code:
            return f"https://flagcdn.com/{iso2_code}.svg"
        return ""
    
    df['flag_url'] = df['country_code'].apply(get_flag_url)
    print(f"[FLAGS] Added flag URLs for {df['flag_url'].notna().sum()} countries")
    return df


def format_population(pop: int) -> str:
    """
    Format population with M/B suffixes.
    
    Args:
        pop: Population value
    
    Returns:
        Formatted string (e.g., "331M")
    """
    if pop >= 1_000_000_000:
        return f"{pop / 1_000_000_000:.1f}B"
    elif pop >= 1_000_000:
        return f"{pop / 1_000_000:.1f}M"
    else:
        return f"{pop:,}"


def create_bar_race(df: pd.DataFrame, top_n: int = 30) -> go.Figure:
    """
    Create animated bar race visualization.
    
    Args:
        df: DataFrame with population data and flags
        top_n: Number of top countries to display per frame
    
    Returns:
        Plotly Figure object
    """
    print(f"[VIZ] Creating bar race for {df['year'].nunique()} years, showing top {top_n} countries")
    
    # Sort data by year and rank
    df_sorted = df.sort_values(['year', 'rank']).copy()
    
    # Filter to top N per year for better visibility
    df_display = df_sorted.groupby('year').head(top_n).reset_index(drop=True)
    
    # Create bar chart
    fig = px.bar(
        df_display,
        x='population',
        y='country_name',
        animation_frame='year',
        color='country_name',
        orientation='h',
        range_x=[0, df_display['population'].max() * 1.1],
        labels={'population': 'Population', 'country_name': 'Country'},
        text='population',
        hover_data={'country_name': True, 'population': True, 'rank': True, 'year': True}
    )
    
    # Update traces for better appearance with high-contrast white text
    fig.update_traces(
        texttemplate='%{text:.2s}',
        textposition='outside',
        textfont=dict(size=14, color='#FFFFFF', family='Arial Black, sans-serif'),
        hovertemplate='<b>%{y}</b><br><br>' +
                      'Population: <b>%{x:,.0f}</b><br>' +
                      'Rank: #%{customdata[0]}<br>' +
                      'Year: %{customdata[1]}' +
                      '<extra></extra>',
        customdata=df_display[['rank', 'year']],
        marker=dict(line=dict(width=1, color='rgba(255,255,255,0.3)'))
    )
    
    # Apply modern dark theme with better contrast
    fig.update_layout(
        title={
            'text': '🌍 World Population Dashboard (1960 - 2024)<br><sub>Top 30 Most Populous Countries</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#FFFFFF'}
        },
        xaxis_title='Population',
        yaxis_title='',
        showlegend=False,
        height=900,
        template='plotly_dark',
        font=dict(family='Arial, sans-serif', size=13, color='#E0E0E0'),
        xaxis=dict(
            tickformat='~s',
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.3)',
            tickfont=dict(size=12, color='#FFFFFF')
        ),
        yaxis=dict(
            showgrid=False,
            categoryorder='total ascending',
            tickfont=dict(size=13, color='#FFFFFF')
        ),
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#121212',
        margin=dict(l=250, r=120, t=120, b=100),
        autosize=True,
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        hoverlabel=dict(
            bgcolor='#1C1C1C',
            font_size=20,
            font_family='Arial, sans-serif',
            font_color='#FFFFFF',
            bordercolor='#666666'
        )
    )
    
    # Update animation settings
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 800
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500
    
    print(f"[VIZ] Bar race created successfully")
    return fig


def save_html(fig: go.Figure, output_path: Path, creator: str = "John Hau", script_name: str = "03_build_visualization.py") -> None:
    """
    Save figure as self-contained HTML with metadata.
    
    Args:
        fig: Plotly Figure object
        output_path: Path to save HTML file
        creator: Name of creator
        script_name: Name of the script that created the visualization
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add metadata to figure layout
    metadata_text = (
        f"<b>Creator:</b> {creator} | "
        f"<b>Script:</b> {script_name} | "
        f"<b>Output:</b> {output_path.name} | "
        f"<b>Date:</b> {datetime.now().strftime('%d %b %Y')}"
    )
    
    fig.add_annotation(
        text=metadata_text,
        xref="paper", yref="paper",
        x=0.5, y=-0.08,
        showarrow=False,
        font=dict(size=10, color='#CCCCCC'),
        xanchor='center',
        yanchor='top'
    )
    
    fig.write_html(
        str(output_path),
        include_plotlyjs='cdn',
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
        }
    )
    
    file_size = output_path.stat().st_size
    print(f"[SAVE] HTML saved to {output_path}")
    print(f"[SAVE] File size: {file_size:,} bytes")


def main():
    """Main execution function."""
    print("=" * 70)
    print("BUILDING POPULATION VISUALIZATION")
    print("=" * 70)
    
    # Define paths
    base_dir = Path(__file__).parent.parent
    
    # Find most recent processed file
    processed_dir = base_dir / "csv" / "processed"
    processed_files = sorted(processed_dir.glob("population_top50_*.csv"))
    
    if not processed_files:
        print("[ERROR] No processed CSV files found")
        return
    
    input_csv = processed_files[-1]
    config_dir = base_dir / "config"
    mapping_csv = config_dir / "country_code_map.csv"
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%d%b%Y")
    output_html = base_dir / "reports" / "html" / f"population_bar_race_{timestamp}.html"
    
    # Load data
    df = load_processed_data(input_csv)
    code_mapping = load_country_mapping(mapping_csv)
    
    # Add flag URLs
    df = add_flag_urls(df, code_mapping)
    
    # Create visualization (Top 30 countries fit on screen without scrolling)
    fig = create_bar_race(df, top_n=30)
    
    # Save HTML with metadata
    save_html(
        fig, 
        output_html,
        creator="John Hau",
        script_name="03_build_visualization.py"
    )
    
    print("=" * 70)
    print(f"COMPLETE: Visualization saved to {output_html.name}")
    print("=" * 70)


if __name__ == "__main__":
    main()
