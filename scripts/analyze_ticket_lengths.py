import argparse
import csv
import math
from collections import Counter
from pathlib import Path


def percentile(values, pct):
    if not values:
        raise ValueError("percentile requires at least one value")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (pct / 100) * (len(ordered) - 1)
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    weight = rank - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def word_count(text):
    return len(text.split())


def estimated_tokens(text):
    # Rough English-token estimate for slide-level workload modelling.
    return math.ceil(len(text) / 4)


def main():
    parser = argparse.ArgumentParser(description="Summarise Team 15 ticket narrative lengths.")
    parser.add_argument("--input", default="context/team15_rows.csv", help="Path to Team 15 CSV")
    parser.add_argument("--outdir", default="analysis", help="Directory for derived outputs")
    args = parser.parse_args()

    input_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    source_counts = Counter()

    with input_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            narrative = row["narrative"]
            rows.append(
                {
                    "row": int(row["row"]),
                    "source_label": row["source_label"],
                    "chars": len(narrative),
                    "words": word_count(narrative),
                    "estimated_tokens": estimated_tokens(narrative),
                }
            )
            source_counts[row["source_label"]] += 1

    if not rows:
        raise SystemExit("No rows found")

    metrics = {
        "characters": [row["chars"] for row in rows],
        "words": [row["words"] for row in rows],
        "estimated_tokens": [row["estimated_tokens"] for row in rows],
    }
    percentiles = [0, 25, 50, 75, 90, 95, 99, 100]

    summary_path = outdir / "ticket_length_distribution.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "count", "mean", "p0_min", "p25", "p50_median", "p75", "p90", "p95", "p99", "p100_max"])
        for metric, values in metrics.items():
            writer.writerow(
                [
                    metric,
                    len(values),
                    round(sum(values) / len(values), 2),
                    *[round(percentile(values, pct), 2) for pct in percentiles],
                ]
            )

    labels_path = outdir / "source_label_distribution.csv"
    with labels_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source_label", "count"])
        for label, count in sorted(source_counts.items(), key=lambda item: (-item[1], item[0])):
            writer.writerow([label, count])

    markdown_path = outdir / "ticket_length_distribution.md"
    with markdown_path.open("w", encoding="utf-8") as handle:
        handle.write("# Team 15 Ticket Length Distribution\n\n")
        handle.write(f"Input: `{input_path}`\n\n")
        handle.write(f"Rows analysed: {len(rows)}\n\n")
        handle.write(f"Row range: {min(row['row'] for row in rows)} to {max(row['row'] for row in rows)}\n\n")
        handle.write("## Length Summary\n\n")
        handle.write("| Metric | Mean | Min | p25 | Median | p75 | p90 | p95 | p99 | Max |\n")
        handle.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for metric, values in metrics.items():
            values_by_pct = {pct: percentile(values, pct) for pct in percentiles}
            handle.write(
                f"| {metric} | {sum(values) / len(values):.2f} | "
                f"{values_by_pct[0]:.0f} | {values_by_pct[25]:.0f} | {values_by_pct[50]:.0f} | "
                f"{values_by_pct[75]:.0f} | {values_by_pct[90]:.0f} | {values_by_pct[95]:.0f} | "
                f"{values_by_pct[99]:.0f} | {values_by_pct[100]:.0f} |\n"
            )
        handle.write("\n## Source Label Distribution\n\n")
        handle.write("| Source label | Count |\n")
        handle.write("|---|---:|\n")
        for label, count in sorted(source_counts.items(), key=lambda item: (-item[1], item[0])):
            handle.write(f"| {label} | {count} |\n")
        handle.write("\nRaw source labels are noisy and are shown only to describe the Team 15 extract.\n")

    print(f"Wrote {summary_path}")
    print(f"Wrote {labels_path}")
    print(f"Wrote {markdown_path}")


if __name__ == "__main__":
    main()
