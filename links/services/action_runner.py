"""Execute user-defined actions through desktop-friendly Linux APIs."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ..models import Action


class ActionError(RuntimeError):
    """An action could not be launched."""


class ActionRunner:
    """Launch URLs/files, copy text, and open commands in a terminal.

    URLs and files intentionally use GIO's default-app API rather than calling
    a hard-coded browser or file manager.  On a Flatpak desktop this follows
    the desktop integration and portal path and behaves on Wayland and X11.
    """

    _terminal_candidates = (
        ("kgx", ("--", "bash", "-lc")),
        ("gnome-terminal", ("--", "bash", "-lc")),
        ("konsole", ("-e", "bash", "-lc")),
        ("xfce4-terminal", ("--command", "bash -lc")),
        ("kitty", ("bash", "-lc")),
        ("alacritty", ("-e", "bash", "-lc")),
        ("foot", ("bash", "-lc")),
        ("xterm", ("-e", "bash", "-lc")),
    )

    def run(self, action: Action, clipboard: Any | None = None) -> None:
        errors = action.validate()
        if errors:
            raise ActionError(" ".join(errors))

        if action.action_type == "url":
            self._open_uri(action.value)
        elif action.action_type == "file":
            path = Path(os.path.expanduser(action.value)).resolve()
            self._open_uri(path.as_uri())
        elif action.action_type == "clipboard":
            if clipboard is None:
                raise ActionError("Clipboard is not available.")
            clipboard.set(action.value)
        elif action.action_type == "command":
            self._open_terminal(action.value)
        else:
            raise ActionError(f"Unknown action type: {action.action_type}")

    @staticmethod
    def _open_uri(uri: str) -> None:
        parsed = urlparse(uri)
        if parsed.scheme not in {"http", "https", "mailto", "file"}:
            raise ActionError("Only http(s), mailto, and file URIs are supported.")

        try:
            import gi

            gi.require_version("Gio", "2.0")
            from gi.repository import Gio

            launched = Gio.AppInfo.launch_default_for_uri(uri, None)
            if launched is False:
                raise OSError(f"No default handler accepted {uri}")
        except (ImportError, ValueError, GLibError, OSError) as error:
            # The fallback keeps development installs useful outside Flatpak.
            xdg_open = shutil.which("xdg-open")
            if not xdg_open:
                raise ActionError(f"Could not open {uri}: {error}") from error
            try:
                subprocess.Popen(
                    [xdg_open, uri],
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except OSError as fallback_error:
                raise ActionError(
                    f"Could not open {uri}: {fallback_error}"
                ) from fallback_error

    @classmethod
    def _open_terminal(cls, command: str) -> None:
        # `bash -lc` is intentional: command actions are explicitly defined by
        # the user.  shlex prevents the command from altering the argv shape.
        shell_command = command.strip()
        for executable, prefix in cls._terminal_candidates:
            binary = shutil.which(executable)
            if binary:
                try:
                    if executable == "xfce4-terminal":
                        argv = [
                            binary,
                            "--command",
                            f"bash -lc {shlex.quote(shell_command)}",
                        ]
                    else:
                        argv = [binary, *prefix, shell_command]
                    subprocess.Popen(
                        argv,
                        start_new_session=True,
                    )
                    return
                except OSError as error:
                    raise ActionError(
                        f"Could not start {executable}: {error}"
                    ) from error

        # Flatpak exposes this helper when the manifest grants the narrowly
        # scoped Flatpak talk permission.  It is tried only after native paths.
        flatpak_spawn = shutil.which("flatpak-spawn")
        if flatpak_spawn:
            quoted_command = shlex.quote(shell_command)
            host_script = (
                "if command -v xdg-terminal-exec >/dev/null 2>&1; then "
                f"exec xdg-terminal-exec bash -lc {quoted_command}; fi; "
                "if command -v gnome-terminal >/dev/null 2>&1; then "
                f"exec gnome-terminal -- bash -lc {quoted_command}; fi; "
                "if command -v konsole >/dev/null 2>&1; then "
                f"exec konsole -e bash -lc {quoted_command}; fi; "
                "if command -v xfce4-terminal >/dev/null 2>&1; then "
                f"exec xfce4-terminal --command "
                f"{shlex.quote(f'bash -lc {quoted_command}')}; fi; "
                "exit 127"
            )
            try:
                subprocess.Popen(
                    [flatpak_spawn, "--host", "sh", "-lc", host_script],
                    start_new_session=True,
                )
                return
            except OSError as error:
                raise ActionError(
                    f"Could not start a host terminal: {error}"
                ) from error

        raise ActionError(
            "No supported terminal emulator was found. "
            "Install GNOME Console, Konsole, Xfce Terminal, or another "
            "supported terminal."
        )


try:
    from gi.repository import GLib as _GLib

    GLibError = _GLib.Error
except (ImportError, ValueError):
    class GLibError(Exception):
        """Fallback exception type when PyGObject is not installed."""
