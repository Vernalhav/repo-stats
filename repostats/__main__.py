import argparse
import asyncio
import os
from typing import Sequence

from repostats import metrics
from repostats.dashboard.dashboard import Dashboard
from repostats.dashboard.provider import Provider


class Args:
    repos: Sequence[str]
    max_prs: int | None
    outfile: str
    port: int


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python3 -m repostats")

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
    parser.add_argument(
        "-p", "--port", type=int, default=8080, help="port to run dasboard server"
    )

    return parser


async def main() -> None:
    import dotenv

    dotenv.load_dotenv()

    token = os.getenv("GITHUB_TOKEN", default="")
    parser = get_parser()
    args: Args = parser.parse_args()

    print(f"Downloading metrics for repos {', '.join(args.repos)}...")
    await metrics.to_json(args.repos, token, args.outfile, args.max_prs)
    print("Finished downloading metrics!")

    provider = Provider.from_json(args.outfile)
    if len(provider.metrics) == 0:
        print(f"No PRs found for repos {', '.join(args.repos)}")
        return

    dashboard = Dashboard(provider)
    dashboard.app.run(port=args.port, debug=True)


if __name__ == "__main__":
    asyncio.run(main())
