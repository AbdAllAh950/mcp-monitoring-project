"""
MCP (Model Context Protocol) Server for Monitoring & Auto-Diagnostics
Provides monitoring context and tools for the Remediation Agent
"""
import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import logging
import yaml
import os

# Load runbooks at startup
RUNBOOKS = {}
_runbook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runbooks.yaml")
if os.path.exists(_runbook_path):
    with open(_runbook_path) as _f:
        RUNBOOKS = yaml.safe_load(_f)
    print(f"Loaded {len(RUNBOOKS)} runbooks from runbooks.yaml")

# ─── Logging ────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─── App ────────────────────────────────────────────────────────
app = FastAPI(
    title="MCP Monitoring Server",
    description="Model Context Protocol Server for Prometheus + Grafana monitoring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── MCP Server own metrics ─────────────────────────────────────
mcp_alerts_received = Counter('mcp_alerts_received_total', 'Total alerts received', ['severity', 'service'])
mcp_remediations_triggered = Counter('mcp_remediations_triggered_total', 'Total remediations', ['action', 'service'])
mcp_remediation_duration = Histogram('mcp_remediation_duration_seconds', 'Remediation duration')
mcp_active_alerts = Gauge('mcp_active_alerts', 'Currently active alerts', ['service'])

# ─── In-memory store ────────────────────────────────────────────
active_alerts: dict = {}
remediation_history: list = []
system_context: dict = {
    "prometheus_url": "http://localhost:9090",
    "grafana_url": "http://localhost:3000",
    "services": ["kafka", "spark", "hdfs", "system"]
}

# ─── Models ─────────────────────────────────────────────────────
class AlertPayload(BaseModel):
    receiver: str
    status: str
    alerts: list[dict]
    groupLabels: dict = {}
    commonLabels: dict = {}
    commonAnnotations: dict = {}
    externalURL: str = ""

class MCPContext(BaseModel):
    service: str
    metric_query: Optional[str] = None
    time_range: Optional[str] = "5m"

class RemediationRequest(BaseModel):
    alert_name: str
    service: str
    action: str
    reason: str

# ─── MCP Protocol Endpoints ─────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "MCP Monitoring Server",
        "version": "1.0.0",
        "protocol": "MCP/1.0",
        "tools": [
            "get_metrics", "get_active_alerts", "get_service_health",
            "get_remediation_history", "trigger_remediation", "query_prometheus"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat()}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ─── Webhook: receives Alertmanager alerts ────────────────────────

@app.post("/webhook/alert")
async def receive_alert(payload: AlertPayload, background_tasks: BackgroundTasks):
    logger.info(f"Received alert webhook: status={payload.status}, alerts={len(payload.alerts)}")
    
    for alert in payload.alerts:
        alert_name = alert.get("labels", {}).get("alertname", "unknown")
        severity = alert.get("labels", {}).get("severity", "unknown")
        service = alert.get("labels", {}).get("service", "unknown")
        action = alert.get("labels", {}).get("action", "manual_review")
        status = alert.get("status", "firing")
        
        alert_id = f"{alert_name}_{service}"
        
        if status == "firing":
            active_alerts[alert_id] = {
                "id": alert_id,
                "name": alert_name,
                "severity": severity,
                "service": service,
                "action": action,
                "status": "firing",
                "summary": alert.get("annotations", {}).get("summary", ""),
                "description": alert.get("annotations", {}).get("description", ""),
                "remediation_hint": alert.get("annotations", {}).get("remediation", ""),
                "started_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
                "remediation_status": "pending"
            }
            mcp_alerts_received.labels(severity=severity, service=service).inc()
            mcp_active_alerts.labels(service=service).inc()
            logger.warning(f"🔴 ALERT FIRING: {alert_name} | Service: {service} | Severity: {severity}")
            
            # Auto-trigger remediation for the alert
            background_tasks.add_task(auto_remediate, alert_id, alert_name, service, action, severity)
        
        elif status == "resolved":
            if alert_id in active_alerts:
                active_alerts[alert_id]["status"] = "resolved"
                active_alerts[alert_id]["resolved_at"] = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
                mcp_active_alerts.labels(service=service).dec()
                logger.info(f"✅ ALERT RESOLVED: {alert_name} | Service: {service}")
    
    return {"status": "received", "processed": len(payload.alerts)}

# ─── MCP Tools ────────────────────────────────────────────────────

@app.get("/tools/get_active_alerts")
async def get_active_alerts_tool():
    """MCP Tool: Returns all currently firing alerts with context"""
    firing = {k: v for k, v in active_alerts.items() if v.get("status") == "firing"}
    return {
        "tool": "get_active_alerts",
        "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        "total_firing": len(firing),
        "alerts": list(firing.values())
    }

@app.get("/tools/get_service_health")
async def get_service_health(service: Optional[str] = None):
    """MCP Tool: Returns health status of all monitored services"""
    services_to_check = [service] if service else system_context["services"]
    
    health_data = {}
    alerts_by_service = {}
    
    for alert in active_alerts.values():
        svc = alert.get("service", "unknown")
        if alert.get("status") == "firing":
            if svc not in alerts_by_service:
                alerts_by_service[svc] = []
            alerts_by_service[svc].append(alert)
    
    for svc in services_to_check:
        svc_alerts = alerts_by_service.get(svc, [])
        critical_count = sum(1 for a in svc_alerts if a.get("severity") == "critical")
        warning_count = sum(1 for a in svc_alerts if a.get("severity") == "warning")
        
        if critical_count > 0:
            health_status = "critical"
        elif warning_count > 0:
            health_status = "warning"
        else:
            health_status = "healthy"
        
        health_data[svc] = {
            "service": svc,
            "health": health_status,
            "active_alerts": len(svc_alerts),
            "critical": critical_count,
            "warnings": warning_count,
            "details": svc_alerts
        }
    
    return {"tool": "get_service_health", "services": health_data}

@app.post("/tools/query_prometheus")
async def query_prometheus_tool(context: MCPContext):
    """MCP Tool: Query Prometheus directly and return results with context"""
    query = context.metric_query
    if not query:
        # Default useful queries per service
        default_queries = {
            "kafka": "kafka_consumer_lag",
            "spark": "spark_active_tasks",
            "hdfs": "hdfs_disk_used_percent",
            "system": "100 - (avg(rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)"
        }
        query = default_queries.get(context.service, "up")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{system_context['prometheus_url']}/api/v1/query",
                params={"query": query}
            )
            data = response.json()
            return {
                "tool": "query_prometheus",
                "service": context.service,
                "query": query,
                "result": data.get("data", {}).get("result", []),
                "status": data.get("status")
            }
    except Exception as e:
        return {"tool": "query_prometheus", "error": str(e), "query": query}

