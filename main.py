import asyncio
import threading
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from alert_fetcher import fetch_all_alerts
from ai_analyzer import analyze_all_alerts
from slack_notifier import notify_all
from config import APP_HOST, APP_PORT, POLL_INTERVAL_SECONDS
import uvicorn

app = FastAPI(
    title="AI-Powered Infrastructure Incident Assistant",
    description="Automatically fetches infrastructure alerts, analyzes them using AI, and notifies on-call engineers via Slack.",
    version="1.0.0",
)

# In-memory store for latest incidents
latest_incidents: list[dict] = []


def run_pipeline():
    """Full pipeline: fetch → analyze → notify."""
    global latest_incidents
    print("[Pipeline] Starting incident detection pipeline...")
    alerts = fetch_all_alerts()

    if not alerts:
        print("[Pipeline] No active alerts found.")
        return []

    incidents = analyze_all_alerts(alerts)
    notify_all(incidents)
    latest_incidents = incidents
    print(f"[Pipeline] Pipeline complete. Processed {len(incidents)} incident(s).")
    return incidents


def background_polling():
    """Continuously poll for alerts at a set interval."""
    while True:
        try:
            run_pipeline()
        except Exception as e:
            print(f"[Polling] Error in polling loop: {e}")
        import time
        time.sleep(POLL_INTERVAL_SECONDS)


@app.on_event("startup")
def start_background_polling():
    """Start background polling thread on app startup."""
    thread = threading.Thread(target=background_polling, daemon=True)
    thread.start()
    print(f"[Startup] Background polling started. Interval: {POLL_INTERVAL_SECONDS}s")


@app.get("/", tags=["Health"])
def root():
    return {"status": "running", "service": "AI Incident Assistant"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


@app.get("/incidents", tags=["Incidents"])
def get_latest_incidents():
    """Return the latest analyzed incidents."""
    return JSONResponse(content={"total": len(latest_incidents), "incidents": latest_incidents})


@app.post("/trigger", tags=["Incidents"])
def trigger_pipeline(background_tasks: BackgroundTasks):
    """Manually trigger the alert fetch + analysis pipeline."""
    background_tasks.add_task(run_pipeline)
    return {"message": "Pipeline triggered. Check /incidents for results."}


if __name__ == "__main__":
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)
