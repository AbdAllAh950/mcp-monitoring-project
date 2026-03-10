<div align="center">

# MCP Monitoring & Auto-Diagnostics System

**Real-time monitoring, anomaly detection, and automated remediation**
**for Apache Kafka · Apache Spark · HDFS big data pipelines**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Prometheus](https://img.shields.io/badge/Prometheus-2.51-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-10.4-F46800?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-33%20passed-brightgreen?style=for-the-badge)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

> **No human intervention required.**
> The system detects anomalies, diagnoses root causes, and fixes itself — automatically.
> Ask it anything in plain English with the built-in AI chat mode.

</div>

---

## Overview

This project is a **production-grade monitoring and auto-diagnostics platform** built for big data pipelines. It simulates a real-world environment with **Apache Kafka**, **Apache Spark**, and **HDFS** — all continuously exporting live metrics to **Prometheus**, visualized in **Grafana**, and protected by an intelligent **MCP (Model Context Protocol) Server** that:

1. **Receives** alerts from Alertmanager via webhook
2. **Diagnoses** the root cause automatically using YAML runbooks
3. **Remediates** the problem by executing fix playbooks via Docker API
4. **Logs** every action taken with full audit history
5. **Exposes an AI agent** for natural language cluster management

The **Remediation Agent CLI** provides an interactive terminal interface for live monitoring, manual interventions, metric queries, AI-powered diagnosis, and conversational AI chat — making it ideal for a live demo or operations screen.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Simulated Big Data Pipeline                        │
│                                                                        │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│   │  Kafka Exporter │  │  Spark Exporter │  │  HDFS Exporter  │      │
│   │   (Python)      │  │   (Python)      │  │   (Python)      │      │
│   │   port :8001    │  │   port :8002    │  │   port :8003    │      │
│   └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │
└────────────┼────────────────────┼────────────────────┼───────────────┘
             │  /metrics          │  /metrics          │  /metrics
             ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     Prometheus  :9090                                 │
│   • Scrapes all exporters every 15 seconds                            │
│   • Evaluates 12 alert rules continuously                             │
│   • Stores time-series metric data                                    │
└──────────────────────────┬───────────────────────────────────────────┘
                           │  Alert fired (threshold breached)
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    Alertmanager  :9093                                │
│   • Groups and deduplicates alerts                                    │
│   • Routes by severity (critical / warning)                           │
│   • Sends webhook POST to MCP Server                                  │
└──────────────────────────┬───────────────────────────────────────────┘
                           │  POST /webhook/alert
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     MCP Server  :8888                                 │
│   • FastAPI application (Model Context Protocol)                      │
│   • Receives and stores all firing/resolved alerts                    │
│   • Auto-triggers remediation engine per alert action label           │
│   • 11 YAML runbooks for structured diagnosis                         │
│   • Exposes 11 REST tools for agents and automation                   │
│   • Exposes its own /metrics endpoint (scraped by Prometheus)         │
└──────────────┬────────────────────────────┬─────────────────────────┘
               │                            │
               ▼                            ▼
┌──────────────────────┐      ┌─────────────────────────────────┐
│   Grafana  :3000     │      │    Remediation Agent CLI        │
│                      │      │                                 │
│  • 11-panel dashboard│      │  • Service health table         │
│  • Live time-series  │      │  • Active alerts view           │
│  • Color thresholds  │      │  • Remediation history          │
│  • Auto-provisioned  │      │  • Prometheus metric query      │
│                      │      │  • Manual trigger               │
│                      │      │  • Live monitor (10s refresh)   │
│                      │      │  • AI diagnosis (option 7)      │
│                      │      │  • AI chat mode (option 8)      │
└──────────────────────┘      └─────────────────────────────────┘
```

---

## Key Features

### Fully Dockerized Stack
One `docker compose up` command launches the entire infrastructure: Prometheus, Grafana, Alertmanager, Node Exporter, cAdvisor, and all 3 custom metric exporters.

### Live Grafana Dashboard (11 Panels)
- Kafka Consumer Lag (time-series with spike detection)
- Kafka Broker Status (up/down stat panel)
- Kafka Messages Per Second (rate graph)
- Spark Active Tasks (stat with thresholds)
- Spark Memory Usage % (gauge, 0–100%)
- Spark Failed Jobs (critical stat)
- HDFS Disk Usage % (gauge, 0–100%)
- HDFS DataNode Status (up/down stat)
- Active Alerts Table (live PromQL)
- Host CPU Usage (time-series)
- Host Memory Usage (time-series)

### 12 Prometheus Alert Rules
Covering Kafka, Spark, HDFS, and host-level anomalies — each with a `severity` label and a specific `action` label used by the remediation engine.

### MCP Server with 11 REST Tools
A custom FastAPI application implementing the Model Context Protocol pattern. It acts as the brain — receiving alerts, running fix playbooks, and exposing monitoring tools that any AI agent or automation can call.

### 11 YAML Runbooks
Every alert has a structured runbook covering: symptom description, diagnosis steps, and remediation actions with safety classification. The AI agent reads these to explain and act on issues.

### Auto-Remediation Engine
When an alert fires, the MCP server immediately runs a specific fix playbook via the Docker API:
- **Kafka lag spike** → restart consumer group / scale consumers
- **Spark job failure** → retry from last checkpoint
- **Spark memory high** → increase executor memory config
- **HDFS disk full** → clean up old temp files and archives
- **DataNode down** → restart DataNode and trigger replication
- **Broker down** → restart Kafka broker and reassign partitions

### AI Diagnosis (Option 7)
Reads all active alerts and matching runbooks, then sends them to an LLM (Qwen via OpenRouter) for structured analysis: most critical issue, root cause, recommended action, business impact, and cascade risk.

### AI Chat Mode (Option 8)
Full conversational natural language interface backed by live MCP tool data. Ask questions, get recommendations, and trigger remediations — all in plain English.

### 33 Pytest Tests
Full test coverage across endpoints, alert rule validation, and runbook completeness.

### Full Observability Loop
The MCP Server itself exports Prometheus metrics (`mcp_alerts_received_total`, `mcp_remediations_triggered_total`, `mcp_remediation_duration_seconds`) — so you can monitor the monitoring system.

---

## Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Python **3.11+**
- macOS or Linux (tested on macOS Apple Silicon M2)

### 1. Clone the repository
```bash
git clone https://github.com/AbdAllAh950/mcp-monitoring-project.git
cd mcp-monitoring-project
```

### 2. Install Python dependencies
```bash
make setup
```

### 3. Start the full Docker monitoring stack
```bash
cd monitoring
docker compose up -d --build
```
> First run takes 3–5 minutes to pull images and build exporters.

### 4. Start the MCP Server
```bash
# Open a new terminal tab — keep this running
cd mcp-server
python3 mcp_server.py
```
Wait for: `Uvicorn running on http://0.0.0.0:8888`

### 5. Start the Remediation Agent CLI
```bash
# Open another new terminal tab
cd remediation-agent
python3 agent.py
```

### 6. Open your dashboards
```bash
make demo
```

| Service | URL | Login |
|---|---|---|
| Grafana Dashboard | http://localhost:3000 | `admin` / `admin123` |
| Prometheus UI | http://localhost:9090 | — |
| MCP Server API Docs | http://localhost:8888/docs | — |
| Alertmanager UI | http://localhost:9093 | — |
| Kafka Metrics | http://localhost:8001/metrics | — |
| Spark Metrics | http://localhost:8002/metrics | — |
| HDFS Metrics | http://localhost:8003/metrics | — |

---

## Alert Rules Reference

| Alert | Service | Severity | Trigger Condition | Auto-Remediation |
|---|---|---|---|---|
| `KafkaConsumerLagHigh` | Kafka | Warning | `lag > 5,000` for 1 min | Restart consumer group |
| `KafkaConsumerLagCritical` | Kafka | Critical | `lag > 15,000` for 2 min | Scale consumer instances |
| `KafkaBrokerDown` | Kafka | Critical | `broker_up == 0` for 30s | Restart Kafka broker (Docker API) |
| `KafkaUnderReplicatedPartitions` | Kafka | Warning | `under_replicated > 0` for 1 min | Check replication factor |
| `SparkJobFailed` | Spark | Critical | `failed_jobs > 0` instantly | Retry job from checkpoint |
| `SparkExecutorMemoryHigh` | Spark | Warning | `memory > 85%` for 2 min | Increase executor memory |
| `SparkActiveTasksLow` | Spark | Warning | `active_tasks < 1` for 3 min | Check Spark cluster |
| `HDFSDiskSpaceHigh` | HDFS | Warning | `disk > 80%` for 2 min | Clean up old files |
| `HDFSDataNodeDown` | HDFS | Critical | `datanode_up == 0` for 1 min | Restart DataNode (Docker API) |
| `HDFSReplicationLow` | HDFS | Warning | `under_replicated > 100` for 2 min | Trigger replication recovery |
| `HighCPUUsage` | System | Warning | `cpu > 80%` for 2 min | Investigate high-CPU processes |
| `HighMemoryUsage` | System | Warning | `memory > 85%` for 2 min | Check for memory leaks |

---

## MCP Server API Reference

All tools available at `http://localhost:8888/docs` (Swagger UI):

| Tool | Method | Endpoint | Description |
|---|---|---|---|
| Health Check | `GET` | `/health` | Server liveness check |
| Alert Webhook | `POST` | `/webhook/alert` | Receives Alertmanager webhooks |
| Active Alerts | `GET` | `/tools/get_active_alerts` | All currently firing alerts |
| Service Health | `GET` | `/tools/get_service_health` | Health summary per service |
| Query Prometheus | `POST` | `/tools/query_prometheus` | Execute any PromQL query |
| Get Metrics | `GET` | `/tools/get_metrics` | Current metric snapshot |
| Remediation History | `GET` | `/tools/get_remediation_history` | Full audit log of all actions |
| Trigger Remediation | `POST` | `/tools/trigger_remediation` | Manually trigger a fix |
| List Runbooks | `GET` | `/tools/list_runbooks` | List all 11 runbooks |
| Get Runbook | `GET` | `/tools/get_runbook` | Get runbook for a specific alert |
| MCP Own Metrics | `GET` | `/metrics` | Prometheus metrics about MCP server |

### Example: Fire a manual alert for demo
```bash
curl -X POST http://localhost:8888/webhook/alert \
  -H "Content-Type: application/json" \
  -d '{
    "receiver": "mcp-webhook",
    "status": "firing",
    "alerts": [{
      "status": "firing",
      "labels": {
        "alertname": "HDFSDataNodeDown",
        "severity": "critical",
        "service": "hdfs",
        "action": "restart_datanode"
      },
      "annotations": {
        "summary": "HDFS DataNode is DOWN",
        "description": "DataNode unreachable for 1 minute"
      }
    }],
    "groupLabels": {},
    "commonLabels": {},
    "commonAnnotations": {},
    "externalURL": ""
  }'
```

---

## AI Agent Features

The Remediation Agent CLI includes two AI-powered modes built on OpenRouter (Qwen/GPT-4o compatible).

### Option 7 — AI Diagnosis

Reads all active alerts and their matching runbooks, then produces a structured LLM analysis:
- Most critical issue identified
- Likely root cause explained
- Exact remediation action recommended
- Business impact if unresolved
- Cascade risk warning

### Option 8 — AI Chat Mode

Full conversational natural language interface. The AI has access to live MCP tool data on every message.

```
You: What alerts are firing right now?
AI:  2 active alerts:
     - KafkaBrokerDown [critical]: Broker unreachable for 30 seconds
     - KafkaConsumerLagHigh [warning]: Consumer group lagging 14,123 on topic transactions
     Data source: GET /tools/get_active_alerts

You: What should I do about the kafka broker?
AI:  1. Verify broker status via kafka_broker_up metric
     2. Review remediation history — restart was already attempted
     3. Trigger restart_broker via /tools/trigger_remediation
     4. Follow KafkaBrokerDown runbook for deep diagnostics
     Data source: GET /tools/get_active_alerts, get_service_health, get_remediation_history

You: Fix it
AI:  Triggered restart_broker for KafkaBrokerDown
     Status: executed
     Action taken: POST /tools/trigger_remediation
```

### Setup for AI features

Create `remediation-agent/.env`:
```bash
cp remediation-agent/.env.example remediation-agent/.env
# Add your OpenRouter API key — free at https://openrouter.ai
```

Contents:
```
OPENAI_API_KEY=sk-or-v1-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=qwen/qwen3-8b
```

---

## How Auto-Remediation Works

```
Prometheus detects: kafka_consumer_lag > 5000 for 1 minute
        ↓
Alertmanager fires: KafkaConsumerLagHigh (severity=warning, action=restart_consumer)
        ↓
MCP Server receives POST /webhook/alert
        ↓
Runbook lookup: KafkaConsumerLagHigh → symptom, diagnosis steps, safe actions
        ↓
Remediation Engine reads alert.labels.action = "restart_consumer"
        ↓
Runs playbook:
  Step 1: Detect affected consumer group via Prometheus query
  Step 2: Pause consumer group temporarily
  Step 3: Reset consumer offset to latest checkpoint
  Step 4: Restart consumer group
  Step 5: Verify lag is decreasing
        ↓
Result logged: { success: true, duration: 2.0s, steps: [...] }
        ↓
Alert auto-resolves when lag drops below 5000
```

---

## Running Tests

```bash
# Start MCP server first, then:
python3 -m pytest tests/ -v
```

33 tests across 3 modules — all passing:

| Module | Tests | What It Covers |
|---|---|---|
| `test_alert_rules.py` | 12 | Every alert has severity, service, action, expr, and summary |
| `test_mcp_endpoints.py` | 11 | Health, webhook, all 9 tools, Prometheus format |
| `test_runbook_coverage.py` | 10 | Every runbook has symptom, diagnosis steps, and safe actions |

---

## Live Demo Guide

```bash
# Tab 1: Docker stack already running in background

# Tab 2: MCP Server
cd mcp-server && python3 mcp_server.py

# Tab 3: Agent
cd remediation-agent && python3 agent.py
# Press 6 for live auto-refresh monitor
# Press 7 for AI diagnosis
# Press 8 for AI chat mode
```

Open all demo tabs at once:
```bash
make demo
# Opens: Grafana, Prometheus /alerts, MCP API /docs, Alertmanager
```

Trigger a live demo alert:
```bash
curl -X POST http://localhost:8888/webhook/alert \
  -H "Content-Type: application/json" \
  -d '{"receiver":"mcp-webhook","status":"firing",
    "alerts":[{"status":"firing",
      "labels":{"alertname":"HDFSDataNodeDown","severity":"critical",
                "service":"hdfs","action":"restart_datanode"},
      "annotations":{"summary":"HDFS DataNode is DOWN",
                     "description":"DataNode unreachable for 1 minute"}}],
    "groupLabels":{},"commonLabels":{},"commonAnnotations":{},"externalURL":""}'
```

Watch the live monitor: HDFS flips from HEALTHY to CRITICAL, remediation runs, status shows completed — all within 10 seconds.

---

## Project Structure

```
mcp-monitoring-project/
│
├── Makefile                                 # Control panel: setup/start/stop/demo
├── README.md
├── .gitignore
│
├── monitoring/                              # Full Docker monitoring stack
│   ├── docker-compose.yml                   # 8 services in one file
│   ├── prometheus/
│   │   ├── prometheus.yml                   # Scrape configs for all targets
│   │   ├── alert_rules.yml                  # 12 alert rules (Kafka/Spark/HDFS/System)
│   │   └── alertmanager.yml                 # Webhook routing to MCP Server
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/prometheus.yml   # Auto-connects Prometheus datasource
│       │   └── dashboards/dashboards.yml    # Auto-loads dashboard on startup
│       └── dashboards/
│           └── mcp-monitoring.json          # 11-panel live dashboard definition
│
├── exporters/                               # Metric simulators
│   ├── kafka_exporter.py                    # Kafka: lag, broker, messages, partitions
│   ├── Dockerfile.kafka
│   ├── spark_exporter.py                    # Spark: tasks, memory, jobs, executors
│   ├── Dockerfile.spark
│   ├── hdfs_exporter.py                     # HDFS: disk, datanodes, blocks, files
│   └── Dockerfile.hdfs
│
├── mcp-server/                              # MCP Server (the brain)
│   ├── mcp_server.py                        # FastAPI app: webhook + tools + remediation
│   ├── runbooks.yaml                        # 11 structured runbooks for every alert
│   └── requirements.txt
│
├── remediation-agent/                       # Interactive CLI agent
│   ├── agent.py                             # Rich terminal UI with AI chat (options 1-8)
│   ├── .env.example                         # Template for OpenRouter API key
│   └── requirements.txt
│
└── tests/                                   # 33 pytest tests
    ├── conftest.py
    ├── test_alert_rules.py                  # 12 tests: alert rule validation
    ├── test_mcp_endpoints.py                # 11 tests: REST API endpoints
    └── test_runbook_coverage.py             # 10 tests: runbook completeness
```

---

## Makefile Commands

```bash
make setup          # Install all Python dependencies for MCP server and agent
make start          # Start Docker stack + MCP server
make stop           # Stop all services cleanly
make restart        # Stop then start everything
make logs           # Follow all Docker container logs live
make mcp-server     # Start only the MCP server
make agent          # Start only the Remediation Agent CLI
make status         # Check health of all services
make demo           # Open all 4 demo URLs in your browser
make clean          # Stop everything and delete all Docker volumes
make incident-kafka # Simulate Kafka broker failure
make incident-spark # Simulate Spark failure
make incident-hdfs  # Simulate HDFS failure
make incident-stop  # Recover all services
```

---

## Tech Stack

| Category | Technology | Version |
|---|---|---|
| Metrics & Alerting | Prometheus | 2.51.0 |
| Visualization | Grafana | 10.4.2 |
| Alert Routing | Alertmanager | 0.27.0 |
| MCP Server Framework | FastAPI + Uvicorn | 0.115 / 0.32 |
| AI Agent | OpenAI SDK + Qwen | via OpenRouter |
| Remediation Agent UI | Python Rich | 13.9+ |
| HTTP Client | httpx | 0.27 |
| Data Validation | Pydantic | 2.10+ |
| Metric Exporters | prometheus-client | 0.21 |
| Host Metrics | Node Exporter | 1.7.0 |
| Container Metrics | cAdvisor | 0.49.1 |
| Containerization | Docker + Compose | Latest |
| Language | Python | 3.11+ |
| Testing | pytest | 8.1+ |

---

## Author

**Abdallah** — [@AbdAllAh950](https://github.com/AbdAllAh950)

---

## Course

This project was developed as part of the **Big Data & Machine Learning** program at **ITMO University** (Semester 3).

> Project 3 — Monitoring and Auto-Diagnostics with Prometheus + Grafana via MCP Server and Remediation Agent

---

## License

This project is for educational purposes as part of the **ITMO University Big Data & ML curriculum**.

This repository is intended as a reference and learning resource.
