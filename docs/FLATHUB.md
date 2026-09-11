# Flathub publication plan

This repository contains a local `flatpak/org.tymko.Links.yml` manifest so a
developer can build from a checkout. Flathub manifests must instead fetch a
public, immutable source revision; they must not depend on a local `type: dir`
source. Before opening a Flathub pull request:

1. Create the public repository `https://github.com/tymko777/links` under the
   developer identity `tymko`.
2. Tag a release such as `v0.5.0` and push it.
3. Copy the manifest into a Flathub submission repository.
4. Replace the local source:

   ```yaml
   sources:
     - type: git
        url: https://github.com/tymko777/links.git
        tag: v0.5.0
        commit: REPLACE_WITH_EXACT_COMMIT_SHA
   ```

5. Run the Flathub checks locally:

   ```bash
   flatpak run --command=sh org.flatpak.Builder
   flatpak run --command=sh org.flathub.flatpak-external-data-checker
   ```

   If those helper applications are not installed, use the equivalent
   commands documented by the current Flathub tooling.
6. Build and install the exact submitted revision:

   ```bash
   flatpak-builder --force-clean --user --install -- og-build \
     org.tymko.Links.yml
   flatpak run org.tymko.Links
   ```

7. Run `flatpak-builder-lint builddir` and address every warning.
8. Submit through the Flathub new-app process. Keep the app ID,
   desktop filename, metainfo ID, and icon basename exactly aligned:
   `org.tymko.Links`.

## Metadata checklist

- The app ID is reverse-DNS style and stable.
- Desktop entry and AppStream metainfo are installed into the standard paths.
- The metainfo has a developer name, license, summary, description, launchable,
  homepage, bug tracker, and release entry.
- The SVG icon is installed under the matching hicolor application icon path.
- The manifest declares both Wayland and fallback X11 sockets.
- No credentials, telemetry, or network access are required.
- The command action permission is explicitly documented and should be
  discussed with Flathub reviewers.

Review the live Flathub requirements and metadata guidelines immediately before
submission; those policies can change independently of this codebase.

## 8. Release contract for Links

The following identifiers must remain identical everywhere:

| Item | Value |
| --- | --- |
| Flatpak app ID | `org.tymko.Links` |
| Desktop file | `org.tymko.Links.desktop` |
| AppStream component ID | `org.tymko.Links` |
| Icon basename | `org.tymko.Links` |
| Runtime | `org.gnome.Platform` |
| Runtime version | `50` |
| Public source repository | `https://github.com/tymko777/links` |

Do not rename the app ID after publication. A changed app ID is a new
application on Flathub and does not update the existing installation.

## 9. Prepare the public GitHub repository

Create the repository at:

```text
https://github.com/tymko777/links
```

The repository should be public, contain the MIT license, and contain the
complete source needed to build the application. Do not commit:

- `.venv/`;
- `__pycache__/`;
- personal configuration files from `~/.config/links`;
- passwords, access tokens, signing keys, or private certificates;
- a locally generated `builddir/` or Flatpak repository;
- generated binary packages.

From the project directory:

```bash
cd ~/links
git init
git branch -M main
git add .
git commit -m "Prepare Links 0.5.0"
git remote add origin https://github.com/tymko777/links.git
git push -u origin main
```

If the repository already exists, use `git status`, inspect the diff, and
create a normal commit instead of re-running `git init`.

Run the project checks before creating a release tag:

```bash
bash scripts/check.sh
python3 -m compileall -q links tests
python3 -m unittest discover -s tests -v
```

Create an immutable release tag only after the exact source has been pushed:

```bash
git add .
git commit -m "Release Links 0.5.0"
git push origin main
git tag -a v0.5.0 -m "Links 0.5.0"
git push origin v0.5.0
git rev-parse v0.5.0^{commit}
```

Save the 40-character commit printed by the last command. Flathub requires
the manifest to pin a source tag to its exact commit, so a moving branch such
as `main` is not an acceptable release source.

