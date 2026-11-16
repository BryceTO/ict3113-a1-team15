"""Ticket triage service.
Assignment 1 baseline: synchronous classification, no caching, no queue, one JSON log line per request.
Assignment 2 adds an optional CASCADE inside POST /tickets:
  a small model classifies every ticket, a rule decides whether to accept that answer,
  otherwise the ticket is escalated to a large model whose answer is final.
The classification prompt, categories, endpoints and Ollama settings are unchanged.
The caller cannot tell which model answered; the log records it (final_model, escalated).

Configuration (environment variables, set per run):
  MODE=single   -> MODEL classifies every ticket (Assignment 1 behaviour)
  MODE=cascade  -> SMALL_MODEL first, then LARGE_MODEL when RULE says escalate
  RULE=category    RULE_SETTING = small-model categories to ACCEPT, separated by ';'
  RULE=length      RULE_SETTING = max narrative length in characters to accept (longer -> escalate)
  RULE=confidence  RULE_SETTING = ignored; small model is asked HIGH/LOW in a second call, LOW -> escalate
  In every rule, an Unclassified small-model answer is escalated.
"""
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

MODE = os.getenv("MODE", "single").strip().lower()  # single | cascade
SMALL_MODEL = os.getenv("SMALL_MODEL", "")
LARGE_MODEL = os.getenv("LARGE_MODEL", "")
RULE = os.getenv("RULE", "").strip().lower()        # category | length | confidence
RULE_SETTING = os.getenv("RULE_SETTING", "").strip()

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

# Used ONLY by RULE=confidence, as a separate second call to the small model.
# The classification PROMPT above is unchanged.
CONFIDENCE_PROMPT = (
    "A complaint ticket was classified as \"{category}\".\n"
    "Possible categories:\n"
    + "\n".join(f"- {c}" for c in CATEGORIES)
    + "\n\nHow confident are you that this classification is correct?\n"
    "Reply with only one word: HIGH or LOW.\n\n"
    "Complaint:\n{narrative}\n\nConfidence:"
)

if MODE not in ("single", "cascade"):
    raise SystemExit(f"MODE must be 'single' or 'cascade', got {MODE!r}")
if MODE == "cascade":
    if not (SMALL_MODEL and LARGE_MODEL):
        raise SystemExit("MODE=cascade needs SMALL_MODEL and LARGE_MODEL")
    if RULE not in ("category", "length", "confidence"):
        raise SystemExit("MODE=cascade needs RULE=category|length|confidence")
    if RULE == "category":
        ACCEPT_CATEGORIES = {c.strip().lower() for c in RULE_SETTING.split(";") if c.strip()}
        unknown = ACCEPT_CATEGORIES - {c.lower() for c in CATEGORIES}
        if not ACCEPT_CATEGORIES or unknown:
            raise SystemExit(f"RULE_SETTING must list categories separated by ';' (unknown: {unknown})")
    if RULE == "length":
        LENGTH_CUTOFF = int(RULE_SETTING)

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


_thinking_capable: dict = {}  # model -> bool, from Ollama /api/show (model metadata, not results)


def model_can_think(model: str) -> bool:
    if model not in _thinking_capable:
        try:
            r = requests.post(f"{OLLAMA_URL}/api/show", json={"model": model}, timeout=30)
            r.raise_for_status()
            _thinking_capable[model] = "thinking" in (r.json().get("capabilities") or [])
        except Exception:
            return False  # Ollama not ready yet: try again on the next request
    return _thinking_capable[model]


