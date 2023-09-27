import asyncio
import os

from repostats import metrics


async def main() -> None:
    import dotenv

    dotenv.load_dotenv()

    token = os.getenv("GITHUB_TOKEN", default="")
    await metrics.to_json(
        ["thebricks/MirroredSouls", "vernalhav/levada"], token, "data/metrics.json"
    )


if __name__ == "__main__":
    asyncio.run(main())
