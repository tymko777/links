"""Application entry point."""

from __future__ import annotations

import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gio, Gtk

from .storage import ConfigStore
from .ui.window import LinksWindow


class LinksApplication(Adw.Application):
    """Single-window Links application."""

    def __init__(self) -> None:
        super().__init__(
            application_id="org.tymko.Links",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.store = ConfigStore()
        self.create_action("about", self._show_about)

    def do_activate(self) -> None:
        window = self.props.active_window
        if window is None:
            window = LinksWindow(self, self.store)
        window.present()

    def _show_about(self, _action: Gio.SimpleAction, _parameter: None) -> None:
        window = self.props.active_window
        about = Adw.AboutWindow(
            transient_for=window,
            application_name="Links",
            application_icon="org.tymko.Links",
            developer_name="tymko",
            version="0.2.2",
            comments="A calm launcher for links, actions, and files.",
            website="https://github.com/tymko777/links",
            issue_url="https://github.com/tymko777/links/issues",
            license_type=Gtk.License.MIT_X11,
        )
        about.present()

    def create_action(self, name: str, callback) -> None:
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)


def main() -> int:
    return LinksApplication().run(None)


if __name__ == "__main__":
    raise SystemExit(main())