## 10. Create the Flathub manifest

The local manifest in `flatpak/org.tymko.Links.yml` uses `type: dir` so it can
build directly from a checkout. That form is for local development only. The
manifest submitted to Flathub must fetch the public Git repository and pin it
to the release commit.

For the Flathub submission repository, place a file named
`org.tymko.Links.yml` at the repository root. Its source section should look
like this:

```yaml
sources:
  - type: git
    url: https://github.com/tymko777/links.git
    tag: v0.5.0
    commit: 0123456789abcdef0123456789abcdef01234567
```

Replace the example commit with the exact output of
`git rev-parse v0.5.0^{commit}`. Keep the existing install commands, but
remove the local `path: ..` source. A Flathub build must be reproducible from
the manifest alone and must not read files outside its source checkout.

The submitted manifest should not run `pip install`, download packages from
PyPI, or use a network connection during the build. Links uses the Python
standard library plus the GTK/GObject bindings supplied by the GNOME runtime,
so the current direct-source build is intentionally simple.

## 11. Install the build tools on Nobara

Install the host tools:

```bash
sudo dnf install \
  flatpak \
  flatpak-builder \
  git \
  appstream \
  appstream-util \
  libxml2
```

Enable Flathub and install the GNOME 50 SDK/runtime:

```bash
flatpak remote-add --if-not-exists flathub \
  https://dl.flathub.org/repo/flathub.flatpakrepo

flatpak install flathub \
  org.gnome.Sdk//50 \
  org.gnome.Platform//50
```

Check that the required refs are visible:

```bash
flatpak info org.gnome.Sdk//50
flatpak info org.gnome.Platform//50
flatpak --version
flatpak-builder --version
```

## 12. Build and install locally

Build the local development manifest:

```bash
cd ~/links
rm -rf builddir
flatpak-builder \
  --user \
  --install \
  --force-clean \
  builddir \
  flatpak/org.tymko.Links.yml
```

Launch the installed application:

```bash
flatpak run org.tymko.Links
```

Confirm the application opens, creates starter data, and can:

1. create and edit a folder;
2. create, edit, duplicate, reorder, and delete a card;
3. create and run URL, file, clipboard, and command actions;
4. import and export JSON;
5. switch between Wayland and X11 fallback when available;
6. show the About window with the new GitHub URL.

To inspect the application metadata installed by the build:

```bash
flatpak info --show-metadata org.tymko.Links
flatpak info --show-permissions org.tymko.Links
```

To remove only the locally installed application:

```bash
flatpak uninstall --user org.tymko.Links
```

## 13. Validate the exact Flathub-style source

Build from the submission manifest, not from the local `type: dir` manifest.
This catches the most common publication mistake: a manifest that works on
the developer's machine but cannot be built by Flathub.

```bash
rm -rf flathub-build
flatpak-builder \
  --user \
  --install \
  --force-clean \
  flathub-build \
  org.tymko.Links.yml
flatpak run org.tymko.Links
```

Validate AppStream metadata:

```bash
appstreamcli validate \
  --pedantic \
  resources/org.tymko.Links.metainfo.xml

desktop-file-validate resources/org.tymko.Links.desktop
```

If `desktop-file-validate` is not installed on Nobara, install the package
that provides it, usually `desktop-file-utils`.

Run the Flatpak manifest linter against the build directory:

```bash
flatpak-builder-lint builddir
```

Treat every error as release-blocking. Review warnings too, especially
warnings about permissions, missing AppStream data, invalid desktop files,
unusual installation paths, or unpinned sources.

Inspect the exported files:

```bash
find flathub-build/files/share \
  \( -path '*applications*' -o -path '*metainfo*' -o -path '*icons*' \) \
  -type f -print
```

The expected files include:

```text
share/applications/org.tymko.Links.desktop
share/metainfo/org.tymko.Links.metainfo.xml
share/icons/hicolor/scalable/apps/org.tymko.Links.svg
```

