"""Summarize a bounded number of episodes from publisher metadata."""

from __future__ import annotations

import argparse
import json
from typing import Optional, Sequence

from .feed import parse_feed
from .source import load_feed
from .summary import summarize_notes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feed", required=True, help="local XML or public HTTP(S) feed")
    parser.add_argument("--max-episodes", type=int, default=1)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    output = []
    for episode in parse_feed(load_feed(args.feed), max_episodes=args.max_episodes):
        item = episode.to_public_dict()
        item["summary"] = summarize_notes(episode.notes)
        item.pop("notes")
        output.append(item)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
