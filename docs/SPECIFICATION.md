# Links product specification

## 1. Product intent

Links is a personal, local-first launcher for the small set of things a user
opens, runs, or pastes repeatedly. It should make the useful action visible
without turning the desktop into a dashboard full of noise.

The product is intentionally not a browser bookmark manager, a task manager,
or a cloud sync service. Its job is to provide a fast, user-owned layer above
the applications already installed on Linux.

## 2. Target users

- People who keep recurring URLs, project directories, terminal commands, and
  response templates in scattered notes.
- GNOME users who want a native Adwaita utility rather than an Electron
  launcher.
- KDE, XFCE, and other Linux desktop users who still want their default
  browser/file manager and desktop theme to decide how actions open.
- Power users who want a transparent JSON backup instead of a proprietary
  database.

## 3. Functional requirements

### F-01: Hierarchy

The user can create an unlimited number of folders. Each folder can contain an
unlimited number of cards. Each card has a title, optional description, tags,
and up to ten ordered actions.

### F-02: Action types

Each action has a title, optional description/icon, and one of:

1. URL — open `http` or `https` in the desktop default handler.
2. File — open a local file or directory in the default file manager.
3. Command — run a user-authored Bash command in a terminal after confirmation.
4. Clipboard — copy a prepared text template to the GTK clipboard.

### F-03: Search

The search field filters the current view by folder title, card title,
description, tags, action title, action description, and action value. Search
is case-insensitive and does not modify the document.

### F-04: Editing

The first release can create folders, cards, and actions through focused
dialogs. Edit mode provides drag-and-drop sorting:

- drag a card onto another card to reorder cards;
- drag an action button onto another action button to reorder actions.

Editing existing titles and deleting objects are planned follow-up operations.

### F-05: Persistence

The canonical document is stored at:

```text
$XDG_CONFIG_HOME/links/links.json
```

When `XDG_CONFIG_HOME` is absent, this resolves to
`~/.config/links/links.json`. Writes are atomic. Import/export supports JSON
by default and YAML when the optional PyYAML extra is installed.

### F-06: Distribution

The app is packaged as a Flatpak with:

- app ID `org.tymko.Links`;
- GNOME Platform 50 runtime;
- Wayland socket and fallback X11 socket;
- desktop entry, AppStream metadata, and hicolor SVG icon;
- no network or broad home-directory permission;
- a documented, reviewable permission for host command fallback.

## 4. UX specification

### Primary window

- `Adw.ApplicationWindow` with one primary surface.
- `Adw.HeaderBar` with title, search entry, Edit toggle, and menu.
- Horizontal split: folder navigation on the left, cards on the right.
- The sidebar remains simple and shallow; no deeply nested navigation.
- Empty states use `Adw.StatusPage`.
- Card actions use compact pill buttons with icon and tooltip.

### Interaction rules

- A URL/file/clipboard action runs immediately.
- A command action always shows a confirmation dialog with the exact command.
- Save failures remain visible as an in-window toast.
- Search does not destroy selection or reorder the underlying document.
- Drag-and-drop is a move operation and immediately persists the new order.
- The default style comes from Adwaita; no hard-coded light/dark color system.

### Keyboard and accessibility

- GTK search entry is reachable using the standard widget navigation order.
- Dialogs set a default response and a cancel/close response.
- Every icon-only button has a tooltip.
- Labels and status pages explain empty/error states.
- Future iterations should add explicit shortcuts for search, new card, and
  moving through folders.

## 5. Platform behavior

Links does not inspect or choose a browser/file manager by desktop name. It
uses GIO's default-application API, which is the correct abstraction for both
Wayland and X11 and can route through desktop portals in Flatpak. Native GTK
rendering is left to the selected backend, so GNOME, KDE, XFCE, and other
desktops can provide their normal scaling and theme integration.

Terminal launch is necessarily less universal because Linux has no single
standard terminal-execution portal. The service tries common terminal
executables, then uses `flatpak-spawn --host` in Flatpak. This behavior and
its permission are documented separately so a Flathub review can make an
informed decision.

## 6. Non-functional requirements

- Python 3.10+ with type annotations on public service methods.
- GTK4 and Libadwaita only for UI; no webview or Electron runtime.
- PEP8-compatible formatting and small testable modules.
- Pure model/search/storage tests must run without a display server.
- No credentials or remote account are required.
- Configuration is human-readable and backup-friendly.
- All user-visible copy is English in the initial release.

## 7. Acceptance checklist for 0.2.2

- [x] `python -m compileall links tests` succeeds.
- [x] Model validation rejects more than ten actions.
- [x] Search finds tags and action values.
- [x] JSON save/load round-trips a document.
- [x] URL, file, clipboard, and command services exist.
- [x] Desktop metadata and SVG icon are installed by the manifest.
- [x] Local Flatpak manifest separates app metadata, permissions, and module.
- [x] README explains Nobara setup, local run, tests, Flatpak, and Flathub.
- [x] Flathub source replacement and immutable commit workflow are documented.
- [x] Existing folders, cards, and actions can be edited or deleted in Edit mode.
- [ ] CI on Fedora/Nobara with real GTK display smoke test.
- [ ] Flathub review and publication under `tymko`.
