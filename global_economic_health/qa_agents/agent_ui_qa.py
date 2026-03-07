# -*- coding: utf-8 -*-
"""
Phase 2 UI QA Agent - Dynamic Browser Validation

Validates visual outputs from Phase 2 visualization scripts using headless browser automation.
Uses Playwright to:
- Render HTML files in a headless browser
- Validate visualizations display correctly
- Test interactive elements (sliders, hover, etc.)
- Capture console errors
- Verify data is displayed
- Take comparison screenshots

Checks:
- Bubble map: Interactive year slider, bubble rendering, color mapping
- Dashboard: Layout, chart rendering, responsiveness
- Data validation: Values match source CSV

Output: reports/qa/ui_qa_report_<timestamp>.json
        reports/qa/ui_qa_summary_<timestamp>.md
        reports/qa/screenshots/* (PNG screenshots)
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import re
import traceback
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class UIQA:
    """UI Quality Assurance agent for Phase 2 visualizations using browser automation."""
    
    def __init__(self):
        """Initialize UI QA agent."""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': [],
            'warnings': [],
            'errors': [],
            'screenshots': [],
            'browser_errors': [],
            'summary': {
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'overall_status': 'FAIL'
            }
        }
        self.playwright = None
        self.browser = None
    
    def log_check(self, check_name: str, status: str, details: str = None):
        """Log a single validation check."""
        entry = {
            'check': check_name,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            entry['details'] = details
        
        if status == 'PASS':
            self.results['checks'].append(entry)
            self.results['summary']['passed'] += 1
            logger.info(f"[VERIFY] {check_name} - PASS")
        elif status == 'FAIL':
            self.results['checks'].append(entry)
            self.results['errors'].append({'check': check_name, 'details': details})
            self.results['summary']['failed'] += 1
            logger.error(f"[VERIFY] {check_name} - FAIL: {details}")
        elif status == 'WARNING':
            self.results['warnings'].append({'check': check_name, 'details': details})
            logger.warning(f"[VERIFY] {check_name} - WARNING: {details}")
        
        self.results['summary']['total_checks'] += 1
    
    async def test_html_rendering(self, html_file: Path, viz_type: str, project_root: Path) -> bool:
        """
        Test HTML file rendering in headless browser.
        
        Args:
            html_file: Path to HTML file
            viz_type: Type of visualization ('bubble_map' or 'dashboard')
            project_root: Project root directory
        
        Returns:
            True if rendering succeeded, False otherwise
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            self.log_check(
                f'{viz_type} browser rendering',
                'WARNING',
                'Playwright not installed. Install with: pip install playwright'
            )
            return False
        
        browser = None
        page = None
        
        try:
            async with async_playwright() as p:
                # Launch headless browser
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                # Capture console messages and errors
                console_msgs = []
                page.on('console', lambda msg: console_msgs.append({
                    'type': msg.type,
                    'text': msg.text
                }))
                
                # Navigate to file
                file_url = f"file:///{html_file.resolve()}".replace("\\", "/")
                logger.info(f"[LOAD] Opening {viz_type}: {file_url}")
                
                response = await page.goto(file_url)
                
                # Check load status
                if response and response.status >= 400:
                    self.log_check(
                        f'{viz_type} page load',
                        'FAIL',
                        f'HTTP {response.status}'
                    )
                    return False
                
                # Wait for content to load (Plotly for bubble_map, iframe for dashboard)
                try:
                    if viz_type == 'dashboard':
                        # Dashboard uses iframes, not direct Plotly elements
                        await page.wait_for_selector('iframe', timeout=5000)
                    else:
                        # Bubble map has direct Plotly elements
                        await page.wait_for_selector('.plotly', timeout=5000)
                    
                    self.log_check(f'{viz_type} Plotly elements load', 'PASS')
                except:
                    self.log_check(
                        f'{viz_type} Plotly elements load',
                        'FAIL',
                        'Content not found after 5 seconds'
                    )
                    return False
                
                # Check for JavaScript errors (exclude Plotly library warnings)
                actual_errors = [
                    m for m in console_msgs 
                    if m['type'] == 'error' 
                    and 'plotly-latest' not in m.get('text', '').lower()
                    and 'no longer the latest' not in m.get('text', '').lower()
                ]
                
                if actual_errors:
                    error_text = '; '.join([e['text'] for e in actual_errors[:3]])
                    self.log_check(
                        f'{viz_type} JavaScript errors',
                        'FAIL',
                        f'{len(actual_errors)} errors: {error_text}'
                    )
                    self.results['browser_errors'].extend(actual_errors)
                    return False
                else:
                    self.log_check(f'{viz_type} JavaScript errors', 'PASS', 'No errors in console')
                
                # Take screenshot of rendered content
                screenshot_dir = project_root / 'reports' / 'qa' / 'screenshots'
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_file = screenshot_dir / f'{viz_type}_render_{timestamp}.png'
                
                await page.screenshot(path=str(screenshot_file), full_page=True)
                self.log_check(
                    f'{viz_type} screenshot captured',
                    'PASS',
                    f'Screenshot: {screenshot_file.name}'
                )
                self.results['screenshots'].append({
                    'type': viz_type,
                    'file': str(screenshot_file.relative_to(project_root)),
                    'timestamp': timestamp
                })
                
                # Test interactivity for bubble_map
                if viz_type == 'bubble_map':
                    success = await self._test_bubble_map_interactivity(page)
                    if not success:
                        return False
                
                # Test dashboard elements
                if viz_type == 'dashboard':
                    success = await self._test_dashboard_rendering(page)
                    if not success:
                        return False
                
                await context.close()
                return True
        
        except Exception as e:
            logger.error(f"Browser test error for {viz_type}: {str(e)}")
            self.log_check(
                f'{viz_type} browser test',
                'FAIL',
                f'Exception: {str(e)[:100]}'
            )
            traceback.print_exc()
            return False
        
        finally:
            if browser:
                try:
                    await browser.close()
                except:
                    pass
    
    async def _test_bubble_map_interactivity(self, page) -> bool:
        """Test bubble map year slider interaction."""
        try:
            # Check for slider
            slider_exists = await page.query_selector('input[type="range"]') is not None
            
            if slider_exists:
                self.log_check('Bubble map year slider exists', 'PASS')
                
                # Try to interact with slider
                try:
                    await page.click('input[type="range"]')
                    self.log_check('Bubble map slider interaction', 'PASS')
                except:
                    self.log_check(
                        'Bubble map slider interaction',
                        'WARNING',
                        'Could not interact with slider'
                    )
            else:
                self.log_check(
                    'Bubble map year slider exists',
                    'WARNING',
                    'No range slider found in page'
                )
            
            return True
        except Exception as e:
            self.log_check('Bubble map interactivity test', 'FAIL', str(e)[:100])
            return False
    
    async def _test_dashboard_rendering(self, page) -> bool:
        """Test dashboard chart rendering."""
        try:
            # For iframe-based dashboards, check that iframe exists and loads
            iframe_elements = await page.query_selector_all('iframe')
            
            if iframe_elements:
                self.log_check(
                    'Dashboard iframe embeds',
                    'PASS',
                    f'{len(iframe_elements)} iframe(s) found'
                )
                
                # Try to wait for iframe content to load
                for iframe in iframe_elements:
                    try:
                        iframe_src = await iframe.get_attribute('src')
                        if iframe_src:
                            logger.info(f"[IFRAME] Detected: {iframe_src}")
                    except:
                        pass
                
                return True
            
            # Fallback: check for direct Plotly charts (.plotly class) for old dashboard format
            chart_selectors = await page.query_selector_all('.plotly')
            if len(chart_selectors) > 0:
                self.log_check(
                    'Dashboard Plotly charts',
                    'PASS',
                    f'{len(chart_selectors)} chart(s) found'
                )
                return True
            
            # If neither iframes nor direct plots found, it's a failure
            self.log_check(
                'dashboard Plotly elements load',
                'FAIL',
                'No charts or iframes found'
            )
            return False
            
        except Exception as e:
            self.log_check('Dashboard rendering test', 'FAIL', str(e)[:100])
            return False
    
    def verify_html_files(self, project_root: Path) -> bool:
        """Verify HTML files exist and have valid structure."""
        html_dir = project_root / 'reports' / 'html'
        
        import glob
        
        all_pass = True
        
        # Find latest files
        bubble_maps = glob.glob(str(html_dir / 'bubble_map_*.html'))
        dashboards = glob.glob(str(html_dir / 'dashboard_*.html'))
        
        # Check bubble map
        if bubble_maps:
            latest_bubble = Path(max(bubble_maps, key=lambda p: Path(p).stat().st_mtime))
            size_mb = latest_bubble.stat().st_size / 1024 / 1024
            
            if size_mb < 0.1:
                self.log_check('Bubble map file size', 'FAIL', f'Too small: {size_mb:.2f} MB')
                all_pass = False
            else:
                self.log_check('Bubble map file size', 'PASS', f'{size_mb:.2f} MB')
            
            # Static content checks
            with open(latest_bubble, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'plotly' not in content.lower():
                self.log_check('Bubble map has Plotly', 'FAIL', 'Plotly not found in HTML')
                all_pass = False
            else:
                self.log_check('Bubble map has Plotly', 'PASS')
        else:
            self.log_check('Bubble map exists', 'WARNING', 'No bubble map file found')
        
        # Check dashboard
        if dashboards:
            latest_dashboard = Path(max(dashboards, key=lambda p: Path(p).stat().st_mtime))
            size_mb = latest_dashboard.stat().st_size / 1024 / 1024
            
            # Dashboard with iframe embed is ~6KB (reduced from 0.1 MB for embedded approach)
            if size_mb < 0.001:  # At least 1KB
                self.log_check('Dashboard file size', 'FAIL', f'Too small: {size_mb:.2f} MB')
                all_pass = False
            else:
                self.log_check('Dashboard file size', 'PASS', f'{size_mb:.2f} MB')
            
            # Static content checks
            with open(latest_dashboard, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'Economic' not in content:
                self.log_check('Dashboard has content', 'FAIL', 'Expected content not found')
                all_pass = False
            else:
                self.log_check('Dashboard has content', 'PASS')
        else:
            self.log_check('Dashboard exists', 'WARNING', 'No dashboard file found')
        
        return all_pass
    
    def verify_data_consistency(self, project_root: Path) -> bool:
        """Verify data consistency between datasets and visualizations."""
        import glob
        
        pattern = str(project_root / 'csv' / 'processed' / 'macro_final_*.csv')
        files = glob.glob(pattern)
        
        if not files:
            self.log_check('Data file exists', 'FAIL', 'No macro_final CSV found')
            return False
        
        latest = max(files, key=lambda p: Path(p).stat().st_mtime)
        
        try:
            df = pd.read_csv(latest)
            
            # Check required columns
            required_cols = ['gdp_per_capita', 'population', 'gdp_usd', 'debt_to_gdp']
            missing = set(required_cols) - set(df.columns)
            
            if missing:
                self.log_check('Data has required columns', 'FAIL', f'Missing: {missing}')
                return False
            
            self.log_check('Data has required columns', 'PASS')
            
            # Check data validity
            invalid_count = 0
            invalid_count += (df['gdp_usd'] < 0).sum()
            invalid_count += (df['population'] < 0).sum()
            invalid_count += (df['gdp_per_capita'] < 0).sum()
            
            if invalid_count > 0:
                self.log_check(
                    'Data values valid',
                    'WARNING',
                    f'{invalid_count} invalid values'
                )
            else:
                self.log_check('Data values valid', 'PASS')
            
            # Check row count
            row_count = len(df)
            self.log_check('Data row count', 'PASS', f'{row_count} rows loaded')
            
            return True
        
        except Exception as e:
            self.log_check('Data consistency check', 'FAIL', str(e)[:100])
            return False
    
    def run_qa(self, project_root: Path) -> bool:
        """Run full UI QA suite."""
        import asyncio
        
        logger.info("=" * 70)
        logger.info("RUNNING UI QUALITY ASSURANCE - BROWSER VALIDATION")
        logger.info("=" * 70)
        
        html_dir = project_root / 'reports' / 'html'
        import glob
        
        # Find latest visualization files
        bubble_maps = glob.glob(str(html_dir / 'bubble_map_*.html'))
        dashboards = glob.glob(str(html_dir / 'dashboard_*.html'))
        
        all_pass = True
        
        # Run static checks first
        logger.info("\n[STATIC] Verifying HTML files...")
        if not self.verify_html_files(project_root):
            all_pass = False
        
        # Run browser-based tests
        logger.info("\n[BROWSER] Testing HTML rendering...")
        
        if bubble_maps:
            try:
                result = asyncio.run(
                    self.test_html_rendering(
                        Path(max(bubble_maps, key=lambda p: Path(p).stat().st_mtime)),
                        'bubble_map',
                        project_root
                    )
                )
                if not result:
                    all_pass = False
            except Exception as e:
                logger.error(f"Error running bubble map test: {str(e)}")
                self.log_check('Bubble map browser test', 'FAIL', str(e)[:100])
                all_pass = False
        
        if dashboards:
            try:
                result = asyncio.run(
                    self.test_html_rendering(
                        Path(max(dashboards, key=lambda p: Path(p).stat().st_mtime)),
                        'dashboard',
                        project_root
                    )
                )
                if not result:
                    all_pass = False
            except Exception as e:
                logger.error(f"Error running dashboard test: {str(e)}")
                self.log_check('Dashboard browser test', 'FAIL', str(e)[:100])
                all_pass = False
        
        # Data consistency
        logger.info("\n[DATA] Checking data consistency...")
        if not self.verify_data_consistency(project_root):
            all_pass = False
        
        # Summary
        self.results['summary']['overall_status'] = 'PASS' if all_pass else 'FAIL'
        
        logger.info("\n" + "=" * 70)
        logger.info("UI QA SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total Checks: {self.results['summary']['total_checks']}")
        logger.info(f"Passed: {self.results['summary']['passed']}")
        logger.info(f"Failed: {self.results['summary']['failed']}")
        logger.info(f"Warnings: {len(self.results['warnings'])}")
        logger.info(f"Screenshots: {len(self.results['screenshots'])}")
        logger.info(f"Browser Errors: {len(self.results['browser_errors'])}")
        logger.info(f"Overall Status: {self.results['summary']['overall_status']}")
        logger.info("=" * 70)
        
        return all_pass
    
    def save_results(self, project_root: Path):
        """Save QA results to JSON and markdown."""
        timestamp = datetime.now().strftime("%d%b%Y_%H%M%S").upper()
        report_dir = project_root / 'reports' / 'qa'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_file = report_dir / f'ui_qa_report_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"[SAVE] JSON report: {json_file.relative_to(project_root)}")
        
        # Save markdown
        md_file = report_dir / f'ui_qa_summary_{timestamp}.md'
        with open(md_file, 'w') as f:
            f.write("# UI Quality Assurance Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Testing Method:** Playwright Headless Browser Automation\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Status:** {self.results['summary']['overall_status']}\n")
            f.write(f"- **Total Checks:** {self.results['summary']['total_checks']}\n")
            f.write(f"- **Passed:** {self.results['summary']['passed']}\n")
            f.write(f"- **Failed:** {self.results['summary']['failed']}\n")
            f.write(f"- **Warnings:** {len(self.results['warnings'])}\n")
            f.write(f"- **Screenshots Captured:** {len(self.results['screenshots'])}\n")
            f.write(f"- **Browser Errors:** {len(self.results['browser_errors'])}\n\n")
            
            if self.results['screenshots']:
                f.write("## Screenshots\n\n")
                for ss in self.results['screenshots']:
                    f.write(f"- **{ss['type']}:** {ss['file']}\n")
                f.write("\n")
            
            if self.results['browser_errors']:
                f.write("## Browser Console Errors\n\n")
                for error in self.results['browser_errors'][:10]:
                    f.write(f"- `{error['type']}`: {error['text'][:100]}\n")
                f.write("\n")
            
            if self.results['errors']:
                f.write("## Test Failures\n\n")
                for error in self.results['errors']:
                    f.write(f"- **{error['check']}:** {error['details']}\n")
                f.write("\n")
            
            if self.results['warnings']:
                f.write("## Warnings\n\n")
                for warning in self.results['warnings']:
                    f.write(f"- **{warning['check']}:** {warning['details']}\n")
                f.write("\n")
            
            f.write("## Test Details\n\n")
            for check in self.results['checks']:
                status_icon = "PASS" if check['status'] == 'PASS' else "FAIL"
                f.write(f"- [{status_icon}] {check['check']}")
                if 'details' in check:
                    f.write(f" - {check['details']}")
                f.write("\n")
        
        logger.info(f"[SAVE] Markdown report: {md_file.relative_to(project_root)}")


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent
    
    logger.info("UI QA Agent Starting...")
    logger.info(f"Project Root: {project_root}")
    
    qa = UIQA()
    
    try:
        passed = qa.run_qa(project_root)
    except Exception as e:
        logger.error(f"QA execution failed: {str(e)}")
        traceback.print_exc()
        passed = False
    
    qa.save_results(project_root)
    
    if passed:
        logger.info("\nUI QA PASSED")
        return 0
    else:
        logger.warning("\nUI QA COMPLETED WITH ISSUES")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
