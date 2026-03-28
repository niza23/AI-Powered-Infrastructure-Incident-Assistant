#  AI-Powered Infrastructure Incident Assistant

An intelligent SRE tool that automatically fetches infrastructure alerts from **Prometheus** and **AWS CloudWatch**, analyzes them using **AI (LangChain + OpenAI)**, and delivers actionable root cause analysis and remediation steps to your **Slack** channel — in real time.

---

## 🏗️ Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│   Prometheus        │     │   AWS CloudWatch     │
│   (Firing Alerts)   │     │   (ALARM State)      │
└────────┬────────────┘     └──────────┬───────────┘
         │                             │
         └──────────┬──────────────────┘
                    ▼
         ┌─────────────────────┐
         │   alert_fetcher.py  │  ← Polls every N seconds
         └────────┬────────────┘
                  ▼
         ┌─────────────────────┐
         │   ai_analyzer.py    │  ← LangChain + OpenAI GPT
         │   - Root Cause      │
         │   - Impact          │
         │   - Remediation     │
         │   - Escalate?       │
         └────────┬────────────┘
                  ▼
    ┌─────────────────────────────┐
    │  slack_notifier.py          │  ← Rich Slack Block Kit message
    └─────────────────────────────┘
                  +
    ┌─────────────────────────────┐
    │  FastAPI (main.py)          │  ← REST API for manual trigger & viewing
    │  GET  /incidents            │
    │  POST /trigger              │
    │  GET  /health               │
    └─────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| AI/LLM | OpenAI GPT-3.5 + LangChain |
| Alert Sources | Prometheus, AWS CloudWatch |
| Notifications | Slack Incoming Webhooks |
| API | FastAPI + Uvicorn |
| Containerization | Docker |
| Cloud | AWS (CloudWatch, IAM) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker (optional)
- OpenAI API Key
- Prometheus instance OR AWS CloudWatch access
- Slack Incoming Webhook URL

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/incident-assistant.git
cd incident-assistant
```

### 2. Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your actual keys
nano .env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python main.py
```

The API will be available at: `http://localhost:8000`

---

## 🐳 Docker Setup

### Build and Run
```bash
docker build -t incident-assistant .
docker run -d \
  --env-file .env \
  -p 8000:8000 \
  --name incident-assistant \
  incident-assistant
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service status |
| GET | `/health` | Health check |
| GET | `/incidents` | View latest analyzed incidents |
| POST | `/trigger` | Manually trigger the pipeline |

### Example Response — `/incidents`
```json
{
  "total": 1,
  "incidents": [
    {
      "alert": {
        "source": "Prometheus",
        "name": "HighCPUUsage",
        "severity": "critical",
        "instance": "node-1:9100",
        "summary": "CPU usage above 90%",
        "description": "CPU has been above 90% for 5 minutes"
      },
      "analysis": {
        "severity": "critical",
        "root_cause": "Possible memory leak or CPU-intensive process on node-1 causing resource exhaustion.",
        "impact": "Degraded performance for all services running on node-1; potential pod evictions.",
        "remediation_steps": [
          "Step 1: SSH into node-1 and run `top` to identify the CPU-intensive process",
          "Step 2: Check pod resource usage with `kubectl top pods -A`",
          "Step 3: Restart the offending pod or scale the deployment horizontally"
        ],
        "escalate": true
      }
    }
  ]
}
```

---

## 📲 Slack Notification Preview

```
🔴 Incident Alert: HighCPUUsage
─────────────────────────────────
Source: Prometheus       Severity: CRITICAL
Instance: node-1:9100    Escalate: ⚠️ ESCALATE NOW

🔍 Root Cause:
Possible memory leak or CPU-intensive process causing resource exhaustion.

💥 Impact:
Degraded performance; potential pod evictions on node-1.

🛠️ Remediation Steps:
  1. SSH into node-1 and run `top`
  2. Check pod usage with `kubectl top pods -A`
  3. Restart the offending pod or scale horizontally
```

---

## 📁 Project Structure

```
incident-assistant/
├── main.py               # FastAPI app + background polling
├── alert_fetcher.py      # Fetch alerts from Prometheus & CloudWatch
├── ai_analyzer.py        # LangChain + OpenAI RCA analysis
├── slack_notifier.py     # Slack Block Kit notifications
├── config.py             # Configuration & env vars
├── Dockerfile            # Container setup
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
└── README.md             # Project documentation
```

---

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `PROMETHEUS_URL` | Prometheus base URL | `http://localhost:9090` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key | Optional (uses IAM role) |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Optional (uses IAM role) |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook | Required |
| `POLL_INTERVAL_SECONDS` | Alert polling interval | `60` |

---

## 👩‍💻 Author

**Nidhi Zala** — CloudOps / SRE Engineer  
[LinkedIn](https://linkedin.com/in/nidhi-zala-2307) | [GitHub](https://github.com/niza23)

---

## 📄 License

MIT License — feel free to use and modify.
