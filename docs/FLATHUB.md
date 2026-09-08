# Flathub publication plan

This repository contains a local `flatpak/org.tymko.Links.yml` manifest so a
developer can build from a checkout. Flathub manifests must instead fetch a
public, immutable source revision; they must not depend on a local `type: dir`
source. Before opening a Flathub pull request:

1. Create the public repository `https://github.com/tymko/links` under the
   developer identity `tymko`.
2. Tag a release such as `v0.2.2` and push it.
3. Copy the manifest into a Flathub submission repository.
4. Replace the local source:

   ```yaml
   sources:
     - type: git
       url: https://github.com/tymko/links.git
       tag: v0.2.2
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
