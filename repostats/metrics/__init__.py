from typing import Sequence

from repostats.metrics import github, metrics


async def to_json(
    repos: Sequence[str], token: str, outfile: str, prs_per_repo: int | None = None
) -> None:
    client = github.Client(token)
    analyzer = metrics.PRAnalyzer(client, repos)
    data = await analyzer.get_metrics(prs_per_repo)
    metrics.export_metrics_to_json(data, outfile)
