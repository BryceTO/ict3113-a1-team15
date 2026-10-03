"""Baseline ticket triage service (Assignment 1).
Deliberately simple: synchronous classification, no caching, no queue.
Instrumentation patch: every request logged via middleware, Ollama timing fields,
RUN_ID per log line, explicit num_ctx / keep_alive, optional row_id for traceability."""
import json
import logging
import os
import sqlite3
import time
import uuid
from datetime import datetime, timezone

import requests
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL = os.getenv("MODEL", "llama3.2:1b")
DB_PATH = os.getenv("DB_PATH", "/data/tickets.db")
LOG_PATH = os.getenv("LOG_PATH", "/app/logs/requests.log")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "300"))
RUN_ID = os.getenv("RUN_ID", "dev")                 # set per run, e.g. llama3.2-1b_r2_run1
NUM_CTX = int(os.getenv("NUM_CTX", "4096"))         # keep identical across candidates
KEEP_ALIVE = os.getenv("KEEP_ALIVE", "30m")         # avoid mid-run model unloads

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
    fields["ts"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    fields["run_id"] = RUN_ID
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


@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    """Logs EVERY request (incl. validation 422s and unhandled 500s).
    Endpoints add extra fields via request.state.extra."""
    start = time.perf_counter()
    request.state.rid = str(uuid.uuid4())
    request.state.extra = {}
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request.state.rid
        return response
    finally:
        log_request(
            request_id=request.state.rid,
            endpoint=f"{request.method} {request.url.path}",
            status=status,
            latency_ms=round((time.perf_counter() - start) * 1000, 1),
            **request.state.extra,
        )


class TicketIn(BaseModel):
    narrative: str
    row_id: int | None = None   # optional: dataset row number, logged only (not used to classify)


def match_category(text: str) -> str:
    t = text.strip().lower()
    for c in CATEGORIES:
        if t == c.lower():
            return c
    # model added extra words: take the category mentioned EARLIEST in the output
    hits = [(t.find(c.lower()), c) for c in CATEGORIES if c.lower() in t]
    return min(hits)[1] if hits else "Unclassified"


@app.post("/tickets")
def create_ticket(ticket: TicketIn, request: Request):
    rid = request.state.rid
    extra = request.state.extra
    if ticket.row_id is not None:
        extra["row_id"] = ticket.row_id
    if not ticket.narrative.strip():
        extra["error"] = "empty narrative"
        raise HTTPException(422, "narrative must not be empty")
    try:
        t0 = time.perf_counter()
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": PROMPT.format(narrative=ticket.narrative),
                "stream": False,
                "keep_alive": KEEP_ALIVE,
                "options": {"temperature": 0, "num_predict": 16, "num_ctx": NUM_CTX},
            },
            timeout=OLLAMA_TIMEOUT,
        )
        r.raise_for_status()
        ollama_ms = (time.perf_counter() - t0) * 1000
        body = r.json()
        raw = body.get("response", "")
        extra.update(
            model=MODEL,
            ollama_ms=round(ollama_ms, 1),
            # Ollama's own timings are in nanoseconds
            ollama_total_ns=body.get("total_duration"),
            ollama_load_ns=body.get("load_duration"),
            prompt_eval_count=body.get("prompt_eval_count"),
            eval_count=body.get("eval_count"),
        )
    except Exception as e:
        extra.update(model=MODEL, error=str(e)[:200])
        raise HTTPException(502, f"model backend error: {e}")

    category = match_category(raw)
    with db() as c:
        c.execute(
            "INSERT INTO tickets VALUES (?,?,?,?,?,datetime('now'))",
            (rid, ticket.narrative, category, raw, MODEL),
        )
    extra.update(category=category, narrative_chars=len(ticket.narrative))
    return {"id": rid, "category": category}


@app.get("/search")
def search(request: Request, q: str = Query(..., min_length=1)):
    with db() as c:
        rows = c.execute(
            "SELECT id, narrative, category FROM tickets WHERE narrative LIKE ? LIMIT 100",
            (f"%{q}%",),
        ).fetchall()
    request.state.extra.update(results=len(rows))
    return {"query": q, "count": len(rows), "results": [dict(r) for r in rows]}


@app.get("/stats")
def stats():
    with db() as c:
        rows = c.execute("SELECT category, COUNT(*) n FROM tickets GROUP BY category").fetchall()
    return {r["category"]: r["n"] for r in rows}
