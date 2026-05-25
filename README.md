# Larry the Screensaver

Larry is a sleeping robot screensaver built in a single HTML file. He drifts around the screen to prevent burn-in, his sensors move slowly, and he occasionally uses his cybernetic eyes to run a retinal scan. Tap anywhere to wake him and return to your dashboard.

He was built for a Raspberry Pi 5 running a Home Assistant kiosk on a 10.1" touchscreen, but he'll run in any modern browser on any screen size.

---

## Features

- **Drifts around the screen** — bounces off all four edges using `getBoundingClientRect()` for pixel-accurate bounds, never stays still, no burn-in
- **Breathes** — subtle scale animation gives him a slow, steady inhale/exhale
- **Cybernetic eyes** — segmented iris rings rotate slowly clockwise at all times
- **Scan mode** — every few seconds the iris spins up, a scanline sweeps top to bottom, and the pupil dilates, then returns to idle
- **ZZZ bubbles** — three staggered Z's float upward from his head in sequence
- **Snore bubbles** — small circles pulse out from the corner of his mouth
- **Chest LEDs** — four lights blink independently on randomized timers
- **Activity bar** — a green bar on his chest pulses back and forth like a VU meter
- **Antenna pulse** — the tip of his antenna fades in and out
- **CRT scanline overlay** — a subtle full-screen scanline texture over everything
- **Tap to wake** — any click, touch, or keypress closes the screensaver window
- **"Tap to wake Larry" hint** — fades in and out at the bottom of the screen

---

## Files

```
screensaver/
└── larry.html    # The entire screensaver — self-contained, no dependencies
```

Larry has no external dependencies. No JavaScript libraries, no CDN calls, no fonts. Pure HTML, CSS, SVG, and vanilla JS. It will work completely offline.

---

## Configuration

All adjustable values live as `const` declarations at the top of the `<script>` block in `larry.html`. You never need to touch the SVG markup to change how Larry looks or behaves.

```javascript
const LARRY_WIDTH       = Math.min(window.innerWidth * 0.30, window.innerHeight * 0.38);
const LARRY_HEIGHT      = LARRY_WIDTH * (320 / 260);
const SPEED_MIN         = 0.9;
const SPEED_MAX         = 1.4;
const SCAN_INTERVAL_MIN = 5000;
const SCAN_INTERVAL_MAX = 13000;
const SCAN_SPIN_SPEED   = 1.8;
const IDLE_SPIN_SPEED   = 0.045;
const SCAN_DURATION     = 2400;
const BG_COLOR          = '#0a0a0a';
const WAKE_URL          = '';
```

### LARRY_WIDTH / LARRY_HEIGHT

Larry's size is calculated relative to the viewport so he fits any screen automatically. The formula picks whichever axis is smaller and takes a percentage of it, then derives the height from the SVG's natural aspect ratio (260:320).

To make him bigger or smaller, adjust the multipliers:

| Size feel | Width multiplier | Height multiplier |
|-----------|-----------------|-------------------|
| Smaller   | 0.22            | 0.28              |
| Default   | 0.30            | 0.38              |
| Larger    | 0.42            | 0.52              |

### SPEED_MIN / SPEED_MAX

Controls how fast Larry drifts. Each axis gets an independent random speed between these values.

| Feel | speedMin | speedMax |
|------|----------|----------|
| Barely drifting | 0.2 | 0.4 |
| Calm float | 0.4 | 0.7 |
| Default | 0.9 | 1.4 |
| Energetic | 1.5 | 2.2 |
| Chaotic | 2.5 | 4.0 |

### SCAN_INTERVAL_MIN / SCAN_INTERVAL_MAX

How long Larry waits between eye scans (milliseconds). A new random interval is chosen after each scan.

| Feel | Min | Max |
|------|-----|-----|
| Constantly scanning | 1000 | 3000 |
| Frequent | 3000 | 6000 |
| Default | 5000 | 13000 |
| Rare and surprising | 15000 | 30000 |

### SCAN_SPIN_SPEED

How fast the iris rings spin during a scan (degrees per frame). Default: `1.8`.

### IDLE_SPIN_SPEED

How fast the iris rotates when idle. Should be very small. Default: `0.045`.

### SCAN_DURATION

How long each scan sweep takes in milliseconds. Default: `2400`.

### WAKE_URL

Where Larry navigates when tapped. If left empty (`''`), Larry calls `window.close()` instead.

```javascript
const WAKE_URL = '';                                      // close the window (default)
const WAKE_URL = 'http://192.168.1.182:8123?kiosk';      // Home Assistant kiosk mode
const WAKE_URL = 'http://192.168.1.182:8123/lovelace/0'; // specific dashboard
```

### BG_COLOR / Accent Color

`BG_COLOR` sets the background. The accent color (`#00ff46` Razer green) is set directly in the SVG markup. To recolor Larry, do a find-and-replace on `#00ff46` in the file.

| Look | Value |
|------|-------|
| Razer green (default) | `#00ff46` |
| Cyan / ice | `#00cfff` |
| Amber / warm | `#ffaa00` |
| Red alert | `#ff2200` |
| Purple | `#aa44ff` |

---

## How the Animation Works

All dynamic animations are driven by a single `requestAnimationFrame` loop — no SVG `<animate>` tags are used for anything interactive. This prevents the timing-mismatch flicker that SVG animations produce when the element is scaled.

All stroke widths in the SVG are set to a minimum of `1.5px`. Sub-pixel strokes flicker visibly when Chromium scales the SVG on a Pi display.

The bounce uses `getBoundingClientRect()` on every frame to get the true rendered pixel size of the SVG element — including glow filter overflow and the antenna tip — so Larry never clips outside the viewport regardless of screen size.

