import argparse
import time
from pathlib import Path

import pandas as pd
import requests


VALID_CATEGORIES = {
    "credit reporting": "Credit reporting",
    "debt collection": "Debt collection",
    "mortgage": "Mortgage",
    "credit card": "Credit card",
    "bank account or service": "Bank account or service",
    "consumer loan": "Consumer loan",
    "money transfer or service": "Money transfer or service",
}


def normalize_label(label):
    text = str(label).strip().lower()

    if text not in VALID_CATEGORIES:
        raise ValueError(f"Unknown category: {label}")

    return VALID_CATEGORIES[text]


def validate_golden_set(df):
    required_columns = {"ROW", "NARRATIVE", "GOLDEN_LABEL"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Golden set must contain columns {required_columns}. "
            f"Found: {list(df.columns)}"
        )

    if len(df) != 175:
        raise ValueError(
            f"Expected 175 golden-set tickets, found {len(df)}"
        )

    if df["ROW"].duplicated().any():
        duplicates = df.loc[df["ROW"].duplicated(), "ROW"].tolist()
        raise ValueError(f"Duplicate ROW values found: {duplicates}")

    if df["NARRATIVE"].isna().any():
        raise ValueError("Golden set contains blank narratives")

    if df["GOLDEN_LABEL"].isna().any():
        raise ValueError("Golden set contains blank golden labels")

    for label in df["GOLDEN_LABEL"]:
        normalize_label(label)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--golden",
        default="golden_set/golden_set.csv"
    )

    parser.add_argument(
        "--url",
        default="http://localhost:8000"
    )

    parser.add_argument(
        "--model",
        required=True
    )

    parser.add_argument(
        "--output",
        required=True
    )

    args = parser.parse_args()

    golden = pd.read_csv(args.golden)

    validate_golden_set(golden)

    print(f"Model: {args.model}")
    print(f"Golden set: {args.golden}")
    print(f"Service URL: {args.url}")
    print(f"Tickets: {len(golden)}")
    print()

    results = []

    for index, row in golden.iterrows():

        row_id = int(row["ROW"])
        narrative = str(row["NARRATIVE"])
        golden_label = normalize_label(row["GOLDEN_LABEL"])

        start = time.perf_counter()

        try:
            response = requests.post(
                f"{args.url}/tickets",
                json={
                    "narrative": narrative,
                    "row_id": row_id
                },
                timeout=300
            )

            elapsed = time.perf_counter() - start
            http_status = response.status_code

            response.raise_for_status()

            data = response.json()

            predicted_raw = data.get("category", "")

            try:
                predicted_label = normalize_label(predicted_raw)
                classification_valid = True
            except ValueError:
                predicted_label = str(predicted_raw).strip()
                classification_valid = False

            request_id = (
                data.get("id")
                or response.headers.get("X-Request-ID", "")
            )

            correct = (
                classification_valid
                and predicted_label == golden_label
            )

            error = ""

        except Exception as exc:

            elapsed = time.perf_counter() - start

            predicted_label = ""
            request_id = ""

            if "response" in locals():
                http_status = getattr(response, "status_code", "")
            else:
                http_status = ""

            correct = False
            classification_valid = False
            error = str(exc)

        results.append(
            {
                "row": row_id,
                "model": args.model,
                "golden_label": golden_label,
                "predicted_label": predicted_label,
                "correct": correct,
                "request_id": request_id,
                "http_status": http_status,
                "latency_seconds": round(elapsed, 3),
                "error": error
            }
        )

        if error:
            status = "ERROR"
        elif correct:
            status = "CORRECT"
        else:
            status = "WRONG"

        print(
            f"[{index + 1:03}/{len(golden)}] "
            f"Row {row_id} | "
            f"Golden: {golden_label} | "
            f"Predicted: {predicted_label} | "
            f"{status}"
        )

    result_df = pd.DataFrame(results)

    output_path = Path(args.output)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result_df.to_csv(
        output_path,
        index=False
    )

    total = len(result_df)

    error_count = int(
        result_df["error"].astype(str).str.len().gt(0).sum()
    )

    successful_requests = total - error_count

    correct_count = int(
        result_df["correct"].sum()
    )

    wrong_count = (
        successful_requests - correct_count
    )

    accuracy = (
        correct_count / successful_requests * 100
        if successful_requests > 0
        else 0
    )

    print()
    print("=== Accuracy Run Summary ===")
    print(f"Model: {args.model}")
    print(f"Total golden tickets: {total}")
    print(f"Successful requests: {successful_requests}")
    print(f"Request errors: {error_count}")
    print(f"Correct classifications: {correct_count}")
    print(f"Wrong classifications: {wrong_count}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Results saved to: {output_path}")

    if error_count > 0:
        print()
        print(
            "WARNING: This run contains request errors. "
            "Investigate them before treating this as the final official result."
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()