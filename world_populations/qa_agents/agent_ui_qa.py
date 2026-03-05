# -*- coding: utf-8 -*-
"""
Phase 3 - UI QA Agent
Validate HTML visualization for visual correctness and usability.
"""

from pathlib import Path
from datetime import datetime
import json
import re
from typing import Dict, List


def validate_html_exists(html_path: Path) -> dict:
    """
    Validate that HTML file exists and has content.
    
    Args:
        html_path: Path to HTML file
    
    Returns:
        Validation result dict
    """
    exists = html_path.exists()
    size = html_path.stat().st_size if exists else 0
    
    result = {
        "passed": exists and size > 0,
        "file_path": str(html_path),
        "exists": exists,
        "file_size": size,
        "issues": []
    }
    
    if not exists:
        result["issues"].append("HTML file does not exist")
    elif size == 0:
        result["issues"].append("HTML file is empty")
    
    status = "PASS" if result["passed"] else "FAIL"
    print(f"[VALIDATION] HTML file existence: {status}")
    
    return result


def validate_flag_urls(html_content: str) -> dict:
    """
    Validate that flag URLs are present in HTML.
    Note: Flags are optional but recommended for enhanced visualization.
    
    Args:
        html_content: HTML file content as string
    
    Returns:
        Validation result dict
    """
    # Look for flagcdn.com URLs
    flag_pattern = r'https://flagcdn\.com/[a-z]{2}\.svg'
    flag_urls = re.findall(flag_pattern, html_content)
    
    # Flags are optional - warn if missing but don't fail
    has_flags = len(flag_urls) > 0
    
    result = {
        "passed": True,  # Always pass, flags are optional
        "flag_urls_found": len(flag_urls),
        "unique_flags": len(set(flag_urls)),
        "flags_enabled": has_flags,
        "issues": []
    }
    
    if not has_flags:
        result["issues"].append("INFO: No flag URLs found (flags are optional but recommended)")
    elif len(set(flag_urls)) < 30:
        result["issues"].append(f"INFO: Only {len(set(flag_urls))} unique flags found")
    
    status = "PASS" if result["passed"] else "FAIL"
    print(f"[VALIDATION] Flag URLs: {status} ({'with flags' if has_flags else 'without flags - optional'})")
    
    return result


def validate_number_formatting(html_content: str) -> dict:
    """
    Validate that SI number formatting (1M, 1B) is used via Plotly config.
    
    Args:
        html_content: HTML file content as string
    
    Returns:
        Validation result dict
    """
    # Check for Plotly's SI formatting directive
    has_si_format = 'tickformat":"~s"' in html_content or "tickformat:'~s'" in html_content
    
    # Also check for explicit M/B values in text
    has_m_suffix = re.search(r'\d+(\.\d+)?M', html_content) is not None
    has_b_suffix = re.search(r'\d+(\.\d+)?B', html_content) is not None
    
    result = {
        "passed": has_si_format or (has_m_suffix and has_b_suffix),
        "si_format_config": has_si_format,
        "m_values_found": has_m_suffix,
        "b_values_found": has_b_suffix,
        "issues": []
    }
    
    if not result["passed"]:
        result["issues"].append("No SI formatting (1M/1B) detected in HTML")
    
    status = "PASS" if result["passed"] else "FAIL"
    print(f"[VALIDATION] Number formatting (SI): {status}")
    
    return result


def validate_title_and_metadata(html_content: str) -> dict:
    """
    Validate that proper title and metadata are present.
    
    Args:
        html_content: HTML file content as string
    
    Returns:
        Validation result dict
    """
    # Check for title text
    has_title = "World Population Dashboard" in html_content
    has_year_range = re.search(r'196\d\s*-\s*202\d', html_content) is not None
    has_plotly = "plotly" in html_content.lower()
    
    result = {
        "passed": has_title and has_year_range and has_plotly,
        "has_dashboard_title": has_title,
        "has_year_range": has_year_range,
        "has_plotly_library": has_plotly,
        "issues": []
    }
    
    if not has_title:
        result["issues"].append("Dashboard title not found")
    if not has_year_range:
        result["issues"].append("Year range (196X-202X) not found")
    if not has_plotly:
        result["issues"].append("Plotly library not detected")
    
    status = "PASS" if result["passed"] else "FAIL"
    print(f"[VALIDATION] Title and metadata: {status}")
    
    return result


