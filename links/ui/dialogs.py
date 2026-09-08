"""Small, reusable Libadwaita dialog helpers."""

from __future__ import annotations

from collections.abc import Callable

import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gtk


def ask_text(
    parent: Gtk.Window,
    title: str,
    placeholder: str,
    callback: Callable[[str], None],
    initial: str = "",
) -> None:
    """Show a one-field dialog and invoke callback for a non-empty value."""

    dialog = Adw.MessageDialog.new(parent, title, None)
    entry = Gtk.Entry()
    entry.set_placeholder_text(placeholder)
    entry.set_text(initial)
    entry.set_activates_default(True)
    dialog.set_extra_child(entry)
    dialog.add_response("cancel", "Cancel")
    dialog.add_response("save", "Save")
    dialog.set_default_response("save")
    dialog.set_close_response("cancel")

    def on_response(_dialog: Adw.MessageDialog, response: str) -> None:
        if response == "save" and entry.get_text().strip():
            callback(entry.get_text().strip())
        dialog.close()

    dialog.connect("response", on_response)
    dialog.present()


def confirm(
    parent: Gtk.Window,
    title: str,
    body: str,
    callback: Callable[[], None],
    destructive: bool = True,
    continue_label: str = "Continue",
) -> None:
    """Ask for confirmation before a destructive or privileged action."""

    dialog = Adw.MessageDialog.new(parent, title, body)
    dialog.add_response("cancel", "Cancel")
    dialog.add_response("continue", continue_label)
    if destructive:
        dialog.set_response_appearance(
            "continue", Adw.ResponseAppearance.DESTRUCTIVE
        )
    dialog.set_default_response("cancel")
    dialog.set_close_response("cancel")

    def on_response(_dialog: Adw.MessageDialog, response: str) -> None:
        if response == "continue":
            callback()
        dialog.close()

    dialog.connect("response", on_response)
    dialog.present()


def ask_card(
    parent: Gtk.Window,
    callback: Callable[[str, str, list[str]], None],
    card=None,
) -> None:
    """Collect or edit a card title, description, and comma-separated tags."""

    dialog = Adw.MessageDialog.new(
        parent,
        "Edit card" if card else "New card",
        None,
    )
    fields = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    title_entry = Gtk.Entry()
    title_entry.set_placeholder_text("Card title")
    description_entry = Gtk.Entry()
    description_entry.set_placeholder_text("Optional description")
    tags_entry = Gtk.Entry()
    tags_entry.set_placeholder_text("Tags separated by commas")
    if card:
        title_entry.set_text(card.title)
        description_entry.set_text(card.description)
        tags_entry.set_text(", ".join(card.tags))
    fields.append(title_entry)
    fields.append(description_entry)
    fields.append(tags_entry)
    dialog.set_extra_child(fields)
    dialog.add_response("cancel", "Cancel")
    dialog.add_response("save", "Save")
    dialog.set_default_response("save")
    dialog.set_close_response("cancel")

    def on_response(_dialog: Adw.MessageDialog, response: str) -> None:
        if response == "save":
            title = title_entry.get_text().strip()
            if title:
                tags = [
                    tag.strip()
                    for tag in tags_entry.get_text().split(",")
                    if tag.strip()
                ]
                callback(title, description_entry.get_text().strip(), tags)
        dialog.close()

    dialog.connect("response", on_response)
    dialog.present()


def ask_action(
    parent: Gtk.Window,
    callback: Callable[[str, str, str, str], None],
    action=None,
) -> None:
    """Collect or edit the fields needed by any supported action type."""

    dialog = Adw.MessageDialog.new(
        parent,
        "Edit action" if action else "New action",
        None,
    )
    fields = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    title_entry = Gtk.Entry()
    title_entry.set_placeholder_text("Button label")
    if action:
        title_entry.set_text(action.title)
    value_entry = Gtk.Entry()
    value_entry.set_placeholder_text("URL, path, command, or text")
    if action:
        value_entry.set_text(action.value)
    description_entry = Gtk.Entry()
    description_entry.set_placeholder_text("Optional description")
    if action:
        description_entry.set_text(action.description)
    types = ["url", "file", "command", "clipboard"]
    action_type = Gtk.DropDown.new_from_strings(
        ["URL", "File or directory", "Terminal command", "Clipboard text"]
    )
    if action:
        action_type.set_selected(types.index(action.action_type))
    fields.append(title_entry)
    fields.append(action_type)
    fields.append(value_entry)
    fields.append(description_entry)
    dialog.set_extra_child(fields)
    dialog.add_response("cancel", "Cancel")
    dialog.add_response("save", "Save")
    dialog.set_default_response("save")
    dialog.set_close_response("cancel")

    def on_response(_dialog: Adw.MessageDialog, response: str) -> None:
        if response == "save":
            title = title_entry.get_text().strip()
            value = value_entry.get_text().strip()
            if title and value:
                callback(
                    title,
                    types[action_type.get_selected()],
                    value,
                    description_entry.get_text().strip(),
                )
        dialog.close()

    dialog.connect("response", on_response)
    dialog.present()
