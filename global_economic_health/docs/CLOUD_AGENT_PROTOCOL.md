# CLOUD AGENT COMMUNICATION PROTOCOL
**Project:** Global Economic Health Dashboard  
**Document:** Cloud Agent Integration Specification  
**Date:** March 7, 2026  
**Version:** 1.0.0  

---

## 1. Overview

This document specifies how the **cloud agent** communicates with the **local agent**, **background agent**, and **orchestrator** to execute Project 2's ETL, visualization, QA, and verification pipeline.

The protocol ensures:
- Reliable task submission and execution
- Real-time heartbeat monitoring
- Consistent error reporting
- Timestamped result delivery
- Integration with verification layer

---

## 2. Architecture

```
┌─────────────────┐
│  Local Agent    │  Request orchestration, verify outputs
│  (Gatekeeper)   │
└────────┬────────┘
         │ Submits task manifest
         │ (HTTP POST + JSON)
         ▼
┌─────────────────────────────┐
│   Cloud Agent Gateway       │  Receives task, starts orchestrator
│   (HTTP Server)             │  Monitors heartbeat, polls logs
└────────┬────────────────────┘
         │ Spawns orchestrator process
         │ (background shell)
         ▼
┌─────────────────────────────┐
│   Background Agent Worker   │
│   (Orchestrator Process)    │
│   - Runs ETL phases         │
│   - Runs visualization      │
│   - Runs QA & verification  │
│   - Writes heartbeat logs   │
│   - Produces outputs        │
└────────┬────────────────────┘
         │ Heartbeat every 5 sec
         │ (append to log file)
         ▼
┌─────────────────────────────┐
│   Cloud Agent Log Polling   │  Reads heartbeat entries
│   (Monitoring)              │  Detects completion/failure
└─────────────────────────────┘
```

---

## 3. Task Submission Format

### 3.1 Request (Local Agent → Cloud Agent)

**Endpoint:**  
```
POST http://localhost:8000/api/task-queue/submit
```

**Request Headers:**
```
Content-Type: application/json
X-Project-ID: geh
X-Timestamp: 7Mar2026_143022
X-Request-ID: task_7mar2026_001
```

**Request Body (JSON Schema):**
```json
{
  "task_id": "geh_phase1_etl_7mar2026",
  "project_code": "geh",
  "project_root": "C:\\Users\\haujo\\projects\\DEV\\Data_visualization\\global_economic_health",
  "orchestrator_script": "scripts/orchestrator.py",
  "phase": "Phase 1 - ETL",
  "description": "Fetch GDP, population, debt; merge and transform",
  
  "expected_outputs": [
    "csv/raw/gdp_raw_7Mar2026.csv",
    "csv/raw/population_raw_7Mar2026.csv",
    "csv/raw/debt_raw_7Mar2026.csv",
    "csv/processed/macro_merged_7Mar2026.csv",
    "csv/processed/macro_clean_7Mar2026.csv",
    "csv/processed/macro_final_7Mar2026.csv",
    "reports/qa/data_qa_report_7Mar2026.json"
  ],
  
  "verification_rules": {
    "required_files": [
      "csv/processed/macro_final_7Mar2026.csv"
    ],
    "schema_checks": {
      "macro_final": [
        "country_name", "country_code", "year",
        "gdp_usd", "population", "debt_total_usd",
        "gdp_per_capita", "debt_to_gdp", "gdp_growth"
      ]
    },
    "value_ranges": {
      "gdp_usd": {"min": 0, "max": 100000000000000},
      "debt_to_gdp": {"min": 0, "max": 10}
    },
    "row_count_tolerance": 0.15
  },
  
  "timeout_seconds": 300,
  "max_retries": 1,
  "priority": "HIGH"
}
```

### 3.2 Response (Cloud Agent → Local Agent)

**Success Response (HTTP 202 - Accepted):**
```json
{
  "status": "ACCEPTED",
  "task_id": "geh_phase1_etl_7mar2026",
  "status_url": "http://localhost:8000/api/tasks/geh_phase1_etl_7mar2026",
  "heartbeat_log": "C:\\...\\reports\\logs\\orchestrator_log_7Mar2026.txt",
  "orchestrator_pid": 12345,
  "timestamp": "2026-03-07T14:30:22Z",
  "message": "Task submitted. Monitor heartbeat at status_url"
}
```