def validate_animation_controls(html_content: str) -> dict:
    """
    Validate that animation controls (play/pause, slider) are present.
    
    Args:
        html_content: HTML file content as string
    
    Returns:
        Validation result dict
    """
    # Check for updatemenus (play/pause buttons)
    has_buttons = "updatemenus" in html_content
    has_slider = "sliders" in html_content
    has_animation_frame = "animation_frame" in html_content or "frames" in html_content
    
    result = {
        "passed": has_buttons and has_slider,
        "has_play_pause_buttons": has_buttons,
        "has_year_slider": has_slider,
        "has_animation_frames": has_animation_frame,
        "issues": []
    }
    
    if not has_buttons:
        result["issues"].append("Play/pause buttons not detected")
    if not has_slider:
        result["issues"].append("Year slider not detected")
    
    status = "PASS" if result["passed"] else "FAIL"
    print(f"[VALIDATION] Animation controls: {status}")
    
    return result


def validate_dark_theme(html_content: str) -> dict:
    """
    Validate that dark theme is applied.
    
    Args:
        html_content: HTML file content as string
    
    Returns:
        Validation result dict
    """
    # Check for dark theme indicators
    has_plotly_dark = "plotly_dark" in html_content
    has_dark_colors = "#121212" in html_content or "#1e1e1e" in html_content
    
    result = {
        "passed": has_plotly_dark or has_dark_colors,
        "has_plotly_dark_template": has_plotly_dark,
        "has_dark_background_colors": has_dark_colors,
        "issues": []
    }
    
    if not result["passed"]:
        result["issues"].append("Dark theme not detected (expected plotly_dark template or dark background colors)")
    
    status = "PASS" if result["passed"] else "FAIL"
    print(f"[VALIDATION] Dark theme: {status}")
    
    return result


def validate_responsive_layout(html_content: str) -> dict:
    """
    Validate that layout is configured for responsiveness.
    
    Args:
        html_content: HTML file content as string
    
    Returns:
        Validation result dict
    """
    # Check for autosize or responsive config
    has_autosize = "autosize" in html_content.lower()
    has_height = re.search(r'"height":\s*\d+', html_content) is not None
    has_responsive_config = '"responsive":true' in html_content or "'responsive':true" in html_content
    
    result = {
        "passed": has_autosize or has_responsive_config,
        "has_autosize": has_autosize,
        "has_explicit_height": has_height,
        "has_responsive_config": has_responsive_config,
        "issues": []
    }
    
    if not result["passed"]:
        result["issues"].append("Responsive layout configuration not detected")
    
    status = "PASS" if result["passed"] else "FAIL"
    print(f"[VALIDATION] Responsive layout: {status}")
    
    return result


def validate_data_completeness(html_content: str) -> dict:
    """
    Validate that sufficient data is embedded in the HTML.
    
    Args:
        html_content: HTML file content as string
    
    Returns:
        Validation result dict
    """
    # Count year labels in slider (should be around 65 for 1960-2024)
    year_pattern = r'"label":"(19\d{2}|20\d{2})"'
    years_found = re.findall(year_pattern, html_content)
    unique_years = len(set(years_found))
    
    # Check for country data
    has_country_data = "China" in html_content and "India" in html_content and "United States" in html_content
    
    result = {
        "passed": unique_years >= 60 and has_country_data,
        "unique_years_found": unique_years,
        "expected_years": "~65 (1960-2024)",
        "has_major_countries": has_country_data,
        "issues": []
    }
    
    if unique_years < 60:
        result["issues"].append(f"Only {unique_years} years found, expected ~65")
    if not has_country_data:
        result["issues"].append("Major countries (China, India, USA) not found in data")
    
    status = "PASS" if result["passed"] else "FAIL"
    print(f"[VALIDATION] Data completeness: {status} ({unique_years} years)")
    
    return result


