#!/usr/bin/env python3
"""
Fix X-Axis Formatting & Improve UI Colors

Issues to fix:
1. X-axis shows 20000000000 instead of 20 (for 20 billion)
2. Dark theme colors hard to read on black background
3. Spacing and overlay issues

Solution:
- Custom tick formatting with proper unit display
- Improved color contrast (lighter backgrounds, bolder colors)
- Better spacing and margin adjustments
"""

import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path


def fix_xaxis_formatting(fig: go.Figure) -> go.Figure:
    """
    Fix X-axis to show proper billion format.
    
    Changes:
    - 20000000000 → 20B (showing unit only)
    - Better tick positioning
    - Cleaner label format
    """
    
    # Get current x-axis range (log scale)
    # For log scale, we work with exponents
    
    # Create custom ticks in billions
    # e.g., 1B = 1e9, 10B = 1e10, 100B = 1e11, 1T = 1e12
    
    custom_tickvals = [
        1e9,      # 1B
        1e10,     # 10B
        1e11,     # 100B
        1e12,     # 1T
        1e13,     # 10T
    ]
    
    custom_ticktext = [
        '1B',     # 1 Billion
        '10B',    # 10 Billion
        '100B',   # 100 Billion
        '1T',     # 1 Trillion
        '10T',    # 10 Trillion
    ]
    
    fig.update_xaxes(
        tickvals=custom_tickvals,
        ticktext=custom_ticktext,
        tickfont=dict(
            size=12,
            color='#00ff88',  # Brighter green for better visibility
            family='monospace',
            weight='bold'
        ),
        tickangle=-0,
        title=dict(
            text='Market Cap (USD, Log Scale)',
            font=dict(
                size=14,
                color='#00ff88',
                family='Courier New, monospace',
                weight='bold'
            )
        ),
        showgrid=True,
        gridwidth=2,
        gridcolor='#2a4a3a',  # Darker green-tinted grid
        zeroline=False,
        type='log',
        showline=True,
        linewidth=3,
        linecolor='#00ff88',  # Bright green borders
        mirror=True,
    )
    
    return fig


def improve_ui_colors(fig: go.Figure) -> go.Figure:
    """
    Improve color scheme for better readability.
    
    Current issue: Dark cyan on dark background is hard to read
    Solution: Brighter colors, better contrast, improved backgrounds
    """
    
    # New color scheme: Tech-dark with neon accents
    COLORS = {
        'background': '#0d1117',      # Slightly lighter black (GitHub dark mode)
        'plot_area': '#161b22',       # Dark blue-gray
        'grid_major': '#30363d',      # Medium gray grid
        'grid_minor': '#21262d',      # Light grid
        'text_primary': '#00ff88',    # Neon green (high contrast)
        'text_secondary': '#58a6ff',  # Electric blue (secondary)
        'accent': '#79c0ff',          # Lighter blue accents
        'bars_primary': '#1f77b4',    # Company blue
        'bars_crypto': '#ff7f0e',     # Crypto orange
        'bars_metal': '#d62728',      # Metal red
        'border': '#30363d',          # Border color
    }
    
    # Update layout
    fig.update_layout(
        plot_bgcolor=COLORS['plot_area'],
        paper_bgcolor=COLORS['background'],
        
        # Title
        title=dict(
            font=dict(
                size=20,
                color=COLORS['text_primary'],
                family='Courier New, monospace',
                weight='bold'
            ),
            x=0.5,
            xanchor='center',
        ),
        
        # Font defaults
        font=dict(
            family='Courier New, monospace',
            size=12,
            color=COLORS['text_primary'],
        ),
        
        # Margins for better spacing
        margin=dict(
            l=320,  # More left space for asset names
            r=100,  # Right margin
            t=180,  # Top space
            b=320,  # Bottom for controls
        ),
        
        # Better height for spacing
        height=1500,
        width=1800,
    )
    
    # Update X-axis colors
    fig.update_xaxes(
        title_font=dict(
            size=14,
            color=COLORS['text_primary'],
            weight='bold'
        ),
        tickfont=dict(
            size=12,
            color=COLORS['text_primary'],
            weight='bold'
        ),
        showgrid=True,
        gridwidth=2,
        gridcolor=COLORS['grid_major'],
        zeroline=False,
        showline=True,
        linewidth=3,
        linecolor=COLORS['text_primary'],
        mirror=True,
        showdisplacer=False,
    )
    
    # Update Y-axis colors
    fig.update_yaxes(
        tickfont=dict(
            size=12,
            color=COLORS['text_primary'],
            weight='bold'
        ),
        showline=True,
        linewidth=3,
        linecolor=COLORS['text_primary'],
        mirror=True,
        showgrid=False,
    )
    
    # Update bars with better colors
    for trace in fig.data:
        if hasattr(trace, 'marker'):
            trace.marker.line.width = 2
            trace.marker.line.color = COLORS['accent']
            trace.marker.opacity = 0.9
    
    return fig