## 14. Check sandbox permissions before submission

Links currently requests:

- `--share=ipc`;
- `--socket=wayland`;
- `--socket=fallback-x11`;
- `--talk-name=org.freedesktop.Flatpak`.

The first three are used for a normal GTK desktop application. The
`org.freedesktop.Flatpak` permission is broader: it is used only for the
optional terminal-command fallback through `flatpak-spawn --host`.

Before submission, decide whether command actions are essential to the
product. If they are retained, document the permission and explain that
commands run only after an explicit confirmation dialog. If command actions
are removed or changed to a portal-only design, remove the permission from the
manifest and update `docs/SECURITY.md`, the README, and the AppStream
description together.

Never add `--share=network`, `--filesystem=home`, `--device=all`, or broad
session-bus permissions just to make a local test pass. Links does not need
network access to do its normal work.

## 15. Submit the application to Flathub

Use the current Flathub new-app procedure and issue template:

```text
https://github.com/flathub/flathub/issues/new
```

The exact form and repository workflow can change, so follow the current
instructions shown by Flathub rather than copying an old submission command.
Provide:

- app ID: `org.tymko.Links`;
- public source repository: `https://github.com/tymko777/links`;
- release tag: `v0.5.0`;
- exact immutable commit;
- a short description of the application;
- the reason for `org.freedesktop.Flatpak`, if it remains in the manifest;
- confirmation that the app is open source under MIT;
- confirmation that no credentials or private services are needed to build it.

When Flathub creates or requests the packaging repository, copy the
submission manifest into that repository exactly as required by the current
Flathub tooling. Do not submit the local manifest with `type: dir`.

During review, respond to concrete lint or metadata requests with a new
commit. Do not force-push or rewrite the reviewed history unless Flathub
explicitly asks for it. Keep the app ID unchanged.

## 16. Update procedure after the first publication

For every update:

```bash
cd ~/links
python3 -m unittest discover -s tests -v
bash scripts/check.sh
git add .
git commit -m "Release Links X.Y.Z"
git push origin main
git tag -a vX.Y.Z -m "Links X.Y.Z"
git push origin vX.Y.Z
git rev-parse vX.Y.Z^{commit}
```

Then update the Flathub manifest:

```yaml
tag: vX.Y.Z
commit: EXACT_40_CHARACTER_COMMIT
```

Update the AppStream `<release>` entry and keep at least the recent release
history. Build and lint the new manifest before opening the Flathub update
pull request.

Do not delete or reuse an old release tag. A release tag is part of the
reproducible source history.

## 17. Troubleshooting

### `No such ref org.gnome.Sdk//50`

Refresh the Flathub remote and install the exact branch:

```bash
flatpak update
flatpak install flathub org.gnome.Sdk//50 org.gnome.Platform//50
```

If the GNOME runtime version has moved by the time of submission, use the
runtime version supported by the current Flathub policy and update the
manifest consistently.

### The build says a source is not immutable

The source is probably using `branch: main` or a Git URL without a commit.
Use a release tag plus its exact 40-character commit.

### The app builds but is not visible in the application menu

Check all three identifiers and paths:

```bash
flatpak info --show-metadata org.tymko.Links
desktop-file-validate resources/org.tymko.Links.desktop
appstreamcli validate --pedantic resources/org.tymko.Links.metainfo.xml
```

The desktop file name, `Icon=` value, AppStream `<id>`, launchable desktop
ID, and installed icon basename must all match `org.tymko.Links`.

### The app opens but actions cannot launch

Check the permissions:

```bash
flatpak info --show-permissions org.tymko.Links
```

URL and file actions use the desktop's default handlers. Terminal command
actions need the documented host fallback permission and a terminal emulator
available in the host session. This is separate from the application startup
path.

### The local build works but the Flathub build fails

Rebuild from the Git-pinned submission manifest in a clean directory. Look
for accidental dependencies on files outside the repository, local Python
packages, a local virtual environment, or a source path that only exists on
the developer machine.
