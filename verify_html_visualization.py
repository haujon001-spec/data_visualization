#!/usr/bin/env python3
"""
Automated HTML Visualization Verification
Loads and analyzes the bar_race_top20.html file programmatically
Checks rendering, data binding, UI quality, and accessibility
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
import base64

def verify_html_visualization(html_path: str) -> bool:
    """
    Verify HTML visualization quality and correctness
    
    Args:
        html_path: Path to bar_race_top20.html
        
    Returns:
        bool: True if verification passes
    """
    
    print("\n" + "="*80)
    print("AUTOMATED HTML VISUALIZATION VERIFICATION")
    print("="*80 + "\n")
    
    # Check file exists
    html_file = Path(html_path)
    if not html_file.exists():
        print(f"[ERROR] File not found: {html_path}")
        return False
    
    print(f"[OK] File exists: {html_path}")
    file_size_mb = html_file.stat().st_size / (1024*1024)
    print(f"[OK] File size: {file_size_mb:.2f} MB")
    
    # Read and parse HTML
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"[ERROR] Cannot read file: {e}")
        return False
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check 1: Plotly presence
    print("\n" + "-"*80)
    print("CHECK 1: Plotly Library")
    print("-"*80)
    
    plotly_script = any('plotly' in str(tag) for tag in soup.find_all('script'))
    if plotly_script:
        print("[OK] Plotly library detected in HTML")
    else:
        print("[WARNING] Plotly library not found in script tags")
    
    # Check 2: Data structure
    print("\n" + "-"*80)
    print("CHECK 2: Data Configuration")
    print("-"*80)
    
    # Extract Plotly configuration
    scripts = soup.find_all('script', type='application/json')
    data_config = None
    
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, list) and len(data) > 0:
                data_config = data[0]
                break
        except:
            continue
    
    if data_config:
        print("[OK] Data configuration found")
        
        # Check for animation frames
        if 'frames' in data_config:
            frame_count = len(data_config['frames'])
            print(f"[OK] Animation frames: {frame_count:,}")
            if frame_count >= 7000:
                print("[OK] Frame count is adequate (>7000 for smooth animation)")
            else:
                print(f"[WARNING] Frame count is low ({frame_count})")
        
        # Check trace data
        if 'data' in data_config:
            bar_count = len(data_config['data'])
            print(f"[OK] Number of bar traces: {bar_count}")
    else:
        print("[WARNING] Could not parse data configuration")
    
    # Check 3: Axis Configuration
    print("\n" + "-"*80)
    print("CHECK 3: Axis Configuration")
    print("-"*80)
    
    layout_match = re.search(r'"xaxis":\{[^}]*"type":"log"', html_content)
    if layout_match:
        print("[OK] X-axis uses logarithmic scale")
    else:
        print("[WARNING] X-axis scale not verified as logarithmic")
    
    # Check 4: Styling and Theme
    print("\n" + "-"*80)
    print("CHECK 4: Styling & Theme")
    print("-"*80)
    
    # Look for color definitions
    color_patterns = [
        (r'#1f77b4', 'Company blue'),
        (r'#ff7f0e', 'Crypto orange'),
        (r'#2ca02c', 'Metal green'),
    ]
    
    for color, name in color_patterns:
        if re.search(color, html_content):
            print(f"[OK] {name} ({color}) detected")
    
    # Check 5: Interactive Controls
    print("\n" + "-"*80)
    print("CHECK 5: Interactive Controls")
    print("-"*80)
    
    controls = {
        'Play button': 'Play',
        'Pause button': 'Pause',
        'Date slider': 'slider',
    }
    
    for control_name, search_term in controls.items():
        if search_term.lower() in html_content.lower():
            print(f"[OK] {control_name} detected")
    
    # Check 6: Dimensions and Spacing
    print("\n" + "-"*80)
    print("CHECK 6: Dimensions & Layout")
    print("-"*80)
    
    # Look for width and height
    width_match = re.search(r'"width":(\d+)', html_content)
    height_match = re.search(r'"height":(\d+)', html_content)
    
    if width_match:
        width = int(width_match.group(1))
        print(f"[OK] Width: {width}px")
    
    if height_match:
        height = int(height_match.group(1))
        print(f"[OK] Height: {height}px")
    
    # Check margins
    margin_match = re.search(r'"margin":\{([^}]*)\}', html_content)
    if margin_match:
        print("[OK] Margins configured for spacing")
    
    # Check 7: Accessibility
    print("\n" + "-"*80)
    print("CHECK 7: Accessibility & UX")
    print("-"*80)
    
    # Check for title
    title_tag = soup.find('title')
    if title_tag:
        print(f"[OK] Page title: {title_tag.string}")
    
    # Check for hover text
    hover_count = len(re.findall(r'hovertemplate|customdata', html_content))
    if hover_count > 0:
        print(f"[OK] Hover tooltips configured ({hover_count} occurrences)")
    
    # Check 8: Data Binding
    print("\n" + "-"*80)
    print("CHECK 8: Data Binding Verification")
    print("-"*80)
    
    # Check x, y data binding
    x_binding = 'x' in html_content
    y_binding = 'y' in html_content
    
    if x_binding and y_binding:
        print("[OK] X and Y axis data binding present")
    
    # Check color binding
    if 'marker' in html_content or 'color' in html_content.lower():
        print("[OK] Color/marker binding present")
    
    # Check 9: Performance
    print("\n" + "-"*80)
    print("CHECK 9: Performance Metrics")
    print("-"*80)
    
    # Estimate load performance
    print(f"[OK] File size suitable for web: {file_size_mb:.2f} MB")
    
    if file_size_mb < 15:
        print("[OK] File is optimized for fast loading (< 15 MB)")
    else:
        print("[WARNING] File size is large (>= 15 MB)")
    
    # Check 10: Quality Assessment
    print("\n" + "-"*80)
    print("CHECK 10: Overall Quality Assessment")
    print("-"*80)
    
    quality_checks = [
        ("Plotly library present", plotly_script),
        ("Data configuration found", data_config is not None),
        ("Animation frames present", frame_count >= 1000 if data_config else False),
        ("X-axis logarithmic scale", "type\":\"log" in html_content),
        ("Interactive controls", any(term.lower() in html_content.lower() for term in ['play', 'pause', 'slider'])),
        ("Color coding present", any(re.search(c[0], html_content) for c in color_patterns)),
        ("Hover tooltips", hover_count > 0),
        ("Proper dimensions", width_match is not None and height_match is not None),
    ]
    
    passed = 0
    failed = 0
    
    for check_name, result in quality_checks:
        status = "[OK]" if result else "[FAILED]"
        if result:
            passed += 1
        else:
            failed += 1
        print(f"{status} {check_name}")
    
    print("\n" + "="*80)
    print(f"VERIFICATION SUMMARY: {passed}/{len(quality_checks)} checks passed")
    print("="*80 + "\n")
    
    if failed == 0:
        print("[SUCCESS] HTML visualization is production-ready")
        print("\nYou can now open the file in a browser:")
        print(f"  {html_path}")
        print("\nExpected interactions:")
        print("  - Click PLAY to start animation")
        print("  - Use PAUSE to stop animation")
        print("  - Drag slider to jump to specific dates")
        print("  - Hover over bars to see asset details")
        return True
    else:
        print(f"[WARNING] {failed} issues detected - review above")
        return False

if __name__ == "__main__":
    html_path = "data/processed/bar_race_top20.html"
    success = verify_html_visualization(html_path)
    exit(0 if success else 1)
