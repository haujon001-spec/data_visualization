Here is your complete **Phase 2 Visualization Design** Markdown file, ready to save as:

```
data_visualization/World_population/docs/Phase2_Visualization_Design_5Mar2026.md
```

It follows your strict structure, timestamping, and agent‑oriented workflow. It is written so **VS Code, your agents, and the orchestrator** can understand exactly what to build next.

---

# Phase 2 — Visualization Design (5 Mar 2026)

## 1. Purpose of Phase 2
This phase defines the full visualization architecture for transforming the processed population dataset into a **polished, interactive, agent‑validated bar‑race dashboard**. The visualization must be:

- Visually appealing and modern  
- Mobile‑friendly and desktop‑friendly  
- Enhanced with **SVG country flags**  
- Using **1M/1B number formatting**  
- Timestamped for traceability  
- Ready for HTML QA automation  
- Ready for GIF/MP4 preview generation  
- Ready for LinkedIn publishing  

The output of this phase becomes the input for Phase 3 (QA agents) and Phase 4 (GIF/MP4 preview).

---

## 2. Visualization Objectives

### 2.1 Core Goals
- Display **Top 50 most populous countries** for each year from **1970 → present**.
- Animate population changes over time using a **horizontal bar‑race**.
- Embed **country flags** for visual clarity and appeal.
- Format population values using **SI suffixes** (1M, 1B).
- Ensure readability on both **desktop and mobile**.
- Produce a **timestamped HTML file** suitable for publishing.
- Maintain strict compatibility with the orchestrator and QA agents.

### 2.2 Output File
```
reports/html/population_bar_race_<3Mar2026>.html
```

---

## 3. Visualization Framework

### 3.1 Library
**Plotly** (Python)

Chosen because it supports:

- Smooth animations  
- HTML export  
- Responsive layout  
- Embedded images (SVG flags)  
- High‑quality rendering  
- Agent‑friendly DOM structure for UI QA  

### 3.2 Chart Type
**Horizontal bar‑race animation** with:

- Play/Pause controls  
- Year slider  
- Smooth transitions  
- Dynamic ranking updates  

---

## 4. Data Input Requirements

### 4.1 Source File
```
csv/processed/population_top50_1970_now_<3Mar2026>.csv
```

### 4.2 Required Columns
| Column | Description |
|--------|-------------|
| country_code | ISO‑3 code |
| country_name | Cleaned country name |
| year | Year (int) |
| population | Integer population |
| rank | Rank (1–50) |

### 4.3 Data Assumptions
- Exactly 50 rows per year  
- No aggregates  
- No missing values  
- Population > 0  

These assumptions are enforced by the **Data QA agent**.

---

## 5. Country Flag Integration (SVG)

### 5.1 Flag Source
Use **FlagCDN**:

```
https://flagcdn.com/<alpha2>.svg
```

### 5.2 Mapping ISO‑3 → ISO‑2
A mapping file is stored in:

```
config/country_code_map.csv
```

### 5.3 Embedding Flags in Plotly
Flags will appear:

- Next to bar labels  
- In hover tooltips  
- In the legend (optional)

### 5.4 Label Format
```
<img src="https://flagcdn.com/us.svg" width="20"/> United States
```

Plotly supports HTML in labels, enabling polished visuals.

---

## 6. Number Formatting (1M / 1B)

### 6.1 Requirement
Population values must use SI suffixes:

- 1,000,000 → **1M**  
- 1,000,000,000 → **1B**  

### 6.2 Implementation
Use Plotly’s tick formatting:

```
fig.update_layout(xaxis_tickformat="~s")
```

### 6.3 Tooltip Formatting
Tooltips must show:

```
Country: United States
Population: 331M
Year: 2020
```

---

## 7. Visual Theme and Styling

### 7.1 Theme
A modern, clean theme must be used:

- Dark theme (preferred)  
- High contrast  
- Sans‑serif fonts  
- Rounded bars  
- Soft color gradients  

### 7.2 Color Palette
Use a **distinct color per country**, but avoid:

- Overly bright neon colors  
- Low‑contrast pastels  
- Colors that blend into background  

### 7.3 Layout Requirements
- Title centered  
- Subtitle with data source  
- Footer with timestamp  
- Legend optional (flags already provide identity)  

---

## 8. Mobile + Desktop Responsiveness

### 8.1 Requirements
The visualization must:

- Scale to mobile screens  
- Maintain readable labels  
- Avoid bar clipping  
- Maintain flag visibility  

### 8.2 Implementation
Use:

```
fig.update_layout(autosize=True)
```

And increase:

- Bar height  
- Font size  
- Padding  

### 8.3 UI QA Agent Checks
The UI QA agent will verify:

- Bars readable on mobile  
- Flags visible  
- No overlapping labels  
- Controls accessible  

---

## 9. HTML Export Requirements

### 9.1 Output File
```
reports/html/population_bar_race_<3Mar2026>.html
```

### 9.2 Requirements
- Self‑contained HTML  
- No external JS dependencies  
- Inline Plotly bundle  
- Inline CSS  
- Inline SVG flag references  

### 9.3 Timestamping
Use **human‑friendly** timestamps:

```
3Mar2026
```

### 9.4 HTML Metadata
Include:

- `<title>`  
- `<meta name="viewport">`  
- `<meta name="description">`  

---

## 10. Integration with QA Agents

### 10.1 Data QA Agent
Ensures the processed CSV is valid before visualization.

### 10.2 UI QA Agent
Validates the HTML output:

- Flags load correctly  
- Numbers show as 1M/1B  
- Bars readable  
- No label overlap  
- Mobile layout works  
- Modern theme applied  
- Title + data source visible  

### 10.3 Code Review Agent
Reviews:

- Visualization script  
- HTML generation logic  
- Flag embedding logic  

---

## 11. Integration with GIF/MP4 Preview (Phase 4)

The visualization script must:

- Expose a function to render frames  
- Support static rendering for preview generation  
- Maintain consistent color mapping  
- Maintain consistent flag placement  

The preview generator will use the same data and styling.

---

## 12. Integration with Orchestrator (Phase 5)

The orchestrator will:

1. Run ETL  
2. Run Data QA  
3. Build visualization  
4. Generate timestamped HTML  
5. Run UI QA  
6. Generate GIF/MP4 preview  
7. Publish HTML  
8. Notify via Telegram  

The visualization script must be:

- Modular  
- Deterministic  
- Agent‑friendly  
- Timestamp‑aware  

---

## 13. Phase 2 To‑Do List (5 Mar 2026)

- Implement `03_build_visualization.py`  
- Implement `04_generate_html_timestamped.py`  
- Add SVG flag embedding  
- Add 1M/1B formatting  
- Add responsive layout  
- Add modern theme  
- Add timestamp logic  
- Validate output manually once  
- Prepare for UI QA agent integration  

