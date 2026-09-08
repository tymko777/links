"""Main Links window and its view-model-like coordination logic."""

from __future__ import annotations

from pathlib import Path

import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gio, GLib, Gtk

from ..models import Action, Card, Folder, LinksDocument
from ..operations import move_by_id
from ..search import cards_matching
from ..services.action_runner import ActionError, ActionRunner
from ..storage import ConfigStore, StorageError
from .dialogs import ask_action, ask_card, ask_text, confirm
from .widgets import CardWidget, FolderRow


class LinksWindow(Adw.ApplicationWindow):
    """A GNOME HIG-friendly two-pane organizer."""

    def __init__(self, application: Adw.Application, store: ConfigStore) -> None:
        super().__init__(application=application)
        self.set_default_size(1100, 700)
        self.set_title("Links")
        self.store = store
        self.action_runner = ActionRunner()
        self.document = self._load_document()
        self.selected_folder = (
            self.document.folders[0] if self.document.folders else None
        )
        self.search_query = ""
        self.edit_mode = False
        self._install_actions()

        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)
        toolbar = Adw.ToolbarView()
        self.toast_overlay.set_child(toolbar)
        toolbar.add_top_bar(self._build_header())

        split = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        split.set_position(270)
        toolbar.set_content(split)
        split.set_start_child(self._build_sidebar())
        split.set_end_child(self._build_content())

        self._refresh_sidebar()
        self._refresh_content()

    def _build_header(self) -> Adw.HeaderBar:
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Links"))

        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Search cards, actions, and tags")
        self.search.set_width_chars(28)
        self.search.connect("search-changed", self._on_search_changed)
        header.pack_start(self.search)

        menu = Gio.Menu()
        menu.append("Import…", "win.import")
        menu.append("Export…", "win.export")
        menu.append("About Links", "app.about")
        menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu)
        menu_button.set_tooltip_text("Application menu")
        header.pack_end(menu_button)

        edit = Gtk.ToggleButton(label="Edit")
        edit.set_tooltip_text("Show editing controls")
        edit.connect("toggled", self._on_edit_toggled)
        header.pack_end(edit)
        return header

    def _build_sidebar(self) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        label = Gtk.Label(label="Folders", xalign=0)
        label.add_css_class("heading")
        box.append(label)

        self.folder_list = Gtk.ListBox()
        self.folder_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.folder_list.add_css_class("boxed-list")
        box.append(self.folder_list)

        add_folder = Gtk.Button(label="New folder")
        add_folder.set_icon_name("list-add-symbolic")
        add_folder.connect("clicked", self._on_add_folder)
        box.append(add_folder)
        return box

    def _build_content(self) -> Gtk.Widget:
        self.content_scroller = Gtk.ScrolledWindow()
        self.content_scroller.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC
        )
        return self.content_scroller

    def _install_actions(self) -> None:
        for name, callback in (
            ("import", self._import_document),
            ("export", self._export_document),
        ):
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.add_action(action)

    def _load_document(self) -> LinksDocument:
        try:
            return self.store.load()
        except StorageError as error:
            self._notify(str(error))
            return LinksDocument.starter_document()

    def _refresh_sidebar(self) -> None:
        while child := self.folder_list.get_first_child():
            self.folder_list.remove(child)

        for folder in self.document.folders:
            self.folder_list.append(
                FolderRow(
                    folder,
                    self._select_folder,
                    self._on_edit_folder,
                    self._on_delete_folder,
                    self.edit_mode,
                )
            )

    def _refresh_content(self) -> None:
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        body.set_margin_top(24)
        body.set_margin_bottom(24)
        body.set_margin_start(24)
        body.set_margin_end(24)

        if not self.selected_folder:
            empty = Adw.StatusPage(
                title="No folders yet",
                description="Create a folder to start organizing your shortcuts.",
                icon_name="folder-symbolic",
            )
            body.append(empty)
            self.content_scroller.set_child(body)
            return

        title = Gtk.Label(label=self.selected_folder.title, xalign=0)
        title.add_css_class("title-1")
        body.append(title)

        query = self.search_query.strip()
        visible_cards = cards_matching(self.document, self.selected_folder, query)

        if not visible_cards:
            empty = Adw.StatusPage(
                title="Nothing here yet" if not query else "No matches",
                description=(
                    "Add a card from the button below."
                    if not query
                    else "Try a different title, description, or tag."
                ),
                icon_name="edit-find-symbolic",
            )
            body.append(empty)
        else:
            grid = Gtk.FlowBox()
            grid.set_selection_mode(Gtk.SelectionMode.NONE)
            grid.set_homogeneous(True)
            grid.set_row_spacing(12)
            grid.set_column_spacing(12)
            for card in visible_cards:
                grid.insert(
                    CardWidget(
                        card,
                        self._run_action,
                        self._on_add_action,
                        self._on_edit_card,
                        self._on_delete_card,
                        self._on_edit_action,
                        self._on_delete_action,
                        self._move_card,
                        self._move_action,
                        self.edit_mode,
                    ),
                    -1,
                )
            body.append(grid)

        add_card = Gtk.Button(label="New card")
        add_card.set_icon_name("list-add-symbolic")
        add_card.set_halign(Gtk.Align.START)
        add_card.connect("clicked", self._on_add_card)
        body.append(add_card)
        self.content_scroller.set_child(body)

    def _select_folder(self, folder: Folder) -> None:
        self.selected_folder = folder
        self._refresh_content()

    def _on_search_changed(self, entry: Gtk.SearchEntry) -> None:
        self.search_query = entry.get_text()
        self._refresh_content()

    def _on_edit_toggled(self, button: Gtk.ToggleButton) -> None:
        self.edit_mode = button.get_active()
        self._refresh_sidebar()
        self._refresh_content()
        self._notify(
            "Edit mode enabled. Drag cards or action buttons to reorder them."
            if self.edit_mode
            else "Edit mode disabled."
        )

    def _on_add_folder(self, _button: Gtk.Button) -> None:
        ask_text(self, "New folder", "Folder name", self._create_folder)

    def _create_folder(self, title: str) -> None:
        folder = Folder(title=title)
        self.document.folders.append(folder)
        self.selected_folder = folder
        self._save_and_refresh()

    def _on_add_card(self, _button: Gtk.Button) -> None:
        if not self.selected_folder:
            return
        ask_card(self, self._create_card)

    def _create_card(self, title: str, description: str, tags: list[str]) -> None:
        if self.selected_folder:
            self.selected_folder.cards.append(
                Card(title=title, description=description, tags=tags)
            )
            self._save_and_refresh()

    def _on_add_action(self, card: Card) -> None:
        ask_action(
            self,
            lambda title, action_type, value, description: self._create_action(
                card, title, action_type, value, description
            ),
        )

    def _create_action(
        self,
        card: Card,
        title: str,
        action_type: str,
        value: str,
        description: str = "",
        action: Action | None = None,
    ) -> None:
        try:
            if action:
                updated = Action(
                    id=action.id,
                    title=title,
                    action_type=action_type,
                    value=value,
                    description=description,
                    icon=self._icon_for_action_type(action_type),
                )
            else:
                updated = Action(
                    title=title,
                    action_type=action_type,
                    value=value,
                    description=description,
                    icon=self._icon_for_action_type(action_type),
                )
            if action:
                index = card.actions.index(action)
                card.actions[index] = updated
            else:
                card.add_action(updated)
        except (ValueError, IndexError) as error:
            self._notify(str(error))
            return
        self._save_and_refresh()

    def _on_edit_folder(self, folder: Folder) -> None:
        ask_text(
            self,
            "Edit folder",
            "Folder name",
            lambda title: self._rename_folder(folder, title),
            initial=folder.title,
        )

    def _rename_folder(self, folder: Folder, title: str) -> None:
        folder.title = title
        self._save_and_refresh()

    def _on_delete_folder(self, folder: Folder) -> None:
        confirm(
            self,
            f"Delete “{folder.title}”? ",
            "This also deletes every card and action inside the folder.",
            lambda: self._delete_folder(folder),
            continue_label="Delete folder",
        )

    def _delete_folder(self, folder: Folder) -> None:
        self.document.folders.remove(folder)
        self.selected_folder = (
            self.document.folders[0] if self.document.folders else None
        )
        self._save_and_refresh()

    def _on_edit_card(self, card: Card) -> None:
        ask_card(
            self,
            lambda title, description, tags: self._update_card(
                card, title, description, tags
            ),
            card=card,
        )

    def _update_card(
        self, card: Card, title: str, description: str, tags: list[str]
    ) -> None:
        card.title = title
        card.description = description
        card.tags = tags
        self._save_and_refresh()

    def _on_delete_card(self, card: Card) -> None:
        confirm(
            self,
            f"Delete “{card.title}”? ",
            "All actions in this card will be removed.",
            lambda: self._delete_card(card),
            continue_label="Delete card",
        )

    def _delete_card(self, card: Card) -> None:
        if self.selected_folder:
            self.selected_folder.cards.remove(card)
            self._save_and_refresh()

    def _on_edit_action(self, card: Card, action: Action) -> None:
        ask_action(
            self,
            lambda title, action_type, value, description: self._create_action(
                card,
                title,
                action_type,
                value,
                description,
                action,
            ),
            action=action,
        )

    def _on_delete_action(self, card: Card, action: Action) -> None:
        confirm(
            self,
            f"Delete “{action.title}”? ",
            "This action will be removed from the card.",
            lambda: self._delete_action(card, action),
            continue_label="Delete action",
        )

    def _delete_action(self, card: Card, action: Action) -> None:
        card.actions.remove(action)
        self._save_and_refresh()

    @staticmethod
    def _icon_for_action_type(action_type: str) -> str:
        return {
            "url": "web-browser-symbolic",
            "file": "folder-symbolic",
            "command": "utilities-terminal-symbolic",
            "clipboard": "edit-copy-symbolic",
        }.get(action_type, "emblem-symbolic-link")

    def _move_card(self, source_id: str, target_id: str) -> bool:
        if not self.selected_folder or source_id == target_id:
            return False
        if not move_by_id(
            self.selected_folder.cards,
            source_id,
            target_id,
            lambda card: card.id,
        ):
            return False
        self._save_and_refresh()
        return True

    def _move_action(self, card_id: str, source_id: str, target_id: str) -> bool:
        card = next(
            (
                candidate
                for folder in self.document.folders
                for candidate in folder.cards
                if candidate.id == card_id
            ),
            None,
        )
        if card is None or source_id == target_id:
            return False
        if not move_by_id(
            card.actions,
            source_id,
            target_id,
            lambda action: action.id,
        ):
            return False
        self._save_and_refresh()
        return True

    def _import_document(self, _action: Gio.SimpleAction, _parameter: None) -> None:
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Import Links configuration")
        dialog.open(self, None, self._finish_import)

    def _finish_import(self, dialog: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
        try:
            file = dialog.open_finish(result)
        except GLib.Error:
            return
        if file is None or file.get_path() is None:
            self._notify("Only local configuration files can be imported.")
            return
        try:
            self.document = self.store.import_document(Path(file.get_path()))
        except StorageError as error:
            self._notify(str(error))
            return
        self.selected_folder = (
            self.document.folders[0] if self.document.folders else None
        )
        self._save_and_refresh()
        self._notify("Configuration imported")

    def _export_document(self, _action: Gio.SimpleAction, _parameter: None) -> None:
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Export Links configuration")
        dialog.set_initial_name("links.json")
        dialog.save(self, None, self._finish_export)

    def _finish_export(self, dialog: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
        try:
            file = dialog.save_finish(result)
        except GLib.Error:
            return
        if file is None or file.get_path() is None:
            self._notify("Only local configuration files can be exported.")
            return
        try:
            self.store.export_document(self.document, Path(file.get_path()))
        except StorageError as error:
            self._notify(str(error))
            return
        self._notify("Configuration exported")

    def _run_action(self, action: Action) -> None:
        if action.action_type == "command":
            confirm(
                self,
                f"Run “{action.title}”? ",
                action.value,
                lambda: self._execute_action(action),
                destructive=True,
                continue_label="Run command",
            )
        else:
            self._execute_action(action)

    def _execute_action(self, action: Action) -> None:
        try:
            self.action_runner.run(action, self.get_clipboard())
        except ActionError as error:
            self._notify(str(error))
        else:
            if action.action_type == "clipboard":
                self._notify("Copied to clipboard")

    def _save_and_refresh(self) -> None:
        try:
            self.store.save(self.document)
        except StorageError as error:
            self._notify(str(error))
            return
        self._refresh_sidebar()
        self._refresh_content()

    def _notify(self, message: str) -> None:
        if hasattr(self, "toast_overlay"):
            self.toast_overlay.add_toast(Adw.Toast(title=message))
