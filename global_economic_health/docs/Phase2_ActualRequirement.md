I’ve seen **all four Phase‑2 visuals** *and* all the corresponding Python scripts, VS Code is missing:

A **single, authoritative, unambiguous `.md` specification** that tells the agent:

- what Phase 2 *actually* requires  
- what “complete” means  
- what the QA Specialist must verify **with human eyes**  
- what interactions must be tested  
- what engineering standards must be enforced  
- what folder structure and path rules must be validated  
- what visual behaviors must be confirmed  
- what failures must block completion  

This file is written so that VS Code **cannot misinterpret** or prematurely mark Phase 2 as done.

Below is the complete `.md` file you can drop into:

```
/docs/phase2_visualization_requirements.md
```

It includes:

- Phase‑2 requirements  
- Human‑eye visualization QA protocol  
- Engineering QA protocol  
- Completion criteria  
- Debug‑until‑it‑works mandate  

---

# **Phase 2 – Visualization Layer Requirements & Human‑Eye QA Standard**

## **1. Purpose**
Phase 2 delivers **four fully functional visualization components**:

1. GDP Choropleth  
2. Population Trendline  
3. Debt Bar Chart  
4. Unified 4‑Panel Dashboard with AI Insight Panel Shell  

All components must be visually correct, interactive, synchronized, and compliant with strict engineering standards.

Phase 2 is **not complete** until the QA Specialist performs full human‑eye verification and approves all outputs.

---

## **2. Required Visualization Components**

### **2.1 GDP Choropleth**
- Log‑scaled GDP (`log10(gdp_usd)`)  
- Viridis colorscale  
- Top‑10 economies highlighted with red markers  
- Natural Earth projection  
- Hover tooltips with GDP and log values  
- Year‑specific rendering (no animation in unified dashboard)  

### **2.2 Population Trendline**
- Top‑10 economies by GDP  
- Smoothed trendlines (spline interpolation)  
- Stable y‑axis (no flicker)  
- Historical data points shown as faint markers  
- Hover tooltips with population values  
- Precomputed frames for animation (standalone version)  
- Speed controls (1×, 2×, 5×) in animated version  

### **2.3 Debt Bar Chart**
- Top‑10 economies by total debt  
- Horizontal bar chart  
- Color‑coded by debt‑to‑GDP ratio  
- Smooth transitions in animated version  
- Hover tooltips with debt values  
- Year‑specific rendering in unified dashboard  

### **2.4 Unified Dashboard**
- 4‑panel layout:
  - GDP Choropleth  
  - Population Trendline  
  - Debt Bar Chart  
  - AI Insight Panel Shell  
- Unified year slider synchronizing all three visualization panels  
- AI Insight Panel **must not auto‑update**  
- “Generate Insight” button triggers placeholder logic  
- Responsive layout, gradient background, consistent styling  

---

## **3. Human‑Eye Visualization QA Protocol**

The QA Specialist must verify each visualization **exactly as a human would**, by opening the generated HTML files and visually inspecting them.

### **3.1 Front‑to‑Back Execution**
For each script:

1. Load dataset from correct path  
2. Execute script end‑to‑end  
3. Confirm output file is created  
4. Open HTML output in browser  
5. Visually inspect the rendered chart  
6. Interact with:
   - year slider  
   - animation controls  
   - speed controls  
   - hover tooltips  
   - legend (if present)  
7. Confirm no console errors  

### **3.2 Visual Correctness Checks**
The QA Specialist must confirm:

- Choropleth colors match log‑scaled GDP  
- Top‑10 markers appear in red  
- Trendlines are smooth and continuous  
- Trendline y‑axis is stable across years  
- Debt bars are correctly ordered and colored  
- All labels, titles, and legends are correct  
- No overlapping text or broken layout  
- No missing countries or NaN values  
- No flickering or jitter in animations  
- Dashboard panels align correctly in grid  
- Year slider updates all three panels  

### **3.3 Interaction Checks**
The QA Specialist must confirm:

- Slider updates choropleth, trendline, and debt chart  
- AI panel does **not** update on slider movement  
- “Generate Insight” button works and shows placeholder  
- Speed controls work in animated trendline  
- Animation plays smoothly  
- Hover tooltips show correct values  

### **3.4 Cross‑Panel Consistency**
The QA Specialist must confirm:

- All panels use the same Top‑10 filtering logic  
- All panels use the same dataset  
- All panels use consistent color palettes  
- All panels use the same reference year  
- All panels follow naming conventions  

---

## **4. Engineering QA Protocol**

### **4.1 Folder Structure**
All files must be stored in:

```
/viz/
/viz/components/
/viz/exports/
/output/
```

No files may exist outside the approved structure.

### **4.2 Path‑Correction Requirement**
Every script must reference files using **correct paths inside the strict folder structure**.

If a script references an incorrect path:

- It must be corrected  
- The script must be re‑run  
- QA must re‑verify  

### **4.3 Naming Convention**
All files must include a date suffix:

```
YYYY-MM-DD
```

Examples:

- `gdp_choropleth_2026-03-08.py`  
- `population_trendline_2026-03-08.py`  
- `dashboard_unified_2026-03-08.html`  

### **4.4 Encoding**
All files must be UTF‑8 encoded.

### **4.5 Logging**
Scripts must log:

- start  
- end  
- errors  
- warnings  
- file paths  
- number of rows loaded  

---

## **5. Debug‑Until‑It‑Works Requirement**
If any QA check fails:

- The pipeline must stop  
- The developer must fix the issue  
- The entire script must be re‑run  
- QA must re‑verify from the beginning  

No partial approvals.  
No skipping steps.  
No marking Phase 2 complete until **all** checks pass.

---

## **6. Phase 2 Completion Criteria**

Phase 2 is complete only when:

- All four visualization components render correctly  
- All interactions behave correctly  
- All engineering standards are met  
- All paths are correct  
- All visuals are visually verified  
- The unified dashboard works end‑to‑end  
- The QA Specialist signs off  

If any requirement is missing, Phase 2 is **not complete**.


