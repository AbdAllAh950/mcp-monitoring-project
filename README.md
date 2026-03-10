<div align="center">

# 🔍 MCP Monitoring & Auto-Diagnostics System

**Real-time monitoring, anomaly detection, and automated remediation**  
**for Apache Kafka · Apache Spark · HDFS big data pipelines**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Prometheus](https://img.shields.io/badge/Prometheus-2.51-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-10.4-F46800?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

> 🚀 **No human intervention required.**  
> The system detects anomalies, diagnoses root causes, and fixes itself — automatically.

</div>

---

## 📌 Overview

This project is a **production-grade monitoring and auto-diagnostics platform** built for big data pipelines. It simulates a real-world environment with **Apache Kafka**, **Apache Spark**, and **HDFS** — all continuously exporting live metrics to **Prometheus**, beautifully visualized in **Grafana**, and protected by an intelligent **MCP (Model Context Protocol) Server** that:

1. 📥 **Receives** alerts from Alertmanager via webhook
2. 🧠 **Diagnoses** the root cause automatically
3. ⚡ **Remediates** the problem by executing fix playbooks
4. 📋 **Logs** every action taken with full audit history

The **Remediation Agent CLI** provides an interactive terminal interface for live monitoring, manual interventions, and metric queries — making it perfect for a live demo or operations dashboard.

---

## 🏗️ System Architecture

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
│   • Evaluates 12+ alert rules continuously                            │
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
│   • Exposes 6 REST tools for agents and automation                    │
│   • Exposes its own /metrics endpoint (scraped by Prometheus)         │
└──────────────┬────────────────────────────┬─────────────────────────┘
               │                            │
               ▼                            ▼
┌──────────────────────┐      ┌─────────────────────────────┐
│   Grafana  :3000     │      │    Remediation Agent CLI    │
│                      │      │                             │
│  • 11-panel dashboard│      │  • Service health table     │
│  • Live time-series  │      │  • Active alerts view       │
│  • Color thresholds  │      │  • Remediation history      │
│  • Auto-provisioned  │      │  • Prometheus metric query  │
│                      │      │  • Manual trigger           │
│                      │      │  • Live monitor (10s refresh)│
└──────────────────────┘      └─────────────────────────────┘
```

---

## ✨ Key Features

### 🐳 Fully Dockerized Stack
One `docker compose up` command launches the entire infrastructure: Prometheus, Grafana, Alertmanager, Node Exporter, cAdvisor, and all 3 custom metric exporters.

### 📊 Live Grafana Dashboard (11 Panels)
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

### 🔔 12 Prometheus Alert Rules
Covering Kafka, Spark, HDFS, and host-level anomalies — each with a severity label and a specific `action` label used by the remediation engine.

### 🤖 MCP Server (FastAPI)
A custom REST API implementing the Model Context Protocol pattern. It acts as the brain — receiving alerts, running fix playbooks, and exposing monitoring tools that any AI agent or automation can call.

### ⚡ Auto-Remediation Engine
When an alert fires, the MCP server immediately runs a specific fix playbook:
- **Kafka lag spike** → restart consumer group / scale consumers
- **Spark job failure** → retry from last checkpoint
- **Spark memory high** → increase executor memory config
- **HDFS disk full** → clean up old temp files and archives
- **DataNode down** → restart DataNode and trigger replication
- **Broker down** → restart Kafka broker and reassign partitions

### 🖥️ Remediation Agent CLI
A rich terminal application with a live auto-refresh monitor. It queries the MCP Server to show real-time health, alerts, and full remediation history — ideal for demos and operations screens.

### 📈 Full Observability Loop
The MCP Server itself exports Prometheus metrics (`mcp_alerts_received_total`, `mcp_remediations_triggered_total`, `mcp_remediation_duration_seconds`) — so you can monitor the monitoring system.

---

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and **running**
- Python **3.11+**
- macOS or Linux (tested on macOS Apple Silicon M2)

### 1️⃣ Clone the repository
```bash
git clone https://github.com/AbdAllAh950/mcp-monitoring-project.git
cd mcp-monitoring-project
```

### 2️⃣ Install Python dependencies
```bash
make setup
```

### 3️⃣ Start the full Docker monitoring stack
```bash
cd monitoring
docker compose up -d --build
```
> ⏳ First run takes 3–5 minutes to pull images and build exporters.

### 4️⃣ Start the MCP Server
```bash
# Open a new terminal tab — keep this running
cd mcp-server
python3 mcp_server.py
```
Wait for: `Uvicorn running on http://0.0.0.0:8888`

### 5️⃣ Start the Remediation Agent CLI
```bash
# Open another new terminal tab
cd remediation-agent
python3 agent.py
```

### 6️⃣ Open your dashboards

| Service | URL | Login |
|---|---|---|
| 📊 Grafana Dashboard | http://localhost:3000 | `admin` / `admin123` |
| 🔵 Prometheus UI | http://localhost:9090 | — |
| 🤖 MCP Server API Docs | http://localhost:8888/docs | — |
| 🔔 Alertmanager UI | http://localhost:9093 | — |
| 📦 Kafka Metrics | http://localhost:8001/metrics | — |
| 📦 Spark Metrics | http://localhost:8002/metrics | — |
| 📦 HDFS Metrics | http://localhost:8003/metrics | — |

---

## 🔔 Alert Rules Reference

| Alert Name | Service | Severity | Trigger Condition | Auto-Remediation Action |
|---|---|---|---|---|
| `KafkaConsumerLagHigh` | Kafka | ⚠️ Warning | `lag > 5,000` for 1 min | Restart consumer group |
| `KafkaConsumerLagCritical` | Kafka | 🔴 Critical | `lag > 15,000` for 2 min | Scale consumer instances |
| `KafkaBrokerDown` | Kafka | 🔴 Critical | `broker_up == 0` for 30s | Restart Kafka broker |
| `KafkaUnderReplicatedPartitions` | Kafka | ⚠️ Warning | `under_replicated > 0` for 1 min | Check replication factor |
| `SparkJobFailed` | Spark | 🔴 Critical | `failed_jobs > 0` instantly | Retry job from checkpoint |
| `SparkExecutorMemoryHigh` | Spark | ⚠️ Warning | `memory > 85%` for 2 min | Increase executor memory |
| `SparkActiveTasksLow` | Spark | ⚠️ Warning | `active_tasks < 1` for 3 min | Check Spark cluster |
| `HDFSDiskSpaceHigh` | HDFS | ⚠️ Warning | `disk > 80%` for 2 min | Clean up old files |
| `HDFSDataNodeDown` | HDFS | 🔴 Critical | `datanode_up == 0` for 1 min | Restart DataNode |
| `HDFSReplicationLow` | HDFS | ⚠️ Warning | `under_replicated > 100` for 2 min | Trigger replication recovery |
| `HighCPUUsage` | System | ⚠️ Warning | `cpu > 80%` for 2 min | Investigate high-CPU processes |
| `HighMemoryUsage` | System | ⚠️ Warning | `memory > 85%` for 2 min | Check for memory leaks |

---

## 🤖 MCP Server API Reference

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
| MCP Own Metrics | `GET` | `/metrics` | Prometheus metrics about MCP server itself |

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
        "description": "DataNode unreachable for 1 minute",
        "remediation": "Restart the DataNode service"
      }
    }],
    "groupLabels": {},
    "commonLabels": {},
    "commonAnnotations": {},
    "externalURL": ""
  }'
