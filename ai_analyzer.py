from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from config import OPENAI_API_KEY

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.2,
    openai_api_key=OPENAI_API_KEY,
)

SYSTEM_PROMPT = """
You are an expert Site Reliability Engineer (SRE) and DevOps incident responder.
When given an infrastructure alert or alarm, you must analyze it and respond ONLY in the following JSON format:

{
  "severity": "<critical | high | medium | low>",
  "root_cause": "<likely root cause in 1-2 sentences>",
  "impact": "<potential impact on users or systems>",
  "remediation_steps": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "escalate": <true | false>
}

Be concise, technical, and actionable. Do not include any text outside the JSON.
"""


def analyze_alert(alert: dict) -> dict:
    """Use LangChain + OpenAI to analyze an alert and return structured RCA."""
    try:
        user_message = f"""
Alert Source: {alert.get('source')}
Alert Name: {alert.get('name')}
Severity: {alert.get('severity')}
Instance/Namespace: {alert.get('instance')}
Summary: {alert.get('summary')}
Description: {alert.get('description')}
Started At: {alert.get('started_at')}

Analyze this alert and provide root cause, impact, remediation steps, and whether to escalate.
"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = llm(messages)
        import json
        analysis = json.loads(response.content)
        return analysis

    except Exception as e:
        print(f"[AIAnalyzer] Error analyzing alert '{alert.get('name')}': {e}")
        return {
            "severity": alert.get("severity", "unknown"),
            "root_cause": "AI analysis failed. Manual investigation required.",
            "impact": "Unknown",
            "remediation_steps": ["Check logs manually", "Escalate to on-call engineer"],
            "escalate": True,
        }


def analyze_all_alerts(alerts: list[dict]) -> list[dict]:
    """Analyze a list of alerts and return enriched results."""
    results = []
    for alert in alerts:
        print(f"[AIAnalyzer] Analyzing alert: {alert.get('name')}")
        analysis = analyze_alert(alert)
        results.append({
            "alert": alert,
            "analysis": analysis,
        })
    return results
