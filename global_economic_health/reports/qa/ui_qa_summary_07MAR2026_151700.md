# UI Quality Assurance Report

**Date:** 2026-03-07 15:17:00
**Testing Method:** Playwright Headless Browser Automation

## Summary

- **Status:** FAIL
- **Total Checks:** 13
- **Passed:** 11
- **Failed:** 1
- **Warnings:** 1
- **Screenshots Captured:** 1
- **Browser Errors:** 1

## Screenshots

- **bubble_map:** reports\qa\screenshots\bubble_map_render_20260307_151657.png

## Browser Console Errors

- `error`: WARNING: plotly-latest.min.js and plotly-latest.js are NO LONGER the latest releases of plotly.js. T

## Test Failures

- **dashboard JavaScript errors:** 1 errors: WARNING: plotly-latest.min.js and plotly-latest.js are NO LONGER the latest releases of plotly.js. They are v1.58.5 (released July 2021), the end of the v1.x line, and will not be updated again. To use more recent versions of plotly.js, please update your links to point to an explicit version on cdn.plot.ly. You can find the latest version information at https://github.com/plotly/plotly.js/releases

## Warnings

- **Bubble map year slider exists:** No range slider found in page

## Test Details

- [PASS] Bubble map file size - 8.66 MB
- [PASS] Bubble map has Plotly
- [PASS] Dashboard file size - 0.01 MB
- [PASS] Dashboard has content
- [PASS] bubble_map Plotly elements load
- [PASS] bubble_map JavaScript errors - No errors in console
- [PASS] bubble_map screenshot captured - Screenshot: bubble_map_render_20260307_151657.png
- [PASS] dashboard Plotly elements load
- [FAIL] dashboard JavaScript errors - 1 errors: WARNING: plotly-latest.min.js and plotly-latest.js are NO LONGER the latest releases of plotly.js. They are v1.58.5 (released July 2021), the end of the v1.x line, and will not be updated again. To use more recent versions of plotly.js, please update your links to point to an explicit version on cdn.plot.ly. You can find the latest version information at https://github.com/plotly/plotly.js/releases
- [PASS] Data has required columns
- [PASS] Data values valid
- [PASS] Data row count - 17020 rows loaded
