import pytest
import httpx

MCP_URL = "http://localhost:8888"

@pytest.fixture
def mcp_url():
    return MCP_URL

@pytest.fixture
def sample_alert():
    return {
        "receiver": "mcp-webhook",
        "status": "firing",
        "alerts": [{
            "status": "firing",
            "labels": {
                "alertname": "KafkaBrokerDown",
                "severity": "critical",
                "service": "kafka",
                "action": "restart_broker"
            },
            "annotations": {
                "summary": "Kafka broker is DOWN",
                "description": "Broker unreachable for 30 seconds"
            }
        }],
        "groupLabels": {},
        "commonLabels": {},
        "commonAnnotations": {},
        "externalURL": ""
    }