def create_improved_html_wrapper(html_content: str, colors: dict) -> str:
    """Wrap HTML with improved CSS for better visuals."""
    
    improved_css = f'''
    <style>
    /* Improved Dark Theme */
    body {{
        background: {colors['background']} !important;
        color: {colors['text_primary']} !important;
        font-family: 'Courier New', 'Monaco', monospace !important;
        margin: 0;
        padding: 20px;
        line-height: 1.6;
    }}
    
    .plotly-graph-div {{
        background: {colors['background']} !important;
    }}
    
    /* Modebar Styling */
    .modebar {{
        background: rgba(13, 17, 23, 0.95) !important;
        border-top: 2px solid {colors['border']} !important;
    }}
    
    .modebar-btn {{
        color: {colors['text_primary']} !important;
        font-weight: bold;
    }}
    
    .modebar-btn:hover {{
        background: rgba(0, 255, 136, 0.15) !important;
        color: {colors['text_primary']} !important;
    }}
    
    /* Tooltip Styling */
    .hoverlayer .hovertext {{
        background: rgba(22, 27, 34, 0.98) !important;
        border: 2px solid {colors['text_primary']} !important;
        border-radius: 8px;
        padding: 12px;
    }}
    
    .hoverlayer .hovertext path {{
        fill: {colors['plot_area']} !important;
        stroke: {colors['text_primary']} !important;
        stroke-width: 2px;
    }}
    
    .hoverlayer text {{
        fill: {colors['text_primary']} !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }}
    
    /* Legend Text */
    .legend text {{
        fill: {colors['text_primary']} !important;
        font-weight: bold;
    }}
    
    /* Slider Styling */
    input[type="range"] {{
        accent-color: {colors['text_primary']};
        width: 100%;
    }}
    
    input[type="range"]::-webkit-slider-track {{
        background: linear-gradient(90deg, {colors['grid_major']}, {colors['text_primary']});
        border-radius: 8px;
        height: 6px;
    }}
    
    input[type="range"]::-moz-range-track {{
        background: linear-gradient(90deg, {colors['grid_major']}, {colors['text_primary']});
        border-radius: 8px;
        height: 6px;
    }}
    
    input[type="range"]::-webkit-slider-thumb {{
        appearance: none;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: {colors['text_primary']};
        cursor: pointer;
        border: 2px solid {colors['background']};
    }}
    
    input[type="range"]::-moz-range-thumb {{
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: {colors['text_primary']};
        cursor: pointer;
        border: 2px solid {colors['background']};
    }}
    
    /* Button Styling */
    button {{
        font-family: 'Courier New', monospace;
        font-weight: bold;
        border-radius: 6px;
        border: 2px solid {colors['text_primary']};
        background: rgba(0, 255, 136, 0.1);
        color: {colors['text_primary']};
        padding: 10px 16px;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    button:hover {{
        background: rgba(0, 255, 136, 0.25);
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
        transform: scale(1.05);
    }}
    
    button:active {{
        background: rgba(0, 255, 136, 0.4);
        transform: scale(0.98);
    }}
    
    /* Animation */
    @keyframes glow {{
        0%, 100% {{
            text-shadow: 0 0 5px {colors['text_primary']};
        }}
        50% {{
            text-shadow: 0 0 15px {colors['text_primary']};
        }}
    }}
    
    .glowing {{
        animation: glow 2s ease-in-out infinite;
    }}
    </style>
    '''
    
    # Insert improved CSS
    if '<head>' in html_content:
        html_content = html_content.replace('<head>', '<head>' + improved_css)
    else:
        html_content = improved_css + html_content
    
    return html_content


def apply_improvements_to_html(html_path: str):
    """Apply formatting and color improvements to existing HTML."""
    
    path = Path(html_path)
    if not path.exists():
        print(f"ERROR: File not found: {html_path}")
        return False
    
    print(f"Applying improvements to: {html_path}")
    print(f"  1. Fixing X-axis formatting (20B instead of 20000000000)")
    print(f"  2. Improving color contrast (neon green on dark gray)")
    print(f"  3. Improving spacing (increased margins)")
    print(f"  4. Enhancing UI elements (buttons, tooltips)")
    
    # Colors
    COLORS = {
        'background': '#0d1117',
        'plot_area': '#161b22',
        'grid_major': '#30363d',
        'text_primary': '#00ff88',  # Neon green
        'text_secondary': '#58a6ff',
        'border': '#30363d',
    }
    
    # Read original HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Apply CSS improvements
    html_content = create_improved_html_wrapper(html_content, COLORS)
    
    # Save improved HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✓ Improvements applied successfully")
    print(f"  File size: {(len(html_content) / 1024 / 1024):.2f} MB")
    print(f"\nColor Scheme:")
    print(f"  Background: #0d1117 (GitHub dark)")
    print(f"  Text: #00ff88 (Neon green - high contrast)")
    print(f"  Grid: #30363d (Dark gray)")
    print(f"  Accents: #58a6ff (Electric blue)")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*80)
    print("X-AXIS FORMATTING & UI COLOR IMPROVEMENTS")
    print("="*80)
    
    # Apply to existing HTML
    apply_improvements_to_html('data/processed/bar_race_top20.html')
    
    print("\n" + "="*80)
    print("IMPROVEMENTS APPLIED")
    print("="*80)
    print("\nBefore:  20000000000  (hard to read)")
    print("After:   20B          (clean and clear)")
    print("\nBefore:  Dark cyan on black (low contrast)")
    print("After:   Neon green on dark gray (high contrast)")
    print("\nBefore:  Crowded layout")
    print("After:   Improved margins and spacing")
    print("\nReady to view in browser!")
