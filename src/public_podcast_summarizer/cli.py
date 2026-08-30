"""Summarize a bounded number of episodes from publisher metadata."""

from __future__ import annotations

import argparse
import json
from typing import Optional, Sequence

from .feed import parse_feed
from .source import load_feed, load_feeds_from_config
from .summary import summarize_notes
from .mailer import send_digest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--feed", help="local XML or public HTTP(S) feed")
    group.add_argument("--config", action="store_true", help="use PODCAST_CONFIG_JSON")
    parser.add_argument("--max-episodes", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true", help="print email instead of sending")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    output = []
    
    if args.config:
        feeds = load_feeds_from_config()
    else:
        feeds = [{"url": args.feed, "name": args.feed, "max_episodes": args.max_episodes}]
        
    for feed_info in feeds:
        try:
            feed_data = load_feed(feed_info["url"])
            max_ep = feed_info.get("max_episodes", args.max_episodes)
            for episode in parse_feed(feed_data, max_episodes=max_ep):
                item = episode.to_public_dict()
                item["summary"] = summarize_notes(episode.notes)
                # Ensure podcast name is included
                item["podcast_name"] = feed_info.get("name", "Unknown Podcast")
                item.pop("notes", None)
                output.append(item)
        except Exception as e:
            print(f"Error processing {feed_info.get('url')}: {e}")
            continue

    print(json.dumps(output, indent=2, sort_keys=True))
    
    if args.config or args.dry_run:
        send_digest(output, dry_run=args.dry_run)
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