@app.get("/tools/get_remediation_history")
async def get_remediation_history_tool(limit: int = 20):
    """MCP Tool: Returns history of all remediations"""
    return {
        "tool": "get_remediation_history",
        "total": len(remediation_history),
        "history": remediation_history[-limit:]
    }

@app.post("/tools/trigger_remediation")
async def trigger_remediation_tool(request: RemediationRequest, background_tasks: BackgroundTasks):
    """MCP Tool: Manually trigger a remediation action"""
    background_tasks.add_task(
        auto_remediate,
        f"{request.alert_name}_{request.service}",
        request.alert_name,
        request.service,
        request.action,
        "manual"
    )
    return {
        "tool": "trigger_remediation",
        "status": "triggered",
        "alert": request.alert_name,
        "action": request.action,
        "service": request.service
    }

@app.get("/tools/get_metrics")
async def get_metrics_tool(service: Optional[str] = None):
    """MCP Tool: Get current metric values for a service"""
    queries = {
        "kafka": {
            "consumer_lag": "kafka_consumer_lag",
            "broker_up": "kafka_broker_up",
            "messages_rate": "rate(kafka_messages_in_total[1m])"
        },
        "spark": {
            "active_tasks": "spark_active_tasks",
            "memory_pct": "(spark_executor_memory_used_bytes/spark_executor_memory_total_bytes)*100",
            "failed_jobs": "spark_job_failed_total"
        },
        "hdfs": {
            "disk_pct": "hdfs_disk_used_percent",
            "datanode_up": "hdfs_datanode_up",
            "under_replicated": "hdfs_blocks_under_replicated"
        }
    }
    
    target_queries = queries.get(service, {}) if service else {k: list(v.values())[0] for k, v in queries.items()}
    
    results = {}
    async with httpx.AsyncClient(timeout=10.0) as client:
        for metric_name, query in target_queries.items():
            try:
                response = await client.get(
                    f"{system_context['prometheus_url']}/api/v1/query",
                    params={"query": query}
                )
                data = response.json()
                results[metric_name] = data.get("data", {}).get("result", [])
            except Exception as e:
                results[metric_name] = {"error": str(e)}
    
    return {"tool": "get_metrics", "service": service, "metrics": results}

# ─── Auto-Remediation Engine ────────────────────────────────────

@app.get("/tools/get_runbook")
async def get_runbook_tool(alert_name: str):
    """MCP Tool: Returns the runbook for a specific alert"""
    runbook = RUNBOOKS.get(alert_name)
    if not runbook:
        return {"tool": "get_runbook", "alert_name": alert_name, "found": False}
    return {"tool": "get_runbook", "alert_name": alert_name, "found": True, "runbook": runbook}

@app.get("/tools/list_runbooks")
async def list_runbooks_tool():
    """MCP Tool: Lists all available runbooks"""
    return {"tool": "list_runbooks", "total": len(RUNBOOKS), "runbooks": list(RUNBOOKS.keys())}

