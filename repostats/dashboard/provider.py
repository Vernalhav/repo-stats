from __future__ import annotations

import datetime
import json
import pathlib
from collections import Counter
from typing import NamedTuple, Sequence

import pandas as pd

from repostats.metrics.metrics import PRMetric


class HotfixesByRelease(NamedTuple):
    release: str
    hotfixes: int


class Provider:
    def __init__(self, metrics: Sequence[PRMetric]) -> None:
        self.metrics = metrics
        self.df = pd.DataFrame(metric.model_dump() for metric in metrics)
        self.is_release = is_gitflow_release
        self.is_hotfix = is_gitflow_hotfix

    def get_files_changed(self, repos: Sequence[str]) -> pd.DataFrame:
        return self.df[self.df.repo.isin(repos)][["repo", "changed_files"]]

    def get_hotfixes_per_release(self, repo: str) -> pd.DataFrame:
        prs = [pr for pr in self.metrics if pr.repo.casefold() == repo.casefold()]
        releases = determine_hotfix_releases(prs)
        return pd.DataFrame(
            (release for release in releases), columns=["release", "hotfixes"]
        )

    @staticmethod
    def from_json(path: str | pathlib.Path) -> Provider:
        metrics = import_metrics_from_json(path)
        return Provider(metrics)


def import_metrics_from_json(path: str | pathlib.Path) -> Sequence[PRMetric]:
    contents = pathlib.Path(path).read_text()
    data = json.loads(contents)
    return tuple(PRMetric(**metric) for metric in data)


def determine_hotfix_releases(prs: Sequence[PRMetric]) -> Sequence[HotfixesByRelease]:
    prs = sorted(
        prs,
        key=lambda pr: pr.merged_at.replace(tzinfo=None)
        if pr.merged_at is not None
        else datetime.datetime.max,
    )
    release = None
    releases = []
    counts = Counter()
    for pr in prs:
        if is_gitflow_release(pr):
            release = pr.head_ref
            releases.append(release)
        if is_gitflow_hotfix(pr):
            counts[release] += 1
    return tuple(HotfixesByRelease(release, counts[release]) for release in releases)


def is_gitflow_release(pr: PRMetric) -> bool:
    return pr.head_ref.startswith("release/")


def is_gitflow_hotfix(pr: PRMetric) -> bool:
    return pr.head_ref.startswith("hotfix/")


if __name__ == "__main__":
    metrics = import_metrics_from_json("data/metrics.json")
    p = Provider(metrics)
    df = p.get_hotfixes_per_release("theBricks/MirroredSouls")
    print(df)
