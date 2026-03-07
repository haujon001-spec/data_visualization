#!/usr/bin/env python3
"""
HTML Visualization Validator - Checks if HTML chart displays proper data
"""

import re
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HTMLVisualizationValidator:
    """Validates HTML visualization for data completeness"""
    
    def __init__(self, html_file: str = None):
        self.workspace = Path('c:\\Users\\haujo\\projects\\DEV\\Data_visualization')
        self.html_file = Path(html_file) if html_file else self.workspace / 'data' / 'processed' / 'bar_race_top20.html'
        self.issues = []
        self.warnings = []
    
    def load_html(self) -> str:
        """Load HTML file"""
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"✗ HTML file not found: {self.html_file}")
            sys.exit(1)
    
    def extract_plotly_data(self, html: str) -> dict:
        """Extract Plotly data/layout from HTML"""
        logger.info("\n" + "="*80)
        logger.info("EXTRACTING PLOTLY DATA")
        logger.info("="*80)
        
        try:
            # Look for Plotly.newPlot call
            match = re.search(r'Plotly\.newPlot\(["\']([^"\']+)["\'],\s*(\[.*?\]),\s*(\{.*?\})\s*[,)]', html, re.DOTALL)
            
            if not match:
                logger.warning("⚠️  Could not find Plotly.newPlot call")
                return {}
            
            div_id = match.group(1)
            data_str = match.group(2)
            layout_str = match.group(3)
            
            logger.info(f"✓ Found Plotly.newPlot for div: {div_id}")
            
            try:
                # Try to parse as JSON (may fail due to JavaScript notation)
                data = json.loads(data_str)
                logger.info(f"✓ Parsed trace data: {len(data)} traces")
                
                layout = json.loads(layout_str)
                logger.info(f"✓ Parsed layout configuration")
                
                return {
                    'data': data,
                    'layout': layout,
                    'div_id': div_id
                }
            except json.JSONDecodeError:
                logger.warning("⚠️  Could not parse Plotly JSON (may use JavaScript notation)")
                return {'raw': (data_str[:200], layout_str[:200])}
            
        except Exception as e:
            logger.error(f"✗ Error extracting Plotly data: {e}")
            return {}
    
    def validate_trace_data(self, html: str) -> bool:
        """Validate that trace data contains proper bar information"""
        logger.info("\n" + "="*80)
        logger.info("TRACE DATA VALIDATION")
        logger.info("="*80)
        
        has_names = 'name' in html
        has_values = 'y' in html or 'x' in html
        has_labels = 'label' in html or 'text' in html
        
        logger.info(f"✓ Contains 'name' fields: {has_names}")
        logger.info(f"✓ Contains data values (x/y): {has_values}")
        logger.info(f"✓ Contains labels/text: {has_labels}")
        
        if not (has_names and has_values):
            self.issues.append("Missing critical trace data (name and values)")
            logger.error("✗ Missing trace data")
            return False
        
        # Count unique assets mentioned
        asset_names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
        if asset_names:
            unique_assets = set(asset_names)
            logger.info(f"\nUnique assets in traces: {len(unique_assets)}")
            logger.info(f"  {sorted(unique_assets)[:10]}")  # Show first 10
            
            if len(unique_assets) < 5:
                self.issues.append(f"Only {len(unique_assets)} unique assets (expected 20+)")
                logger.error(f"✗ Too few unique assets: {len(unique_assets)}")
                return False
            else:
                logger.info(f"✓ Good asset diversity: {len(unique_assets)} assets")
                return True
        
        return True
    
    def validate_animation_frames(self, html: str) -> bool:
        """Check if animation frames exist"""
        logger.info("\n" + "="*80)
        logger.info("ANIMATION FRAMES VALIDATION")
        logger.info("="*80)
        
        # Look for frames array
        if '"frames"' in html or "'frames'" in html:
            logger.info("✓ Animation frames array found")
            
            # Count frames
            frame_matches = re.findall(r'"name"\s*:\s*"(\d{4}-\d{2}-\d{2})"', html)
            if frame_matches:
                unique_frames = set(frame_matches)
                logger.info(f"✓ Extracted {len(unique_frames)} unique date frames")
                
                if len(unique_frames) > 100:
                    logger.info(f"✓ Good frame count: {len(unique_frames)} frames")
                    return True
                else:
                    self.warnings.append(f"Low frame count: {len(unique_frames)} (expected 100+)")
                    logger.warning(f"⚠️  Only {len(unique_frames)} frames")
                    return False
            else:
                self.warnings.append("Could not extract frame dates")
                logger.warning("⚠️  Could not extract frame metadata")
                return False
        else:
            self.warnings.append("No animation frames detected")
            logger.warning("⚠️  No animation frames found in HTML")
            return False
    
    def validate_layout_config(self, html: str) -> bool:
        """Check if layout has proper configuration"""
        logger.info("\n" + "="*80)
        logger.info("LAYOUT CONFIGURATION VALIDATION")
        logger.info("="*80)
        
        checks = {
            'title': '"title"' in html,
            'xaxis': '"xaxis"' in html,
            'yaxis': '"yaxis"' in html,
            'updatemenus': '"updatemenus"' in html,  # Play button controls
            'sliders': '"sliders"' in html,  # Date slider
        }
        
        passed = 0
        for name, found in checks.items():
            symbol = "✓" if found else "✗"
            logger.info(f"{symbol} {name}: {'Found' if found else 'Missing'}")
            if found:
                passed += 1
        
        logger.info(f"\n✓ Configuration completeness: {passed}/{len(checks)}")
        
        if passed < 3:
            self.issues.append(f"Missing layout configuration ({passed}/{len(checks)})")
            logger.error("✗ Incomplete layout configuration")
            return False
        
        return True
    
    def validate_file_integrity(self, html: str) -> bool:
        """Check HTML file integrity"""
        logger.info("\n" + "="*80)
        logger.info("FILE INTEGRITY CHECK")
        logger.info("="*80)
        
        checks = {
            'DOCTYPE': html.strip().startswith('<!DOCTYPE'),
            '<html>': '<html' in html.lower(),
            '<head>': '<head>' in html.lower(),
            '<body>': '<body>' in html.lower(),
            'closing tags': html.rstrip().endswith('</html>'),
            'Plotly library': 'plotly' in html.lower(),
        }
        
        passed = 0
        for name, found in checks.items():
            symbol = "✓" if found else "✗"
            logger.info(f"{symbol} {name}: {'OK' if found else 'Missing'}")
            if found:
                passed += 1
        
        if passed < 5:
            self.issues.append(f"File integrity issues ({passed}/{len(checks)})")
            return False
        
        return True
    
    def generate_report(self) -> dict:
        """Generate validation report"""
        logger.info("\n" + "="*80)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*80)
        
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        if total_issues > 0:
            logger.error(f"\n❌ ISSUES FOUND ({total_issues}):")
            for issue in self.issues:
                logger.error(f"   - {issue}")
        
        if total_warnings > 0:
            logger.warning(f"\n⚠️  WARNINGS ({total_warnings}):")
            for warning in self.warnings:
                logger.warning(f"   - {warning}")
        
        if total_issues == 0:
            logger.info("\n✅ VALIDATION PASSED")
        else:
            logger.error("\n❌ VALIDATION FAILED")
        
        return {
            'file': str(self.html_file),
            'issues': total_issues,
            'warnings': total_warnings,
            'issue_list': self.issues,
            'warning_list': self.warnings,
            'status': 'PASSED' if total_issues == 0 else 'FAILED'
        }
    
    def validate(self) -> dict:
        """Run complete validation"""
        logger.info("\n" + "="*80)
        logger.info("HTML VISUALIZATION VALIDATOR")
        logger.info("="*80)
        
        html = self.load_html()
        
        logger.info(f"✓ Loaded HTML file: {self.html_file.name}")
        logger.info(f"  Size: {len(html)/1e6:.2f} MB")
        
        # Run all validation checks
        self.validate_file_integrity(html)
        self.validate_layout_config(html)
        self.validate_trace_data(html)
        self.validate_animation_frames(html)
        
        # Generate report
        report = self.generate_report()
        
        return report


if __name__ == '__main__':
    validator = HTMLVisualizationValidator()
    report = validator.validate()
    
    sys.exit(0 if report['status'] == 'PASSED' else 1)
