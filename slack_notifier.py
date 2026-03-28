import requests
import json
from config import SLACK_WEBHOOK_URL


SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
    "unknown": "⚪",
}


def format_slack_message(incident: dict) -> dict:
    """Format an incident result into a Slack Block Kit message."""
    alert = incident["alert"]
    analysis = incident["analysis"]

    severity = analysis.get("severity", "unknown").lower()
    emoji = SEVERITY_EMOJI.get(severity, "⚪")
    escalate_text = "⚠️ *ESCALATE NOW*" if analysis.get("escalate") else "✅ Team can handle"

    steps = "\n".join(
        f"  {i+1}. {step}" for i, step in enumerate(analysis.get("remediation_steps", []))
    )

    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Incident Alert: {alert.get('name')}",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Source:*\n{alert.get('source')}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity.upper()}"},
                    {"type": "mrkdwn", "text": f"*Instance:*\n{alert.get('instance')}"},
                    {"type": "mrkdwn", "text": f"*Escalate:*\n{escalate_text}"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔍 Root Cause:*\n{analysis.get('root_cause')}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*💥 Impact:*\n{analysis.get('impact')}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🛠️ Remediation Steps:*\n{steps}",
                },
            },
            {"type": "divider"},
        ]
    }
    return message


def send_to_slack(incident: dict) -> bool:
    """Send a single incident analysis to Slack."""
    try:
        payload = format_slack_message(incident)
        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if response.status_code == 200:
            print(f"[Slack] Notification sent for: {incident['alert'].get('name')}")
            return True
        else:
            print(f"[Slack] Failed to send. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[Slack] Error sending notification: {e}")
        return False


def notify_all(incidents: list[dict]):
    """Send Slack notifications for all incidents."""
    for incident in incidents:
        send_to_slack(incident)
