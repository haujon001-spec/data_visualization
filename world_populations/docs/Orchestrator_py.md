Understood — you want the **actual `orchestrator.py` skeleton**, fully aligned with your Phase 1–6 design, and built to work with:

- Your **strict folder structure**  
- Your **verification layer**  
- Your **local agent as CI/CD auditor**  
- Your **background + cloud agents as workers**  
- Your **timestamped outputs**  
- Your **QA agents**  
- Your **preview generator**  
- Your **publishing pipeline**  
- Your **future OpenClaw/Telegram control**  

Below is the complete, production‑grade **`orchestrator.py` skeleton**.  
It is intentionally modular, agent‑friendly, and verification‑ready.

You can paste this directly into:

```
data_visualization/World_population/scripts/orchestrator.py
```

---

# `orchestrator.py` — Full Code Skeleton (5 Mar 2026)

```python
import sys
import traceback
from pathlib import Path
from datetime import datetime

# --- Script Imports ---
from scripts.fetch_population import run_fetch_population
from scripts.transform_rank_top50 import run_transform_rank
from scripts.build_visualization import run_visualization
from scripts.generate_html_timestamped import run_html_generation
from scripts.generate_gif_mp4_preview import run_mp4_generation, run_gif_generation

# --- QA Agent Imports ---
from qa_agents.agent_data_qa import run_data_qa
from qa_agents.agent_ui_qa import run_ui_qa
from qa_agents.agent_code_review import run_code_review

# --- Verification Layer ---
from verification.verify_all import verify_all

# --- Optional Publishing ---
# from publishing.github_pages import publish_to_github
# from publishing.vps_publisher import publish_to_vps

# --- Telegram (Day‑2) ---
# from cloud.telegram_notifier import send_telegram_message, send_telegram_file


def generate_timestamp():
    """Human‑friendly timestamp: 3Mar2026"""
    return datetime.now().strftime("%-d%b%Y")


def orchestrator_log(message: str, log_file: Path):
    """Append message to orchestrator log."""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)


def run_pipeline():
    """Main orchestrator pipeline."""
    project_root = Path(__file__).resolve().parents[1]
    timestamp = generate_timestamp()

    log_dir = project_root / "reports" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"orchestrator_log_{timestamp}.txt"

    orchestrator_log(f"=== World Population Pipeline Started ({timestamp}) ===", log_file)

    try:
        # ---------------------------------------------------------
        # Step 1 — Fetch Raw Population Data
        # ---------------------------------------------------------
        orchestrator_log("[1/10] Fetching population data...", log_file)
        raw_csv_path = run_fetch_population(project_root, timestamp)

        # ---------------------------------------------------------
        # Step 2 — Transform + Rank Top 50
        # ---------------------------------------------------------
        orchestrator_log("[2/10] Transforming + ranking data...", log_file)
        processed_csv_path = run_transform_rank(project_root, timestamp)

        # ---------------------------------------------------------
        # Step 3 — Data QA Agent
        # ---------------------------------------------------------
        orchestrator_log("[3/10] Running Data QA...", log_file)
        data_qa_result = run_data_qa(project_root, timestamp)
        if data_qa_result["status"] == "FAIL":
            orchestrator_log("Data QA FAILED. Aborting pipeline.", log_file)
            return {"status": "FAIL", "stage": "Data QA", "timestamp": timestamp}

        # ---------------------------------------------------------
        # Step 4 — Build Visualization
        # ---------------------------------------------------------
        orchestrator_log("[4/10] Building visualization...", log_file)
        fig = run_visualization(project_root, timestamp)

        # ---------------------------------------------------------
        # Step 5 — Generate Timestamped HTML
        # ---------------------------------------------------------
        orchestrator_log("[5/10] Generating HTML report...", log_file)
        html_path = run_html_generation(project_root, fig, timestamp)

        # ---------------------------------------------------------
        # Step 6 — UI QA Agent
        # ---------------------------------------------------------
        orchestrator_log("[6/10] Running UI QA...", log_file)
        ui_qa_result = run_ui_qa(project_root, timestamp)
        if ui_qa_result["status"] == "FAIL":
            orchestrator_log("UI QA FAILED. Aborting pipeline.", log_file)
            return {"status": "FAIL", "stage": "UI QA", "timestamp": timestamp}

        # ---------------------------------------------------------
        # Step 7 — Generate MP4 Preview
        # ---------------------------------------------------------
        orchestrator_log("[7/10] Generating MP4 preview...", log_file)
        mp4_path = run_mp4_generation(project_root, timestamp)

        # ---------------------------------------------------------
        # Step 8 — Generate GIF Preview
        # ---------------------------------------------------------
        orchestrator_log("[8/10] Generating GIF preview...", log_file)
        gif_path = run_gif_generation(project_root, timestamp)

        # ---------------------------------------------------------
        # Step 9 — Optional Publishing
        # ---------------------------------------------------------
        orchestrator_log("[9/10] Publishing (optional)...", log_file)
        # publish_to_github(html_path)
        # publish_to_vps(html_path)

        # ---------------------------------------------------------
        # Step 10 — Verification Layer (Local Agent CI/CD)
        # ---------------------------------------------------------
        orchestrator_log("[10/10] Running full verification...", log_file)
        verification_result = verify_all(str(project_root), timestamp)

        if verification_result["status"] == "FAIL":
            orchestrator_log("Verification FAILED. Pipeline halted.", log_file)
            return {"status": "FAIL", "stage": "Verification", "timestamp": timestamp}

        # ---------------------------------------------------------
        # Success
        # ---------------------------------------------------------
        orchestrator_log("=== Pipeline Completed Successfully ===", log_file)
        return {
            "status": "PASS",
            "timestamp": timestamp,
            "html": str(html_path),
            "mp4": str(mp4_path),
            "gif": str(gif_path),
            "verification": verification_result
        }

    except Exception as e:
        orchestrator_log("Pipeline crashed due to an exception:", log_file)
        orchestrator_log(str(e), log_file)
        orchestrator_log(traceback.format_exc(), log_file)
        return {"status": "FAIL", "stage": "Exception", "error": str(e), "timestamp": timestamp}


if __name__ == "__main__":
    result = run_pipeline()
    print(result)
```

---

# What this orchestrator gives you

### **1. Full end‑to‑end automation**
It runs:

- ETL  
- Data QA  
- Visualization  
- HTML generation  
- UI QA  
- MP4 preview  
- GIF preview  
- Publishing  
- Verification layer  

### **2. Local agent as CI/CD auditor**
The orchestrator calls:

```
verify_all()
```

which enforces:

- Code correctness  
- Output correctness  
- Visualization correctness  
- Orchestrator sequencing correctness  
- Folder structure correctness  

### **3. Cloud agent compatibility**
Cloud agent can run:

```
python3 orchestrator.py
```

and return:

- HTML  
- MP4  
- GIF  
- QA reports  
- Verification results  

### **4. Telegram/OpenClaw ready**
The orchestrator returns a structured dictionary that the cloud agent can send back to Telegram.

### **5. Human‑friendly timestamps**
Everything uses:

```
3Mar2026
```

### **6. Strict folder structure compliance**
All paths align with your Phase 1–6 design.

---

If you want, I can now generate the **worker scripts** (`01_fetch_population.py`, `02_transform_rank_top50.py`, etc.) in the same production‑grade style.
