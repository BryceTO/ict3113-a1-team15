# ICT3113 Assignment 1 — Complaint Ticket Triage (Team 15)

Baseline ticket triage service for a financial services complaints desk, plus the requirements, golden test set and measurements used to decide which CPU-only Ollama model to deploy.

## Team
| Name | Student ID |
|---|---|---|
| TOH ZHENGDA||
| AROKKIASAMY LIANDOMAXIN| | 
| LIN YUHAO| | 
| BRYAN KOH KAI XUN| | 
| BRYCE TEOH YI| 2401073 | 

## System overview
```
JMeter (separate machine)  ->  Triage service (FastAPI, :8000)  ->  Ollama (CPU, :11434)
                                        |
                                     SQLite
```
The baseline is **synchronous**: `POST /tickets` waits for the model to answer. There is **no caching and no queue**. Optimisation is Assignment 2.

### Endpoints
| Endpoint | Description |
|---|---|
| `POST /tickets` | Body `{"narrative": "..."}`. Classifies the ticket into one of 7 categories via Ollama, stores it, returns `{"id", "category"}` |
| `GET /search?q=<text>` | Returns stored tickets whose narrative contains the text (max 100) |
| `GET /stats` | Returns counts of stored tickets by category |

Categories: Credit reporting, Debt collection, Mortgage, Credit card, Bank account or service, Consumer loan, Money transfer or service.

## Requirements
- Docker Desktop (includes Docker Compose)
- Enough RAM for the models you run (8 GB or more recommended for Docker)

## Run it
From the repo root:
```
docker compose up -d --build
docker compose exec ollama ollama pull <model:tag>
```
The service is then at http://localhost:8000 (interactive test page at `/docs`).

The service starts **empty**. Tickets only enter through `POST /tickets`.

### Choose the model
The default model is set in `docker-compose.yml`. Override it with the `MODEL` variable:

- Mac/Linux: `MODEL=<model:tag> docker compose up -d`
- PowerShell: `$env:MODEL="<model:tag>"; docker compose up -d`

The model must already be pulled into Ollama (`docker compose exec ollama ollama list` shows what is available).

### Reset between runs
To start from an empty database (keeps downloaded models):
```
docker compose down
docker volume rm ict3113-a1-team15_triage_data
docker compose up -d
```

### Stop
```
docker compose down
```

## Logging
Every request is logged as one JSON line to `results/logs/requests.log`, with timestamp, endpoint, model, status, latency, and the assigned category for `POST /tickets`. Move or rename the log for each reported run so it matches that run's JMeter `.jtl` file.

## Repository layout
```
docker-compose.yml     Service + Ollama (CPU only)
service/               Triage service source and Dockerfile
results/logs/          Service request logs
results/jtl/           Raw JMeter result files (every reported run)
jmeter/                JMeter test plans
data/                  Team 15 rows and golden test set
predictions/           Prediction record
scripts/               Sampling, agreement and accuracy scripts
docs/                  Labelling protocol, workload model, model tags and digests
```
Folders are added as the work is done.

## Evidence rules
- The golden test set and the prediction record are committed **before** the first benchmark run. Do not edit them afterwards.
- Do not rewrite Git history (no force push or reset).
- Keep the raw `.jtl` files and service logs for every run reported in the slides. Every reported number must reconcile with them.

