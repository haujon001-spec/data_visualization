# -*- coding: utf-8 -*-
"""
Phase 2: Generate HTML Dashboard

Combines bubble map and population trendline into unified HTML dashboard.
Creates responsive layout with desktop (2-column) and mobile (1-column) views.

Output: reports/html/dashboard_<timestamp>.html
"""

import os
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class DashboardBuilder:
    """Builds unified HTML dashboard from visualization components."""
    
    def __init__(self, project_root: Path = None):
        """Initialize dashboard builder."""
        self.project_root = project_root or Path(__file__).parent.parent
    
    def find_latest_bubble_map(self) -> Path:
        """Find latest bubble map HTML file."""
        import glob
        
        pattern = str(self.project_root / 'reports' / 'html' / 'bubble_map_*.html')
        files = glob.glob(pattern)
        
        if not files:
            raise ValueError("No bubble_map HTML files found")
        
        latest = max(files, key=lambda p: Path(p).stat().st_mtime)
        logger.info(f"[FIND] Bubble map: {Path(latest).name}")
        
        return Path(latest)
    
    def find_latest_trendline(self) -> Path:
        """Find latest trendline visualization from Project 1 reuse."""
        import glob
        
        pattern = str(self.project_root / 'reports' / 'html' / '*trendline*.html')
        files = glob.glob(pattern)
        
        if not files:
            logger.warning("[FIND] No trendline visualization found (expected from Project 1 reuse)")
            return None
        
        latest = max(files, key=lambda p: Path(p).stat().st_mtime)
        logger.info(f"[FIND] Trendline: {Path(latest).name}")
        
        return Path(latest)
    
    def extract_figure_from_html(self, html_file: Path) -> tuple:
        """Use iframe embedding instead of complex regex extraction."""
        logger.info(f"[EXTRACT] Processing {html_file.name}...")
        
        if not html_file.exists():
            logger.error(f"[EXTRACT] File not found: {html_file}")
            return "", ""
        
        # Use iframe embedding - simpler and more reliable than regex extraction
        # This way the Plotly file is loaded independently in its own context
        iframe_html = f'<iframe src="{html_file.name}" style="width:100%;height:600px;border:none;margin:0;padding:0;"></iframe>'
        logger.info(f"[EXTRACT] Using iframe embed for {html_file.name}")
        
        # Return the iframe + empty script (no need for script when using iframe)
        return iframe_html, ""
    
    def build_dashboard_html(self, bubble_map_path: Path, trendline_path: Path = None) -> str:
        """Build complete dashboard HTML."""
        logger.info("[BUILD] Creating dashboard HTML...")
        
        # Extract figures
        bubble_div, bubble_script = self.extract_figure_from_html(bubble_map_path)
        
        trendline_div = ""
        trendline_script = ""
        
        if trendline_path:
            try:
                trendline_div, trendline_script = self.extract_figure_from_html(trendline_path)
            except Exception as e:
                logger.warning(f"[BUILD] Could not extract trendline: {str(e)}")
        
        # Build HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Economic Health Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
            color: #333;
        }}
        
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .dashboard-item {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: box-shadow 0.3s ease;
        }}
        
        .dashboard-item:hover {{
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}
        
        .dashboard-item h2 {{
            background-color: #34495e;
            color: white;
            padding: 15px 20px;
            font-size: 1.3em;
            margin: 0;
        }}
        
        .dashboard-item .plotly-graph-div {{
            width: 100% !important;
            height: 600px !important;
        }}
        
        .info-section {{
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .info-section h3 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        
        .info-section p {{
            line-height: 1.6;
            color: #555;
            margin-bottom: 10px;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #888;
            font-size: 0.9em;
        }}
        
        @media (max-width: 1200px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .dashboard-item .plotly-graph-div {{
                height: 500px !important;
            }}
        }}
        
        @media (max-width: 768px) {{
            .header {{
                padding: 20px 15px;
            }}
            
            .header h1 {{
                font-size: 1.7em;
            }}
            
            .container {{
                padding: 10px;
            }}
            
            .dashboard {{
                gap: 10px;
            }}
            
            .dashboard-item .plotly-graph-div {{
                height: 400px !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 Global Economic Health Dashboard</h1>
        <p>Interactive analysis of GDP, population, and debt relationships</p>
    </div>
    
    <div class="container">
        <div class="info-section">
            <h3>Dashboard Overview</h3>
            <p>
                This dashboard visualizes the relationships between national GDP, population, and debt levels.
                Use the year slider to see how these metrics have evolved over time.
            </p>
            <p>
                <strong>Bubble Map:</strong> Each bubble represents a country. Size indicates total GDP, color shows debt-to-GDP ratio (red = high debt burden, green = low).
            </p>
            <p>
                <strong>Trendline:</strong> Shows population trends with polynomial fit for selected countries.
            </p>
        </div>
        
        <div class="dashboard">
            <div class="dashboard-item">
                <h2>Economic Positioning</h2>
                {bubble_div}
            </div>
            {"<div class='dashboard-item'><h2>Population Trends</h2>" + trendline_div + "</div>" if trendline_div else ""}
        </div>
        
        <div class="info-section">
            <h3>Data Sources & Methodology</h3>
            <p>
                <strong>GDP:</strong> World Bank API (World Development Indicators)
            </p>
            <p>
                <strong>Population:</strong> World Bank API (World Development Indicators)
            </p>
            <p>
                <strong>External Debt:</strong> World Bank International Debt Statistics with IMF backup
            </p>
            <p>
                All figures in USD with annual data from 1960-2026.
            </p>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Global Economic Health Analytics v1.0</p>
    </div>
    
    <script type="text/javascript">
        {bubble_script}
    </script>
    
    {f'<script type="text/javascript">{trendline_script}</script>' if trendline_script else ''}
    
    <script>
        // Responsive layout adjustments
        window.addEventListener('resize', function() {{
            Plotly.Plots.resize('plot');
        }});
    </script>
</body>
</html>
        """
        
        return html_content
    
    def save_dashboard(self, html_content: str) -> Path:
        """Save dashboard to HTML file."""
        timestamp = datetime.now().strftime("%d%b%Y_%H%M%S").upper()
        output_dir = self.project_root / 'reports' / 'html'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f'dashboard_{timestamp}.html'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"[SAVE] Dashboard saved to {output_file.relative_to(self.project_root)}")
        logger.info(f"[SIZE] {output_file.stat().st_size / 1024:.1f} KB")
        
        return output_file


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent
    
    builder = DashboardBuilder(project_root)
    
    try:
        logger.info("=" * 70)
        logger.info("BUILDING DASHBOARD")
        logger.info("=" * 70)
        
        # Find visualization files
        bubble_map = builder.find_latest_bubble_map()
        logger.info(f"[LOAD] Bubble map size: {bubble_map.stat().st_size / 1024 / 1024:.2f} MB")
        
        trendline = builder.find_latest_trendline()
        if trendline:
            logger.info(f"[LOAD] Trendline size: {trendline.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Build dashboard
        logger.info("[BUILD] Extracting Plotly figures...")
        html_content = builder.build_dashboard_html(bubble_map, trendline)
        
        if not html_content:
            raise ValueError("Dashboard HTML content is empty")
        
        logger.info(f"[BUILD] Generated {len(html_content)} characters of HTML")
        
        output_path = builder.save_dashboard(html_content)
        
        logger.info("\n[SUCCESS] Dashboard generation complete")
        logger.info("=" * 70)
        return 0
    
    except Exception as e:
        logger.error(f"\n[ERROR] Dashboard generation failed")
        logger.error(f"[ERROR] {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
