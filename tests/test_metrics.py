import pandas as pd

from src.ab_testing import build_experiment_report
from src.funnel import build_funnel_report


def test_funnel_report_contains_expected_columns():
    data = pd.DataFrame(
        [
            {"user_id": 1, "event_name": "visit", "channel": "organic", "device": "mobile", "variant": "control"},
            {"user_id": 1, "event_name": "signup", "channel": "organic", "device": "mobile", "variant": "control"},
            {"user_id": 1, "event_name": "add_to_cart", "channel": "organic", "device": "mobile", "variant": "control"},
            {"user_id": 1, "event_name": "purchase", "channel": "organic", "device": "mobile", "variant": "control"},
        ]
    )
    report = build_funnel_report(data)
    assert "visit_to_purchase_rate" in report.columns
    assert report.loc[0, "visit_to_purchase_rate"] == 1.0


def test_experiment_report_outputs_single_row():
    data = pd.DataFrame(
        [
            {"user_id": 1, "event_name": "visit", "variant": "control"},
            {"user_id": 1, "event_name": "purchase", "variant": "control"},
            {"user_id": 2, "event_name": "visit", "variant": "treatment"},
            {"user_id": 2, "event_name": "purchase", "variant": "treatment"},
            {"user_id": 3, "event_name": "visit", "variant": "treatment"},
        ]
    )
    report = build_experiment_report(data)
    assert len(report) == 1
    assert "p_value" in report.columns
