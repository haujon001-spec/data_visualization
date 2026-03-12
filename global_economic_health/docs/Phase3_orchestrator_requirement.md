Here is the **Phase 3 – Orchestrator + AI Integration Requirements** written as a **single, authoritative, implementation‑ready `.md` file**. It is designed so VS Code cannot misinterpret or skip steps. It defines:

- the orchestrator’s responsibilities  
- the multi‑agent workflow  
- the AI ensemble logic  
- the evaluator scoring system  
- the API contract  
- the human‑eye QA requirements for AI outputs  
- the debug‑until‑it‑works mandate  


```

---

# **Phase 3 – Orchestrator & AI Integration Requirements**

## **1. Purpose**
Phase 3 introduces the **AI Orchestrator**, which coordinates all AI‑related tasks:

- Context extraction  
- Prompt construction  
- Multi‑model inference (DeepSeek, Mistral, Qwen)  
- Evaluator scoring & consolidation  
- Tooltip reasoning generation  
- Integration with the unified dashboard  

The orchestrator must behave deterministically, reproducibly, and transparently, following strict engineering and QA standards.

---

## **2. Orchestrator Responsibilities**

### **2.1 Pipeline Coordination**
The orchestrator must run the AI pipeline in this exact order:

1. Extract global context  
2. Build normalized prompts  
3. Call DeepSeek  
4. Call Mistral  
5. Call Qwen  
6. Validate all three JSON outputs  
7. Run evaluator scoring  
8. Select anchor model  
9. Consolidate narrative  
10. Generate tooltip reasoning  
11. Return final structured JSON to dashboard  

No steps may be skipped or reordered.

### **2.2 Environment Routing**
The orchestrator must use:

- **Local** for file validation, path checks, and QA  
- **CLI** for workflow automation  
- **Cloud** for LLM inference and evaluator logic  

Each environment must receive correct inputs and produce correct outputs.

---

## **3. Global Context Extraction**

### **3.1 Required Context Inputs**
The orchestrator must extract:

- GDP trend (20‑year slope)  
- Population trend (20‑year slope)  
- Debt trajectory (20‑year slope)  
- Commodity trends (oil, metals, food)  
- Major global events (recessions, wars, pandemics)  
- Regional shocks (currency crises, sanctions)  
- Inflation & interest rate environment  

### **3.2 Context Format**
Context must be delivered to the models in a **normalized JSON block**:

```
{
  "year": 2024,
  "gdp_trend": "...",
  "population_trend": "...",
  "debt_trend": "...",
  "commodity_context": "...",
  "global_events": "...",
  "regional_events": "...",
  "inflation_interest": "..."
}
```

---

## **4. Prompt Construction**

### **4.1 Prompt Normalization**
All three models must receive:

- identical structure  
- identical context  
- identical instructions  
- identical output schema  

### **4.2 Required Output Schema**
Each model must return:

```
{
  "narrative": "...",
  "forecast": {
    "gdp_growth": [...],
    "population_growth": [...],
    "debt_projection": [...]
  },
  "confidence": 0-1
}
```

If a model returns anything outside this schema, the orchestrator must reject it and retry once.

---

## **5. Multi‑Model Execution**

### **5.1 Required Models**
The orchestrator must call:

- DeepSeek  
- Mistral  
- Qwen  

### **5.2 Execution Rules**
- All models must run independently  
- All outputs must be validated  
- All outputs must be logged  
- No model may influence another  

### **5.3 Failure Handling**
If a model fails:

- Retry once  
- If still invalid, mark as `"model_status": "failed"`  
- Evaluator must still run using remaining models  

---

## **6. Evaluator Agent Requirements**

### **6.1 Purpose**
The evaluator selects the **anchor model** and produces:

- consolidated narrative  
- 5‑year forecast  
- tooltip reasoning  

### **6.2 Anchor Model Selection**
The evaluator must use a **programmatic scoring system** based on:

- GDP trend alignment  
- Population trend alignment  
- Debt trajectory alignment  
- Internal consistency  
- Cross‑model consistency  
- Plausibility  
- Confidence (secondary only)  

The model with the highest score becomes the anchor.

### **6.3 Evaluator Output Schema**
The evaluator must return:

```
{
  "final_narrative": "...",
  "final_forecast": {...},
  "reasoning_tooltip": "...",
  "anchor_model": "deepseek|mistral|qwen",
  "scores": {...}
}
```

---

## **7. API Contract for Dashboard Integration**

### **7.1 Dashboard → Orchestrator Request**
When the user clicks **Generate Insight**, the dashboard sends:

```
{
  "year": 2024,
  "top10_countries": [...],
  "metrics": {
    "gdp": {...},
    "population": {...},
    "debt": {...}
  }
}
```

### **7.2 Orchestrator → Dashboard Response**
The orchestrator must return:

```
{
  "narrative": "...",
  "forecast": {...},
  "tooltip": "...",
  "anchor_model": "...",
  "timestamp": "..."
}
```

---

## **8. Human‑Eye QA Requirements (AI Outputs)**

### **8.1 Narrative QA**
The QA Specialist must verify:

- narrative is coherent  
- no hallucinated numbers  
- no contradictory statements  
- no missing sections  
- no duplicated sentences  
- no model‑specific artifacts  

### **8.2 Forecast QA**
The QA Specialist must confirm:

- values are realistic  
- no negative populations  
- no impossible GDP growth rates  
- no sudden debt collapses  
- all numbers are in **human‑readable units (K, M, B, T)**  

### **8.3 Tooltip QA**
The QA Specialist must confirm:

- reasoning is concise  
- reasoning matches evaluator logic  
- no hallucinated events  
- no references to internal model names  

### **8.4 Integration QA**
The QA Specialist must confirm:

- dashboard displays narrative correctly  
- tooltip appears on hover  
- no layout breaks  
- no console errors  

---

## **9. Debug‑Until‑It‑Works Requirement**
If any QA check fails:

- orchestrator must halt  
- developer must fix the issue  
- entire pipeline must be re‑run  
- QA must re‑verify from the beginning  

No partial approvals.  
No skipping steps.  
No marking Phase 3 complete until **all** checks pass.

---

## **10. Phase 3 Completion Criteria**
Phase 3 is complete only when:

- all three models produce valid outputs  
- evaluator selects anchor model correctly  
- consolidated narrative is coherent  
- forecast is realistic and formatted  
- tooltip reasoning is correct  
- dashboard displays everything correctly  
- QA Specialist signs off  

If any requirement is missing, Phase 3 is **not complete**.

