import asyncio
import os

from repostats.metrics import github, metrics


async def main() -> None:
    import dotenv

    dotenv.load_dotenv()

    token = os.getenv("GITHUB_TOKEN", default="")
    client = github.Client(token)
    analyzer = metrics.PRAnalyzer(
        client, ["thebricks/MirroredSouls", "vernalhav/levada"]
    )
    data = await analyzer.get_metrics(3)
    metrics.export_metrics_to_json(data, "data/metrics.json")


if __name__ == "__main__":
    asyncio.run(main())
