# -*- coding: utf-8 -*-
"""Quick test of preview generation"""

from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

# Setup paths
base_dir = Path(__file__).parent.parent
processed_dir = base_dir / "csv" / "processed"
media_dir = base_dir / "reports" / "media"
media_dir.mkdir(parents=True, exist_ok=True)

# Find data
csv_path = sorted(processed_dir.glob("population_top50_*.csv"))[-1]
df = pd.read_csv(csv_path)

# Create one test frame
year = 2024
year_data = df[df['year'] == year].nsmallest(10, 'rank')

fig = go.Figure()
fig.add_trace(go.Bar(
    x=year_data['population'],
    y=year_data['country_name'],
    orientation='h'
))

fig.update_layout(
    title=f"Population {year}",
    height=800,
    width=1200,
    template='plotly_dark'
)

# Save test frame
test_path = media_dir / "test_frame.png"
fig.write_image(str(test_path))
print(f"✓ Created test frame: {test_path}")
print(f"  File size: {test_path.stat().st_size / 1024:.1f} KB")
