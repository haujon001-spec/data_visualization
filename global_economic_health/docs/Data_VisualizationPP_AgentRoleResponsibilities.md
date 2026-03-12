John, here is the **third Markdown file**, fully structured for VS Code, documenting the **LLM prompt templates**, **input schema**, **output schema**, and **evaluator agent logic** for your 3‑model ensemble forecasting system. It follows your engineering rules: strict folder structure, date‑suffix naming, UTF‑8, and full end‑to‑end testing expectations.

---

# **LLM Prompt Templates & Evaluator Logic (Macro‑Economic Dashboard System)**

## **1. Overview**
This document defines the standardized prompt templates used by the three LLMs (DeepSeek Reasoner, Mistral, Qwen) and the Evaluator Specialist Agent. All prompts must follow the same structure to ensure consistent outputs, reduce hallucination, and support reliable consolidation.

All files must be saved in **UTF‑8**, follow strict folder structure, and include a **date suffix** in filenames (e.g., `llm_prompts_2026-03-08.md`).

---

# **2. Folder Structure**

```
/ai/
/ai/prompts/
/ai/prompts/base/
/ai/prompts/models/
/ai/prompts/evaluator/
/ai/logs/
/ai/logs/2026-03-08/
```

No files should be placed outside these directories.

---

# **3. Input Schema for All LLMs**

Each LLM receives the same structured JSON input. This ensures consistency and makes evaluator comparison easier.

### **3.1 Input Fields**
```
{
  "selected_year": 2015,
  "countries": [
    {
      "name": "United States",
      "gdp": 18200000000000,
      "population": 321000000,
      "debt_total": 18000000000000,
      "debt_to_gdp": 0.99,
      "gdp_growth_10yr": 0.021,
      "population_growth_10yr": 0.006,
      "debt_growth_10yr": 0.035
    },
    ...
  ],
  "top10_ranked_by_gdp": ["United States", "China", "Japan", ...],
  "global_context": {
    "commodity_trends": "...",
    "regional_shifts": "...",
    "major_events": "..."
  }
}
```

### **3.2 Requirements**
- All numeric values must be validated by ETL agent before passing to LLMs.  
- No missing fields allowed.  
- All strings must be UTF‑8.  
- All arrays must be sorted and validated.  

---

# **4. Output Schema for All LLMs**

Each LLM must return a structured JSON output to simplify evaluator comparison.

### **4.1 Output Fields**
```
{
  "summary": "...",
  "cross_metric_insights": "...",
  "five_year_forecast": {
    "gdp_projection": "...",
    "population_projection": "...",
    "debt_projection": "...",
    "risk_flags": ["...", "..."]
  },
  "confidence_markers": {
    "data_alignment": 0.0 - 1.0,
    "trend_consistency": 0.0 - 1.0,
    "internal_consistency": 0.0 - 1.0
  }
}
```

### **4.2 Requirements**
- No hallucinated numbers.  
- No invented countries.  
- No extreme or speculative claims.  
- Tone must be professional and neutral.  
- All text must be UTF‑8.  

---

# **5. Base Prompt Template (Used by All LLMs)**

```
You are an economic analysis model. Your task is to analyze the top 10 global economies for the selected year and produce:

1. A concise summary of the selected year.
2. Cross-metric insights linking GDP, population, and debt.
3. A 5-year forecast grounded in historical trends.
4. Risk flags for fiscal, demographic, or structural vulnerabilities.
5. Confidence markers evaluating your own reasoning.

Rules:
- Use only the data provided.
- Do not hallucinate numbers.
- Do not invent countries or events.
- Keep tone professional and neutral.
- Forecasts must align with the last 10–20 years of historical trends.
- Avoid extreme or speculative claims.
- Output must follow the required JSON schema.

Input data:
{{structured_json_input}}
```

---

# **6. Model‑Specific Prompt Variants**

Each model receives the base prompt plus a small modifier to encourage diversity.

### **6.1 DeepSeek Reasoner**
```
Add emphasis on numerical reasoning and long-term trend alignment.
```

### **6.2 Mistral**
```
Add emphasis on clarity, readability, and narrative coherence.
```

### **6.3 Qwen**
```
Add emphasis on cross-country comparisons and structural patterns.
```

These modifiers create diversity without breaking structure.

---

# **7. Evaluator Agent Prompt Template**

The evaluator agent receives the three LLM outputs plus the original input data.

### **7.1 Evaluator Prompt**
```
You are the Evaluator Specialist Agent. Your task is to consolidate three LLM outputs into a single, balanced, historically aligned forecast.

Steps:
1. Identify which model aligns most closely with the last 10–20 years of historical trends.
2. Use that model as the anchor.
3. Integrate consistent insights from the other two models.
4. Remove contradictions, hallucinations, and extreme claims.
5. Produce a final narrative and 5-year forecast.
6. Generate a reasoning block for the "Why this forecast?" tooltip.

Rules:
- Do not invent numbers.
- Do not introduce new claims not present in the inputs.
- Tone must remain professional and neutral.
- Output must follow the final JSON schema.

Inputs:
- Original structured data
- Model A output
- Model B output
- Model C output
```

---

# **8. Evaluator Output Schema**

```
{
  "final_narrative": "...",
  "five_year_forecast": "...",
  "risk_flags": ["...", "..."],
  "reasoning_tooltip": {
    "anchor_model": "Model B",
    "historical_alignment_reason": "...",
    "contradictions_resolved": ["...", "..."],
    "confidence_score": 0.0 - 1.0,
    "model_comparison": {
      "model_a": "slightly optimistic",
      "model_b": "historically aligned",
      "model_c": "inconsistent with debt trends"
    }
  }
}
```

---

# **9. Engineering Rules for All Prompts**

### **DO**
- Use UTF‑8 encoding.  
- Follow strict folder structure.  
- Use date‑suffix filenames.  
- Validate all inputs before sending to LLMs.  
- Ensure outputs follow JSON schema exactly.  
- Test the entire pipeline end‑to‑end.  
- Debug until the system behaves exactly as expected.  

### **DON’T**
- Don’t allow free‑form LLM outputs.  
- Don’t accept hallucinated numbers.  
- Don’t bypass evaluator agent logic.  
- Don’t expose raw LLM outputs to the user.  
- Don’t break naming conventions.  
- Don’t save files in non‑UTF‑8 formats.  

