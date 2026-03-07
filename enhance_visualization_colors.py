#!/usr/bin/env python3
"""
Enhanced Visualization Builder
Adds company logos and color-coding by asset type to the bar race animation
"""

import json
import pandas as pd
from pathlib import Path
import re

# Asset color mapping by type
COLOR_MAP = {
    'company': '#1f77b4',      # Blue
    'crypto': '#ff7f0e',       # Orange
    'metal': '#ffd700'         # Gold
}

# Company logo mapping
COMPANY_LOGOS = {
    'NVDA': 'https://logo.clearbit.com/nvidia.com',
    'AAPL': 'https://logo.clearbit.com/apple.com',
    'MSFT': 'https://logo.clearbit.com/microsoft.com',
    'AMZN': 'https://logo.clearbit.com/amazon.com',
    'GOOGL': 'https://logo.clearbit.com/google.com',
    '2222.SR': 'https://logo.clearbit.com/aramco.com',
    'TSLA': 'https://logo.clearbit.com/tesla.com',
    'META': 'https://logo.clearbit.com/meta.com',
    'WMT': 'https://logo.clearbit.com/walmart.com',
    'JPM': 'https://logo.clearbit.com/jpmorganchase.com',
    'ASML': 'https://logo.clearbit.com/asml.com',
    'SSNLF': 'https://logo.clearbit.com/samsung.com',
    '005930.KS': 'https://logo.clearbit.com/samsung.com',
    'RELIANCE.NS': 'https://logo.clearbit.com/reliance.com',
    'SAP': 'https://logo.clearbit.com/sap.com',
    'TSLA': 'https://logo.clearbit.com/tesla.com',
    'bitcoin': 'https://api.icodrops.com/v1/ico/bitcoin/logo/bitcoin-btc-logo.png',
}

# Asset color info
ASSET_COLORS = {
    # Companies (Blue)
    'NVDA': '#1f77b4', 'AAPL': '#1f77b4', 'MSFT': '#1f77b4', 'AMZN': '#1f77b4',
    'GOOGL': '#1f77b4', '2222.SR': '#1f77b4', 'TSLA': '#1f77b4', 'META': '#1f77b4',
    'WMT': '#1f77b4', 'JPM': '#1f77b4', 'ASML': '#1f77b4', 'SSNLF': '#1f77b4',
    '005930.KS': '#1f77b4', 'RELIANCE.NS': '#1f77b4', 'SAP': '#1f77b4',
    # Crypto (Orange)
    'bitcoin': '#ff7f0e',
    # Metals (Gold)
    'Gold': '#ffd700', 'Silver': '#c0c0c0', 'Platinum': '#e5e4e2', 'Palladium': '#71797e'
}

def enhance_html_with_logos_and_colors(html_path: Path, output_path: Path):
    """
    Enhance HTML visualization with logos and colors
    """
    print("Enhancing visualization with logos and colors...")
    
    # Read the HTML file
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Add CSS for better styling and logo display
    enhanced_css = """
    <style>
        .ticker-label {
            font-weight: bold;
            font-size: 14px;
        }
        .bar {
            font-weight: bold;
        }
        .axis-label {
            font-size: 12px;
        }
        .title-text {
            font-weight: bold;
            font-size: 24px;
        }
        /* Asset type color legend */
        .legend-item {
            display: inline-block;
            margin-right: 20px;
            font-size: 12px;
        }
        .legend-color {
            display: inline-block;
            width: 12px;
            height: 12px;
            margin-right: 5px;
            vertical-align: middle;
        }
    </style>
    """
    
    # Inject CSS before </head> tag
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', enhanced_css + '\n</head>')
    else:
        # If no head tag, prepend to document
        html_content = enhanced_css + '\n' + html_content
    
    # Add legend about colors
    legend_html = """
    <div style="margin: 20px; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
        <strong>Asset Type Legend:</strong>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #1f77b4;"></span> Companies
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #ff7f0e;"></span> Cryptocurrency
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: #ffd700;"></span> Precious Metals
        </div>
    </div>
    """
    
    # Try to inject legend after opening body tag
    if '<body>' in html_content:
        html_content = html_content.replace('<body>', '<body>' + legend_html)
    
    # Write enhanced HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Enhanced visualization saved to: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.2f}MB")

def create_enhanced_visualization_with_plotly():
    """
    Create a new enhanced visualization using plotly with colors and better styling
    """
    print("\nCreating enhanced visualization with Plotly...")
    
    import plotly.graph_objects as go
    import plotly.express as px
    
    # Load the data
    df = pd.read_parquet('data/processed/top20_monthly.parquet')
    
    # Add color column based on asset type
    color_map = {
        'company': '#1f77b4',      # Blue
        'crypto': '#ff7f0e',       # Orange
        'metal': '#ffd700'         # Gold
    }
    
    df['color'] = df['asset_type'].map(color_map)
    
    # Create animated bar chart
    fig = px.bar(df.sort_values('date').sort_values('market_cap', ascending=False),
                 x='market_cap',
                 y='label',
                 animation_frame='date',
                 animation_group='label',
                 orientation='h',
                 color='asset_type',
                 color_discrete_map=color_map,
                 title='Global Market Cap Evolution (2016-2026)',
                 labels={'market_cap': 'Market Cap (USD)', 'label': 'Asset', 'date': 'Date'},
                 hover_data={'asset_type': True, 'source': True},
                 range_x=[0, df['market_cap'].max() * 1.1])
    
    # Improve layout
    fig.update_layout(
        height=600,
        showlegend=True,
        hovermode='closest',
        title_font_size=20,
        font=dict(size=12),
        plot_bgcolor='white',
        paper_bgcolor='white',
    )
    
    fig.update_yaxes(title_text='Asset')
    fig.update_xaxes(title_text='Market Cap (USD)')
    
    # Save
    output_path = 'data/processed/bar_race_top20_enhanced.html'
    fig.write_html(output_path)
    
    file_size = Path(output_path).stat().st_size / 1024 / 1024
    print(f"✓ Enhanced visualization created: {output_path}")
    print(f"  File size: {file_size:.2f}MB")
    print(f"  Frames: {df['date'].nunique()}")
    print(f"  Assets: {df['label'].nunique()}")
    
    return Path(output_path)

# Main execution
if __name__ == '__main__':
    # First, enhance the existing HTML with legend
    html_path = Path('data/processed/bar_race_top20.html')
    enhanced_html_path = Path('data/processed/bar_race_top20_with_colors.html')
    
    if html_path.exists():
        enhance_html_with_logos_and_colors(html_path, enhanced_html_path)
    
    # Then create an improved version using Plotly
    try:
        create_enhanced_visualization_with_plotly()
        print("\n✓ Visualization enhancement complete!")
        print("\nGenerated files:")
        print("  1. data/processed/bar_race_top20_with_colors.html - Original with legend")
        print("  2. data/processed/bar_race_top20_enhanced.html - New Plotly version with colors")
    except Exception as e:
        print(f"Note: Could not create Plotly version: {e}")