```

---

## 📁 Project Structure

```
mcp-monitoring-project/
│
├── Makefile                                 # 🎛️  Control panel: setup/start/stop/demo
├── README.md                                # 📖 This file
├── .gitignore
│
├── monitoring/                              # 🐳 Full Docker monitoring stack
│   ├── docker-compose.yml                   #    8 services in one file
│   ├── prometheus/
│   │   ├── prometheus.yml                   #    Scrape configs for all targets
│   │   ├── alert_rules.yml                  #    12 alert rules (Kafka/Spark/HDFS/System)
│   │   └── alertmanager.yml                 #    Webhook routing to MCP Server
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/prometheus.yml   #    Auto-connects Prometheus datasource
│       │   └── dashboards/dashboards.yml    #    Auto-loads dashboard on startup
│       └── dashboards/
│           └── mcp-monitoring.json          #    11-panel live dashboard definition
│
├── exporters/                               # 📡 Metric simulators
│   ├── kafka_exporter.py                    #    Kafka: lag, broker, messages, partitions
│   ├── Dockerfile.kafka
│   ├── spark_exporter.py                    #    Spark: tasks, memory, jobs, executors
│   ├── Dockerfile.spark
│   ├── hdfs_exporter.py                     #    HDFS: disk, datanodes, blocks, files
│   └── Dockerfile.hdfs
│
├── mcp-server/                              # 🤖 MCP Server (the brain)
│   ├── mcp_server.py                        #    FastAPI app: webhook + tools + remediation
│   └── requirements.txt
│
└── remediation-agent/                       # 🖥️  Interactive CLI agent
    ├── agent.py                             #    Rich terminal UI: health/alerts/history/live
    └── requirements.txt
