# Architecture

Links uses a deliberately small MVVM-style boundary:

```text
GTK / Libadwaita widgets
        │ user intent
        ▼
LinksWindow (presentation coordinator / view-model)
        │
        ├── ConfigStore  ── JSON/YAML document
        ├── ActionRunner ── GIO / xdg-open / terminal
        └── search_document (pure query service)
```

## Modules

- `links/models.py` — dataclasses, schema validation, stable IDs, starter data.
- `links/operations.py` — pure identity-based reorder operations.
- `links/storage.py` — XDG config location, atomic writes, JSON and optional YAML.
- `links/search.py` — pure search logic, independently testable without GTK.
- `links/services/action_runner.py` — action execution and desktop integration.
- `links/ui/widgets.py` — reusable folder, card, and action widgets.
- `links/ui/dialogs.py` — Libadwaita confirmation and text-entry dialogs.
- `links/ui/window.py` — window composition and coordination of user intents.
- `links/main.py` — application lifecycle and About window.

The UI is not allowed to serialize objects or decide how URLs are launched.
That separation keeps future work (undo, sync, database storage, or a mobile
companion) from leaking into every widget.

## Data model

The document is intentionally portable:

```json
{
  "schema_version": 1,
  "folders": [
    {
      "id": "folder-example",
      "title": "Work",
      "cards": [
        {
          "id": "card-example",
          "title": "Release",
          "description": "Production shortcuts",
          "tags": ["shipping"],
          "actions": [
            {
              "id": "action-example",
              "title": "Dashboard",
              "action_type": "url",
              "value": "https://example.com",
              "description": "",
              "icon": "web-browser-symbolic"
            }
          ]
        }
      ]
    }
  ]
}
```

`schema_version` is reserved for forward migrations. IDs are kept stable so
drag-and-drop sorting, future search indexing, and external backups can refer
to an item without depending on its position in a list.

## Deliberate v0.1 boundaries

The repository is a useful, buildable foundation rather than pretending that
unfinished interactions are complete. URL/file/clipboard actions work from
the main UI, folders/cards/actions can be added, edited, and deleted, and the
data model supports all four action types. Card and action sorting use GTK4
`Gtk.DragSource` and `Gtk.DropTarget`. The next implementation slice should
add undoable mutations and keyboard shortcuts for common editing operations.
