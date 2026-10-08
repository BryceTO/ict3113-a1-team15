import pandas as pd
from pathlib import Path

FILES = {
    "llama3.2:1b": "results/accuracy/llama3.2_1b_predictions.csv",
    "gemma3:4b": "results/accuracy/gemma3_4b_predictions.csv",
    "mistral:7b-instruct": "results/accuracy/mistral_7b_predictions.csv",
}

OUT_DIR = Path("results/accuracy")
OUT_DIR.mkdir(parents=True, exist_ok=True)

summary_rows = []
per_category_rows = []

for model, file_path in FILES.items():
    df = pd.read_csv(file_path)

    total = len(df)
    successful = (df["http_status"] == 200).sum()
    errors = total - successful
    correct = ((df["correct"] == True) & (df["http_status"] == 200)).sum()
    wrong = ((df["correct"] == False) & (df["http_status"] == 200)).sum()

    accuracy_successful = (correct / successful * 100) if successful else 0
    end_to_end_correct = (correct / total * 100) if total else 0
    error_rate = (errors / total * 100) if total else 0

    summary_rows.append({
        "model": model,
        "total": total,
        "successful": successful,
        "errors": errors,
        "error_rate_percent": round(error_rate, 2),
        "correct": correct,
        "wrong": wrong,
        "accuracy_successful_percent": round(accuracy_successful, 2),
        "end_to_end_correct_percent": round(end_to_end_correct, 2),
    })

    success_df = df[df["http_status"] == 200].copy()

    category_stats = (
        success_df.groupby("golden_label")
        .agg(
            successful_requests=("row", "count"),
            correct=("correct", "sum"),
        )
        .reset_index()
    )

    category_stats["accuracy_percent"] = (
        category_stats["correct"] /
        category_stats["successful_requests"] * 100
    ).round(2)

    category_stats["model"] = model

    per_category_rows.append(
        category_stats[
            [
                "model",
                "golden_label",
                "successful_requests",
                "correct",
                "accuracy_percent",
            ]
        ]
    )

    confusion = pd.crosstab(
        success_df["golden_label"],
        success_df["predicted_label"],
        rownames=["golden_label"],
        colnames=["predicted_label"],
        dropna=False,
    )

    safe_model = (
        model.replace(":", "_")
        .replace("/", "_")
        .replace(".", "_")
    )

    confusion.to_csv(
        OUT_DIR / f"confusion_{safe_model}.csv"
    )

    wrong_df = success_df[
        success_df["golden_label"] != success_df["predicted_label"]
    ]

    misclassifications = (
        wrong_df.groupby(
            ["golden_label", "predicted_label"]
        )
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    misclassifications.to_csv(
        OUT_DIR / f"misclassifications_{safe_model}.csv",
        index=False
    )


summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(
    OUT_DIR / "accuracy_summary.csv",
    index=False
)

per_category_df = pd.concat(
    per_category_rows,
    ignore_index=True
)

per_category_df.to_csv(
    OUT_DIR / "per_category_accuracy.csv",
    index=False
)

print("\n=== Overall Accuracy Summary ===")
print(summary_df.to_string(index=False))

print("\n=== Per Category Accuracy ===")
print(per_category_df.to_string(index=False))

print("\nFiles created:")
print("results/accuracy/accuracy_summary.csv")
print("results/accuracy/per_category_accuracy.csv")
print("results/accuracy/confusion_llama3_2_1b.csv")
print("results/accuracy/confusion_gemma3_4b.csv")
print("results/accuracy/confusion_mistral_7b-instruct.csv")
print("results/accuracy/misclassifications_*.csv")