The main loop calls these functions every frame:

- `moveLarry()` — updates position and bounces off edges
- `updateEyes(dt)` — rotates iris rings, triggers and animates scan mode
- `updateLEDs(ts)` — each LED has an independent sine wave with randomized period and phase
- `updateVU(ts)` — compound sine wave drives the activity bar for an organic feel
- `updateAntenna(ts)` — smooth sine pulse on the antenna tip
- `updateSnore(ts)` — three staggered bubble circles drift upward and fade
- `updateZZZ(ts)` — three staggered Z characters float and fade at different sizes

---

## How the Screensaver Loop Works

The Pi boots straight into labwc (a Wayland compositor) with no traditional desktop environment. Chromium is launched by `lxsession-xdg-autostart` via XDG autostart files in `~/.config/autostart/`.

Idle detection is handled by `swayidle`, which watches for inactivity at the Wayland compositor level. This is more reliable than browser-based idle detection because it works regardless of what Home Assistant is doing inside Chromium.

The loop works like this:

1. Pi boots → Chromium opens Home Assistant in kiosk mode
2. After 5 minutes of no input → `swayidle` launches a second Chromium window with Larry
3. User touches the screen or presses a key → Larry calls `window.close()` and exits
4. `swayidle` resets its timer and starts counting again
5. After another 5 minutes → Larry appears again

There is no `resume` action in the swayidle config. `swayidle` resets its own timer automatically when input is detected, so no cleanup command is needed. Larry closes himself via `window.close()`.

---

## Autostart Files

All autostart files live in `~/.config/autostart/`. They are processed by `lxsession-xdg-autostart`, which is called by labwc on every boot.

### kiosk.desktop — launches Home Assistant

```ini
[Desktop Entry]
Type=Application
Name=HA Kiosk
Exec=chromium --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble --disable-restore-session-state --check-for-update-interval=31536000 --password-store=basic --use-mock-keychain "http://192.168.1.182:8123?kiosk"
X-GNOME-Autostart-enabled=true
```

### screensaver.desktop — launches swayidle to trigger Larry

```ini
[Desktop Entry]
Type=Application
Name=Larry Screensaver
Exec=swayidle -w timeout 300 'WAYLAND_DISPLAY=wayland-1 chromium --kiosk --noerrdialogs file:///home/countermandaxis/screensaver/larry.html'
X-GNOME-Autostart-enabled=true
```

> **Note:** `WAYLAND_DISPLAY=wayland-1` is required because swayidle runs before the display variable is exported to its child processes. Without it, Chromium has no display to open on.

> **Note:** There is no `resume` action. swayidle resets its own timer automatically when input is detected, so no cleanup command is needed.

### unclutter.desktop — hides the mouse cursor

```ini
[Desktop Entry]
Type=Application
Name=Unclutter
Exec=unclutter -idle 3
X-GNOME-Autostart-enabled=true
```

Hides the cursor after 3 seconds of no mouse movement. Keeps the display clean on a touchscreen.

---

## Screensaver Timeout

The idle timeout is set in `screensaver.desktop`. Change the `300` in the `timeout` value to the number of seconds you want:

| Timeout | Value |
|---------|-------|
| 2 minutes | 120 |
| 5 minutes (default) | 300 |
| 10 minutes | 600 |
| 30 minutes | 1800 |

After editing, apply with:

```bash
systemctl --user restart lxsession-xdg-autostart
# or just reboot
sudo reboot
```

---

## Testing Larry Without Waiting for Idle

Launch him directly from SSH:

```bash
DISPLAY=:0 WAYLAND_DISPLAY=wayland-1 chromium --kiosk --noerrdialogs file:///home/countermandaxis/screensaver/larry.html
```

Press `Ctrl+C` in the SSH session to close him.

Or open the file directly in the Pi's browser by navigating to:

```
file:///home/countermandaxis/screensaver/larry.html
```

---

## Updating Larry

Edit the file directly on the Pi:

```bash
nano ~/screensaver/larry.html
```

Or edit it on your computer and scp it over:

```powershell
# Windows PowerShell
scp C:\Users\user\Downloads\larry.html countermandaxis@192.168.1.100:~/screensaver/larry.html
```

```bash
# macOS / Linux
scp ~/Downloads/larry.html countermandaxis@192.168.1.100:~/screensaver/larry.html
```

---

## Browser Compatibility

Larry uses standard SVG and vanilla JS. He works in any modern browser. Specifically tested on Chromium on Pi OS Bookworm (labwc/Wayland).

| Browser | Status |
|---------|--------|
| Chromium (Pi OS, Windows, macOS) | ✅ Tested |
| Firefox | ✅ Compatible |
| Safari | ✅ Compatible |
| Edge | ✅ Compatible |

---

## Technical Notes

- **No burn-in risk** — Larry never stays in one place. Bounce uses `getBoundingClientRect()` for true pixel-accurate edges including glow filter overflow.
- **Frame-rate independent** — all animation timings use `dt` (delta time between frames) so Larry moves and scans at the same speed at 30fps or 60fps.
- **No flicker** — all strokes are minimum `1.5px`. All dynamic animations use `requestAnimationFrame`, not SVG `<animate>`.
- **Self-contained** — one HTML file, no external requests, safe to run fully offline.
- **Wayland compatible** — runs inside Chromium under labwc. `swayidle` handles idle detection at the compositor level.
- **TTY session** — the Pi boots to a TTY, not a full desktop. XDG autostart files are processed by `lxsession-xdg-autostart` via labwc.
- **window.close()** — Larry closes himself on any tap, click, or keypress. This works in a standard Chromium kiosk window opened by swayidle as a child process.