**Error Response (HTTP 400 - Bad Request):**
```json
{
  "status": "ERROR",
  "error_code": "INVALID_PROJECT_ROOT",
  "message": "Project root directory does not exist",
  "task_id": "geh_phase1_etl_7mar2026",
  "timestamp": "2026-03-07T14:30:22Z"
}
```

---

## 4. Heartbeat Mechanism

### 4.1 Background Agent Heartbeat

**Location:** Orchestrator writes heartbeat entries to log file every 5 seconds

**Log File Path:**
```
reports/logs/orchestrator_log_<timestamp>.txt
```

**Heartbeat Entry Format:**
```
[2026-03-07 14:32:10] [HEARTBEAT] orchestrator_pid=12345, timestamp=2026-03-07T14:32:10Z, phase=ETL, step=Fetch GDP, status=IN_PROGRESS, stage_progress=1/5
[2026-03-07 14:32:15] [HEARTBEAT] orchestrator_pid=12345, timestamp=2026-03-07T14:32:15Z, phase=ETL, step=Fetch GDP, status=IN_PROGRESS, stage_progress=1/5
[2026-03-07 14:32:20] [HEARTBEAT] orchestrator_pid=12345, timestamp=2026-03-07T14:32:20Z, phase=ETL, step=Fetch Population, status=IN_PROGRESS, stage_progress=2/5
[2026-03-07 14:32:25] [HEARTBEAT] orchestrator_pid=12345, timestamp=2026-03-07T14:32:25Z, phase=ETL, step=Fetch Population, status=IN_PROGRESS, stage_progress=2/5
```

### 4.2 Cloud Agent Heartbeat Monitoring

**Cloud Agent Monitoring Loop:**
```python
def monitor_heartbeat(task_id, heartbeat_log_path, timeout=60):
    """
    Poll heartbeat log for task progress.
    
    Returns:
    - "IN_PROGRESS": Task is running, heartbeat within timeout
    - "TIMEOUT": No heartbeat received for 60 seconds
    - "COMPLETE": Task finished (final log entry)
    - "FAILED": Task failed (error in log)
    """
    last_heartbeat = None
    
    while True:
        # Read last 10 lines of log
        lines = tail(heartbeat_log_path, 10)
        
        # Check for latest heartbeat
        for line in reversed(lines):
            if "[HEARTBEAT]" in line:
                last_heartbeat = parse_timestamp(line)
                break
        
        # Check timeout
        if last_heartbeat:
            elapsed = now() - last_heartbeat
            if elapsed > timeout:
                return "TIMEOUT"
        
        # Check for completion
        if any("[COMPLETE]" in line for line in lines):
            return "COMPLETE"
        
        if any("[FAILED]" in line for line in lines):
            return "FAILED"
        
        # Sleep before next check
        sleep(5)
```

### 4.3 Heartbeat Interval

- **Background Agent:** Emit heartbeat every **5 seconds**
- **Cloud Agent Polling:** Check every **5 seconds**
- **Cloud Agent Timeout:** Fail if no heartbeat for **60 seconds**

---

## 5. Status Query API

### 5.1 Status Endpoint

**Endpoint:**
```
GET http://localhost:8000/api/tasks/{task_id}/status
```

**Response:**
```json
{
  "task_id": "geh_phase1_etl_7mar2026",
  "status": "IN_PROGRESS",
  "phase": "Phase 1 - ETL",
  "current_step": "Fetch GDP",
  "step_index": 1,
  "total_steps": 5,
  "progress_percent": 20,
  "last_heartbeat": "2026-03-07T14:32:25Z",
  "elapsed_seconds": 125,
  "estimated_remaining_seconds": 500,
  "log_path": "C:\\...\\reports\\logs\\orchestrator_log_7Mar2026.txt",
  "timestamp": "2026-03-07T14:32:30Z"
}
```

---

## 6. Orchestrator Communication

### 6.1 Orchestrator Result Format

**On Success (orchestrator completes):**

Orchestrator writes final result to log:
```
[2026-03-07 14:55:22] [COMPLETE] status=PASS, timestamp=7Mar2026, html=reports/html/global_economic_health_dashboard_7Mar2026.html, gif=reports/media/global_economic_health_preview_7Mar2026.gif, mp4=reports/media/global_economic_health_preview_7Mar2026.mp4, verification_result=PASS
```

Also writes JSON summary:
```json
{
  "result_file": "reports/orchestrator_result_7Mar2026.json"
}
```

