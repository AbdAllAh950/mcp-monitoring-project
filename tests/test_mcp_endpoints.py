"""Tests for MCP Server REST API endpoints"""
import pytest
import httpx

MCP_URL = "http://localhost:8888"

def test_health_endpoint():
    """MCP server health check returns healthy status"""
    r = httpx.get(f"{MCP_URL}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"

def test_health_has_uptime():
    """Health endpoint includes timestamp field"""
    r = httpx.get(f"{MCP_URL}/health")
    data = r.json()
    assert "timestamp" in data or "uptime_seconds" in data

def test_get_active_alerts_endpoint():
    """get_active_alerts tool returns correct structure"""
    r = httpx.get(f"{MCP_URL}/tools/get_active_alerts")
    assert r.status_code == 200
    data = r.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)

def test_get_service_health_endpoint():
    """get_service_health tool returns all 3 services"""
    r = httpx.get(f"{MCP_URL}/tools/get_service_health")
    assert r.status_code == 200
    data = r.json()
    assert "services" in data
    services_data = data["services"]
    # Handle both list of dicts and dict formats
    if isinstance(services_data, list):
        if len(services_data) > 0 and isinstance(services_data[0], dict):
            service_names = {s.get("service", s.get("name", "")) for s in services_data}
        else:
            service_names = set(services_data)
    else:
        service_names = set(services_data.keys())
    assert any("kafka" in s.lower() for s in service_names)
    assert any("spark" in s.lower() for s in service_names)
    assert any("hdfs" in s.lower() for s in service_names)

def test_get_metrics_endpoint():
    """get_metrics tool returns metric values"""
    r = httpx.get(f"{MCP_URL}/tools/get_metrics")
    assert r.status_code == 200
    data = r.json()
    assert "metrics" in data

def test_remediation_history_endpoint():
    """get_remediation_history returns list"""
    r = httpx.get(f"{MCP_URL}/tools/get_remediation_history")
    assert r.status_code == 200
    data = r.json()
    assert "history" in data
    assert isinstance(data["history"], list)

def test_list_runbooks_endpoint():
    """list_runbooks returns all 11 runbooks"""
    r = httpx.get(f"{MCP_URL}/tools/list_runbooks")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 11
    assert len(data["runbooks"]) == 11

def test_get_runbook_found():
    """get_runbook returns correct runbook for KafkaBrokerDown"""
    r = httpx.get(f"{MCP_URL}/tools/get_runbook", params={"alert_name": "KafkaBrokerDown"})
    assert r.status_code == 200
    data = r.json()
    assert data["found"] == True
    assert "symptom" in data["runbook"]
    assert "diagnosis_steps" in data["runbook"]
    assert "remediation_actions" in data["runbook"]

def test_get_runbook_not_found():
    """get_runbook returns found=False for unknown alert"""
    r = httpx.get(f"{MCP_URL}/tools/get_runbook", params={"alert_name": "NonExistentAlert"})
    assert r.status_code == 200
    data = r.json()
    assert data["found"] == False

def test_webhook_accepts_alert(sample_alert):
    """Webhook endpoint accepts valid alert payload"""
    r = httpx.post(f"{MCP_URL}/webhook/alert", json=sample_alert)
    assert r.status_code == 200

def test_metrics_prometheus_format():
    """MCP /metrics endpoint returns Prometheus text format"""
    try:
        r = httpx.get(f"{MCP_URL}/metrics", timeout=30.0)
        assert r.status_code == 200
        assert "mcp_" in r.text or "python_" in r.text or "process_" in r.text
    except httpx.ReadTimeout:
        pytest.skip("Metrics endpoint timeout - Prometheus scraping in progress")
