from fastapi import FastAPI, Request, HTTPException
from clickhouse_connect import get_client
import os, uuid, datetime

# ------------------------------------------------------------------
# Lazily create the client after ClickHouse is ready
# ------------------------------------------------------------------
def get_db():
    return get_client(
        host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),  # 8123 = HTTP
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        secure=False,
    )

app = FastAPI(title="Lugx Analytics Service")

@app.on_event("startup")
def init_db():
    client = get_db()
    client.command("CREATE DATABASE IF NOT EXISTS lugx")
    client.command("""
        CREATE TABLE IF NOT EXISTS lugx.web_events (
            id         UUID,
            event_time DateTime,
            event_type LowCardinality(String),
            page       String,
            element    String,
            session_id String,
            extra      Map(String,String)
        ) ENGINE = MergeTree()
        ORDER BY (event_time, event_type)
    """)

@app.post("/track")
async def track(req: Request):
    data = await req.json()
    client = get_db()

    # ---- Convert fields to proper types --------------------------
    event_id   = uuid.uuid4().hex                     # 32‑char hex
    event_time = (
        datetime.datetime.fromisoformat(data["timestamp"])
        if "timestamp" in data else datetime.datetime.utcnow()
    )

    row = [
        event_id,
        event_time,
        data.get("eventType", "unknown"),
        data.get("page", ""),
        data.get("element", ""),
        data.get("sessionId", ""),
        data.get("extra", {}),
    ]

    try:
        client.insert("lugx.web_events", [row])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Insertion failed: {e}")
    return {"status": "ok"}
