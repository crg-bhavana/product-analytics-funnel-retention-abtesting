from pathlib import Path

import numpy as np
import pandas as pd


def generate_synthetic_events(
    n_users: int = 12000,
    seed: int = 42,
    start_date: str = "2025-01-01",
    end_date: str = "2025-03-31",
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    total_days = (end - start).days + 1

    user_ids = np.arange(1, n_users + 1)
    signup_dates = start + pd.to_timedelta(rng.integers(0, total_days, size=n_users), unit="D")

    channels = rng.choice(
        ["organic", "paid_search", "social", "email", "referral"],
        size=n_users,
        p=[0.30, 0.24, 0.18, 0.12, 0.16],
    )
    devices = rng.choice(["mobile", "desktop", "tablet"], size=n_users, p=[0.58, 0.34, 0.08])
    variants = rng.choice(["control", "treatment"], size=n_users, p=[0.5, 0.5])

    base_df = pd.DataFrame(
        {
            "user_id": user_ids,
            "signup_date": signup_dates,
            "channel": channels,
            "device": devices,
            "variant": variants,
        }
    )

    events = []

    channel_signup = {
        "organic": 0.60,
        "paid_search": 0.54,
        "social": 0.46,
        "email": 0.68,
        "referral": 0.64,
    }
    device_modifier = {"mobile": -0.03, "desktop": 0.03, "tablet": 0.01}

    for row in base_df.itertuples(index=False):
        signup_prob = channel_signup[row.channel] + device_modifier[row.device]
        signed_up = rng.random() < signup_prob

        first_ts = row.signup_date + pd.to_timedelta(int(rng.integers(0, 86400)), unit="s")
        events.append(
            {
                "user_id": row.user_id,
                "event_time": first_ts,
                "event_name": "visit",
                "channel": row.channel,
                "device": row.device,
                "variant": row.variant,
                "order_value": 0.0,
            }
        )

        if not signed_up:
            continue

        signup_ts = first_ts + pd.to_timedelta(int(rng.integers(60, 7200)), unit="s")
        events.append(
            {
                "user_id": row.user_id,
                "event_time": signup_ts,
                "event_name": "signup",
                "channel": row.channel,
                "device": row.device,
                "variant": row.variant,
                "order_value": 0.0,
            }
        )

        cart_prob = 0.48 + (0.04 if row.device == "desktop" else 0.0) + (0.02 if row.channel == "email" else 0.0)
        added_to_cart = rng.random() < cart_prob

        if added_to_cart:
            cart_ts = signup_ts + pd.to_timedelta(int(rng.integers(300, 72000)), unit="s")
            events.append(
                {
                    "user_id": row.user_id,
                    "event_time": cart_ts,
                    "event_name": "add_to_cart",
                    "channel": row.channel,
                    "device": row.device,
                    "variant": row.variant,
                    "order_value": 0.0,
                }
            )

            purchase_prob = 0.26
            if row.variant == "treatment":
                purchase_prob += 0.04
            if row.channel == "referral":
                purchase_prob += 0.02
            if row.device == "mobile":
                purchase_prob -= 0.02

            purchased = rng.random() < purchase_prob
            if purchased:
                purchase_ts = cart_ts + pd.to_timedelta(int(rng.integers(60, 172800)), unit="s")
                order_value = float(np.round(np.exp(rng.normal(3.8, 0.45)), 2))
                events.append(
                    {
                        "user_id": row.user_id,
                        "event_time": purchase_ts,
                        "event_name": "purchase",
                        "channel": row.channel,
                        "device": row.device,
                        "variant": row.variant,
                        "order_value": order_value,
                    }
                )

        # retention-style follow-up sessions
        n_return_sessions = rng.poisson(1.3)
        for _ in range(n_return_sessions):
            day_offset = int(rng.choice([1, 2, 3, 7, 14, 21, 30, 45], p=[0.18,0.15,0.12,0.18,0.13,0.10,0.09,0.05]))
            return_date = row.signup_date + pd.Timedelta(days=day_offset)
            if return_date > end:
                continue
            session_ts = return_date + pd.to_timedelta(int(rng.integers(0, 86400)), unit="s")
            events.append(
                {
                    "user_id": row.user_id,
                    "event_time": session_ts,
                    "event_name": "session",
                    "channel": row.channel,
                    "device": row.device,
                    "variant": row.variant,
                    "order_value": 0.0,
                }
            )

    events_df = pd.DataFrame(events).sort_values(["event_time", "user_id"]).reset_index(drop=True)
    return events_df


def main() -> None:
    out_path = Path("data/raw/events.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_synthetic_events()
    df.to_csv(out_path, index=False)
    print(f"Saved synthetic data to {out_path} with {len(df):,} rows.")


if __name__ == "__main__":
    main()
