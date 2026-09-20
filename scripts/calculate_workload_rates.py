import csv
from pathlib import Path


COMPLAINTS_SENT_TO_COMPANIES = 2_829_400
COMPANY_COUNT = 3_600
CLIENT_SCALE_FACTOR = 10
BUSINESS_DAYS_PER_YEAR = 250
BUSINESS_HOURS_PER_DAY = 8
BUSINESS_HOURS_SHARE = 0.70
PEAK_MULTIPLIER = 3
SEARCHES_PER_TICKET = 1 / 5


def rounded(value):
    return round(value, 3)


def main():
    outdir = Path("analysis")
    outdir.mkdir(parents=True, exist_ok=True)

    mean_company_tickets_year = COMPLAINTS_SENT_TO_COMPANIES / COMPANY_COUNT
    client_tickets_year = mean_company_tickets_year * CLIENT_SCALE_FACTOR
    tickets_business_day = client_tickets_year / BUSINESS_DAYS_PER_YEAR
    business_hour_tickets_day = tickets_business_day * BUSINESS_HOURS_SHARE
    average_tickets_hour = business_hour_tickets_day / BUSINESS_HOURS_PER_DAY
    average_tickets_minute = average_tickets_hour / 60
    peak_tickets_hour = average_tickets_hour * PEAK_MULTIPLIER
    peak_tickets_minute = peak_tickets_hour / 60
    peak_searches_hour = peak_tickets_hour * SEARCHES_PER_TICKET
    peak_searches_minute = peak_searches_hour / 60

    calculations = [
        ("Mean company-forwarded complaints/year", "2,829,400 / 3,600", mean_company_tickets_year),
        ("Draft client tickets/year", "mean company complaints/year * 10", client_tickets_year),
        ("Tickets/business day", "client tickets/year / 250", tickets_business_day),
        ("Business-hours tickets/day", "tickets/business day * 70%", business_hour_tickets_day),
        ("Average POST /tickets per hour", "business-hours tickets/day / 8", average_tickets_hour),
        ("Average POST /tickets per minute", "average tickets/hour / 60", average_tickets_minute),
        ("Peak POST /tickets per hour", "average tickets/hour * 3", peak_tickets_hour),
        ("Peak POST /tickets per minute", "peak tickets/hour / 60", peak_tickets_minute),
        ("Peak GET /search per hour", "peak tickets/hour / 5", peak_searches_hour),
        ("Peak GET /search per minute", "peak searches/hour / 60", peak_searches_minute),
    ]

    scenarios = [
        ("normal", "Typical complaint intake", 3, 0.05, 0, "Mostly POST /tickets"),
        ("peak", "Main requirement condition", 9, 0.15, 2, "POST /tickets plus GET /search"),
        ("stretch", "Headroom demonstration", 60, 1.0, 12, "Same endpoint mix as peak"),
        ("stress", "Find system limit", None, None, None, "Increase POST /tickets until failure or unbounded latency"),
    ]

    calculations_path = outdir / "workload_calculations.csv"
    with calculations_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "formula", "value"])
        for metric, formula, value in calculations:
            writer.writerow([metric, formula, rounded(value)])

    scenarios_path = outdir / "load_scenarios.csv"
    with scenarios_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scenario", "purpose", "post_per_hour", "post_per_minute", "search_per_hour", "endpoint_mix"])
        for scenario in scenarios:
            writer.writerow(scenario)

    markdown_path = outdir / "workload_calculations.md"
    with markdown_path.open("w", encoding="utf-8") as handle:
        handle.write("# Workload Calculations\n\n")
        handle.write("## Inputs\n\n")
        handle.write("| Input | Value |\n")
        handle.write("|---|---:|\n")
        handle.write(f"| CFPB complaints sent to companies in 2024 | {COMPLAINTS_SENT_TO_COMPANIES:,} |\n")
        handle.write(f"| Companies receiving complaints | {COMPANY_COUNT:,} |\n")
        handle.write(f"| Client scale factor | {CLIENT_SCALE_FACTOR}x mean company volume |\n")
        handle.write(f"| Business days/year | {BUSINESS_DAYS_PER_YEAR} |\n")
        handle.write(f"| Business hours/day | {BUSINESS_HOURS_PER_DAY} |\n")
        handle.write(f"| Share of tickets during business hours | {BUSINESS_HOURS_SHARE:.0%} |\n")
        handle.write(f"| Peak multiplier | {PEAK_MULTIPLIER}x average business-hour rate |\n")
        handle.write(f"| Search rate | 1 search per 5 classified tickets |\n")
        handle.write("\n## Derived Workload\n\n")
        handle.write("| Metric | Formula | Value |\n")
        handle.write("|---|---|---:|\n")
        for metric, formula, value in calculations:
            handle.write(f"| {metric} | {formula} | {rounded(value)} |\n")
        handle.write("\n## Load Scenarios\n\n")
        handle.write("| Scenario | Purpose | POST/hour | POST/minute | Search/hour | Endpoint mix |\n")
        handle.write("|---|---|---:|---:|---:|---|\n")
        for name, purpose, post_hour, post_minute, search_hour, endpoint_mix in scenarios:
            post_hour_text = "TBD" if post_hour is None else str(post_hour)
            post_minute_text = "TBD" if post_minute is None else str(post_minute)
            search_hour_text = "TBD" if search_hour is None else str(search_hour)
            handle.write(
                f"| {name} | {purpose} | {post_hour_text} | {post_minute_text} | "
                f"{search_hour_text} | {endpoint_mix} |\n"
            )

    print(f"Wrote {calculations_path}")
    print(f"Wrote {scenarios_path}")
    print(f"Wrote {markdown_path}")


if __name__ == "__main__":
    main()
