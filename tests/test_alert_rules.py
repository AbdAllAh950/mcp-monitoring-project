"""Tests for Prometheus alert rules configuration"""
import pytest
import yaml
import os

RULES_PATH = os.path.join(
    os.path.dirname(__file__), 
    "../monitoring/prometheus/alert_rules.yml"
)

@pytest.fixture
def alert_rules():
    with open(RULES_PATH) as f:
        data = yaml.safe_load(f)
    rules = []
    for group in data.get("groups", []):
        for rule in group.get("rules", []):
            if "alert" in rule:
                rules.append(rule)
    return rules

def test_alert_rules_file_exists():
    """Alert rules file exists"""
    assert os.path.exists(RULES_PATH), f"Alert rules file not found at {RULES_PATH}"

def test_minimum_alert_count(alert_rules):
    """At least 12 alert rules are defined"""
    assert len(alert_rules) >= 12, f"Only {len(alert_rules)} rules found, expected 12+"

def test_all_alerts_have_severity(alert_rules):
    """Every alert has a severity label"""
    for rule in alert_rules:
        labels = rule.get("labels", {})
        assert "severity" in labels, f"Alert {rule['alert']} missing severity label"

def test_all_alerts_have_valid_severity(alert_rules):
    """Every alert severity is either warning or critical"""
    for rule in alert_rules:
        severity = rule.get("labels", {}).get("severity", "")
        assert severity in ["warning", "critical"], \
            f"Alert {rule['alert']} has invalid severity: {severity}"

def test_all_alerts_have_action_label(alert_rules):
    """Every alert has an action label for remediation engine"""
    for rule in alert_rules:
        labels = rule.get("labels", {})
        assert "action" in labels, f"Alert {rule['alert']} missing action label"

def test_all_alerts_have_service_label(alert_rules):
    """Every alert has a service label"""
    for rule in alert_rules:
        labels = rule.get("labels", {})
        assert "service" in labels, f"Alert {rule['alert']} missing service label"

def test_all_alerts_have_summary_annotation(alert_rules):
    """Every alert has a summary annotation"""
    for rule in alert_rules:
        annotations = rule.get("annotations", {})
        assert "summary" in annotations, f"Alert {rule['alert']} missing summary annotation"

def test_all_alerts_have_expr(alert_rules):
    """Every alert has a PromQL expression"""
    for rule in alert_rules:
        assert "expr" in rule, f"Alert {rule['alert']} missing expr"
        assert len(rule["expr"]) > 0

def test_kafka_alerts_exist(alert_rules):
    """Kafka-related alerts are defined"""
    kafka_alerts = [r for r in alert_rules if "kafka" in r["alert"].lower()]
    assert len(kafka_alerts) >= 3, "Expected at least 3 Kafka alert rules"

def test_spark_alerts_exist(alert_rules):
    """Spark-related alerts are defined"""
    spark_alerts = [r for r in alert_rules if "spark" in r["alert"].lower()]
    assert len(spark_alerts) >= 3, "Expected at least 3 Spark alert rules"

def test_hdfs_alerts_exist(alert_rules):
    """HDFS-related alerts are defined"""
    hdfs_alerts = [r for r in alert_rules if "hdfs" in r["alert"].lower()]
    assert len(hdfs_alerts) >= 3, "Expected at least 3 HDFS alert rules"

def test_critical_alerts_have_short_for_duration(alert_rules):
    """Critical alerts should fire within 2 minutes or 120 seconds"""
    for rule in alert_rules:
        if rule.get("labels", {}).get("severity") == "critical":
            for_duration = str(rule.get("for", "0m"))
            if for_duration.endswith("s"):
                seconds = int(for_duration.replace("s", ""))
            elif for_duration.endswith("m"):
                seconds = int(for_duration.replace("m", "")) * 60
            else:
                seconds = 0
            assert seconds <= 120, \
                f"Critical alert {rule['alert']} fires too slowly: {for_duration}"
