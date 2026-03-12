John, perfect — that confirmation gives me exactly what I need. I’ll now generate the **fourth Markdown file** as a **GENERAL QA STANDARD** for *all* your agent‑orchestrated projects, with:

- Full engineering QA protocol  
- Practical testing checklist  
- Strict folder structure enforcement  
- Date‑suffix naming rules  
- UTF‑8 encoding rules  
- Path‑correction requirements (your latest instruction)  
- End‑to‑end testing requirements  
- Debug‑until‑it‑works mandate  

This will become your **master QA standard**, reusable across every future project.

---

# **GENERAL QA STANDARD FOR ALL AGENT‑ORCHESTRATED PROJECTS**

## **1. Purpose**
This document defines the universal Quality Assurance (QA) standards for all agent‑orchestrated projects. It ensures that every script, dataset, visualization, AI model, and automation pipeline behaves consistently, predictably, and reliably across your entire ecosystem.

These standards apply to:
- ETL pipelines  
- Visualization pipelines  
- AI ensemble systems  
- Evaluator agents  
- Orchestrators  
- Automation workflows  
- Any codebase under your strict folder structure  

All files must be UTF‑8 encoded, follow strict naming conventions, and pass full end‑to‑end testing.

---

## **2. Folder Structure Requirements**
All projects must follow a strict, auditable folder structure:

```
/etl/
/etl/inputs/
/etl/outputs/
/etl/logs/

/viz/
/viz/components/
/viz/exports/

/ai/
/ai/models/
/ai/prompts/
/ai/evaluator/
/ai/logs/

/automation/
/automation/scripts/
/automation/logs/

/docs/
/docs/archive/

/tests/
/tests/unit/
/tests/integration/
/tests/e2e/
```

### **Rules**
- No files may be placed outside the approved structure.  
- No ad‑hoc folders may be created without approval.  
- All scripts must reference files using **correct paths inside this structure**.  
- If a script references a file in the wrong location, the developer must **correct the path** so the script points to the exact location inside the project tree.

---

## **3. Naming Convention Requirements**
All files must include a date suffix in the format:

```
YYYY-MM-DD
```

Examples:
- `etl_clean_gdp_2026-03-08.py`  
- `viz_population_trend_2026-03-08.py`  
- `ai_evaluator_2026-03-08.py`  
- `todolist_2026-03-08.md`  

### **Rules**
- No file may be saved without a date suffix.  
- No file may overwrite a previous version.  
- Logs must always include timestamps.  

---

## **4. UTF‑8 Encoding Requirement**
All scripts, data files, logs, and documentation must be saved in **UTF‑8** encoding.

### **Rules**
- No ANSI, ASCII‑extended, or platform‑specific encodings.  
- Any non‑UTF‑8 file must be converted before use.  
- QA must verify encoding during testing.  

---

## **5. Path‑Correction Standard**
Whenever a script references a file under the strict folder structure:

> The developer must verify and correct the path so the script points to the exact location inside the project tree. If the path is incorrect, the script must be adjusted to the correct path so that it runs successfully.

### **Rules**
- No hard‑coded absolute paths.  
- No relative paths that escape the project root.  
- All paths must be validated during testing.  
- Any script with incorrect paths automatically fails QA.  

---

## **6. Full Engineering QA Protocol**

### **6.1 Unit Testing**
Each script must have unit tests covering:
- Input validation  
- Output correctness  
- Error handling  
- Edge cases  
- UTF‑8 encoding compliance  

### **6.2 Integration Testing**
Integration tests must validate:
- ETL → Visualization  
- ETL → AI models  
- AI models → Evaluator agent  
- Evaluator → Final output  
- Automation workflows  

### **6.3 End‑to‑End Testing**
Every project must pass a full pipeline test:
- Load raw data  
- Run ETL  
- Generate visualizations  
- Run AI ensemble  
- Run evaluator  
- Produce final output  
- Validate UI behavior  
- Confirm correct file paths  
- Confirm correct folder structure  
- Confirm correct naming conventions  

### **6.4 Regression Testing**
Any change to:
- ETL logic  
- Visualization scripts  
- AI prompts  
- Evaluator logic  
- Automation scripts  

must trigger regression tests.

### **6.5 Performance Testing**
Validate:
- Script runtime  
- Memory usage  
- Visualization rendering speed  
- AI inference latency  

### **6.6 Data Validation**
Check:
- Missing values  
- Incorrect types  
- Out‑of‑range values  
- Duplicates  
- Schema mismatches  

### **6.7 Debug‑Until‑It‑Works Mandate**
If any script fails:
- Unit tests  
- Integration tests  
- End‑to‑end tests  
- Path validation  
- Encoding validation  
- Folder structure validation  

the developer must debug until the script works exactly as expected.

No script is considered complete until it passes all QA stages.

---

## **7. Practical Testing Checklist (Daily Use)**

### **Before coding**
- Verify existing scripts.  
- Identify what already works.  
- Enhance instead of rewriting.  

### **During coding**
- Use UTF‑8 encoding.  
- Follow strict folder structure.  
- Use date‑suffix naming.  
- Validate all file paths.  

### **After coding**
- Run unit tests.  
- Run integration tests.  
- Run full end‑to‑end pipeline.  
- Confirm correct paths.  
- Confirm correct folder structure.  
- Confirm correct naming conventions.  
- Confirm UTF‑8 encoding.  
- Debug until everything works.  

### **Before final approval**
- Validate outputs visually.  
- Validate outputs programmatically.  
- Validate AI ensemble behavior.  
- Validate evaluator consolidation.  
- Validate tooltip reasoning.  
- Validate automation workflows.  

If any step fails, the script is not approved.

---

## **8. DOs and DON’Ts**

### **DO**
- Verify existing scripts before writing new ones.  
- Enhance instead of rewriting.  
- Follow strict folder structure.  
- Use date‑suffix naming.  
- Save all files in UTF‑8.  
- Validate all file paths.  
- Test the entire pipeline end‑to‑end.  
- Debug until everything works.  
- Log all operations with timestamps.  

### **DON’T**
- Don’t create new scripts without checking existing ones.  
- Don’t break folder structure.  
- Don’t use filenames without date suffix.  
- Don’t save files in non‑UTF‑8 formats.  
- Don’t assume a script works without testing.  
- Don’t use incorrect file paths.  
- Don’t bypass QA or evaluator logic.  
- Don’t leave failing tests unresolved.  