def generate_ui_qa_report(validations: Dict, output_path: Path, html_path: Path) -> None:
    """
    Generate UI QA report in Markdown format.
    
    Args:
        validations: Dictionary of all validation results
        output_path: Path to output MD file
        html_path: Path to HTML file being validated
    """
    overall_status = "PASS" if all(v["passed"] for v in validations.values()) else "FAIL"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Build markdown report
    report_lines = [
        f"# UI QA Validation Report",
        f"",
        f"**Report ID:** UI_QA_{datetime.now().strftime('%Y%m%d_%H%M%S')}  ",
        f"**Timestamp:** {timestamp}  ",
        f"**HTML File:** {html_path}  ",
        f"**Overall Status:** **{overall_status}**  ",
        f"",
        f"---",
        f"",
        f"## Validation Summary",
        f"",
        f"| Check | Status | Issues |",
        f"|-------|--------|--------|"
    ]
    
    for check_name, result in validations.items():
        status_icon = "✅" if result["passed"] else "❌"
        issues_count = len(result.get("issues", []))
        issues_text = f"{issues_count} issues" if issues_count > 0 else "None"
        report_lines.append(f"| {check_name.replace('_', ' ').title()} | {status_icon} | {issues_text} |")
    
    report_lines.extend([
        f"",
        f"---",
        f"",
        f"## Detailed Results",
        f""
    ])
    
    for check_name, result in validations.items():
        report_lines.extend([
            f"",
            f"### {check_name.replace('_', ' ').title()}",
            f"",
            f"**Status:** {'PASS' if result['passed'] else 'FAIL'}  ",
            f""
        ])
        
        # Add specific details (exclude 'passed' and 'issues' keys)
        for key, value in result.items():
            if key not in ['passed', 'issues']:
                report_lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        
        # Add issues if any
        if result.get("issues"):
            report_lines.append(f"")
            report_lines.append(f"**Issues:**")
            for issue in result["issues"]:
                report_lines.append(f"- {issue}")
    
    report_lines.extend([
        f"",
        f"---",
        f"",
        f"## Recommendations",
        f""
    ])
    
    if overall_status == "PASS":
        report_lines.append(f"All UI validations passed. HTML visualization is ready for publishing.")
    else:
        report_lines.append(f"UI validation FAILED. Please review the issues above and regenerate the visualization.")
    
    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    
    print(f"[REPORT] UI QA report saved to {output_path}")
    print(f"[REPORT] Overall status: {overall_status}")
    print(f"[REPORT] Checks: {sum(1 for v in validations.values() if v['passed'])}/{len(validations)} passed")


def main():
    """Main execution function."""
    print("=" * 70)
    print("UI QA VALIDATION")
    print("=" * 70)
    
    # Define paths
    base_dir = Path(__file__).parent.parent
    html_dir = base_dir / "reports" / "html"
    
    # Find most recent HTML file
    html_files = sorted(html_dir.glob("population_bar_race_*.html"))
    
    if not html_files:
        print("[ERROR] No HTML files found in reports/html/")
        return
    
    html_path = html_files[-1]
    print(f"[QA] Validating {html_path.name}")
    
    # Read HTML content
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"[QA] HTML file size: {len(html_content):,} bytes")
    
    # Run all validations
    validations = {
        "file_existence": validate_html_exists(html_path),
        "flag_urls": validate_flag_urls(html_content),
        "number_formatting": validate_number_formatting(html_content),
        "title_metadata": validate_title_and_metadata(html_content),
        "animation_controls": validate_animation_controls(html_content),
        "dark_theme": validate_dark_theme(html_content),
        "responsive_layout": validate_responsive_layout(html_content),
        "data_completeness": validate_data_completeness(html_content)
    }
    
    # Generate report
    timestamp = datetime.now().strftime("%d%b%Y")
    report_output = base_dir / "reports" / "qa" / f"ui_qa_report_{timestamp}.md"
    
    generate_ui_qa_report(validations, report_output, html_path)
    
    # Print summary
    overall_status = "PASS" if all(v["passed"] for v in validations.values()) else "FAIL"
    print("=" * 70)
    print(f"QA STATUS: {overall_status}")
    print("=" * 70)


if __name__ == "__main__":
    main()
