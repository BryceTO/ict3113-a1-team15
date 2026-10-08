# Load and Stress Test Playbook

Owner: Performance Testing Lead

This playbook covers the JMeter load tests and the stress test. The golden-set accuracy test is a separate procedure owned by the Model & Accuracy Lead.

## 1. Gate: do not start until all of these are true

- The golden test set and the prediction record are committed to the repository.
- The candidate models are pinned by tag and digest, and the requirements are frozen.
- The arrival rates in section 4 are confirmed. They are fixed before run 1 and are the same for every model.
- Nothing else is using the service host: no accuracy run, no other load run, no other heavy program.

## 2. Machines

| Role | Runs | Notes |
|---|---|---|
| Service host | Docker: triage service + Ollama (CPU only) | The same machine for every run |
| Load generator | JMeter 5.6.3, Java 8 or later | A different physical machine. It reached the service over the Internet through Tailscale |

Details of each machine are in `docs/test_environment.md`.

## 3. One-time setup

On the service host:

1. `docker compose up -d --build`
2. `docker compose exec ollama ollama pull <model:tag>` for every candidate.
3. Install Tailscale, sign in, and invite the load generator's user to the tailnet. Note the host's Tailscale address (`tailscale ip -4`). Allow inbound TCP 8000 through the firewall if asked.

On the load generator:

1. Clone the repository. Put the Team 15 extract (rows 15000 to 15999, columns `row,source_label,narrative`) at `context/team15_rows.csv`. This folder is git-ignored.
2. `py scripts\make_feeder.py` writes `jmeter/feeder.tsv`: 1,000 lines, one ready-made JSON request body per ticket, in dataset order.
3. Set `JMETER_HOME` to the JMeter folder, for example `$env:JMETER_HOME = "C:\Users\<you>\Downloads\apache-jmeter-5.6.3"`.
4. Install Tailscale and join the service host's tailnet. Check the link: `tailscale status` must list the service host as `direct`, and `Invoke-RestMethod http://<service-host-ip>:8000/stats` must return JSON.

## 4. Test configurations

Rates are arrivals per minute. They were fixed before the first load run and are the same for every model.

| Scenario | `POST /tickets` | `GET /search` | Arrival window | Runs | Models |
|---|---:|---:|---:|---:|---|
| `stretch` | 1 /min (60 /h) | 0.2 /min (12 /h) | 20 min | 3 | every candidate |
| `high` | 3 /min (180 /h) | 0.6 /min (36 /h) | 20 min | 3 | every candidate |
| `stress` | steps of 2, 4, 6, 8, 10, 12 /min | none | 10 min per step | 1 | one candidate |

The workload model's peak is 9 tickets per hour. At that rate a one-hour run yields 9 samples, too few for a p95 or p99. The requirement is therefore tested at `stretch`, which is 6.7 times the peak rate: a single-server queue that meets the latency target at 60 per hour also meets it at 9 per hour.

## 5. How the load is generated

Test plan: `jmeter/triage_load.jmx`. It is always started by `jmeter/run_load.ps1`, in non-GUI mode.

- **Open-loop.** Two Open Model Thread Groups, one for tickets and one for searches. Each arrival starts a new thread at its scheduled time whether or not earlier requests have finished, so a slow server cannot throttle the load.
- **Schedule.** `rate(R/min) random_arrivals(D min) rate(R/min) pause(6 min)`. Arrivals are random (Poisson-like) at a constant average rate R for D minutes. The final 6-minute pause sends nothing and lets in-flight requests finish.
- **Random seed.** Equal to the run number, so run 1 has the same arrival times for every model, and runs 1, 2 and 3 differ from each other.
- **Tickets.** A CSV Data Set Config reads `feeder.tsv` from the top in every run and posts each line's body unchanged to `POST /tickets`. The body is `{"narrative": "...", "row_id": <row>}`.
- **Searches.** `GET /search?q=<term>`, terms taken in order from `jmeter/search_terms.csv`.
- **Timeouts.** Connect 10 s, response 330 s. The service gives up on Ollama after 300 s and returns 502, so JMeter records the service's own failure and does not cut it short.
- **Results.** CSV `.jtl` with two extra columns: `row_id` and `request_id`. `request_id` is read from the `X-Request-ID` response header and equals `request_id` in the service log.

