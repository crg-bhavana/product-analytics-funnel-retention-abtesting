from pathlib import Path

import pandas as pd


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_events(path: str) -> pd.DataFrame:
    events = pd.read_csv(path, parse_dates=["event_time"])
    events["event_date"] = events["event_time"].dt.normalize()
    return events
