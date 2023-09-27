import argparse
import asyncio
import os
from typing import Sequence

from repostats import metrics


class Args:
    repos: Sequence[str]
    max_prs: int | None
    outfile: str


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python3 -m repostats.metrics")

    parser.add_argument(
        "repos",
        metavar="repo",
        action="extend",
        nargs="+",
        help="owner and name of repo to add to dashboard, e.g. vernalhav/repo-stats",
    )
    parser.add_argument(
        "-n",
        "--max-prs",
        type=int,
        help="max PRs to fetch per repo. If unspecified, fetches all PRs",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        default="data/metrics.json",
        help="json file to dump repo metrics",
    )

    return parser


async def main() -> None:
    import dotenv

    dotenv.load_dotenv()

    parser = get_parser()
    args: Args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN", default="")

    print(f"Downloading metrics for repos {', '.join(args.repos)}...")
    await metrics.to_json(args.repos, token, args.outfile, args.max_prs)
    print("Finished downloading metrics!")


if __name__ == "__main__":
    asyncio.run(main())
