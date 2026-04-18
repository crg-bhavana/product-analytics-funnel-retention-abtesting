from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def build_kpi_summary(
    events: pd.DataFrame,
    funnel_report: pd.DataFrame,
    retention_report: pd.DataFrame,
    experiment_report: pd.DataFrame,
) -> pd.DataFrame:
    dau = events.groupby("event_date")["user_id"].nunique()
    revenue = events.loc[events["event_name"] == "purchase", "order_value"].sum()
    purchasers = events.loc[events["event_name"] == "purchase", "user_id"].nunique()
    visitors = events.loc[events["event_name"] == "visit", "user_id"].nunique()

    summary = pd.DataFrame(
        [
            ("total_users", events["user_id"].nunique()),
            ("total_visitors", visitors),
            ("total_purchasers", purchasers),
            ("purchase_rate", purchasers / visitors if visitors else 0.0),
            ("total_revenue", revenue),
            ("average_daily_active_users", dau.mean()),
            ("best_segment_visit_to_purchase_rate", funnel_report["visit_to_purchase_rate"].max()),
            ("mean_day_7_retention", retention_report.loc[retention_report["retention_day"] == 7, "retention_rate"].mean()),
            ("experiment_absolute_lift", experiment_report.loc[0, "absolute_lift"]),
            ("experiment_p_value", experiment_report.loc[0, "p_value"]),
        ],
        columns=["metric_name", "metric_value"],
    )
    return summary


def create_charts(events: pd.DataFrame, funnel_report: pd.DataFrame, retention_report: pd.DataFrame, output_dir: Path) -> None:
    daily_users = events.groupby("event_date")["user_id"].nunique()

    plt.figure(figsize=(10, 5))
    daily_users.plot()
    plt.title("Daily Active Users")
    plt.xlabel("Date")
    plt.ylabel("Unique Active Users")
    plt.tight_layout()
    plt.savefig(output_dir / "daily_active_users.png")
    plt.close()

    top_funnel = funnel_report.sort_values("visit_to_purchase_rate", ascending=False).head(8).copy()
    top_funnel["segment"] = top_funnel["channel"] + " | " + top_funnel["device"]

    plt.figure(figsize=(10, 5))
    plt.bar(top_funnel["segment"], top_funnel["visit_to_purchase_rate"])
    plt.title("Top Segments by Visit-to-Purchase Conversion")
    plt.xlabel("Segment")
    plt.ylabel("Conversion Rate")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_dir / "segment_conversion.png")
    plt.close()

    day7 = retention_report[retention_report["retention_day"] == 7].copy()
    day7["cohort_date"] = day7["cohort_date"].astype(str)

    plt.figure(figsize=(10, 5))
    plt.plot(day7["cohort_date"], day7["retention_rate"])
    plt.title("Day-7 Retention by Cohort")
    plt.xlabel("Cohort Date")
    plt.ylabel("Retention Rate")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_dir / "day7_retention.png")
    plt.close()
