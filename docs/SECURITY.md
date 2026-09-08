# Security and sandbox notes

## What is safe by default

- URLs and local files use GIO's default-application API. This honors the
  desktop's default browser/file manager and works with portals in Flatpak.
- Clipboard actions only write the exact text stored in the user's document.
- The JSON file is written atomically, so a crash does not leave a half-written
  configuration.

## Command actions are powerful

A command action is explicitly a user-authored `bash -lc` command. Links shows
a confirmation dialog before it runs. It must still be treated as arbitrary
code: do not import a configuration from an untrusted source and run it
without reviewing command actions first.

In the Flatpak manifest, command fallback uses `flatpak-spawn --host` and
therefore requests `--talk-name=org.freedesktop.Flatpak`. This is the least
surprising way to support host terminal commands, but it expands the trust
boundary. A Flathub maintainer may ask for this permission to be removed or
for command actions to be redesigned around a portal. The rest of the app does
not need broad filesystem access.

## File paths

The app stores paths as user-entered values and expands `~` at launch time.
Opening a path is delegated to the desktop. Future file-picker editing should
use `Gtk.FileDialog` so the portal can grant access without adding
`--filesystem=home`.
