# Changelog

## 0.5.0 — 2026-09-11

- Added an All cards view with cross-folder search and folder labels.
- Added the headless `links-cli` command for listing and searching configurations.

## 0.4.0 — 2026-09-11

- Added favorite cards and a favorite-only filter for the selected folder.
- Added automatic `.bak` snapshots before every saved change.
- Added a menu action to restore the last valid backup.
- Added card statistics showing action and tag counts.

## 0.3.0 — 2026-09-07

- Added keyboard shortcuts for search, creating folders/cards, importing, and exporting.
- Added duplicate actions for cards and individual actions in edit mode.
- Updated project links to `github.com/tymko777/links`.

## 0.2.2 — 2026-09-07

- Fixed `python -m links.main` so it actually enters the GTK application loop.
- This fixes the silent no-window behavior reported on Nobara.

## 0.2.1 — 2026-09-06

- Fixed folder-title search so matching folders keep their cards visible.
- Extracted identity-based reorder operations into a tested backend module.
- Added model-level URL scheme validation for imported configurations.
- Disabled the action-add control after the ten-action card limit.
- Expanded the headless suite to 17 tests.

## 0.2.0 — 2026-09-06

- Added full Edit mode controls for folders, cards, and actions.
- Added card descriptions/tags and action descriptions in dialogs.
- Added delete confirmation dialogs for all object levels.
- Added headless `unittest` coverage for action dispatch and malformed data.
- Added a no-pip Flatpak launcher and a GitHub Checks workflow.
- Switched the development manifest to GNOME Platform 50.

## 0.1.0 — 2026-09-06

- Added the Python/GTK4/Libadwaita application skeleton.
- Added folders, cards, stable IDs, tags, validation, and starter content.
- Added JSON storage with atomic writes and optional YAML import/export.
- Added URL, file, command, and clipboard action services.
- Added search over folders, cards, tags, and actions.
- Added desktop entry, AppStream metadata, icon, tests, and Flatpak manifest.
- Documented GNOME HIG decisions, Flatpak permissions, and the Flathub path.
