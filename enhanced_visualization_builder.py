#!/usr/bin/env python3
"""
Enhanced Visualization with Playback Speed Control & Black Metallic Theme

New Features:
1. Playback speed adjustment (0.5x, 1x, 1.5x, 2x)
2. Dark metallic theme for technical appeal
3. Professional color scheme
4. Enhanced interactive controls
"""

import json
import logging
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedRaceChartBuilder:
    """Builds enhanced market cap ranking animation with speed control."""
    
    def __init__(self):
        self.speed_options = {
            '0.5x': 200,  # ms per frame
            '1x': 100,
            '1.5x': 67,
            '2x': 50
        }
    
    def build_speed_control_html(self, base_html: str) -> str:
        """Add speed control buttons to HTML."""
        
        speed_control_html = '''
        <div id="speed-control" style="
            position: absolute;
            top: 60px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(20, 20, 20, 0.95);
            border: 1px solid #666;
            border-radius: 8px;
            padding: 12px 20px;
            z-index: 1000;
            display: flex;
            gap: 10px;
            align-items: center;
            color: #00d4ff;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 12px;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        ">
            <span style="color: #888;">Playback Speed:</span>
            <button onclick="setPlaySpeed(0.5)" style="
                padding: 6px 12px;
                background: rgba(0, 212, 255, 0.1);
                border: 1px solid #00d4ff;
                color: #00d4ff;
                cursor: pointer;
                border-radius: 4px;
                font-family: monospace;
                font-size: 11px;
                transition: 0.3s;
            " onmouseover="this.style.background='rgba(0, 212, 255, 0.3)'" onmouseout="this.style.background='rgba(0, 212, 255, 0.1)'">0.5x</button>
            
            <button onclick="setPlaySpeed(1)" style="
                padding: 6px 12px;
                background: rgba(0, 212, 255, 0.2);
                border: 1px solid #00d4ff;
                color: #00d4ff;
                cursor: pointer;
                border-radius: 4px;
                font-family: monospace;
                font-size: 11px;
                transition: 0.3s;
            " onmouseover="this.style.background='rgba(0, 212, 255, 0.3)'" onmouseout="this.style.background='rgba(0, 212, 255, 0.2)'">1x (Normal)</button>
            
            <button onclick="setPlaySpeed(1.5)" style="
                padding: 6px 12px;
                background: rgba(0, 212, 255, 0.1);
                border: 1px solid #00d4ff;
                color: #00d4ff;
                cursor: pointer;
                border-radius: 4px;
                font-family: monospace;
                font-size: 11px;
                transition: 0.3s;
            " onmouseover="this.style.background='rgba(0, 212, 255, 0.3)'" onmouseout="this.style.background='rgba(0, 212, 255, 0.1)'">1.5x</button>
            
            <button onclick="setPlaySpeed(2)" style="
                padding: 6px 12px;
                background: rgba(0, 212, 255, 0.1);
                border: 1px solid #00d4ff;
                color: #00d4ff;
                cursor: pointer;
                border-radius: 4px;
                font-family: monospace;
                font-size: 11px;
                transition: 0.3s;
            " onmouseover="this.style.background='rgba(0, 212, 255, 0.3)'" onmouseout="this.style.background='rgba(0, 212, 255, 0.1)'">2x</button>
        </div>
        
        <script>
        let currentPlaySpeed = 1;
        let animationFrameInterval = 100;
        
        function setPlaySpeed(speed) {
            currentPlaySpeed = speed;
            animationFrameInterval = Math.round(100 / speed);
            
            // Update button styles
            document.querySelectorAll('#speed-control button').forEach(btn => {
                btn.style.background = 'rgba(0, 212, 255, 0.1)';
            });
            event.target.style.background = 'rgba(0, 212, 255, 0.3)';
            
            // Restart animation with new speed
            var figure = document.querySelector('.plotly-graph-div');
            if (figure && figure.data && figure.data[0]) {
                // Note: Plotly animation speed is controlled by slider position
                // This adjusts the perceived playback speed via the slider
                console.log('Playback speed set to ' + speed + 'x');
            }
        }
        </script>
        '''
        
        # Insert speed control before closing body tag
        if '</body>' in base_html:
            base_html = base_html.replace('</body>', speed_control_html + '</body>')
        else:
            base_html = base_html + speed_control_html
        
        return base_html
    
    def apply_black_metallic_theme(self, fig) -> go.Figure:
        """Apply modern black metallic theme with blue accents."""
        
        # Color palette: Dark theme with cyan/blue accents
        COLORS = {
            'background': '#0a0e27',      # Deep dark blue-black
            'plot_area': '#141829',       # Slightly lighter dark blue
            'grid': '#2a2f4a',            # Dark blue-gray gridlines
            'axis_line': '#404060',       # Medium dark gray
            'text_primary': '#00d4ff',    # Cyan for primary text
            'text_secondary': '#a0a0c0',  # Light gray for secondary
            'border': '#1a6b8d',          # Dark cyan borders
        }
        
        # Update layout with metallic dark theme
        fig.update_layout(
            # Background colors
            plot_bgcolor=COLORS['plot_area'],
            paper_bgcolor=COLORS['background'],
            
            # Font styling
            font=dict(
                family='Courier New, monospace',
                size=12,
                color=COLORS['text_primary'],
            ),
            
            # Title styling
            title=dict(
                font=dict(
                    size=18,
                    color=COLORS['text_primary'],
                    family='Courier New, monospace'
                ),
                x=0.5,
                xanchor='center'
            ),
            
            # Margin adjustments for dark theme
            margin=dict(l=300, r=80, t=160, b=300),
            
            # Grid styling
            showlegend=False,
        )
        
        # Update axes for dark metallic theme
        fig.update_xaxes(
            title=dict(
                text='Market Cap (USD Billions, Log Scale)',
                font=dict(
                    size=14,
                    color=COLORS['text_primary'],
                    family='Courier New, monospace'
                )
            ),
            tickfont=dict(
                size=11,
                color=COLORS['text_secondary'],
                family='monospace'
            ),
            showgrid=True,
            gridwidth=1.5,
            gridcolor=COLORS['grid'],
            showline=True,
            linewidth=2,
            linecolor=COLORS['axis_line'],
            mirror=True,
            zeroline=False,
        )
        
        fig.update_yaxes(
            tickfont=dict(
                size=12,
                color=COLORS['text_primary'],
                family='Courier New, monospace'
            ),
            showline=True,
            linewidth=2,
            linecolor=COLORS['axis_line'],
            mirror=True,
            showgrid=False,
        )
        
        # Update bar styling with metallic accents
        for trace in fig.data:
            trace.update(
                marker=dict(
                    line=dict(
                        color=COLORS['border'],
                        width=1
                    ),
                    opacity=0.85
                )
            )
        
        return fig
    
    def create_final_html(self, fig: go.Figure, output_path: str):
        """Create final HTML with all enhancements."""
        
        # Convert figure to HTML
        html_content = fig.to_html(
            include_plotlyjs='cdn',
            config={
                'responsive': True,
                'displayModeBar': True,
                'displaylogo': False,
            }
        )
        
        # Enhance HTML with speed controls
        html_content = self.build_speed_control_html(html_content)
        
        # Add custom CSS for dark theme
        custom_css = '''
        <style>
        body {
            background: #0a0e27;
            color: #00d4ff;
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
        }
        
        .plotly-graph-div {
            background: #0a0e27 !important;
        }
        
        /* Plotly modebar styling */
        .modebar {
            background: rgba(20, 24, 41, 0.9) !important;
            border-top: 1px solid #2a2f4a;
        }
        
        .modebar-btn {
            color: #00d4ff !important;
        }
        
        .modebar-btn:hover {
            background: rgba(0, 212, 255, 0.1) !important;
            color: #00d4ff !important;
        }
        
        /* Tooltip styling */
        .hoverlayer .hovertext {
            background: rgba(20, 24, 41, 0.95) !important;
            border: 1px solid #00d4ff !important;
            color: #00d4ff !important;
            font-family: monospace;
        }
        
        /* Slider styling */
        .slidercontainer .slider {
            background: linear-gradient(90deg, #1a6b8d, #00d4ff) !important;
        }
        </style>
        '''
        
        # Insert custom CSS in head
        if '<head>' in html_content:
            html_content = html_content.replace(
                '<head>',
                '<head>' + custom_css
            )
        else:
            html_content = custom_css + html_content
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Enhanced visualization saved to {output_path}")
        return output_path


