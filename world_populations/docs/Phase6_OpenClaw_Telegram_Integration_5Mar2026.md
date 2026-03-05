Here is your complete **Phase 6 OpenClaw + Telegram Integration** Markdown file, ready to save as:

```
data_visualization/World_population/docs/Phase6_OpenClaw_Telegram_Integration_5Mar2026.md
```

It defines the full remote‑control architecture for your agent‑orchestrated visualization pipeline, including Telegram bot commands, OpenClaw routing, security, deployment, and notification formatting. It is written so **VS Code, your orchestrator, and your cloud agents** can execute this reliably.

---

# Phase 6 — OpenClaw + Telegram Integration (5 Mar 2026)

## 1. Purpose of Phase 6
This phase defines how the entire world‑population dashboard pipeline can be **remotely controlled** using:

- **Telegram Bot** (user interface)
- **OpenClaw** (agent execution layer)
- **Orchestrator** (pipeline automation)

The goal is to allow John to trigger the full workflow from anywhere—desktop, mobile, or cloud—without opening VS Code or SSH. This enables:

- Remote execution  
- Remote QA checks  
- Remote publishing  
- Remote preview retrieval  
- Automated notifications  

This phase completes the full agentic architecture.

---

## 2. System Architecture Overview

### 2.1 Components

- **Telegram Bot**  
  Receives commands from John and sends results back.

- **OpenClaw**  
  Executes commands, runs scripts, manages agents, and returns outputs.

- **Orchestrator**  
  Runs the full pipeline: ETL → QA → Visualization → HTML → GIF/MP4 → Publish.

- **VS Code Local Environment**  
  Used for development and debugging.

- **VPS Cloud Environment**  
  Used for production execution and Telegram integration.

### 2.2 High‑Level Flow

```
[John on Telegram]
      ↓
Telegram Bot
      ↓
OpenClaw Command Router
      ↓
orchestrator.py
      ↓
QA Agents + Scripts
      ↓
Outputs (HTML, MP4, GIF, QA reports)
      ↓
Telegram Bot sends results back to John
```

---

## 3. Telegram Bot Design

### 3.1 Bot Requirements

- Must accept commands only from authorized user (John).
- Must support sending:
  - Text messages  
  - HTML links  
  - MP4 files  
  - GIF files  
  - QA reports  
  - Screenshots  

### 3.2 Bot Token Storage

Store token securely in:

```
config/settings.yaml
```

Example:

```yaml
telegram:
  bot_token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_CHAT_ID"
```

Never commit this file to GitHub.

---

## 4. Supported Telegram Commands

### 4.1 Core Commands

```
/run_population_dashboard
```
Runs the full orchestrator pipeline.

```
/get_latest_preview
```
Returns the latest MP4 + GIF preview.

```
/get_latest_html
```
Returns the latest HTML link or file.

```
/check_data
```
Runs Data QA agent only.

```
/check_ui
```
Runs UI QA agent only.

```
/check_code
```
Runs Code Review agent only.

```
/check_all
```
Runs all QA agents without generating visualization.

---

## 5. OpenClaw Command Routing

### 5.1 Command Router File

```
qa_agents/agent_orchestrator.py
```

### 5.2 Responsibilities

- Receive Telegram command  
- Map to correct script or agent  
- Execute with correct timestamp  
- Capture outputs  
- Return results to Telegram  

### 5.3 Routing Table

| Telegram Command | Action |
|------------------|--------|
| `/run_population_dashboard` | Run full orchestrator |
| `/get_latest_preview` | Return latest MP4 + GIF |
| `/get_latest_html` | Return latest HTML |
| `/check_data` | Run Data QA agent |
| `/check_ui` | Run UI QA agent |
| `/check_code` | Run Code Review agent |
| `/check_all` | Run all QA agents |

---

## 6. Orchestrator Integration

### 6.1 Orchestrator Entry Point

```
python3 scripts/orchestrator.py
```

### 6.2 Orchestrator Must Return

- Status (PASS/FAIL)
- Timestamp used
- File paths:
  - HTML  
  - MP4  
  - GIF  
  - QA reports  
  - Screenshot  

### 6.3 OpenClaw Must Package These Into Telegram Messages

---

## 7. Telegram Notification Formatting

### 7.1 Success Message Format

```
World Population Dashboard — SUCCESS (3Mar2026)

HTML Report:
<URL or file attached>

MP4 Preview:
[file attached]

GIF Preview:
[file attached]

QA Reports:
- Data QA: PASS
- UI QA: PASS
- Code Review: PASS

Timestamp: 3Mar2026
```

### 7.2 Failure Message Format

```
World Population Dashboard — FAILED (3Mar2026)

Failure Point:
UI QA Agent — Flags not rendering correctly

QA Report:
[file attached]

Please review the visualization script.
```

---

## 8. Security Requirements

### 8.1 Authorized User Only

The bot must verify:

- `chat_id == John’s chat_id`

If not:

```
Unauthorized user. Access denied.
```

### 8.2 No Arbitrary Code Execution

Only predefined commands allowed.

### 8.3 No File Uploads from Telegram

All data must originate from ETL pipeline.

---

## 9. Deployment Strategy

### 9.1 VPS Setup

- Python 3.10+  
- FFmpeg installed  
- Playwright installed (for UI QA)  
- Cron optional  
- Systemd service for bot  

### 9.2 Directory Structure on VPS

```
/opt/world_population/
    ├── scripts/
    ├── qa_agents/
    ├── csv/
    ├── reports/
    ├── config/
    └── venv/
```

### 9.3 Auto‑Restart Bot

Use systemd:

```
systemctl enable telegram_bot
systemctl start telegram_bot
```

---

## 10. Logging and Monitoring

### 10.1 Log File

```
reports/logs/orchestrator_log_<3Mar2026>.txt
```

### 10.2 Telegram Alerts for Errors

- API failures  
- QA failures  
- Encoding failures  
- Missing files  

---

## 11. Phase 6 To‑Do List (5 Mar 2026)

- Create Telegram bot  
- Add bot token + chat ID to settings.yaml  
- Implement OpenClaw command router  
- Implement Telegram message formatting  
- Implement file attachment logic  
- Implement security checks  
- Deploy bot to VPS  
- Test all commands  
- Validate remote execution end‑to‑end  

---

