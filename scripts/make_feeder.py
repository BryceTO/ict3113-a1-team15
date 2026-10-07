"""Build the JMeter feeder file from the Team 15 rows.

Narratives contain quotes and line breaks, which break both JMeter's CSV Data
Set Config and a hand-built JSON body. This writes one line per ticket:

    <row_id> TAB <complete JSON request body>

json.dumps escapes every quote, newline and tab and emits ASCII only, so each
body is a single line and a raw TAB can only ever be the delimiter.
Rows are kept in dataset order, so every run draws the same tickets in the
same sequence.
"""
import argparse
import csv
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Build the JMeter feeder file.")
    parser.add_argument("--input", default="context/team15_rows.csv", help="Path to Team 15 CSV")
    parser.add_argument("--output", default="jmeter/feeder.tsv", help="Feeder file to write")
    args = parser.parse_args()

    lines = []
    with Path(args.input).open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            row_id = int(row["row"])
            if not 15000 <= row_id <= 15999:
                raise SystemExit(f"row {row_id} is outside Team 15's range 15000-15999")
            if not row["narrative"].strip():
                raise SystemExit(f"row {row_id} has an empty narrative")
            body = json.dumps({"narrative": row["narrative"], "row_id": row_id})
            lines.append(f"{row_id}\t{body}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    print(f"wrote {len(lines)} tickets to {out}")


if __name__ == "__main__":
    main()
