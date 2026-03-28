import requests
import boto3
from datetime import datetime, timedelta
from config import PROMETHEUS_URL, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def fetch_prometheus_alerts() -> list[dict]:
    """Fetch firing alerts from Prometheus Alertmanager."""
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/alerts", timeout=10)
        response.raise_for_status()
        data = response.json()

        alerts = []
        for alert in data.get("data", {}).get("alerts", []):
            if alert.get("state") == "firing":
                alerts.append({
                    "source": "Prometheus",
                    "name": alert["labels"].get("alertname", "Unknown"),
                    "severity": alert["labels"].get("severity", "unknown"),
                    "instance": alert["labels"].get("instance", "unknown"),
                    "summary": alert.get("annotations", {}).get("summary", "No summary"),
                    "description": alert.get("annotations", {}).get("description", "No description"),
                    "started_at": alert.get("activeAt", "unknown"),
                })
        return alerts

    except Exception as e:
        print(f"[Prometheus] Error fetching alerts: {e}")
        return []


def fetch_cloudwatch_alarms() -> list[dict]:
    """Fetch ALARM state CloudWatch alarms from AWS."""
    try:
        session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY or None,
            region_name=AWS_REGION,
        )
        client = session.client("cloudwatch")

        response = client.describe_alarms(StateValue="ALARM")
        alarms = []

        for alarm in response.get("MetricAlarms", []):
            alarms.append({
                "source": "CloudWatch",
                "name": alarm["AlarmName"],
                "severity": "critical" if "critical" in alarm["AlarmName"].lower() else "warning",
                "instance": alarm.get("Namespace", "AWS"),
                "summary": alarm.get("AlarmDescription", "No description"),
                "description": (
                    f"Metric: {alarm.get('MetricName')} | "
                    f"Threshold: {alarm.get('Threshold')} | "
                    f"Comparison: {alarm.get('ComparisonOperator')}"
                ),
                "started_at": str(alarm.get("StateUpdatedTimestamp", "unknown")),
            })
        return alarms

    except Exception as e:
        print(f"[CloudWatch] Error fetching alarms: {e}")
        return []


def fetch_all_alerts() -> list[dict]:
    """Fetch and combine alerts from all sources."""
    prometheus_alerts = fetch_prometheus_alerts()
    cloudwatch_alarms = fetch_cloudwatch_alarms()
    all_alerts = prometheus_alerts + cloudwatch_alarms
    print(f"[AlertFetcher] Total alerts fetched: {len(all_alerts)}")
    return all_alerts
