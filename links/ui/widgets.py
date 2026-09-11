"""Reusable GTK widgets for folders, cards, and action controls."""

from __future__ import annotations

from collections.abc import Callable

import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gdk, Gtk

from ..models import MAX_ACTIONS_PER_CARD, Action, Card, Folder


def icon_button(
    icon_name: str,
    tooltip: str,
    callback: Callable[[], None],
) -> Gtk.Button:
    """Build a small, accessible icon-only button."""

    button = Gtk.Button.new_from_icon_name(icon_name)
    button.set_tooltip_text(tooltip)
    button.add_css_class("flat")
    button.connect("clicked", lambda _button: callback())
    return button


class ActionButton(Gtk.Button):
    """A compact action button with optional drag-and-drop support."""

    def __init__(
        self,
        action: Action,
        on_activate: Callable[[Action], None],
        on_drop: Callable[[str, str], bool],
        editable: bool,
    ) -> None:
        super().__init__(label=action.title)
        self.action = action
        self.set_tooltip_text(action.description or action.value)
        self.set_icon_name(action.icon)
        self.add_css_class("pill")
        self.connect("clicked", lambda _button: on_activate(action))

        if editable:
            source = Gtk.DragSource.new()
            source.set_actions(Gdk.DragAction.MOVE)
            source.connect(
                "prepare",
                lambda _source, _x, _y: Gdk.ContentProvider.new_for_value(
                    action.id
                ),
            )
            self.add_controller(source)

            target = Gtk.DropTarget.new(str, Gdk.DragAction.MOVE)
            target.connect(
                "drop",
                lambda _target, value, _x, _y: on_drop(action.id, value),
            )
            self.add_controller(target)


class CardWidget(Gtk.Frame):
    """A card with actions, editing controls, and reorder drop targets."""

    def __init__(
        self,
        card: Card,
        folder_title: str | None,
        on_action: Callable[[Action], None],
        on_toggle_favorite: Callable[[Card], None],
        on_add_action: Callable[[Card], None],
        on_edit_card: Callable[[Card], None],
        on_duplicate_card: Callable[[Card], None],
        on_delete_card: Callable[[Card], None],
        on_edit_action: Callable[[Card, Action], None],
        on_duplicate_action: Callable[[Card, Action], None],
        on_delete_action: Callable[[Card, Action], None],
        on_move_card: Callable[[str, str], bool],
        on_move_action: Callable[[str, str, str], bool],
        editable: bool,
    ) -> None:
        super().__init__()
        self.card = card
        self.set_css_classes(["card", "view"])

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        body.set_margin_top(16)
        body.set_margin_bottom(16)
        body.set_margin_start(16)
        body.set_margin_end(16)
        self.set_child(body)

        heading_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        heading = Gtk.Label(label=card.title, xalign=0)
        heading.set_hexpand(True)
        heading.add_css_class("heading")
        heading_box.append(heading)
        heading_box.append(
            icon_button(
                "starred-symbolic" if card.favorite else "non-starred-symbolic",
                "Remove from favorites" if card.favorite else "Add to favorites",
                lambda: on_toggle_favorite(card),
            )
        )
        if editable:
            heading_box.append(
                icon_button(
                    "document-edit-symbolic",
                    "Edit card",
                    lambda: on_edit_card(card),
                )
            )
            heading_box.append(
                icon_button(
                    "edit-copy-symbolic",
                    "Duplicate card",
                    lambda: on_duplicate_card(card),
                )
            )
            heading_box.append(
                icon_button(
                    "user-trash-symbolic",
                    "Delete card",
                    lambda: on_delete_card(card),
                )
            )
        body.append(heading_box)

        if folder_title:
            location = Gtk.Label(label=folder_title, xalign=0)
            location.add_css_class("dim-label")
            location.add_css_class("caption")
            body.append(location)

        if card.description:
            description = Gtk.Label(label=card.description, xalign=0)
            description.set_wrap(True)
            description.add_css_class("dim-label")
            body.append(description)

        stats = Gtk.Label(
            label=f"{len(card.actions)} actions · {len(card.tags)} tags",
            xalign=0,
        )
        stats.add_css_class("dim-label")
        stats.add_css_class("caption")
        body.append(stats)

        actions_box = Gtk.FlowBox()
        actions_box.set_selection_mode(Gtk.SelectionMode.NONE)
        actions_box.set_row_spacing(6)
        actions_box.set_column_spacing(6)
        actions_box.set_homogeneous(False)
        for action in card.actions:
            action_line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            action_line.append(
                ActionButton(
                    action,
                    on_action,
                    lambda source_id, target_id: on_move_action(
                        card.id, source_id, target_id
                    ),
                    editable,
                )
            )
            if editable:
                action_line.append(
                    icon_button(
                        "document-edit-symbolic",
                        "Edit action",
                        lambda action=action: on_edit_action(card, action),
                    )
                )
                duplicate_button = icon_button(
                    "edit-copy-symbolic",
                    "Duplicate action",
                    lambda action=action: on_duplicate_action(card, action),
                )
                duplicate_button.set_sensitive(
                    len(card.actions) < MAX_ACTIONS_PER_CARD
                )
                action_line.append(duplicate_button)
                action_line.append(
                    icon_button(
                        "user-trash-symbolic",
                        "Delete action",
                        lambda action=action: on_delete_action(card, action),
                    )
                )
            actions_box.insert(action_line, -1)

        add_button = Gtk.Button.new_from_icon_name("list-add-symbolic")
        add_button.set_tooltip_text(
            "Maximum of 10 actions per card"
            if len(card.actions) >= MAX_ACTIONS_PER_CARD
            else "Add action"
        )
        add_button.set_sensitive(len(card.actions) < MAX_ACTIONS_PER_CARD)
        add_button.add_css_class("flat")
        add_button.connect("clicked", lambda _button: on_add_action(card))
        actions_box.insert(add_button, -1)
        body.append(actions_box)

        if editable:
            card_target = Gtk.DropTarget.new(str, Gdk.DragAction.MOVE)
            card_target.connect(
                "drop",
                lambda _target, value, _x, _y: on_move_card(value, card.id),
            )
            self.add_controller(card_target)
            card_source = Gtk.DragSource.new()
            card_source.set_actions(Gdk.DragAction.MOVE)
            card_source.connect(
                "prepare",
                lambda _source, _x, _y: Gdk.ContentProvider.new_for_value(card.id),
            )
            self.add_controller(card_source)

        tags = ", ".join(f"#{tag}" for tag in card.tags)
        if tags:
            tag_label = Gtk.Label(label=tags, xalign=0)
            tag_label.add_css_class("dim-label")
            body.append(tag_label)


class FolderRow(Adw.ActionRow):
    """Sidebar row for a folder, with optional edit controls."""

    def __init__(
        self,
        folder: Folder,
        on_select: Callable[[Folder], None],
        on_edit: Callable[[Folder], None],
        on_delete: Callable[[Folder], None],
        editable: bool,
    ) -> None:
        super().__init__(title=folder.title, subtitle=f"{len(folder.cards)} cards")
        self.folder = folder
        self.add_prefix(Gtk.Image.new_from_icon_name("folder-symbolic"))
        self.connect("activated", lambda _row: on_select(folder))
        if editable:
            self.add_suffix(
                icon_button(
                    "document-edit-symbolic",
                    "Edit folder",
                    lambda: on_edit(folder),
                )
            )
            self.add_suffix(
                icon_button(
                    "user-trash-symbolic",
                    "Delete folder",
                    lambda: on_delete(folder),
                )
            )