```

---

## 🛠️ Makefile Commands

```bash
make setup      # Install all Python dependencies for MCP server and agent
make start      # Start Docker stack + MCP server
make stop       # Stop all services cleanly
make restart    # Stop then start everything
make logs       # Follow all Docker container logs live
make mcp-server # Start only the MCP server
make agent      # Start only the Remediation Agent CLI
make status     # Check health of all services
make demo       # Open all 4 demo URLs in your browser
make clean      # Stop everything and delete all Docker volumes
```

---

## 🧰 Tech Stack

| Category | Technology | Version |
|---|---|---|
| Metrics & Alerting | Prometheus | 2.51.0 |
| Visualization | Grafana | 10.4.2 |
| Alert Routing | Alertmanager | 0.27.0 |
| MCP Server Framework | FastAPI + Uvicorn | 0.115 / 0.32 |
| Remediation Agent UI | Python Rich | 13.9+ |
| HTTP Client | httpx | 0.27 |
| Data Validation | Pydantic | 2.10+ |
| Metric Exporters | prometheus-client | 0.21 |
| Host Metrics | Node Exporter | 1.7.0 |
| Container Metrics | cAdvisor | 0.49.1 |
| Containerization | Docker + Compose | Latest |
| Language | Python | 3.11+ |

---

## 💡 How Auto-Remediation Works

```
Prometheus detects: kafka_consumer_lag > 5000 for 1 minute
        ↓
Alertmanager fires: KafkaConsumerLagHigh (severity=warning, action=restart_consumer)
        ↓
MCP Server receives POST /webhook/alert
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

## 🎬 Live Demo Guide

### Terminal setup
```bash
# Tab 1: Docker stack already running in background
# Tab 2: MCP Server
cd mcp-server && python3 mcp_server.py

# Tab 3: Agent live monitor
cd remediation-agent && python3 agent.py
# Press 6 for live auto-refresh monitor
```

### Open all demo tabs at once
```bash
make demo
# Opens: Grafana, Prometheus /alerts, MCP API /docs, Alertmanager
```

### Trigger a live demo alert
```bash
curl -X POST http://localhost:8888/webhook/alert \
  -H "Content-Type: application/json" \
  -d '{
    "receiver":"mcp-webhook","status":"firing",
    "alerts":[{"status":"firing",
      "labels":{"alertname":"HDFSDataNodeDown","severity":"critical",
                "service":"hdfs","action":"restart_datanode"},
      "annotations":{"summary":"HDFS DataNode is DOWN",
                     "description":"DataNode unreachable for 1 minute"}}],
    "groupLabels":{},"commonLabels":{},"commonAnnotations":{},"externalURL":""}'
```
Watch the live monitor: HDFS flips 🟢 HEALTHY → 🔴 CRITICAL, remediation runs, status shows ✅ completed — all within 10 seconds.

---

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
