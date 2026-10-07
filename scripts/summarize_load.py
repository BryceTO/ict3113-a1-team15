"""Summarise JMeter load/stress runs and reconcile each one with its service log.

For every results/jtl/<RUN_ID>.jtl it reads <RUN_ID>.meta.json (written by
jmeter/run_load.ps1) and results/logs/<RUN_ID>.log (written by the service), then writes:

    results/summary/load_runs.csv        one row per run and endpoint
    results/summary/load_configs.csv     mean and spread across the runs of a configuration
    results/summary/timeline/<RUN_ID>.csv   per-minute arrivals, completions, backlog, latency
    results/summary/stress_steps.csv     per-step figures for runs made with -StepRates

Definitions (state these wherever the numbers are quoted):
- Latency is JMeter's `elapsed` in ms, over ALL samples of the endpoint, failed ones included.
- Percentiles are nearest-rank, so every reported percentile is a latency that a real
  request in the .jtl actually had.
- Error = JMeter `success` is not true (non-2xx response or client-side timeout).
- Achieved throughput = successful responses / test time, where test time is the arrival
  window or the time from JMeter start to the last response, whichever is longer.
- Backlog = requests that had arrived but not yet finished at that instant.
"""
import argparse
import csv
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

ENDPOINTS = ["POST /tickets", "GET /search"]
METRICS = ["p50_ms", "p95_ms", "p99_ms", "mean_ms", "max_ms", "throughput_per_min", "error_rate_pct"]


def percentile(values, pct):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(pct / 100 * len(ordered)) - 1)]


def read_jtl(path):
    samples = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            start = int(row["timeStamp"])
            elapsed = int(row["elapsed"])
            samples.append(
                {
                    "start": start,
                    "end": start + elapsed,
                    "elapsed": elapsed,
                    "label": row["label"],
                    "code": row["responseCode"],
                    "ok": row["success"].strip().lower() == "true",
                    "request_id": row.get("request_id", "NA"),
                }
            )
    return samples


def read_log(path):
    entries = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def endpoint_stats(samples, start_ms, window_min):
    elapsed = [s["elapsed"] for s in samples]
    ok = sum(s["ok"] for s in samples)
    minutes = max(window_min, (max(s["end"] for s in samples) - start_ms) / 60000)
    return {
        "samples": len(samples),
        "errors": len(samples) - ok,
        "error_rate_pct": round(100 * (len(samples) - ok) / len(samples), 2),
        "p50_ms": percentile(elapsed, 50),
        "p95_ms": percentile(elapsed, 95),
        "p99_ms": percentile(elapsed, 99),
        "mean_ms": round(statistics.fmean(elapsed), 1),
        "max_ms": max(elapsed),
        "throughput_per_min": round(ok / minutes, 3),
    }


def reconcile(samples, log_path, endpoint, run_id, warmup_id):
    """Compare the .jtl samples of one endpoint with the service log lines of that endpoint."""
    if not log_path.exists():
        return {"reconciled": "NO LOG", "notes": f"{log_path} not found"}
    entries = [e for e in read_log(log_path) if e.get("endpoint") == endpoint and e.get("request_id") != warmup_id]
    notes = []
    by_id = {e["request_id"]: e for e in entries}
    if len(entries) != len(samples):
        notes.append(f"log has {len(entries)} lines, jtl has {len(samples)} samples")
    wrong_run = sum(e.get("run_id") != run_id for e in entries)
    if wrong_run:
        notes.append(f"{wrong_run} log lines carry a different run_id")
    no_id = sum(s["request_id"] not in by_id for s in samples)
    if no_id:
        notes.append(f"{no_id} jtl samples have no matching request_id in the log")
    matched = [(s, by_id[s["request_id"]]) for s in samples if s["request_id"] in by_id]
    status_diff = sum(s["code"] != str(e.get("status")) for s, e in matched)
    if status_diff:
        notes.append(f"{status_diff} samples differ in status code")
    out = {"reconciled": "no" if notes else "yes", "log_lines": len(entries), "notes": "; ".join(notes)}
    if matched:
        # time the request spent outside the service: network plus waiting to be accepted
        out["median_outside_service_ms"] = round(statistics.median(s["elapsed"] - e["latency_ms"] for s, e in matched), 1)
    if endpoint == "POST /tickets":
        ollama = [e["ollama_ms"] for e in entries if "ollama_ms" in e]
        if ollama:
            out["mean_ollama_ms"] = round(statistics.fmean(ollama), 1)
        out["models"] = "|".join(sorted({e["model"] for e in entries if "model" in e}))
        out["model_reloads"] = sum((e.get("ollama_load_ns") or 0) > 1e9 for e in entries)
        out["unclassified"] = sum(e.get("category") == "Unclassified" for e in entries)
    return out


def timeline(samples, start_ms):
    """Per-minute view of POST /tickets, bucketed by arrival minute."""
    rows = []
    last = max(s["end"] for s in samples)
    for minute in range(math.ceil((last - start_ms) / 60000)):
        lo, hi = start_ms + minute * 60000, start_ms + (minute + 1) * 60000
        arrived = [s for s in samples if lo <= s["start"] < hi]
        done = [s for s in samples if lo <= s["end"] < hi]
        rows.append(
            {
                "minute": minute + 1,
                "arrivals": len(arrived),
                "completions": len(done),
                "errors": sum(not s["ok"] for s in done),
                "backlog_at_end": sum(s["start"] < hi <= s["end"] for s in samples),
                "p50_ms_of_arrivals": percentile([s["elapsed"] for s in arrived], 50) if arrived else "",
                "max_ms_of_arrivals": max(s["elapsed"] for s in arrived) if arrived else "",
            }
        )
    return rows


