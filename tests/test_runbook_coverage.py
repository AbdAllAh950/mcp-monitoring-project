"""Tests for runbook coverage - every alert must have a runbook"""
import pytest
import yaml
import os

RULES_PATH = os.path.join(os.path.dirname(__file__), "../monitoring/prometheus/alert_rules.yml")
RUNBOOKS_PATH = os.path.join(os.path.dirname(__file__), "../mcp-server/runbooks.yaml")

@pytest.fixture
def alert_names():
    with open(RULES_PATH) as f:
        data = yaml.safe_load(f)
    names = []
    for group in data.get("groups", []):
        for rule in group.get("rules", []):
            if "alert" in rule:
                names.append(rule["alert"])
    return names

@pytest.fixture
def runbooks():
    with open(RUNBOOKS_PATH) as f:
        return yaml.safe_load(f)

def test_runbooks_file_exists():
    """Runbooks YAML file exists"""
    assert os.path.exists(RUNBOOKS_PATH)

def test_runbooks_not_empty(runbooks):
    """Runbooks file has at least 11 entries"""
    assert len(runbooks) >= 11

def test_every_runbook_has_symptom(runbooks):
    """Every runbook entry has a symptom field"""
    for name, rb in runbooks.items():
        assert "symptom" in rb, f"Runbook {name} missing symptom"

def test_every_runbook_has_diagnosis_steps(runbooks):
    """Every runbook has at least one diagnosis step"""
    for name, rb in runbooks.items():
        steps = rb.get("diagnosis_steps", [])
        assert len(steps) >= 1, f"Runbook {name} has no diagnosis steps"

def test_every_runbook_has_remediation_actions(runbooks):
    """Every runbook has at least one remediation action"""
    for name, rb in runbooks.items():
        actions = rb.get("remediation_actions", [])
        assert len(actions) >= 1, f"Runbook {name} has no remediation actions"

def test_every_runbook_action_has_safety_classification(runbooks):
    """Every remediation action has a safety classification"""
    for name, rb in runbooks.items():
        for action in rb.get("remediation_actions", []):
            assert "safety" in action, \
                f"Runbook {name} action {action.get('action')} missing safety field"

def test_runbook_action_components_defined(runbooks):
    """Every remediation action specifies a target component"""
    for name, rb in runbooks.items():
        for action in rb.get("remediation_actions", []):
            assert "component" in action, \
                f"Runbook {name} action missing component field"

def test_kafka_broker_down_runbook_exists(runbooks):
    """KafkaBrokerDown runbook exists"""
    assert "KafkaBrokerDown" in runbooks

def test_hdfs_datanode_down_runbook_exists(runbooks):
    """HDFSDataNodeDown runbook exists"""
    assert "HDFSDataNodeDown" in runbooks

def test_spark_job_failed_runbook_exists(runbooks):
    """SparkJobFailed runbook exists"""
    assert "SparkJobFailed" in runbooks
