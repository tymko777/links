"""Headless command-line tools for inspecting a Links document."""

from __future__ import annotations

import argparse
from pathlib import Path

from .search import search_document
from .storage import ConfigStore, StorageError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect a Links configuration without opening GTK."
    )
    parser.add_argument(
        "--config-home",
        type=Path,
        help="Override XDG_CONFIG_HOME for this command.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List folders, cards, and actions.",
    )
    parser.add_argument(
        "--search",
        metavar="TEXT",
        help="Search folder, card, tag, and action text.",
    )
    return parser


def _print_document(document) -> None:
    for folder in document.folders:
        print(f"[{folder.title}]")
        for card in folder.cards:
            favorite = " ★" if card.favorite else ""
            print(f"  {card.title}{favorite}")
            for action in card.actions:
                print(f"    - {action.title} ({action.action_type}): {action.value}")


def _print_search(document, query: str) -> None:
    hits = search_document(document, query)
    for hit in hits:
        folder = next(
            folder for folder in document.folders if folder.id == hit.folder_id
        )
        if hit.card_id is None:
            print(f"{folder.title}/")
            continue
        card = next(card for card in folder.cards if card.id == hit.card_id)
        if hit.action_id is None:
            print(f"{folder.title}/{card.title}")
            continue
        action = next(action for action in card.actions if action.id == hit.action_id)
        print(f"{folder.title}/{card.title}/{action.title}: {action.value}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.list and not args.search:
        parser.print_help()
        return 0

    store = ConfigStore(args.config_home)
    try:
        document = store.load()
    except StorageError as error:
        parser.error(str(error))

    if args.list:
        _print_document(document)
    if args.search:
        _print_search(document, args.search)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())