def call_ollama(model: str, prompt: str) -> dict:
    """One synchronous /api/generate call. Same options for every model and every call."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": KEEP_ALIVE,
        "options": {"temperature": 0, "num_predict": 16, "num_ctx": NUM_CTX},
    }
    if model_can_think(model):
        payload["think"] = False
    t0 = time.perf_counter()
    r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=OLLAMA_TIMEOUT)
    r.raise_for_status()
    body = r.json()
    return {
        "raw": body.get("response", ""),
        "ms": round((time.perf_counter() - t0) * 1000, 1),
        "load_ns": body.get("load_duration"),
        "prompt_tokens": body.get("prompt_eval_count"),
        "eval_tokens": body.get("eval_count"),
    }


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


def classify(model: str, narrative: str) -> tuple[str, dict]:
    res = call_ollama(model, PROMPT.format(narrative=narrative))
    return match_category(res["raw"]), res


def should_escalate(narrative: str, small_category: str) -> tuple[bool, str, dict | None]:
    """Returns (escalate?, reason, extra-call result or None). Uses only the PREDICTED category,
    never the true one (unknown when a ticket arrives)."""
    if small_category == "Unclassified":
        return True, "unclassified", None
    if RULE == "category":
        if small_category.lower() in ACCEPT_CATEGORIES:
            return False, "category_accepted", None
        return True, "category_not_accepted", None
    if RULE == "length":
        if len(narrative) <= LENGTH_CUTOFF:
            return False, "short_enough", None
        return True, "too_long", None
    # RULE == "confidence": a second, separate call to the small model (its time counts)
    res = call_ollama(SMALL_MODEL, CONFIDENCE_PROMPT.format(category=small_category, narrative=narrative))
    word = res["raw"].strip().upper()
    res["answer"] = word[:20]
    if word.startswith("HIGH"):
        return False, "confidence_high", res
    return True, "confidence_low", res


@app.post("/tickets")
def create_ticket(ticket: TicketIn, request: Request):
    rid = request.state.rid
    extra = request.state.extra
    if ticket.row_id is not None:
        extra["row_id"] = ticket.row_id
    if not ticket.narrative.strip():
        extra["error"] = "empty narrative"
        raise HTTPException(422, "narrative must not be empty")
    extra["mode"] = MODE
    try:
        if MODE == "single":
            category, res = classify(MODEL, ticket.narrative)
            final_model, raw = MODEL, res["raw"]
            extra.update(
                model=MODEL,
                final_model=MODEL,
                escalated=False,
                ollama_ms=res["ms"],
                ollama_load_ns=res["load_ns"],
                prompt_eval_count=res["prompt_tokens"],
                eval_count=res["eval_tokens"],
            )
        else:
            extra.update(small_model=SMALL_MODEL, large_model=LARGE_MODEL, rule=RULE, rule_setting=RULE_SETTING)
            small_cat, small = classify(SMALL_MODEL, ticket.narrative)
            extra.update(small_category=small_cat, small_ms=small["ms"], small_load_ns=small["load_ns"])
            escalate, reason, conf = should_escalate(ticket.narrative, small_cat)
            extra.update(escalated=escalate, escalation_reason=reason)
            if conf is not None:
                extra.update(confidence_answer=conf["answer"], confidence_ms=conf["ms"])
            ollama_ms = small["ms"] + (conf["ms"] if conf else 0)
            if escalate:
                category, large = classify(LARGE_MODEL, ticket.narrative)
                final_model, raw = LARGE_MODEL, large["raw"]
                extra.update(large_category=category, large_ms=large["ms"], large_load_ns=large["load_ns"])
                ollama_ms += large["ms"]
            else:
                category, final_model, raw = small_cat, SMALL_MODEL, small["raw"]
            extra.update(model=final_model, final_model=final_model, ollama_ms=round(ollama_ms, 1))
    except Exception as e:
        extra.update(model=extra.get("final_model", MODEL if MODE == "single" else SMALL_MODEL),
                     error=str(e)[:200])
        raise HTTPException(502, f"model backend error: {e}")

    with db() as c:
        c.execute(
            "INSERT INTO tickets VALUES (?,?,?,?,?,datetime('now'))",
            (rid, ticket.narrative, category, raw, final_model),
        )
    extra.update(category=category, narrative_chars=len(ticket.narrative))
    return {"id": rid, "category": category}


@app.get("/health")
def health():
    """Service is up + which models Ollama currently holds in memory (for the cascade memory check)."""
    models = [MODEL] if MODE == "single" else [SMALL_MODEL, LARGE_MODEL]
    try:
        r = requests.get(f"{OLLAMA_URL}/api/ps", timeout=10)
        r.raise_for_status()
        loaded = [m.get("name") for m in r.json().get("models", [])]
        ollama = "up"
    except Exception as e:
        loaded, ollama = [], f"down: {str(e)[:100]}"
    return {
        "status": "ok",
        "mode": MODE,
        "configured_models": models,
        "rule": RULE if MODE == "cascade" else None,
        "rule_setting": RULE_SETTING if MODE == "cascade" else None,
        "ollama": ollama,
        "loaded_models": loaded,
        "all_configured_loaded": all(m in loaded for m in models),
    }


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
