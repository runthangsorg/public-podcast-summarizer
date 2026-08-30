"""Summarize a bounded number of episodes from publisher metadata."""

from __future__ import annotations

import argparse
import json
import re
from typing import Optional, Sequence

from .feed import parse_feed
from .source import load_feed, load_feeds_from_config
from .summary import summarize_notes
from .mailer import send_digest


def _title_key(value: object) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(value or "").casefold()))


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
    feed_errors = 0
    
    if args.config:
        feeds = load_feeds_from_config()
    else:
        feeds = [{"url": args.feed, "name": args.feed, "max_episodes": args.max_episodes}]
        
    for feed_info in feeds:
        try:
            feed_data = load_feed(feed_info["url"])
            max_ep = feed_info.get("max_episodes", args.max_episodes)
            episodes = parse_feed(feed_data, max_episodes=max_ep)
            if not episodes:
                feed_errors += 1
                continue
            expected_title = _title_key(feed_info.get("expected_title"))
            actual_title = _title_key(episodes[0].podcast)
            title_matches = actual_title == expected_title or actual_title.startswith(
                expected_title + " "
            )
            if expected_title and not title_matches:
                feed_errors += 1
                continue
            for episode in episodes:
                item = episode.to_public_dict()
                item["summary"] = summarize_notes(episode.notes)
                # Resolve real podcast title: prefer XML channel title, then feed name, then fallback
                xml_title = str(episode.podcast or "").strip()
                configured_name = str(feed_info.get("name") or "").strip()
                if xml_title and not xml_title.startswith("http"):
                    item["podcast_name"] = xml_title
                elif configured_name and not configured_name.startswith("http"):
                    item["podcast_name"] = configured_name
                else:
                    item["podcast_name"] = "Podcast Episode"
                    
                item["category"] = feed_info.get("category", "General Knowledge")
                item.pop("notes", None)
                output.append(item)
        except Exception:
            feed_errors += 1
            continue

    if args.config and not output:
        raise RuntimeError("no configured feed yielded a validated episode")

    email_sent = False
    if args.config or args.dry_run:
        email_sent = send_digest(output, dry_run=args.dry_run)

    if args.config or args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": args.dry_run,
                    "email_sent": email_sent,
                    "episode_count": len(output),
                    "feed_errors": feed_errors,
                },
                sort_keys=True,
            )
        )
    else:
        print(json.dumps(output, indent=2, sort_keys=True))
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
