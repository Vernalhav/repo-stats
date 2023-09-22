import asyncio
import datetime
import itertools
from dataclasses import dataclass
import pathlib
from typing import Iterable, Sequence, overload

from pydantic import RootModel

from repostats.metrics import github
from repostats.metrics.models import State

MAX_PRS_PER_PAGE = 1000


@dataclass(frozen=True)
class PRMetric:
    repo: str
    head_ref: str
    base_ref: str
    created_at: datetime.datetime
    merged_at: datetime.datetime | None
    state: State
    changed_files: int


class PRAnalyzer:
    def __init__(self, client: github.Client, repos: Sequence[str]) -> None:
        self.client = client
        self.repos: list[github.Repo] = []
        for repo in repos:
            owner, repo_name, *_ = repo.split("/")
            self.repos.append(github.Repo(owner, repo_name))

    @overload
    async def get_metrics(self) -> Sequence[PRMetric]:
        pass

    @overload
    async def get_metrics(self, prs_per_repo: int) -> Sequence[PRMetric]:
        pass

    async def get_metrics(self, prs_per_repo: int | None = None) -> Sequence[PRMetric]:
        tasks = (self._get_metrics_for_repo(repo, prs_per_repo) for repo in self.repos)
        metrics = await asyncio.gather(*tasks)
        return tuple(itertools.chain.from_iterable(metrics))

    async def _get_metrics_for_repo(
        self, repo: github.Repo, prs_per_repo: int | None
    ) -> Sequence[PRMetric]:
        cursor = None
        should_stop = False

        metrics: list[PRMetric] = []
        while not should_stop:
            n_items = (
                min(MAX_PRS_PER_PAGE, prs_per_repo - len(metrics))
                if prs_per_repo is not None
                else MAX_PRS_PER_PAGE
            )
            params = github.Params(n_items, cursor)
            graphql_data = await self.client.get_pr_metrics(repo, params)

            metrics.extend(map_graphql_to_metric(graphql_data))

            should_stop = (
                not graphql_data.data.repository.pull_requests.page_info.has_next
                or (prs_per_repo is not None and len(metrics) >= prs_per_repo)
            )

        return metrics


def map_graphql_to_metric(graphql: github.GraphQLPRMetrics) -> Iterable[PRMetric]:
    for pr in graphql.data.repository.pull_requests.edges:
        yield PRMetric(
            repo=graphql.data.repository.name,
            head_ref=pr.node.head_ref,
            base_ref=pr.node.base_ref,
            created_at=pr.node.created_at,
            merged_at=pr.node.merged_at,
            state=pr.node.state,
            changed_files=pr.node.changed_files,
        )
def export_metrics_to_json(metrics: Iterable[PRMetric], path: str) -> None:
    class PRMetricList(RootModel):
        root: tuple[PRMetric, ...]

    model = PRMetricList(root=tuple(metrics))
    contents = model.model_dump_json(indent=4)
    pathlib.Path(path).write_text(contents)
