from __future__ import annotations

import json
import pathlib
from typing import Sequence

import pandas as pd

from repostats.metrics.metrics import PRMetric


class Provider:
    def __init__(self, metrics: Sequence[PRMetric]) -> None:
        self.metrics = metrics
        self.df = pd.DataFrame(metric.model_dump() for metric in metrics)

    def get_files_changed(self, repos: Sequence[str]) -> pd.DataFrame:
        return self.df[self.df["repo"].isin(repos)][["repo", "changed_files"]]

    def get_changes_per_release(self) -> pd.DataFrame:
        pass

    @staticmethod
    def from_json(path: str | pathlib.Path) -> Provider:
        metrics = import_metrics_from_json(path)
        return Provider(metrics)


def import_metrics_from_json(path: str | pathlib.Path) -> Sequence[PRMetric]:
    contents = pathlib.Path(path).read_text()
    data = json.loads(contents)
    return tuple(PRMetric(**metric) for metric in data)


if __name__ == "__main__":
    metrics = import_metrics_from_json("data/metrics.json")
    p = Provider(metrics)
    print(p.get_files_changed(["theBricks/MirroredSouls", "Vernalhav/levada"]))
