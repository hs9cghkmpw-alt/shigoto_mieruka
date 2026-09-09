"""Validate and summarize a real-data experiment CSV."""

import argparse
import json

from experiment.aggregator import aggregate_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and summarize a real-data experiment CSV")
    parser.add_argument("path", help="path to the experiment CSV")
    args = parser.parse_args()
    try:
        summary = aggregate_csv(args.path)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