Content of JSON file:
```json
{
  "task_id": "geh_phase1_etl_7mar2026",
  "status": "PASS",
  "timestamp": "7Mar2026",
  "duration_seconds": 1502,
  "timestamp_iso": "2026-03-07T14:55:22Z",
  
  "outputs": {
    "csv_final": "csv/processed/macro_final_7Mar2026.csv",
    "html_dashboard": "reports/html/global_economic_health_dashboard_7Mar2026.html",
    "gif_preview": "reports/media/global_economic_health_preview_7Mar2026.gif",
    "mp4_preview": "reports/media/global_economic_health_preview_7Mar2026.mp4"
  },
  
  "verification": {
    "code_structure": "PASS",
    "outputs": "PASS",
    "visualizations": "PASS",
    "orchestrator_flow": "PASS",
    "overall": "PASS"
  },
  
  "qa_results": {
    "data_qa": {"status": "PASS", "report": "reports/qa/data_qa_report_7Mar2026.json"},
    "ui_qa": {"status": "PASS", "report": "reports/qa/ui_qa_report_7Mar2026.md"},
    "code_review": {"status": "PASS", "report": "reports/qa/code_review_7Mar2026.md"}
  }
}
```

**On Failure:**

Orchestrator writes error information:
```
[2026-03-07 14:45:12] [FAILED] phase=Visualization, step=Build Bubble Map, error=Missing GDP data for 5 countries, error_code=DATA_MERGE_ERROR
```

JSON result file:
```json
{
  "task_id": "geh_phase1_etl_7mar2026",
  "status": "FAIL",
  "timestamp": "7Mar2026",
  "duration_seconds": 892,
  
  "error": {
    "phase": "Visualization",
    "step": "Build Bubble Map",
    "error_code": "DATA_MERGE_ERROR",
    "message": "Missing GDP data for 5 countries in final merge",
    "affected_data": ["gdp_raw_7Mar2026.csv"],
    "remediation": "Re-run ETL phase with data validation enabled"
  }
}
```

### 6.2 Cloud Agent Result Retrieval

**After task completion, cloud agent:**

1. Reads result JSON file
2. Retrieves all output file paths
3. Transfers outputs back to local agent
4. Verifies output integrity
5. Returns completion notification

---

## 7. Error Notification Format

### 7.1 Notification on Failure

**Telegram Message:**
```
❌ Global Economic Health Dashboard - Phase 1 FAILED

Task ID: geh_phase1_etl_7mar2026
Phase: Phase 1 - ETL
Step: Build Bubble Map
Duration: 14m 52s

Error: Missing GDP data for 5 countries in final merge
Code: DATA_MERGE_ERROR

Logs: C:\...\reports\logs\orchestrator_log_7Mar2026.txt

Remediation: Re-run ETL phase with data validation enabled
```

**Local Log Entry:**
```
[ERROR] Task geh_phase1_etl_7mar2026 failed at Visualization phase
[ERROR] Error code: DATA_MERGE_ERROR
[ERROR] Root cause: Missing GDP data
[ERROR] See reports/logs/orchestrator_log_7Mar2026.txt for full details
```

---

## 8. Retry Logic

### 8.1 Automatic Retry on Timeout

If orchestrator doesn't send heartbeat for 60 seconds:

1. Cloud agent logs timeout
2. Terminates orchestrator process
3. Waits 10 seconds
4. Re-submits task (if max_retries > 0)
5. Increments retry counter

**Max Retries:** Configurable per task (default: 1)

### 8.2 Automatic Retry on API Failure

Background agent (orchestrator) handles API retries internally:

- **Max Retries:** 3 (configurable in settings.yaml)
- **Backoff:** Exponential (2s, 4s, 8s)
- **On Permanent Failure:** Log error and stop

---

## 9. Timeout Handling

### 9.1 Phase Timeouts

Each phase has a timeout defined in `config/settings.yaml`:

- **ETL Phase:** 300 seconds (5 minutes)
- **Visualization Phase:** 400 seconds (6.7 minutes)
- **Preview Generation:** 300 seconds (5 minutes)
- **Verification:** 120 seconds (2 minutes)

### 9.2 Step Timeouts

Each ETL/viz step has a timeout (e.g., "Fetch GDP": 60s)

If a step exceeds its timeout:
1. Orchestrator logs timeout
2. Terminates the step process
3. Returns FAIL with timeout error
4. Cloud agent marks task as FAILED

### 9.3 Overall Task Timeout

