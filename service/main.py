"""Baseline ticket triage service (Assignment 1).
Deliberately simple: synchronous classification, no caching, no queue."""
import json
import logging
import os
import sqlite3
import time
import uuid

import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL = os.getenv("MODEL", "llama3.2:1b")
DB_PATH = os.getenv("DB_PATH", "/data/tickets.db")
LOG_PATH = os.getenv("LOG_PATH", "/app/logs/requests.log")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "300"))

CATEGORIES = [
    "Credit reporting",
    "Debt collection",
    "Mortgage",
    "Credit card",
    "Bank account or service",
    "Consumer loan",
    "Money transfer or service",
]

PROMPT = (
    "You are a complaint ticket classifier for a financial services company.\n"
    "Classify the customer complaint into exactly ONE of these categories:\n"
    + "\n".join(f"- {c}" for c in CATEGORIES)
    + "\n\nReply with only the category name, exactly as written above, and nothing else.\n\n"
    "Complaint:\n{narrative}\n\nCategory:"
)

# --- request logging: one JSON line per request -------------------------
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
req_log = logging.getLogger("requests")
req_log.setLevel(logging.INFO)
_h = logging.FileHandler(LOG_PATH)
_h.setFormatter(logging.Formatter("%(message)s"))
req_log.addHandler(_h)


def log_request(**fields):
    fields["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + f".{int(time.time()*1000)%1000:03d}Z"
    req_log.info(json.dumps(fields))


# --- storage ------------------------------------------------------------
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


with db() as c:
    c.execute(
        """CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            narrative TEXT NOT NULL,
            category TEXT NOT NULL,
            raw_output TEXT,
            model TEXT,
            created_at TEXT
        )"""
    )

app = FastAPI(title="Ticket Triage Service (baseline)")


class TicketIn(BaseModel):
    narrative: str


def match_category(text: str) -> str:
    t = text.strip().lower()
    for c in CATEGORIES:
        if t == c.lower():
            return c
    for c in CATEGORIES:  # model added extra words: take first category mentioned
        if c.lower() in t:
            return c
    return "Unclassified"


@app.post("/tickets")
def create_ticket(ticket: TicketIn):
    rid = str(uuid.uuid4())
    start = time.perf_counter()
    if not ticket.narrative.strip():
        log_request(request_id=rid, endpoint="POST /tickets", status=422, error="empty narrative")
        raise HTTPException(422, "narrative must not be empty")
    try:
        t0 = time.perf_counter()
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": PROMPT.format(narrative=ticket.narrative),
                "stream": False,
                "options": {"temperature": 0, "num_predict": 16},
            },
            timeout=OLLAMA_TIMEOUT,
        )
        r.raise_for_status()
        ollama_ms = (time.perf_counter() - t0) * 1000
        raw = r.json().get("response", "")
    except Exception as e:
        log_request(
            request_id=rid, endpoint="POST /tickets", model=MODEL, status=502,
            latency_ms=round((time.perf_counter() - start) * 1000, 1), error=str(e)[:200],
        )
        raise HTTPException(502, f"model backend error: {e}")

    category = match_category(raw)
    with db() as c:
        c.execute(
            "INSERT INTO tickets VALUES (?,?,?,?,?,datetime('now'))",
            (rid, ticket.narrative, category, raw, MODEL),
        )
    latency_ms = (time.perf_counter() - start) * 1000
    log_request(
        request_id=rid, endpoint="POST /tickets", model=MODEL, status=200,
        latency_ms=round(latency_ms, 1), ollama_ms=round(ollama_ms, 1),
        category=category, narrative_chars=len(ticket.narrative),
    )
    return {"id": rid, "category": category}


@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    start = time.perf_counter()
    with db() as c:
        rows = c.execute(
            "SELECT id, narrative, category FROM tickets WHERE narrative LIKE ? LIMIT 100",
            (f"%{q}%",),
        ).fetchall()
    log_request(
        endpoint="GET /search", status=200, results=len(rows),
        latency_ms=round((time.perf_counter() - start) * 1000, 1),
    )
    return {"query": q, "count": len(rows), "results": [dict(r) for r in rows]}


@app.get("/stats")
def stats():
    start = time.perf_counter()
    with db() as c:
        rows = c.execute("SELECT category, COUNT(*) n FROM tickets GROUP BY category").fetchall()
    log_request(
        endpoint="GET /stats", status=200,
        latency_ms=round((time.perf_counter() - start) * 1000, 1),
    )
    return {r["category"]: r["n"] for r in rows}