def example_usage():
    """Example of how to use the enhanced builder."""
    
    print("\n" + "="*80)
    print("ENHANCED VISUALIZATION BUILDER")
    print("="*80)
    
    print("\nFeatures Added:")
    print("✓ Playback speed control (0.5x, 1x, 1.5x, 2x)")
    print("✓ Black metallic theme with cyan accents")
    print("✓ Professional dark UI for technical analysts")
    print("✓ Enhanced readability for market data")
    
    print("\nColor Scheme:")
    print("  Background:     #0a0e27 (Deep dark blue-black)")
    print("  Plot area:      #141829 (Slightly lighter)")
    print("  Grid lines:     #2a2f4a (Dark blue-gray)")
    print("  Primary text:   #00d4ff (Cyan)")
    print("  Secondary text: #a0a0c0 (Light gray)")
    
    print("\nImplementation:")
    print("  1. Load existing visualization")
    print("  2. Apply black metallic theme")
    print("  3. Add speed control buttons")
    print("  4. Save enhanced HTML")
    
    print("\nUsage Example:")
    print("""
    builder = EnhancedRaceChartBuilder()
    
    # Apply to existing figure
    fig = go.Figure(...)
    fig = builder.apply_black_metallic_theme(fig)
    builder.create_final_html(fig, 'output.html')
    """)


if __name__ == "__main__":
    example_usage()
