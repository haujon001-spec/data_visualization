
---

## Dashboard structure and required panels
The dashboard uses **three visualization panels** and **one AI panel**, with no substitutions or alternatives. This structure is fixed and must not be changed by the agent.

- **GDP Choropleth** using log‑scaled GDP values, highlighting the Top‑10 economies.
- **Population Trendline** with smoothing, stable y‑axis, Top‑10 filtering, and optional speed controls.
- **Debt Bar Chart** showing total debt for the Top‑10 economies with animation.
- **AI Insight Panel** containing:
  - A “Generate Insight” button.
  - The consolidated narrative and 5‑year forecast.
  - A hover tooltip labeled “Why this forecast?” showing evaluator reasoning.

The layout remains a **4‑panel grid** with the unified year slider at the bottom.

---

## Unified year slider behavior
The unified year slider is a **hard requirement** and must behave exactly as follows:

- It synchronizes **all three visualization panels**.
- It does **not** trigger updates to the AI Insight Panel.
- The AI panel updates **only** when the user clicks “Generate Insight”.

This ensures deterministic behavior and prevents unnecessary LLM calls.

---

## Trendline enhancements
The Population Trendline panel must include:

- Smoothing (LOESS or polynomial).
- Stable y‑axis to avoid flicker.
- Precomputed animation frames for smooth playback.
- Optional speed controls (1×, 2×, 5×).
- Consistent color palette.
- Top‑10 filtering only.

These enhancements are required for visual clarity and QA stability.

---

## Data filtering and metrics
All panels must use **Top‑10 economies only**, based on GDP ranking for the selected year.

Only the following metrics are used:

- GDP  
- Population  
- Debt  

No additional metrics should be added.

---

## AI Insight Panel requirements
The AI Insight Panel must include:

- A **Generate Insight** button.
- A consolidated narrative and 5‑year forecast.
- A hover tooltip labeled **“Why this forecast?”** containing evaluator reasoning.

The panel must not auto‑update when the year slider moves.

---

## Evaluator anchor‑model selection
The evaluator must select the anchor model using a **programmatic scoring system** based on:

- Alignment with 10–20 years of historical GDP trends.
- Alignment with demographic momentum.
- Alignment with debt trajectory.
- Internal consistency.
- Cross‑model consistency.
- Plausibility (no extreme optimism or pessimism).

The model with the highest score becomes the anchor.  
Self‑reported confidence markers are secondary and cannot override the scoring system.

---

## Engineering and QA requirements
All scripts must follow your global engineering standards:

- Strict folder structure.
- Date‑suffix naming (YYYY‑MM‑DD).
- UTF‑8 encoding.
- Path‑correction requirement:
  - Every script must reference files using correct paths inside the strict folder structure.
  - Any incorrect path must be corrected before approval.
- Full end‑to‑end testing:
  - ETL → Visualization → AI Ensemble → Evaluator → Final Output.
  - Debug until the entire pipeline works exactly as expected.

These rules apply to all agents: local, CLI, and cloud.

---

## Summary for VS Code (copy‑paste)
This is the exact specification VS Code needs:

**Visualization Panels:**  
Use GDP choropleth (log‑scaled), Population trendline (smooth, Top‑10, speed control), and Debt bar chart (Top‑10). No replacements or additional charts.

**Year Slider:**  
The unified year slider must synchronize all three visualization panels. The AI Insight Panel must not auto‑update.

**AI Insight Panel:**  
Keep the “Generate Insight” button. The panel updates only when the user clicks it. Include a “Why this forecast?” hover tooltip.

**Dashboard Layout:**  
Use the same 4‑panel layout: three visualization panels + AI Insight Panel + unified year slider.

**Trendline Enhancements:**  
Smoothing, stable y‑axis, Top‑10 filtering, consistent colors, optional speed control, and precomputed frames.

**Speed Controls:**  
Required only for the Population Trendline panel.

**Data Filtering:**  
Top‑10 only for all panels.

**Metrics:**  
GDP, Population, Debt only.

**Evaluator Logic:**  
Select the anchor model using a programmatic scoring system based on historical‑trend alignment. Confidence markers are secondary.

**Engineering Standards:**  
Strict folder structure, date‑suffix naming, UTF‑8 encoding, path‑correction enforcement, and full end‑to‑end testing.

