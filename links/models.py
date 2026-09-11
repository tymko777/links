"""Domain models and validation for the Links data file.

The UI never needs to know how configuration is serialized.  Models are
ordinary dataclasses so they are easy to inspect, test, and migrate later.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

MAX_ACTIONS_PER_CARD = 10
SUPPORTED_ACTION_TYPES = {"url", "file", "command", "clipboard"}
SUPPORTED_URL_SCHEMES = {"http", "https", "mailto"}


def new_id(prefix: str) -> str:
    """Return a stable, human-readable identifier for a new object."""

    return f"{prefix}-{uuid4().hex[:12]}"


@dataclass
class Action:
    """One executable shortcut shown as a button on a card."""

    title: str
    action_type: str
    value: str
    description: str = ""
    icon: str = "emblem-symbolic-link"
    id: str = field(default_factory=lambda: new_id("action"))

    def validate(self) -> list[str]:
        """Return validation messages without mutating the action."""

        errors: list[str] = []
        if not self.title.strip():
            errors.append("Action title cannot be empty.")
        if self.action_type not in SUPPORTED_ACTION_TYPES:
            errors.append(f"Unsupported action type: {self.action_type}.")
        if not self.value.strip():
            errors.append("Action value cannot be empty.")
        if self.action_type == "url":
            scheme = urlparse(self.value.strip()).scheme.casefold()
            if scheme not in SUPPORTED_URL_SCHEMES:
                errors.append(
                    "URL actions must use http, https, or mailto."
                )
        return errors

    def clone(self) -> Action:
        """Return an independent copy with a new stable ID."""

        return Action(
            title=self.title,
            action_type=self.action_type,
            value=self.value,
            description=self.description,
            icon=self.icon,
        )

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Action:
        """Build an action while tolerating older/missing fields."""

        return cls(
            id=str(raw.get("id") or new_id("action")),
            title=str(raw.get("title", "Untitled action")),
            action_type=str(raw.get("action_type", "url")),
            value=str(raw.get("value", "")),
            description=str(raw.get("description", "")),
            icon=str(raw.get("icon", "emblem-symbolic-link")),
        )


@dataclass
class Card:
    """A named group of up to ten actions."""

    title: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    id: str = field(default_factory=lambda: new_id("card"))
    favorite: bool = False

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.title.strip():
            errors.append("Card title cannot be empty.")
        if len(self.actions) > MAX_ACTIONS_PER_CARD:
            errors.append(
                f"A card can contain at most {MAX_ACTIONS_PER_CARD} actions."
            )
        for action in self.actions:
            errors.extend(action.validate())
        return errors

    def add_action(self, action: Action) -> None:
        if len(self.actions) >= MAX_ACTIONS_PER_CARD:
            raise ValueError(
                f"A card can contain at most {MAX_ACTIONS_PER_CARD} actions."
            )
        self.actions.append(action)

    def clone(self) -> Card:
        """Return an independent card copy with fresh nested action IDs."""

        return Card(
            title=f"{self.title} (copy)",
            description=self.description,
            tags=list(self.tags),
            actions=[action.clone() for action in self.actions],
            favorite=self.favorite,
        )

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Card:
        return cls(
            id=str(raw.get("id") or new_id("card")),
            title=str(raw.get("title", "Untitled card")),
            description=str(raw.get("description", "")),
            tags=[str(tag) for tag in raw.get("tags", [])],
            actions=[
                Action.from_dict(item)
                for item in raw.get("actions", [])
                if isinstance(item, dict)
            ],
            favorite=bool(raw.get("favorite", False)),
        )


@dataclass
class Folder:
    """A top-level category containing cards."""

    title: str
    cards: list[Card] = field(default_factory=list)
    id: str = field(default_factory=lambda: new_id("folder"))

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.title.strip():
            errors.append("Folder title cannot be empty.")
        for card in self.cards:
            errors.extend(card.validate())
        return errors

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Folder:
        return cls(
            id=str(raw.get("id") or new_id("folder")),
            title=str(raw.get("title", "Untitled folder")),
            cards=[
                Card.from_dict(item)
                for item in raw.get("cards", [])
                if isinstance(item, dict)
            ],
        )


@dataclass
class LinksDocument:
    """The complete user document persisted by :mod:`links.storage`."""

    folders: list[Folder] = field(default_factory=list)
    schema_version: int = 1

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.schema_version != 1:
            errors.append(f"Unsupported schema version: {self.schema_version}.")
        seen_ids: set[str] = set()
        for folder in self.folders:
            if not folder.id.strip():
                errors.append("Folder IDs cannot be empty.")
            elif folder.id in seen_ids:
                errors.append(f"Duplicate object ID: {folder.id}.")
            seen_ids.add(folder.id)
            errors.extend(folder.validate())
            for card in folder.cards:
                if not card.id.strip():
                    errors.append("Card IDs cannot be empty.")
                elif card.id in seen_ids:
                    errors.append(f"Duplicate object ID: {card.id}.")
                seen_ids.add(card.id)
                for action in card.actions:
                    if not action.id.strip():
                        errors.append("Action IDs cannot be empty.")
                    elif action.id in seen_ids:
                        errors.append(f"Duplicate object ID: {action.id}.")
                    seen_ids.add(action.id)
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> LinksDocument:
        folders = [
            Folder.from_dict(item)
            for item in raw.get("folders", [])
            if isinstance(item, dict)
        ]
        return cls(
            folders=folders,
            schema_version=int(raw.get("schema_version", 1)),
        )

    @classmethod
    def starter_document(cls) -> LinksDocument:
        """Return a useful first-run document instead of an empty window."""

        return cls(
            folders=[
                Folder(
                    title="Getting Started",
                    cards=[
                        Card(
                            title="Your shortcuts",
                            description=(
                                "Create a calm home for the things you open "
                                "every day."
                            ),
                            tags=["welcome", "starter"],
                            actions=[
                                Action(
                                    title="GNOME",
                                    action_type="url",
                                    value="https://www.gnome.org",
                                    description="Open the GNOME website.",
                                    icon="web-browser-symbolic",
                                ),
                                Action(
                                    title="Home folder",
                                    action_type="file",
                                    value="~",
                                    description="Open your home directory.",
                                    icon="folder-symbolic",
                                ),
                            ],
                        )
                    ],
                )
            ]
        )
