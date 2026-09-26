# 04 — Installation

*[Deutsche Version](../de/04_installation.md) (primary, authoritative)*

Two repositories, one state: **[GitLab](https://gitlab.com/SyberAlf/ah-homeassistent-addon)**
is the main development repo, **[GitHub](https://github.com/Andreas8476/AH-HomeAssistent-AddOn)**
is a public mirror — needed because **HACS only supports public GitHub
repositories** ("Only public repositories hosted on GitHub will be
compatible with HACS.", per the official HACS docs). Always use the GitHub
URL for the HACS installation below.

## Option A: install via HACS (recommended for other users)

This option is described completely from scratch — even if you've never
worked with a terminal or with HACS before:

- **Step 1:** set up terminal access (only if not already available)
- **Step 2:** install HACS (only if not already installed)
- **Steps 3–5:** install and set up ASKOHEAT+ via HACS

### Step 1 — set up terminal access (if not already available)

Prerequisite: your Home Assistant runs as **Home Assistant OS** or
**Supervised** (with the add-on store). Check this by looking in the
sidebar under **Settings** for **"Add-ons"** or **"Add-on Store"** — if
that's not there (plain "Home Assistant Container"/"Core"), skip this step
and go directly to the terminal-less alternative further below.

1. Click **Settings** in the left sidebar.
2. Click **Add-ons** there.
3. Click the blue **Add-on Store** button at the bottom right.
4. Type **"Terminal"** into the search field at the top.
5. Click the **"Terminal & SSH"** add-on (an official Home Assistant
   add-on, no extra repository needed). If it doesn't show up,
   **"Advanced SSH & Web Terminal"** works just as well — for that you may
   first need to add an extra add-on repository, see
   <https://github.com/hassio-addons/repository>.
6. Click **Install** at the top right and wait for the installation to
   finish (can take 1–2 minutes, a progress bar shows the status).
7. After installation: enable the **"Start on boot"** toggle (recommended,
   so the terminal is automatically available after a restart), then click
   **Start** at the top.
8. A new menu item now appears in the left sidebar (**"Terminal"** or
   **"SSH & Web Terminal"**). Clicking it opens a command line directly in
   the browser — enter the HACS install command there in the next step.

### Step 2 — install HACS (if not already installed)

If "HACS" doesn't yet show up under **Settings → Devices & Services** in
your Home Assistant instance:

1. In the terminal from step 1 (or via SSH, if you prefer), enter the
   following command and confirm with Enter:
   ```sh
   wget -O - https://get.hacs.xyz | bash -
   ```
   The script downloads HACS and sets it up automatically. A success
   message should appear at the end.

   **Alternative with no terminal add-on at all:** download the HACS ZIP
   from <https://github.com/hacs/integration/releases/latest>, upload/copy
   the `hacs` folder it contains via the **"File editor"** add-on (or a
   Samba network share) to `<config>/custom_components/hacs/`. Detailed,
   illustrated guide: <https://hacs.xyz/docs/use/download/download/>.
2. Restart Home Assistant: **Settings → System → Restart** (or on this
   host via terminal: `ha core restart`).
3. After the restart: **Settings → Devices & Services → Add Integration**
   (blue button at the bottom right) → enter and select **"HACS"**.
4. Follow the setup dialog — HACS requires a login via a **GitHub
   account** (no account yet? create one for free at
   <https://github.com/signup>). The dialog shows a code; enter it at
   <https://github.com/login/device> and confirm HACS access in the
   browser.
5. Once done, **"HACS"** appears as a new menu item in the sidebar.

Detailed, up-to-date instructions if anything differs:
<https://hacs.xyz/docs/use/download/download/>.

### Step 3 — add ASKOHEAT+ as a custom repository

HACS doesn't know this project automatically (no entry in the official
HACS default store) — it must be added once as a **custom repository**:

1. Open **HACS** in the sidebar.
2. Three dots (⋮) at the top right → **"Custom repositories"**.
3. **Repository URL:** `https://github.com/Andreas8476/AH-HomeAssistent-AddOn`
4. **Category:** `Integration`
5. Click **Add**.

### Step 4 — install

1. Search for **"ASKOHEAT+"** in HACS (now visible as a result).
2. Open it → **Download** → pick the latest version → install.
3. Restart Home Assistant when HACS asks (`ha core restart`).

### Step 5 — set up (applies to all installation options)

1. **Settings → Devices & Services → Add Integration**.
2. Search for and select **"ASKOHEAT+"**.
3. Fill in the form:

   | Field | Required | Default | Example |
   |---|---|---|---|
   | Host / IP address | yes | — | `192.168.20.54` |
   | Port | no | `80` | |
   | Polling interval (seconds) | no | `30` | 10–300s |

4. Submit — the integration immediately tests the connection
   (`gethome.json`). On success, the device is created with its model name
   as the title, including all sensors/binary sensors/number entities (see
   [05_entities.md](05_entities.md)).

### Changing host/port/polling interval later

Not only possible during initial setup — adjustable at any time afterward,
without removing and re-adding the integration:

1. Open **Settings → Devices & Services → ASKOHEAT+**.
2. On the device tile, the three dots (⋮) → **"Reconfigure"**.
3. Adjust the values, submit — the integration tests the new connection
   just like at initial setup and then reloads automatically.

**Important:** when reconfiguring, the same physical device (same device
ID) must respond at the new address as at the original setup — otherwise
the dialog aborts with an error message. For a completely different device,
set up a second, separate integration instead (see "Adding multiple heating
elements" below).

### Adding multiple heating elements

Each ASKOHEAT+ is set up as its own integration instance — simply go
through **Settings → Devices & Services → Add Integration → "ASKOHEAT+"**
again (step 5) with the address of the second device. Afterward, for a
dedicated dashboard view per device, run:
[`dashboard/generate_dashboard.py`](../../../../dashboard/generate_dashboard.py),
see [11_dashboard.md](11_dashboard.md).

### Removing a device

**Settings → Devices & Services → ASKOHEAT+** → the affected device → ⋮ →
**Delete**. Home Assistant automatically removes the device and all its
entities from the registry — no manual cleanup needed. (Pure historical
data in the recorder database is deliberately kept, that's normal Home
Assistant behavior.) Afterward, re-run `generate_dashboard.py` if needed so
the removed device's view also disappears from the dashboard.

## Option B: manual installation (without HACS)

1. Download the repository (GitHub or GitLab link, e.g. "Download ZIP" or
   `git clone`).
2. Copy the `custom_components/askoheat_plus/` folder from the repo to
   `<HA config folder>/custom_components/askoheat_plus/`.
3. Restart Home Assistant.
4. Continue as above from "Step 5 — set up".

## Option C: local development on this host (current setup)

The code already lives under `/homeassistant/askoheat_plus/` and is mounted
into `custom_components/` via a symlink (see
[03_architecture.md](03_architecture.md)) — nothing to install on this host,
just:

1. `ha core check` (validate the configuration)
2. `ha core restart`
3. Continue as above from "Step 5 — set up"

## Prerequisites

- ASKOHEAT+ device on the same local network as Home Assistant, reachable
  via HTTP (default port 80), no authentication needed.
- No additional Python packages (`requirements: []` in the manifest) —
  only the `aiohttp` library already bundled with Home Assistant is used.
- For option A (HACS), if HACS isn't installed yet: a terminal add-on
  ("Advanced SSH & Web Terminal" or similar, from the add-on store) **or**
  access to the "File editor"/Samba for the terminal-less alternative —
  plus a GitHub account to sign in to HACS (independent of the ASKOHEAT+
  repo itself). If HACS is already installed, this isn't needed.
