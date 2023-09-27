import argparse

from repostats.dashboard.dashboard import Dashboard
from repostats.dashboard.provider import Provider


class Args:
    file: str
    port: int


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "file",
        default="data/metrics.json",
        help="json file to read repo metrics",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8080, help="port to run dasboard server"
    )

    return parser


def main() -> None:
    parser = get_parser()
    args: Args = parser.parse_args()

    dashboard = Dashboard(Provider.from_json(args.file))
    dashboard.app.run(debug=True, port=args.port)


if __name__ == "__main__":
    main()
