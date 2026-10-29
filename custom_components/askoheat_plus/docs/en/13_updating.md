# 13 — Updating the add-on

*[Deutsche Version](../de/13_aktualisieren.md)*

How to bring ASKOHEAT+ to a new version once a new release appears on
[GitHub](https://github.com/Andreas8476/AH-HomeAssistent-AddOn/releases).
Which variant applies depends on how the integration was installed (see
[04_installation.md](04_installation.md)).

> **Note:** An update keeps your setup, entities, history, dashboard and
> options (e.g. the feed-in value link). The settings on the device itself
> are not affected anyway.

## Variant A: Installed via HACS (recommended)

HACS already has a built-in update mechanism, nothing extra to set up. HACS
regularly checks whether there is a new release on GitHub.

### How to see that an update is available

- **Settings** (sidebar) shows an entry **"ASKOHEAT+ update"** at the top,
  just like updates of Home Assistant itself.
- Alternatively: open **HACS** → **ASKOHEAT+** shows an update notice with
  the new version number.

### Installing the update

1. Click the **"ASKOHEAT+ update"** entry.
2. Optionally read the **release notes** (what changed, see also
   [CHANGELOG.md](../../../../CHANGELOG.md)).
3. Click **Install**.
4. **Restart** Home Assistant when asked
   (**Settings → System → ⏻ top right → Restart Home Assistant**). The new
   version only runs after the restart.

### Update doesn't show up?

- HACS doesn't check instantly but at intervals. To trigger it manually:
  **HACS** → three dots (⋮) next to **ASKOHEAT+** → **"Update information"**.
- To install a specific (also older) version: **HACS** → **ASKOHEAT+** → ⋮ →
  **"Redownload"** → pick the version → restart afterwards. Handy if a new
  version causes problems and you want to go back.

## Variant B: Manual installation (without HACS)

There is no automatic notification here — check the
[releases page](https://github.com/Andreas8476/AH-HomeAssistent-AddOn/releases)
for a new version (tip: on GitHub, top right, enable
**Watch → Custom → Releases** to get an email).

1. In the new release under **Assets**, download **Source code (zip)** and
   extract it.
2. Take the `custom_components/askoheat_plus/` folder from the ZIP and use it
   to **completely replace** the existing folder
   `/config/custom_components/askoheat_plus/` (delete it first rather than
   copying over it, so no outdated files are left behind).
3. Restart Home Assistant.

If you installed manually and want convenient updates from now on: simply
switch to variant A (HACS) — delete the manually copied folder, then install
via HACS as described in [04_installation.md](04_installation.md). Your setup
in Home Assistant is kept.

## Variant C: Development setup (git clone + symlink)

Only for development (see [06_development.md](06_development.md)): this always
runs the state of the local git repo directly.

```bash
cd /config/askoheat_plus
git pull
ha core restart
```

## Which version is running?

- **Version of the integration (this add-on):** in **HACS** under
  **ASKOHEAT+**.
- **Firmware of the heating element:** **Settings → Devices & services →
  ASKOHEAT+** → open the device → "Firmware" line.

Don't mix the two up: the device firmware is updated via the device's own
web UI or by the manufacturer, not via HACS.

## For developers: publishing a new version

For HACS users to be shown an update at all, every new version has to be
published on GitHub as a **release** — a git tag alone is not enough, HACS
evaluates the releases.

1. Bump the version in `custom_components/askoheat_plus/manifest.json`
   (semantic versioning, e.g. `0.8.0` → `0.9.0`).
2. Update [CHANGELOG.md](../../../../CHANGELOG.md)
   (`[Unreleased]` → new version number + date).
3. Commit, set tag `vX.Y.Z`, **push both to GitLab and GitHub**
   (`git push origin main --tags` and `git push github main --tags`).
4. On GitHub under **Releases → Draft a new release**, pick the tag, paste
   the matching CHANGELOG section as the text, **Publish release**.
