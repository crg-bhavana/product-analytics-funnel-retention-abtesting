from pathlib import Path

import pandas as pd

from src.funnel import build_funnel_report
from src.retention import build_retention_report
from src.ab_testing import build_experiment_report
from src.reporting import build_kpi_summary, create_charts
from src.utils import ensure_directory, load_events


def main() -> None:
    output_dir = Path("outputs")
    ensure_directory(output_dir)

    events = load_events("data/raw/events.csv")

    funnel_report = build_funnel_report(events)
    retention_report = build_retention_report(events)
    experiment_report = build_experiment_report(events)
    kpi_summary = build_kpi_summary(events, funnel_report, retention_report, experiment_report)

    funnel_report.to_csv(output_dir / "funnel_report.csv", index=False)
    retention_report.to_csv(output_dir / "retention_report.csv", index=False)
    experiment_report.to_csv(output_dir / "experiment_report.csv", index=False)
    kpi_summary.to_csv(output_dir / "kpi_summary.csv", index=False)

    create_charts(events, funnel_report, retention_report, output_dir)

    print("Analytics pipeline complete.")
    print("Generated files:")
    for path in sorted(output_dir.glob("*")):
        print(f" - {path}")


if __name__ == "__main__":
    main()
