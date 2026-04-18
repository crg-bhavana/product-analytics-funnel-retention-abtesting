import pandas as pd


FUNNEL_STEPS = ["visit", "signup", "add_to_cart", "purchase"]


def _user_step_flags(events: pd.DataFrame) -> pd.DataFrame:
    flags = (
        events.assign(value=1)
        .pivot_table(
            index=["user_id", "channel", "device", "variant"],
            columns="event_name",
            values="value",
            aggfunc="max",
            fill_value=0,
        )
        .reset_index()
    )

    for step in FUNNEL_STEPS:
        if step not in flags.columns:
            flags[step] = 0

    return flags


def build_funnel_report(events: pd.DataFrame) -> pd.DataFrame:
    flags = _user_step_flags(events)

    grouped = (
        flags.groupby(["channel", "device"], as_index=False)[FUNNEL_STEPS]
        .sum()
        .rename(
            columns={
                "visit": "visitors",
                "signup": "signups",
                "add_to_cart": "add_to_carts",
                "purchase": "purchases",
            }
        )
    )

    grouped["visit_to_signup_rate"] = grouped["signups"] / grouped["visitors"]
    grouped["signup_to_cart_rate"] = grouped["add_to_carts"] / grouped["signups"].clip(lower=1)
    grouped["cart_to_purchase_rate"] = grouped["purchases"] / grouped["add_to_carts"].clip(lower=1)
    grouped["visit_to_purchase_rate"] = grouped["purchases"] / grouped["visitors"]

    return grouped.sort_values("visit_to_purchase_rate", ascending=False).reset_index(drop=True)