## 6. Procedure for one run

The run ID is `<model with ":" replaced by "-">_<scenario>_run<N>`, for example `llama3.2-1b_stretch_run1`.

1. **Service host:** start the service for this run. A new `RUN_ID` gives an empty database and a new log file.
   ```
   $env:MODEL="llama3.2:1b"; $env:RUN_ID="llama3.2-1b_stretch_run1"; docker compose up -d
   ```
2. **Load generator:** start the run.
   ```
   .\jmeter\run_load.ps1 -TargetHost <service-host-ip> -Model llama3.2:1b -Scenario stretch -Run 1 -Rate 1 -SearchRate 0.2 -DurationMin 20
   ```
   The script checks that `GET /stats` is empty, sends one warm-up ticket (row 15999) to load the model, records the warm-up's request ID, then runs JMeter.
3. Do not touch either machine until JMeter prints `... end of run`.
4. **Service host:** commit and push `results/logs/<RUN_ID>.log`.
5. **Load generator:** pull, then run `py scripts\summarize_load.py`. The run's row must show `reconciled = yes`. If it does not, the run is not reported: keep its files, note the reason, and repeat it under the next run number.
6. Commit `results/jtl/<RUN_ID>.jtl`, `.properties` and `.meta.json` together with `results/summary/`.

Repeat for runs 2 and 3, then for the next scenario and the next model.

## 7. Stress test

Purpose: find the highest ticket arrival rate the baseline sustains before the queue grows without bound.

1. Start the service as in step 6.1 with `RUN_ID=<model>_stress_run1`.
2. Run:
   ```
   .\jmeter\run_load.ps1 -TargetHost <service-host-ip> -Model llama3.2:1b -Scenario stress -Run 1 -StepRates "2,4,6,8,10,12" -StepMin 10
   ```
   The rate rises in steps with no pause between them. The list must be in quotes.
3. Summarise as in step 6.5. Read `results/summary/stress_steps.csv` and `results/summary/timeline/<RUN_ID>.csv`.

**Reading the result.** The backlog is the number of requests that have arrived but not finished. The queue is growing in a step when the backlog rises over the step by more than 3 requests and more than 20% of that step's arrivals. The reported limit is the last step before the first growing step. Confirm it in the timeline: past the limit, completions per minute stay flat while arrivals, backlog and latency keep rising.

If no step is growing, repeat with higher rates. If the first step is already growing, repeat with lower rates.

**Cross-check.** Ollama serves one request at a time, so the limit should be close to 60,000 / `mean_ollama_ms` requests per minute, using `mean_ollama_ms` from an unsaturated load run of the same model in `load_runs.csv`.

## 8. What the numbers mean

| Reported figure | Definition | Source |
|---|---|---|
| p50, p95, p99 latency | Nearest-rank percentile of JMeter `elapsed`, over all samples of the endpoint, failures included | `.jtl` |
| Error rate | Samples where JMeter `success` is not true: non-2xx response or client timeout | `.jtl` |
| Achieved throughput | Successful responses divided by test time. Test time is the arrival window or the time to the last response, whichever is longer | `.jtl`, `.meta.json` |
| Mean and spread | Mean, minimum, maximum and standard deviation of each figure across the three runs | `load_configs.csv` |
| Reconciled | The `.jtl` and the service log have the same number of requests for the endpoint (warm-up excluded), every `request_id` matches, and status codes agree | `.jtl`, service log |

The warm-up request is in the service log but not in the `.jtl`. Its request ID is in `<RUN_ID>.meta.json`.