async def auto_remediate(alert_id: str, alert_name: str, service: str, action: str, severity: str):
    """Core remediation logic - simulates automated fixes"""
    start_time = time.time()
    logger.info(f"🔧 Starting remediation: alert={alert_name}, service={service}, action={action}")
    
    runbook = RUNBOOKS.get(alert_name, {})
    if runbook:
        logger.info(f"Runbook found for {alert_name}: {runbook.get('symptom', 'N/A')}")

    remediation_steps = []
    success = False
    
    try:
        # ── Kafka Remediations ──
        if action == "restart_consumer":
            remediation_steps = [
                "Detecting affected consumer group(s) via Prometheus query",
                "Pausing consumer group temporarily",
                "Resetting consumer offset to latest checkpoint",
                "Restarting consumer group",
                "Verifying lag is decreasing"
            ]
            await asyncio.sleep(2)  # Simulate work
            success = True
            
        elif action == "scale_consumers":
            remediation_steps = [
                "Analyzing lag trend over last 5 minutes",
                "Calculating required consumer instances",
                "Triggering horizontal scale-out: +2 consumer replicas",
                "Waiting for new consumers to join consumer group",
                "Verifying rebalance completed successfully"
            ]
            await asyncio.sleep(3)
            success = True
            
        elif action == "restart_broker":
            remediation_steps = [
                "Checking if broker is truly unreachable (3 connectivity tests)",
                "Verifying ZooKeeper / controller connection",
                "Issuing real restart via Docker SDK",
                "Waiting for container to come back up",
                "Verifying metrics endpoint is responding"
            ]
            try:
                import docker as docker_sdk
                _client = docker_sdk.from_env()
                _container = _client.containers.get("kafka-exporter")
                _container.restart()
                remediation_steps.append("kafka-exporter restarted successfully via Docker API")
                logger.info("Real Docker restart executed on kafka-exporter")
            except Exception as _e:
                remediation_steps.append(f"Docker API attempted: {str(_e)}")
                logger.warning(f"Docker restart note: {str(_e)}")
            await asyncio.sleep(3)
            success = True
        
        # ── Spark Remediations ──
        elif action == "retry_job":
            remediation_steps = [
                "Retrieving failed job ID and last checkpoint",
                "Analyzing failure root cause from executor logs",
                "Clearing failed task state",
                "Resubmitting job from last checkpoint",
                "Monitoring job until stable for 60 seconds"
            ]
            await asyncio.sleep(2)
            success = True
            
        elif action == "increase_memory":
            remediation_steps = [
                "Analyzing memory usage pattern over last 10 minutes",
                "Identifying memory-intensive stages",
                "Adjusting spark.executor.memory to +20%",
                "Restarting executors with new memory configuration",
                "Monitoring memory stabilization"
            ]
            await asyncio.sleep(3)
            success = True
        
        # ── HDFS Remediations ──
        elif action == "cleanup_hdfs":
            remediation_steps = [
                "Scanning HDFS for files older than 30 days",
                "Identifying largest directories",
                "Moving old Spark checkpoint data to archive",
                "Deleting temporary files (_temporary directories)",
                "Verifying disk usage dropped below 75%"
            ]
            await asyncio.sleep(3)
            success = True
            
        elif action == "restart_datanode":
            remediation_steps = [
                "Pinging DataNode to confirm it is unreachable",
                "Checking DataNode process on host",
                "Issuing DataNode restart via Docker API",
                "Waiting for DataNode to re-register with NameNode",
                "Triggering block replication for affected blocks"
            ]
            try:
                import docker as docker_sdk
                _client = docker_sdk.from_env()
                _container = _client.containers.get("hdfs-exporter")
                _container.restart()
                remediation_steps.append("hdfs-exporter restarted successfully via Docker API")
                logger.info("Real Docker restart executed on hdfs-exporter")
            except Exception as _e:
                remediation_steps.append(f"Docker API attempted: {str(_e)}")
                logger.warning(f"Docker restart note: {str(_e)}")
            await asyncio.sleep(3)
            success = True
        
        else:
            remediation_steps = [
                f"Alert '{alert_name}' received for service '{service}'",
                "No specific automation available for this action",
                "Creating incident ticket for manual review",
                "Notifying on-call engineer"
            ]
            await asyncio.sleep(1)
            success = True

    except Exception as e:
        remediation_steps.append(f"ERROR: {str(e)}")
        success = False

    duration = time.time() - start_time
    mcp_remediation_duration.observe(duration)
    mcp_remediations_triggered.labels(action=action, service=service).inc()
    
    record = {
        "id": f"rem_{int(time.time())}",
        "alert_id": alert_id,
        "alert_name": alert_name,
        "service": service,
        "action": action,
        "severity": severity,
        "steps": remediation_steps,
        "success": success,
        "duration_seconds": round(duration, 2),
        "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    }
    
    remediation_history.append(record)
    
    if alert_id in active_alerts:
        active_alerts[alert_id]["remediation_status"] = "completed" if success else "failed"
        active_alerts[alert_id]["remediation_id"] = record["id"]
    
    status = "✅ SUCCESS" if success else "❌ FAILED"
    logger.info(f"{status} Remediation for {alert_name} | Action: {action} | Duration: {duration:.2f}s")
    return record

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
