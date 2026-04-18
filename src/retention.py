import pandas as pd


RETENTION_DAYS = [1, 7, 14, 30]


def build_retention_report(events: pd.DataFrame) -> pd.DataFrame:
    visits = events[events["event_name"].isin(["visit", "signup", "session", "purchase", "add_to_cart"])].copy()
    first_seen = (
        visits.groupby("user_id", as_index=False)["event_date"]
        .min()
        .rename(columns={"event_date": "cohort_date"})
    )
    visits = visits.merge(first_seen, on="user_id", how="left")
    visits["days_since_cohort"] = (visits["event_date"] - visits["cohort_date"]).dt.days

    cohorts = first_seen.groupby("cohort_date", as_index=False).agg(cohort_users=("user_id", "nunique"))

    records = []
    for cohort_date, cohort_users in cohorts.itertuples(index=False):
        cohort_visits = visits[visits["cohort_date"] == cohort_date]
        for day in RETENTION_DAYS:
            retained_users = cohort_visits.loc[cohort_visits["days_since_cohort"] == day, "user_id"].nunique()
            records.append(
                {
                    "cohort_date": cohort_date,
                    "retention_day": day,
                    "cohort_users": cohort_users,
                    "retained_users": retained_users,
                    "retention_rate": retained_users / cohort_users if cohort_users else 0.0,
                }
            )

    return pd.DataFrame(records).sort_values(["cohort_date", "retention_day"]).reset_index(drop=True)
