"""
Generate Bar Race Visualization with Corrected Data
Uses currency-normalized companies + corrected metals + crypto
Includes company logos from CompaniesLogo API
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json

print("="*80)
print("GENERATING VISUALIZATION WITH CORRECTED DATA")
print("="*80)

# Load corrected top 20 data
df = pd.read_csv('data/processed/latest_top20_snapshot.csv')

print(f"\nData loaded: {len(df)} assets")
print(f"\nTop 10 assets:")
for idx, row in df.head(10).iterrows():
    cap_b = row['market_cap'] / 1e9
    cap_t = row['market_cap'] / 1e12
    if cap_t >= 1:
        print(f"  {int(row['rank'])}. {row['label']:<30} ${cap_t:.2f}T")
    else:
        print(f"  {int(row['rank'])}. {row['label']:<30} ${cap_b:.1f}B")

# Create sorting by market cap (largest to smallest for better bar race order)
df = df.sort_values('market_cap', ascending=False).reset_index(drop=True)

# Create the market cap visualization
fig = go.Figure()

# Define colors by asset type
colors = {
    'company': '#00ff88',  # Neon green
    'metal': '#ffaa00',    # Gold/orange
    'crypto': '#ff00ff',   # Magenta
}

# Add bars
fig.add_trace(go.Bar(
    x=df['market_cap'] / 1e12,  # Convert to trillions for better readability
    y=df['label'],
    orientation='h',
    marker=dict(
        color=[colors.get(asset_type, '#00d4ff') for asset_type in df['asset_type']],
        line=dict(color='#00ff88', width=2)
    ),
    text=[f"${cap/1e12:.2f}T" if cap >= 1e12 else f"${cap/1e9:.1f}B" for cap in df['market_cap']],
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Market Cap: %{x:.2f}T USD<extra></extra>'
))

# Update layout
fig.update_layout(
    title=dict(
        text='<b>Top 20 Assets by Market Cap</b><br><sub>Corrected Data: Companies (USD normalized) + Metals (accurate supplies) + Crypto</sub>',
        font=dict(size=24, color='#00ff88', family='Courier New'),
        x=0.5,
        xanchor='center'
    ),
    xaxis=dict(
        title=dict(text='Market Cap (Trillions USD)', font=dict(size=14, color='#00ff88', family='Courier New')),
        tickfont=dict(size=12, color='#00ff88', family='Courier New'),
        showgrid=True,
        gridwidth=2,
        gridcolor='#2a4a3a',
        zeroline=False,
        tickformat='$.2f',
        range=[0, df['market_cap'].max() / 1e12 * 1.1]
    ),
    yaxis=dict(
        title='',
        tickfont=dict(size=12, color='#00ff88', family='Courier New'),
        showgrid=False,
        categoryorder='total ascending'
    ),
    plot_bgcolor='#0d1117',
    paper_bgcolor='#0d1117',
    font=dict(family='Courier New', color='#00ff88'),
    height=900,
    width=1400,
    margin=dict(l=400, r=150, t=150, b=100),
    hovermode='closest',
    showlegend=False
)

# Add legend annotations
legend_y = 0.95
fig.add_annotation(
    x=1.02, y=legend_y,
    xref='paper', yref='paper',
    text='<b>Asset Types:</b><br>🟩 Companies<br>🟨 Precious Metals<br>🟪 Cryptocurrencies',
    showarrow=False,
    font=dict(size=11, color='#00ff88', family='Courier New'),
    bgcolor='rgba(13, 17, 23, 0.8)',
    bordercolor='#00ff88',
    borderwidth=2,
    align='left'
)

# Add data quality note
fig.add_annotation(
    x=0.0, y=-0.12,
    xref='paper', yref='paper',
    text='<b>Methodology:</b> Companies = Price × Shares (USD normalized with FX conversion) | Metals = Price/oz × Total Mined | Crypto = Price × Circulating Supply<br><b>Data Quality:</b> High confidence (Crypto) | Medium confidence (Companies, Metals) | Date: 2026-02-24',
    showarrow=False,
    font=dict(size=10, color='#58a6ff', family='Courier New'),
    align='left'
)

# Save HTML
output_path = Path('data/processed/bar_race_corrected.html')
fig.write_html(output_path)

print(f"\n{'='*80}")
print(f"✓ Visualization saved: {output_path}")
print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
print(f"{'='*80}\n")

# Also save data as JSON for validation
data_json = {
    'title': 'Top 20 Assets by Market Cap (Corrected)',
    'date': '2026-02-24',
    'methodology': {
        'companies': 'Price × Shares Outstanding (yfinance + currency normalization)',
        'metals': 'Price/oz × Total Mined (210M oz gold, 1.75B oz silver, etc)',
        'crypto': 'Price × Circulating Supply (CoinGecko)'
    },
    'assets': []
}

for idx, row in df.iterrows():
    data_json['assets'].append({
        'rank': int(row['rank']),
        'name': row['label'],
        'market_cap_usd': float(row['market_cap']),
        'market_cap_t': float(row['market_cap'] / 1e12),
        'type': row['asset_type'],
        'confidence': row['confidence']
    })

json_path = Path('data/processed/top20_corrected_data.json')
with open(json_path, 'w') as f:
    json.dump(data_json, f, indent=2)

print(f"✓ Data saved as JSON: {json_path}\n")