If entire task exceeds `task_timeout_seconds` from submission:
1. Cloud agent terminates orchestrator
2. Logs timeout
3. Marks task as FAILED
4. Returns error to local agent

---

## 10. Log Polling Strategy

### 10.1 Efficient Log Polling

Cloud agent uses tail-based monitoring (not full file read):

```python
def tail(file_path, n_lines=20):
    """Read last N lines of file efficiently"""
    with open(file_path, 'rb') as f:
        # Seek to end of file
        f.seek(0, 2)
        file_size = f.tell()
        
        # Read backwards in chunks
        buffer_size = 4096
        pos = file_size
        lines = []
        
        while len(lines) < n_lines and pos > 0:
            pos = max(0, pos - buffer_size)
            f.seek(pos)
            chunk = f.read(buffer_size)
            lines = chunk.decode().split('\n') + lines
        
        return lines[-n_lines:]
```

### 10.2 Polling Frequency

- Poll every **5 seconds**
- Read last **20 lines** of log
- Check for heartbeat, completion, or error

---

## 11. Integration Points

### 11.1 Local Agent Integration

Local agent code to submit task:
```python
import requests

def submit_task_to_cloud(task_manifest):
    """Submit orchestration task to cloud agent"""
    response = requests.post(
        "http://localhost:8000/api/task-queue/submit",
        json=task_manifest,
        headers={"X-Project-ID": "geh"}
    )
    return response.json()
```

### 11.2 Background Agent Integration

Orchestrator code to emit heartbeat:
```python
def orchestrator_log(message, task_id):
    """Log message with timestamp for cloud monitoring"""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {message}"
    
    with open(f"reports/logs/orchestrator_log_{timestamp.split('T')[0]}.txt", "a") as f:
        f.write(log_entry + "\n")
        f.flush()  # Ensure cloud agent sees it immediately
```

---

## 12. Example Workflow

```
1. Local Agent creates task manifest
   ↓
2. Local Agent sends HTTP POST to Cloud Agent
   ↓
3. Cloud Agent responds with 202 ACCEPTED
   ↓
4. Cloud Agent spawns orchestrator process
   ↓
5. Orchestrator runs Phase 1 ETL:
   - Fetch GDP (emits heartbeat every 5s)
   - Fetch Population
   - Fetch Debt
   ↓
6. Cloud Agent polls heartbeat log every 5s
   - Detects "IN_PROGRESS" status
   - Calculates estimated time remaining
   ↓
7. Orchestrator finishes Phase 1, runs Phases 2-5
   ↓
8. Orchestrator completes, writes FINAL result to log
   ↓
9. Cloud Agent detects completion, reads result JSON
   ↓
10. Cloud Agent returns outputs to Local Agent
    ↓
11. Local Agent verifies outputs, approves or rejects
```

---

## 13. Error Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| `INVALID_PROJECT_ROOT` | Project folder doesn't exist | Check project_root path |
| `SCRIPT_NOT_FOUND` | Orchestrator script missing | Verify scripts/ directory |
| `API_TIMEOUT` | World Bank API timeout | Retry (automatic) |
| `DATA_MERGE_ERROR` | Missing data after merge | Re-run ETL with debugging |
| `QA_FAILURE` | QA validation failed | Check QA report |
| `VIZ_RENDERING_ERROR` | Plotly visualization failed | Check input data |
| `ORCHESTRATOR_TIMEOUT` | Task exceeded timeout | Increase timeout, check resource usage |
| `PROCESS_KILLED` | Orchestrator killed externally | Check system logs |

---

## 14. Security Considerations

- All communications over localhost HTTP (no encryption needed for local execution)
- Task manifest validated before execution
- File paths sanitized to prevent directory traversal
- Orchestrator runs with same user/permissions as local agent
- Secrets (API keys) stored in environment variables, not in JSON

---

## 15. Monitoring and Observability

**Cloud Agent maintains dashboard showing:**
- Currently running tasks
- Task status and progress
- Heartbeat health
- Completed tasks and results
- Failed tasks with error details
- Resource usage (CPU, memory, disk)

**Metrics Collected:**
- Task submission rate
- Task success/failure rate
- Average task duration
- Heartbeat response time
- API call success rate
- Data validation errors

---

## 16. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-07 | Initial protocol specification |

---

**Author:** Project 2 Team  
**Last Updated:** March 7, 2026  
**Next Review:** June 7, 2026
