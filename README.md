# fan-lights

Controls the 8 RGB LEDs on a Framework laptop's Mobius fan. Two modes of operation:

1. **`daemon.py`** — standalone daemon that drives LEDs directly via `framework_tool`
2. **`rgb_bridge.py`** — OpenRGB bridge that polls a virtual `FrameworkFan` device in OpenRGB and forwards colors to `framework_tool`
3. **`fanlight`** — interactive CLI tool (installed separately) that wraps `daemon.py` with a live pattern-switching menu

---

## Repository structure

```
fan-lights/
├── daemon.py          # Standalone pattern runner (requires sudo)
├── rgb_bridge.py      # OpenRGB SDK bridge
├── framework_tool     # Binary — low-level LED control (download separately, see below)
├── CLAUDE.md          # Notes for Claude Code
├── README.md          # This file
└── patterns/
    ├── __init__.py    # Auto-discovery of pattern classes
    ├── base.py        # Pattern base class
    ├── breathe.py     # Breathing pulse
    ├── comet.py       # Comet trail chase
    ├── fire.py        # Fire flicker
    └── rainbow.py     # Rotating rainbow
```

---

## Requirements

- Ubuntu (tested on 25.10) or other Linux distro with `sudo`/`sudo-rs`
- Python 3.10+
- `framework_tool` binary in the repo root (see step 2 below)
- OpenRGB (optional — only needed for `rgb_bridge.py` or the GUI option in `fanlight`)

---

## Installation on a new machine

### 1. Clone the repo

```bash
git clone <repo-url> ~/Repos/fan-lights
cd ~/Repos/fan-lights
```

### 2. Download `framework_tool`

The binary is not included in the repo and must be downloaded separately from the [Framework Computer releases page](https://github.com/FrameworkComputer/framework-system/releases).

Download the latest version directly into the repo root:

```bash
curl -fLo ~/Repos/fan-lights/framework_tool \
  https://github.com/FrameworkComputer/framework-system/releases/latest/download/framework_tool
```

Then make it executable:

```bash
chmod +x ~/Repos/fan-lights/framework_tool
```

> **Important:** `framework_tool` must live in the repo root (`fan-lights/`). `daemon.py` calls it via the relative path `./framework_tool` and will fail with `FileNotFoundError` if it is elsewhere.

### 2. Install the `fanlight` CLI tool

Copy the script to your local bin and make it executable:

```bash
cp fanlight ~/.local/bin/fanlight
chmod +x ~/.local/bin/fanlight
```

Make sure `~/.local/bin` is on your PATH. Add this to `~/.zshrc` or `~/.bashrc` if it isn't:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 3. Add the sudoers rule

`daemon.py` calls `framework_tool` which requires root. Add a targeted NOPASSWD rule so `fanlight` can run it without prompting for a password every time.

Open sudoers safely with:

```bash
sudo visudo
```

Add this line at the bottom (replace `yourusername` with your actual username):

```
yourusername ALL=(ALL) NOPASSWD: /usr/bin/python3 /home/yourusername/Repos/fan-lights/daemon.py *
```

> **Important notes on this rule:**
> - Scoped to one specific script — it does not grant general passwordless sudo access
> - The `*` wildcard allows pattern name arguments (e.g. `rainbow`, `fire,comet`)
> - If you move the repo to a different path, update this rule to match
> - On systems using `sudo-rs` (Ubuntu 25.10+), the rule must be in `/etc/sudoers` directly, not in `/etc/sudoers.d/`, unless `@includedir /etc/sudoers.d` is present in the main sudoers file

### 4. (Optional) Install OpenRGB

Only needed if you want the GUI for per-LED precision control or plan to use `rgb_bridge.py`:

```bash
sudo apt install openrgb -y
```

---

## Usage

### `fanlight` — interactive CLI (recommended)

```bash
fanlight
```

Presents a numbered menu of available patterns. While a pattern is running:

| Input | Action |
|---|---|
| `1`–`N` | Switch to that pattern immediately |
| `breathe` (or any name) | Switch by name |
| `rainbow,fire` | Cycle two patterns (30s each) |
| last number | Cycle all patterns |
| `g` | Launch OpenRGB GUI for per-LED control |
| `q` or `Ctrl+C` | Quit and turn lights off |

Selecting the same pattern that is already running does nothing (no restart).

### `daemon.py` — direct CLI

```bash
# List available patterns
sudo python3 daemon.py

# Run a single pattern
sudo python3 daemon.py rainbow

# Cycle patterns (30s each)
sudo python3 daemon.py rainbow,fire,comet
```

Must be run from the `fan-lights/` directory — `framework_tool` is referenced by relative path `./framework_tool`.

### `rgb_bridge.py` — OpenRGB integration

```bash
python3 rgb_bridge.py
```

Requires OpenRGB to be running with its SDK server active on `localhost:6742`. The bridge polls the `FrameworkFan` device in OpenRGB at 10Hz and forwards its colors to `framework_tool`, allowing OpenRGB effects to drive the physical fan LEDs directly.

---

## Adding a new pattern

Create a new file in `patterns/`. It will be auto-discovered — no registration needed.

```python
# patterns/mypattern.py
from patterns.base import Pattern

class MyPattern(Pattern):
    NAME = "mypattern"     # used as the CLI argument
    delay = 0.05           # seconds between frames

    def step(self):
        self.tick += 1
        # Must return a list of exactly 8 (r, g, b) tuples, values 0–255
        return [self.hsv(self.tick * 0.01 + i / self.NUM_LEDS) for i in range(self.NUM_LEDS)]
```

Helper methods available on all patterns:

| Method | Description |
|---|---|
| `self.hsv(h, s=1.0, v=1.0)` | Convert HSV to RGB tuple. `h` is 0–1, wraps around |
| `self.lerp_color(c1, c2, t)` | Interpolate between two RGB tuples. `t` is 0–1 |
| `self.black()` | Returns `(0, 0, 0)` |
| `self.tick` | Frame counter, increments each `step()` call |
| `self.NUM_LEDS` | Constant `8` |

---

## Troubleshooting

### `FileNotFoundError: ./framework_tool`
`daemon.py` uses a relative path. Always run it from the `fan-lights/` directory, or use `fanlight` which handles this automatically.

### `sudo-rs: interactive authentication is required`
The NOPASSWD sudoers rule is missing or not being read. Verify with:
```bash
sudo grep NOPASSWD /etc/sudoers
```
Also check that `fanlight` calls `sudo -n` (non-interactive flag) — without `-n`, sudo-rs may attempt tty-based auth even when a NOPASSWD rule exists.

### `setsid` / no controlling terminal issues
If running `daemon.py` from a script that detaches from the terminal (e.g. using `os.setsid()`), sudo-rs will fail to authenticate even with NOPASSWD. The `fanlight` script intentionally does **not** use `setsid` for this reason.

### sudoers.d not being read
On some Ubuntu 25.10 systems with `sudo-rs`, `/etc/sudoers.d/` is not automatically included. If adding the rule to a file in `sudoers.d/` has no effect, add it directly to `/etc/sudoers` via `sudo visudo`.

---

## Files created outside this repo

| File | Purpose |
|---|---|
| `~/.local/bin/fanlight` | The interactive CLI tool |
| `/etc/sudoers` | Contains the NOPASSWD rule for `daemon.py` |
