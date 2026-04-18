import math

import pandas as pd
from scipy.stats import norm


def _z_test_two_proportions(success_a: int, total_a: int, success_b: int, total_b: int) -> tuple[float, float, float, float]:
    p1 = success_a / total_a
    p2 = success_b / total_b
    pooled = (success_a + success_b) / (total_a + total_b)
    se_pooled = math.sqrt(pooled * (1 - pooled) * (1 / total_a + 1 / total_b))
    z_score = (p2 - p1) / se_pooled if se_pooled else 0.0
    p_value = 2 * (1 - norm.cdf(abs(z_score)))

    se_unpooled = math.sqrt((p1 * (1 - p1) / total_a) + (p2 * (1 - p2) / total_b))
    ci_low = (p2 - p1) - 1.96 * se_unpooled
    ci_high = (p2 - p1) + 1.96 * se_unpooled
    return z_score, p_value, ci_low, ci_high


def build_experiment_report(events: pd.DataFrame) -> pd.DataFrame:
    exposure = (
        events.groupby(["user_id", "variant"], as_index=False)
        .agg(
            saw_visit=("event_name", lambda s: int((s == "visit").any())),
            purchased=("event_name", lambda s: int((s == "purchase").any())),
        )
    )

    summary = exposure.groupby("variant", as_index=False).agg(
        users=("user_id", "nunique"),
        purchasers=("purchased", "sum"),
    )
    summary["conversion_rate"] = summary["purchasers"] / summary["users"]

    control = summary[summary["variant"] == "control"].iloc[0]
    treatment = summary[summary["variant"] == "treatment"].iloc[0]

    z_score, p_value, ci_low, ci_high = _z_test_two_proportions(
        int(control["purchasers"]),
        int(control["users"]),
        int(treatment["purchasers"]),
        int(treatment["users"]),
    )

    lift_abs = float(treatment["conversion_rate"] - control["conversion_rate"])
    lift_rel = float(lift_abs / control["conversion_rate"]) if control["conversion_rate"] else 0.0

    return pd.DataFrame(
        [
            {
                "control_users": int(control["users"]),
                "treatment_users": int(treatment["users"]),
                "control_conversion_rate": float(control["conversion_rate"]),
                "treatment_conversion_rate": float(treatment["conversion_rate"]),
                "absolute_lift": lift_abs,
                "relative_lift": lift_rel,
                "z_score": z_score,
                "p_value": p_value,
                "ci_low": ci_low,
                "ci_high": ci_high,
                "is_significant_at_95pct": p_value < 0.05,
                "recommended_decision": "Ship treatment" if p_value < 0.05 and lift_abs > 0 else "Do not ship yet",
            }
        ]
    )
