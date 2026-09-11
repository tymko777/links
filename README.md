# Links

Links is a native Linux launcher and organizer for the URLs, files, terminal
commands, and clipboard templates that make up a real workday. It is designed
to feel at home in GNOME while remaining usable on KDE Plasma, XFCE, and other
desktop environments.

The application is written in Python 3 with GTK4 and Libadwaita, stores a
portable JSON document in the XDG configuration directory, and is prepared for
Flatpak distribution under the app ID `io.github.tymko777.links`.

> **Current status:** development release `0.5.0`. The core document model,
> storage, search, all four action types, starter UI, tests, local Flatpak
> manifest, card/action drag-and-drop sorting, and full folder/card/action
> editing and deletion are included.

## Product shape

The information architecture is intentionally shallow:

```text
Links
└── Folder
    └── Card
        ├── URL action
        ├── File or directory action
        ├── Terminal command action
        └── Clipboard template action
