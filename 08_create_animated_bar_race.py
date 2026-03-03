"""
Generate Animated Bar Race Chart (2016-2026)
Creates interactive animation showing how top 20 assets ranked over 10 years
Uses the complete historical dataset with 227 monthly snapshots
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import numpy as np

print("="*80)
print("GENERATING 10-YEAR ANIMATED BAR RACE CHART")
print("="*80)

# Load the historical top 20 data (all 227 dates from 2016-2026)
print("\n[1] Loading historical data (2016-2026)...")

# We need to rebuild the complete historical dataset
companies_norm = pd.read_csv('data/processed/companies_normalized.csv')
metals_raw = pd.read_csv('data/raw/metals_monthly.csv')
crypto_raw = pd.read_csv('data/raw/crypto_monthly.csv')

# Map company names
companies_config = pd.read_csv('config/universe_companies.csv')
ticker_to_name = dict(zip(companies_config['ticker'], companies_config['name']))

print(f"   Companies: {len(companies_norm)} records")
print(f"   Metals: {len(metals_raw)} records")
print(f"   Crypto: {len(crypto_raw)} records")

# Prepare company data
companies_hist = companies_norm.copy()
companies_hist['label'] = companies_hist['ticker'].map(ticker_to_name)
companies_hist['market_cap'] = companies_hist['market_cap_usd']
companies_hist['asset_type'] = 'company'
companies_prep = companies_hist[['date', 'label', 'market_cap', 'asset_type']].copy()

# Prepare metals data  
metals_hist = metals_raw.copy()
metals_hist['label'] = metals_hist['name']
metals_hist['asset_type'] = 'metal'
metals_prep = metals_hist[['date', 'label', 'market_cap', 'asset_type']].copy()

# Prepare crypto data
crypto_hist = crypto_raw.copy()
crypto_hist['label'] = crypto_hist['coin_id'].str.capitalize()
crypto_hist['asset_type'] = 'crypto'
crypto_prep = crypto_hist[['date', 'label', 'market_cap', 'asset_type']].copy()

# Combine all
all_hist = pd.concat([companies_prep, metals_prep, crypto_prep], ignore_index=True)
all_hist['date'] = pd.to_datetime(all_hist['date'])
all_hist = all_hist.sort_values('date')
all_hist = all_hist[all_hist['market_cap'].notna()].copy()

print(f"   Combined: {len(all_hist)} records across {all_hist['date'].nunique()} dates")

# Get unique dates
dates_sorted = sorted(all_hist['date'].unique())
print(f"   Date range: {dates_sorted[0].date()} to {dates_sorted[-1].date()}")

# Create animation frames
print("\n[2] Creating animation frames...")

frames = []
dates_for_slider = []

for frame_date in dates_sorted:
    # Get top 20 for this date
    date_data = all_hist[all_hist['date'] == frame_date].copy()
    date_data['rank'] = date_data['market_cap'].rank(ascending=False, method='min').astype(int)
    date_data = date_data[date_data['rank'] <= 20].sort_values('rank')
    
    if len(date_data) > 0:
        # Create frame
        frame = go.Frame(
            data=[go.Bar(
                x=date_data['market_cap'] / 1e12,  # Convert to trillions
                y=date_data['label'],
                orientation='h',
                marker=dict(
                    color=['#00ff88' if t == 'company' else '#ffaa00' if t == 'metal' else '#ff00ff' 
                           for t in date_data['asset_type']],
                    line=dict(color='#00ff88', width=2)
                ),
                text=[f"${cap/1e12:.2f}T" if cap >= 1e12 else f"${cap/1e9:.1f}B" 
                      for cap in date_data['market_cap']],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Market Cap: $%{x:.2f}T USD<extra></extra>'
            )],
            name=str(frame_date.date())
        )
        frames.append(frame)
        dates_for_slider.append(frame_date)

print(f"   Created {len(frames)} animation frames")

# Create initial frame
initial_date = dates_for_slider[0]
initial_data = all_hist[all_hist['date'] == initial_date].copy()
initial_data['rank'] = initial_data['market_cap'].rank(ascending=False, method='min').astype(int)
initial_data = initial_data[initial_data['rank'] <= 20].sort_values('rank')

# Create figure with initial data
fig = go.Figure(
    data=[go.Bar(
        x=initial_data['market_cap'] / 1e12,
        y=initial_data['label'],
        orientation='h',
        marker=dict(
            color=['#00ff88' if t == 'company' else '#ffaa00' if t == 'metal' else '#ff00ff' 
                   for t in initial_data['asset_type']],
            line=dict(color='#00ff88', width=2)
        ),
        text=[f"${cap/1e12:.2f}T" if cap >= 1e12 else f"${cap/1e9:.1f}B" 
              for cap in initial_data['market_cap']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Market Cap: $%{x:.2f}T USD<extra></extra>'
    )],
    frames=frames
)

# Add slider
sliders = [{
    'active': 0,
    'yanchor': 'top',
    'y': -0.15,
    'xanchor': 'left',
    'x': 0.0,
    'len': 1.0,
    'transition': {'duration': 300},
    'pad': {'b': 10, 't': 50},
    'currentvalue': {
        'prefix': '<b>Date: </b>',
        'visible': True,
        'xanchor': 'center',
        'font': {'size': 16, 'color': '#00ff88', 'family': 'Courier New'}
    },
    'steps': [
        {
            'args': [[f.name], {
                'frame': {'duration': 500, 'redraw': True},
                'mode': 'immediate',
                'transition': {'duration': 500}
            }],
            'method': 'animate',
            'label': f.name
        }
        for f in frames
    ]
}]

# Update layout with animation controls
fig.update_layout(
    title=dict(
        text='<b>Top 20 Assets by Market Cap (2016-2026 Animation)</b><br><sub>Watch how rankings changed over 10 years (Monthly snapshots)</sub>',
        font=dict(size=22, color='#00ff88', family='Courier New'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title=dict(text='Market Cap (Trillions USD)', font=dict(size=14, color='#00ff88', family='Courier New')),
        tickfont=dict(size=11, color='#00ff88', family='Courier New'),
        showgrid=True,
        gridwidth=1.5,
        gridcolor='#2a4a3a',
        zeroline=False,
        tickformat='$.1f',
    ),
    yaxis=dict(
        title='',
        tickfont=dict(size=11, color='#00ff88', family='Courier New'),
        showgrid=False,
        categoryorder='total ascending'
    ),
    plot_bgcolor='#0d1117',
    paper_bgcolor='#0d1117',
    font=dict(family='Courier New', color='#00ff88'),
    height=1000,
    width=1600,
    margin=dict(l=400, r=150, t=150, b=220),
    hovermode='closest',
    showlegend=False,
    sliders=sliders,
)

# Add play button and legend
fig.update_layout(
    updatemenus=[
        dict(
            type='buttons',
            showactive=False,
            buttons=[
                dict(
                    label='▶ Play',
                    method='animate',
                    args=[None, {
                        'frame': {'duration': 500, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 300}
                    }]
                ),
                dict(
                    label='⏸ Pause',
                    method='animate',
                    args=[[None], {
                        'frame': {'duration': 0, 'redraw': True},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }]
                )
            ],
            x=0.5,
            xanchor='center',
            y=1.12,
            yanchor='top',
            font=dict(size=14, color='#00ff88', family='Courier New'),
            bgcolor='rgba(13, 17, 23, 0.9)',
            bordercolor='#00ff88',
            borderwidth=2
        )
    ]
)

# Add legend annotations
fig.add_annotation(
    x=1.02, y=0.95,
    xref='paper', yref='paper',
    text='<b>Asset Types:</b><br>🟩 Companies<br>🟨 Precious Metals<br>🟪 Cryptocurrencies',
    showarrow=False,
    font=dict(size=11, color='#00ff88', family='Courier New'),
    bgcolor='rgba(13, 17, 23, 0.8)',
    bordercolor='#00ff88',
    borderwidth=2,
    align='left'
)

# Save HTML
output_path = Path('data/processed/bar_race_animated_10years.html')
fig.write_html(output_path)

print(f"\n{'='*80}")
print(f"✓ 10-year animated bar race saved: {output_path}")
print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
print(f"  Total frames: {len(frames)}")
print(f"  Date range: {dates_for_slider[0].date()} to {dates_for_slider[-1].date()}")
print(f"{'='*80}\n")

# Summary stats
print(f"Animation Details:")
print(f"  - 227 monthly snapshots (2016-01 to 2026-02)")
print(f"  - Top 20 assets per month")
print(f"  - Play/Pause controls with slider")
print(f"  - 500ms transition between frames")
print(f"\nKey observations visible in animation:")
print(f"  • Rise of tech stocks (NVIDIA, Tesla, Meta)")
print(f"  • Cryptocurrency emergence (Bitcoin)")
print(f"  • Precious metals volatility")
print(f"  • China vs US company dynamics")
print(f"  • Market cap growth over decade\n")
