# ICT3113 Assignment 1 — Complaint Ticket Triage (Team 15)

Baseline ticket triage service for a financial services complaints desk, plus the requirements, golden test set and measurements used to decide which CPU-only Ollama model to deploy.

## Team
| Name | Student ID |
|---|---|
| TOH ZHENGDA | 2302113 |
| AROKKIASAMY LIANDOMAXIN | 2400643 |
| LIN YUHAO | 2400703 |
| BRYAN KOH KAI XUN | 2400960 |
| BRYCE TEOH YI | 2401073 |

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

### Request format
```
POST /tickets
{"narrative": "<ticket text>", "row_id": 15123}
```
`row_id` is optional. It is the dataset row number, written to the log only so results can be matched to the golden set and to JMeter rows. It is not shown to the model. Each response carries an `X-Request-ID` header that matches `request_id` in the log.

### Configuration (environment variables)
| Variable | Default | Purpose |
|---|---|---|
| `MODEL` | `llama3.2:1b` | Ollama model tag to classify with (must already be pulled) |
| `RUN_ID` | `dev` | Name of the run. Each run gets its own log `results/logs/<RUN_ID>.log` and its own empty database |
| `NUM_CTX` | `4096` | Model context window. Keep it identical for every candidate |
| `KEEP_ALIVE` | `30m` | Keeps the model loaded between requests |
| `OLLAMA_VERSION` | `0.35.0` | Ollama image version (pinned). Record it with the results |

Ollama runs with `OLLAMA_NUM_PARALLEL=1` (one inference at a time) and `OLLAMA_MAX_QUEUE=512`. This is part of the baseline. Do not change it in Assignment 1.

Run naming convention: `<model>_<scenario>_run<N>`, for example `llama3.2-1b_stretch_run1`. The scenarios are `stretch`, `high`, `stress` and `accuracy`. In `RUN_ID` the model tag's `:` is written as `-` (`gemma3-4b_...`, not `gemma3:4b_...`), because the `RUN_ID` becomes a file name.

- Mac/Linux: `MODEL=llama3.2:1b RUN_ID=llama3.2-1b_stretch_run1 docker compose up -d`
- PowerShell: `$env:MODEL="llama3.2:1b"; $env:RUN_ID="llama3.2-1b_stretch_run1"; docker compose up -d`

Changing `MODEL` or `RUN_ID` recreates the triage container. A new `RUN_ID` starts with an empty database, so no volume reset is needed.

### Load and stress runs
The full procedure is in `docs/test_playbook.md`. In short, for each run:
1. **Service host:** start the service with the run's `MODEL` and `RUN_ID`.
2. **Load generator (a separate machine):** start the run with `jmeter/run_load.ps1`, pointing `-TargetHost` at the service host. The two machines were connected through Tailscale (see `docs/test_environment.md`).
3. The script sends **one warm-up** `POST /tickets` to load the model, then runs JMeter. The warm-up stays in the service log and is excluded from results. Its `request_id` is saved in `results/jtl/<RUN_ID>.meta.json`.
4. **Service host:** commit and push `results/logs/<RUN_ID>.log`.
5. **Load generator:** run `py scripts\summarize_load.py`. It checks every `.jtl` against its service log by `request_id` and writes `results/summary/`. A run that does not reconcile is kept but not reported.
6. Commit the `.jtl`, its `.properties` and `.meta.json`, and `results/summary/`.

### Stop
```
docker compose down
```

## Logging
Every request (including errors) is logged as one JSON line to `results/logs/<RUN_ID>.log`.

| Field | Meaning |
|---|---|
| `ts`, `run_id`, `request_id` | When, which run, and the ID returned in `X-Request-ID` |
| `endpoint`, `status` | e.g. `POST /tickets`, `200` / `422` / `502` |
| `latency_ms` | Total time inside the service |
| `ollama_ms` | Time spent waiting on Ollama |
| `ollama_total_ns`, `ollama_load_ns` | Ollama's own timings (nanoseconds). A large load time means the model was reloaded |
| `prompt_eval_count`, `eval_count` | Input / output tokens |
| `model`, `category`, `narrative_chars`, `row_id` | `POST /tickets` only. `Unclassified` = the model output named no valid category (counts as wrong) |
| `results` | `GET /search` only: number of matches |

Logs are committed to Git as evidence. Do not delete or edit them.

## Repository layout
```
docker-compose.yml     Service + Ollama (CPU only)
service/               Triage service source and Dockerfile
results/logs/          Service request logs, one per run
results/jtl/           Raw JMeter result files, with each run's settings (.properties, .meta.json)
results/summary/       Load and stress figures calculated from the .jtl files and logs
results/accuracy/      Golden-set predictions, accuracy and confusion matrices
jmeter/                JMeter test plan, run script and search terms
golden_set/            Golden test set and labelling evidence
predictions/           Prediction record
scripts/               Feeder, load summary and accuracy scripts
docs/                  Candidate models, test playbook and test environment
```
The Team 15 dataset rows are not in the repository. Each tester places the extract at `context/team15_rows.csv`, which is git-ignored, and builds the JMeter feeder from it with `py scripts\make_feeder.py`.

## Evidence rules
- The golden test set and the prediction record are committed **before** the first benchmark run. Do not edit them afterwards.
- Do not rewrite Git history (no force push or reset).
- Keep the raw `.jtl` files and service logs for every run reported in the slides. Every reported number must reconcile with them.

