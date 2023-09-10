import asyncio
from typing import NamedTuple

import httpx

from repostats.metrics.models import Cursor, GraphQLPRMetrics

METRICS_QUERY = """
query {{
    repository(owner: "{owner}", name: "{name}") {{
        description,
        nameWithOwner,
        pullRequests(
                first: {amount},
                {after_clause}
                orderBy: {{ field: CREATED_AT, direction: DESC }}) {{
            edges {{
                node {{
                    title,
                    state,
                    changedFiles,
                    createdAt,
                    mergedAt,
                    baseRefName,
                    headRefName
                }},
            }},
            pageInfo {{
                endCursor,
                hasNextPage
            }}
        }}
    }}
}}"""


class Repo(NamedTuple):
    owner: str
    name: str


class Params(NamedTuple):
    items_per_page: int
    after: Cursor | None


class Client:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str) -> None:
        self.http = httpx.AsyncClient(headers={"Authorization": f"Bearer {token}"})

    async def get_pr_metrics(self, repo: Repo, params: Params) -> GraphQLPRMetrics:
        after_clause = f'after: "{params.after}",\n' if params.after is not None else ""
        query = METRICS_QUERY.format(
            owner=repo.owner,
            name=repo.name,
            amount=params.items_per_page,
            after_clause=after_clause,
        )
        res = await self.http.post(f"{self.BASE_URL}/graphql", json={"query": query})
        res.raise_for_status()

        return GraphQLPRMetrics(**res.json())


async def main() -> None:
    import os

    import dotenv

    dotenv.load_dotenv()
    token = os.getenv("GITHUB_TOKEN", default="")
    client = Client(token)
    metrics = await client.get_pr_metrics(
        Repo("thebricks", "mirroredsouls"), Params(5, None)
    )
    print(metrics)


if __name__ == "__main__":
    asyncio.run(main())
