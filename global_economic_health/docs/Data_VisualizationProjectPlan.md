Here is the **updated, production‑ready Markdown file** incorporating all your new requirements:  
- verifying existing scripts  
- enhancing on top of them  
- strict folder structure  
- naming conventions with date suffix  
- UTF‑8 coding standard  
- full end‑to‑end testing  
- and a clear **DO / DON’T** section for your agents and developers.

This version is clean, structured, and ready to drop directly into VS Code.

---

# **Macro‑Economic Dashboard Architecture (Top 10 Countries, AI‑Augmented)**

## **1. Overview**
This dashboard presents synchronized macro‑economic indicators for the world’s top 10 economies using a unified year slider and four coordinated panels. It integrates animated visualizations with an AI‑generated narrative powered by a three‑model ensemble and an evaluator agent. The goal is to deliver a clean, modern, and trustworthy macro‑economic experience with explainable AI.

Before implementing new components, all existing scripts must be **verified**, **tested**, and **enhanced** rather than rewritten unless necessary.

---

## **2. Engineering Foundations**

### **2.1 Verify Existing Scripts First**
Before writing new code, developers must:

- Identify which scripts already work as expected.  
- Validate their outputs end‑to‑end.  
- Enhance or extend existing scripts instead of duplicating logic.  
- Document any gaps or failures before modifying code.  

This prevents regressions and ensures continuity across the pipeline.

### **2.2 Strict Folder Structure**
All files must follow a predictable, auditable structure:

```
/etl/
/etl/inputs/
/etl/outputs/
/etl/logs/

/viz/
/viz/gdp/
/viz/population/
/viz/debt/

/ai/
/ai/models/
/ai/evaluator/
/ai/prompts/

/docs/
/docs/archive/

/tests/
/tests/unit/
/tests/integration/
```

No files should be placed outside the approved structure.

### **2.3 Naming Convention With Date Suffix**
All documentation, scripts, and logs must include a date suffix:

- `todolist_2026-03-08.md`  
- `gdp_choropleth_2026-03-08.py`  
- `ai_evaluator_log_2026-03-08.json`  

This ensures traceability and prevents accidental overwrites.

### **2.4 UTF‑8 Encoding**
All scripts, data files, and documentation must be saved in **UTF‑8** encoding to ensure:

- cross‑platform compatibility  
- correct rendering of international characters  
- consistent behavior across agents  

### **2.5 Full End‑to‑End Testing**
After implementing or modifying any script:

- Run the entire pipeline from ETL → Visualization → AI Panel.  
- Validate outputs visually and programmatically.  
- Confirm that the dashboard behaves exactly as expected.  
- Debug until the system passes all tests.  

No script is considered complete until it passes full front‑to‑back testing.

---

## **3. Unified Year Control**
A single global year slider controls all three visual panels:

- GDP Choropleth (log‑scaled)  
- Population Trendline  
- Debt Bar Chart  

The AI Insight Panel updates **only** when the user clicks **Generate Insight**.

---

## **4. Panel 1 — GDP Choropleth (Animated, Log‑Scaled, Top 10 Highlighted)**

### **Purpose**
Show global economic size and long‑term shifts among the top 10 economies.

### **Encoding**
- Color intensity = `log10(GDP)`  
- Year slider = synchronized  
- Top 10 highlighted; others muted  
- Tooltip: GDP, GDP per capita, GDP growth  
- Color scale: Viridis or Cividis  

---

## **5. Panel 2 — Population Trendline (Smooth, Speed Control, Top 10)**

### **Purpose**
Show demographic evolution and long‑term population trajectories.

### **Encoding**
- Line = population  
- Dashed line = trendline  
- Playback speed: 1×, 2×, 5×  
- Year slider = synchronized  

---

## **6. Panel 3 — Debt Bar Chart (Animated, Top 10)**

### **Purpose**
Show total debt levels and fiscal pressure among top economies.

### **Encoding**
- Bar height = total debt (USD)  
- Color = public vs private debt  
- Units = $B / $T  
- Year slider = synchronized  

---

## **7. Panel 4 — AI Insight Panel (3‑Model Ensemble, 5‑Year Forecast)**

### **Purpose**
Provide a narrative summary and forward‑looking projection for the selected year.

### **User Interaction**
- User clicks **Generate Insight**  
- AI panel updates with:  
  - Summary of the selected year  
  - Cross‑metric insights  
  - 5‑year forecast  
  - Risk flags  

### **Models Used**
- DeepSeek Reasoner  
- Mistral  
- Qwen (or similar lightweight model)  

Each model receives the same structured data and produces an independent narrative.

---

## **8. Evaluator Specialist Agent (Consensus + Historical Alignment)**

### **Role**
Consolidate the three LLM outputs into a single, balanced, historically aligned forecast.

### **Evaluation Criteria**
- Alignment with last 10–20 years of GDP, population, and debt trends  
- Plausibility of 5‑year projections  
- Internal consistency  
- Tone and clarity  
- Avoidance of hallucinations  

### **Synthesis Logic**
- Select the model most aligned with historical trends as the **anchor**  
- Integrate consistent insights from the other two models  
- Remove extreme or speculative claims  
- Produce a balanced, data‑aligned narrative  

---

## **9. “Why This Forecast?” Hover Tooltip**

### **Purpose**
Provide transparency without cluttering the main narrative.

### **Tooltip Contents**
- Which model was chosen as anchor  
- Why it aligned best with historical trends  
- Contradictions resolved  
- Confidence score  
- Short comparison of the other models  

---

## **10. Final Dashboard Layout**

```
---------------------------------------------------------
| Panel 1: GDP Choropleth (Animated, Log-Scaled, Top 10) |
---------------------------------------------------------
| Panel 2: Population Trendline (Smooth, Top 10)         |
---------------------------------------------------------
| Panel 3: Debt Bar Chart (Animated, Top 10)             |
---------------------------------------------------------
| Panel 4: AI Insight Panel                              |
|   - Generate Insight Button                            |
|   - Summary + 5-Year Forecast                          |
|   - "Why this forecast?" Hover Tooltip                 |
---------------------------------------------------------
| Unified Year Slider (1970 → Latest Year)               |
---------------------------------------------------------
```

---

## **11. DOs and DON’Ts**

### **DO**
- Verify existing scripts before writing new ones.  
- Enhance instead of rewriting.  
- Follow strict folder structure.  
- Use date‑suffix naming conventions.  
- Save all files in UTF‑8.  
- Test the entire pipeline end‑to‑end.  
- Debug until the system behaves exactly as expected.  
- Keep visual panels synchronized via the unified year slider.  
- Use a 3‑model ensemble for AI forecasting.  
- Let the evaluator agent choose the historically aligned model.  
- Provide reasoning only via hover tooltip.  

### **DON’T**
- Don’t create new scripts without checking existing ones.  
- Don’t break the folder structure or place files arbitrarily.  
- Don’t use ambiguous filenames without date suffixes.  
- Don’t save files in non‑UTF‑8 encodings.  
- Don’t assume a script works without full testing.  
- Don’t allow the AI panel to auto‑update on slider movement.  
- Don’t expose raw LLM outputs without evaluator consolidation.  
- Don’t show evaluator reasoning by default.  
- Don’t allow extreme or speculative forecasts.  
- Don’t bypass the evaluator agent’s validation logic.  