def stress_steps(samples, start_ms, meta):
    """One row per arrival-rate step. The queue is 'growing' when the backlog rises over the
    step by more than 3 requests and more than 20% of the step's arrivals; the limit is the
    last step before that. The flag is a reading aid: the timeline CSV is the evidence."""
    rows = []
    step_ms = meta["step_min"] * 60000
    for i, rate in enumerate(meta["step_rates_per_min"]):
        lo, hi = start_ms + i * step_ms, start_ms + (i + 1) * step_ms
        arrived = [s for s in samples if lo <= s["start"] < hi]
        done = [s for s in samples if lo <= s["end"] < hi]
        backlog_start = sum(s["start"] < lo <= s["end"] for s in samples)
        backlog_end = sum(s["start"] < hi <= s["end"] for s in samples)
        elapsed = [s["elapsed"] for s in arrived]
        rows.append(
            {
                "step": i + 1,
                "target_rate_per_min": rate,
                "arrivals": len(arrived),
                "arrival_rate_per_min": round(len(arrived) / meta["step_min"], 2),
                "completion_rate_per_min": round(len(done) / meta["step_min"], 2),
                "errors_of_arrivals": sum(not s["ok"] for s in arrived),
                "backlog_start": backlog_start,
                "backlog_end": backlog_end,
                "p50_ms": percentile(elapsed, 50) if elapsed else "",
                "p95_ms": percentile(elapsed, 95) if elapsed else "",
                "max_ms": max(elapsed) if elapsed else "",
                "queue_growing": "yes" if backlog_end - backlog_start > max(3, 0.2 * len(arrived)) else "no",
            }
        )
    return rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Summarise JMeter runs and reconcile them with service logs.")
    parser.add_argument("--jtl-dir", default="results/jtl")
    parser.add_argument("--log-dir", default="results/logs")
    parser.add_argument("--out-dir", default="results/summary")
    args = parser.parse_args()
    jtl_dir, log_dir, out_dir = Path(args.jtl_dir), Path(args.log_dir), Path(args.out_dir)

    run_rows, step_rows = [], []
    for jtl in sorted(jtl_dir.glob("*.jtl")):
        run_id = jtl.stem
        samples = read_jtl(jtl)
        if not samples:
            print(f"{run_id}: empty .jtl, skipped")
            continue
        meta_path = jtl.with_suffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8-sig")) if meta_path.exists() else {}
        start_ms = meta.get("jmeter_started_ms") or min(s["start"] for s in samples)
        warmup_id = (meta.get("warmup") or {}).get("request_id")
        for endpoint in ENDPOINTS:
            subset = [s for s in samples if s["label"] == endpoint]
            if not subset:
                continue
            row = {"run_id": run_id, "config": re.sub(r"_run\d+$", "", run_id), "endpoint": endpoint}
            row.update(endpoint_stats(subset, start_ms, meta.get("arrival_window_min", 0)))
            row.update(reconcile(subset, log_dir / f"{run_id}.log", endpoint, run_id, warmup_id))
            run_rows.append(row)
        posts = [s for s in samples if s["label"] == "POST /tickets"]
        if posts:
            write_csv(out_dir / "timeline" / f"{run_id}.csv", timeline(posts, start_ms))
            if meta.get("step_rates_per_min"):
                step_rows += [{"run_id": run_id, **r} for r in stress_steps(posts, start_ms, meta)]

    if not run_rows:
        raise SystemExit(f"no .jtl files with samples in {jtl_dir}")

    groups = defaultdict(list)
    for row in run_rows:
        groups[(row["config"], row["endpoint"])].append(row)
    config_rows = []
    for (config, endpoint), rows in groups.items():
        out = {"config": config, "endpoint": endpoint, "runs": len(rows), "all_reconciled": all(r["reconciled"] == "yes" for r in rows)}
        for metric in METRICS:
            values = [r[metric] for r in rows]
            out[f"{metric}_mean"] = round(statistics.fmean(values), 2)
            out[f"{metric}_min"] = min(values)
            out[f"{metric}_max"] = max(values)
            out[f"{metric}_sd"] = round(statistics.stdev(values), 2) if len(values) > 1 else ""
        config_rows.append(out)

    write_csv(out_dir / "load_runs.csv", run_rows)
    write_csv(out_dir / "load_configs.csv", config_rows)
    if step_rows:
        write_csv(out_dir / "stress_steps.csv", step_rows)

    print("| run | endpoint | n | p50 ms | p95 ms | p99 ms | ok/min | err % | reconciled |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---|")
    for r in run_rows:
        flag = r["reconciled"] + (f" ({r['notes']})" if r.get("notes") else "")
        print(f"| {r['run_id']} | {r['endpoint']} | {r['samples']} | {r['p50_ms']} | {r['p95_ms']} | {r['p99_ms']} | {r['throughput_per_min']} | {r['error_rate_pct']} | {flag} |")
    for r in config_rows:
        if r["runs"] != 3:
            print(f"WARNING: {r['config']} [{r['endpoint']}] has {r['runs']} run(s); the brief requires 3.")
    print(f"\nwrote {out_dir}")


if __name__ == "__main__":
    main()
