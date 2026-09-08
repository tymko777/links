# Contributing

## Principles

- Keep domain logic independent of GTK where possible.
- Prefer GIO and portals over hard-coded desktop applications.
- Follow PEP8 and keep public functions typed.
- Do not add a permission to the Flatpak manifest without documenting why.
- Preserve the stable JSON schema or add an explicit migration.
- Use Adwaita widgets and semantic CSS classes instead of fixed colors.

## Pull requests

Before opening a pull request:

```bash
python -m pytest -q
ruff check .
python -m compileall links tests
```

Describe the user-visible behavior, the tests that cover it, and any change to
Flatpak permissions or AppStream metadata.
