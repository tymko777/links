"""Pure search and filtering helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Card, Folder, LinksDocument


@dataclass(frozen=True)
class SearchHit:
    """A matching object plus a score used for stable ordering."""

    folder_id: str
    card_id: str | None
    action_id: str | None
    score: int


def _contains(query: str, *values: str) -> bool:
    needle = query.casefold().strip()
    return bool(needle) and any(needle in value.casefold() for value in values)


def search_document(document: LinksDocument, query: str) -> list[SearchHit]:
    """Search folder, card, action, descriptions, and tags.

    A card hit is returned once even when several of its actions match.  An
    action hit is returned for matching action titles/values, which lets the UI
    focus a precise button in a future version.
    """

    if not query.strip():
        return []

    hits: list[SearchHit] = []
    for folder in document.folders:
        folder_match = _contains(query, folder.title)
        if folder_match:
            hits.append(SearchHit(folder.id, None, None, 100))

        for card in folder.cards:
            card_match = _contains(query, card.title, card.description, *card.tags)
            if card_match:
                hits.append(SearchHit(folder.id, card.id, None, 80))

            for action in card.actions:
                if _contains(query, action.title, action.description, action.value):
                    hits.append(SearchHit(folder.id, card.id, action.id, 60))

    return sorted(hits, key=lambda hit: (-hit.score, hit.folder_id, hit.card_id or ""))


def cards_matching(
    document: LinksDocument,
    folder: Folder,
    query: str,
) -> list[Card]:
    """Return the cards visible for a query within one selected folder.

    A folder-title match means the folder itself matched, so all of its cards
    remain visible.  This prevents a folder search from producing a misleading
    empty state.
    """

    if not query.strip():
        return list(folder.cards)

    hits = [
        hit for hit in search_document(document, query) if hit.folder_id == folder.id
    ]
    if any(hit.card_id is None for hit in hits):
        return list(folder.cards)

    card_ids = {hit.card_id for hit in hits if hit.card_id}
    return [card for card in folder.cards if card.id in card_ids]
