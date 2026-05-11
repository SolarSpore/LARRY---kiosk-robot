# Larry the Screensaver

Larry is a sleeping cyberpunk robot screensaver built in a single HTML file. He drifts around the screen to prevent burn-in, breathes slowly, and occasionally opens his cybernetic eyes to run a retinal scan. Tap anywhere to wake him and return to your dashboard.

He was built for a Raspberry Pi 5 running a Home Assistant kiosk on a 10.1" touchscreen, but he'll run in any modern browser on any screen size.

![Larry is a dark-themed SVG robot with glowing Razer green accents, closed cybernetic eyes with rotating iris patterns, floating ZZZ bubbles, and animated chest LEDs.]

---

## Features

- **Drifts around the screen** — bounces off all four edges, never stays still, no burn-in
- **Breathes** — subtle scale animation gives him a slow, steady inhale/exhale
- **Cybernetic eyes** — segmented iris rings rotate slowly clockwise at all times
- **Scan mode** — every few seconds the iris spins up, a scanline sweeps top to bottom, and the pupil dilates, then returns to idle
- **ZZZ bubbles** — three staggered Z's float upward from his head in sequence
- **Snore bubbles** — small circles pulse out from the corner of his mouth
- **Chest LEDs** — four lights blink independently on randomized timers
- **Activity bar** — a green bar on his chest pulses back and forth like a VU meter
- **Antenna pulse** — the tip of his antenna fades in and out
- **CRT scanline overlay** — a subtle full-screen scanline texture over everything
- **Tap to wake** — any click, touch, or keypress navigates back to the dashboard
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

All adjustable values are in the `CONFIG` object at the top of `larry.html`, just below the `<script>` tag. You never need to touch the SVG markup to change how Larry looks or behaves.

```javascript
const CONFIG = {
  larryWidth:      420,
  larryHeight:     480,
  speedMin:        0.9,
  speedMax:        1.4,
  scanIntervalMin: 5000,
  scanIntervalMax: 13000,
  scanSpinSpeed:   1.8,
  idleSpinSpeed:   0.04,
  scanDuration:    2200,
  wakeUrl:         'http://192.168.1.182:8123',
  accentColor:     '#00ff46',
  bgColor:         '#0a0a0a',
};
```

---

### `larryWidth` / `larryHeight`
**Type:** number (pixels)
**Default:** `420` / `480`

The rendered size of Larry on screen. The SVG scales cleanly to any size so there is no quality loss.

- Small screen (7"): try `280` / `320`
- Standard (10"): `420` / `480` works well
- Large display (24"+): try `600` / `700` or bigger

> Both values should stay proportional to each other. The natural ratio is roughly 0.875 (width ÷ height). Stretching him too far in either direction will distort the face.

---

### `speedMin` / `speedMax`
**Type:** number (pixels per frame at 60fps)
**Default:** `0.9` / `1.4`

Controls how fast Larry drifts around the screen. Each time he starts moving, a random speed is picked between these two values independently for the X and Y axes.

| Feel | speedMin | speedMax |
|---|---|---|
| Barely drifting | `0.2` | `0.4` |
| Calm float | `0.4` | `0.7` |
| Default | `0.9` | `1.4` |
| Energetic | `1.5` | `2.2` |
| Chaotic | `2.5` | `4.0` |

> Setting both values the same removes the randomness and makes Larry move at a perfectly constant speed.

---

### `scanIntervalMin` / `scanIntervalMax`
**Type:** number (milliseconds)
**Default:** `5000` / `13000`

How long Larry waits between eye scans. After each scan completes, a new random wait time is chosen between these two values.

| Feel | scanIntervalMin | scanIntervalMax |
|---|---|---|
| Constantly scanning | `1000` | `3000` |
| Frequent | `3000` | `6000` |
| Default | `5000` | `13000` |
| Rare and surprising | `15000` | `30000` |

> Setting both to the same value makes scans trigger on a fixed interval.

---

### `scanSpinSpeed`
**Type:** number (degrees per frame)
**Default:** `1.8`

How fast the iris rings spin during an active scan. This is much faster than the idle spin and is part of what makes the scan feel dramatic.

| Feel | Value |
|---|---|
| Subtle | `0.8` |
| Default | `1.8` |
| Dramatic | `3.0` |
| Frantic | `5.0` |

---

### `idleSpinSpeed`
**Type:** number (degrees per frame)
**Default:** `0.04`

How fast the iris rings rotate when Larry is not scanning. Should be very small — just enough to be noticeable if you watch closely.

| Feel | Value |
|---|---|
| Almost still | `0.01` |
| Default | `0.04` |
| Clearly spinning | `0.12` |
| Too fast | `0.3+` |

---

### `scanDuration`
**Type:** number (milliseconds)
**Default:** `2200`

How long each scan sweep takes from top to bottom of the eye. The scanline and pupil dilation both follow this timing.

| Feel | Value |
|---|---|
| Snappy | `1000` |
| Default | `2200` |
| Slow and deliberate | `4000` |

---

### `wakeUrl`
**Type:** string (URL)
**Default:** `'http://192.168.1.182:8123'`

Where Larry navigates when tapped, clicked, or any key is pressed. Set this to your Home Assistant instance URL, or any page you want to return to.

```javascript
wakeUrl: 'http://192.168.1.182:8123',           // Home Assistant (default)
wakeUrl: 'http://192.168.1.182:8123/lovelace/dashboard-larry',  // specific dashboard
wakeUrl: 'http://localhost:8123',               // if running on the same machine as HA
```

---

### `accentColor`
**Type:** string (any valid CSS color)
**Default:** `'#00ff46'`

The color of every glowing element — eyes, LEDs, ZZZs, outlines, scanlines, antenna. Changing this one value recolors the entire robot.

| Look | Value |
|---|---|
| Razer green (default) | `'#00ff46'` |
| Cyan / ice | `'#00cfff'` |
| Amber / warm | `'#ffaa00'` |
| Red alert | `'#ff2200'` |
| Purple | `'#aa44ff'` |
| White | `'#e0ffe0'` |

---

### `bgColor`
**Type:** string (any valid CSS color)
**Default:** `'#0a0a0a'`

The background color behind Larry. Should be very dark so the glowing accents stand out. Pure black (`#000000`) works fine, but a very slightly lifted dark (`#0a0a0a`) looks more natural with the glow filters.

---

## Screensaver Timeout

The idle timeout before Larry appears is controlled by `swayidle`, not by Larry himself. Edit `~/.config/autostart/screensaver.desktop` on the Pi:

```ini
Exec=swayidle -w timeout 300 'chromium --kiosk --noerrdialogs /home/countermandaxis/screensaver/larry.html' resume 'pkill -f larry.html'
```

Change `300` to the number of seconds you want:

| Timeout | Value |
|---|---|
| 2 minutes | `120` |
| 5 minutes (default) | `300` |
| 10 minutes | `600` |
| 30 minutes | `1800` |

After editing, apply the change:

```bash
systemctl --user restart swayidle
# or just reboot
sudo reboot
```

---

## Testing Larry Without Waiting for Idle

Launch him directly from SSH to see changes immediately:

```bash
DISPLAY=:0 chromium --kiosk --noerrdialogs /home/countermandaxis/screensaver/larry.html
```

Press `Ctrl+C` in the SSH session to close him.

Or open the file directly on the Pi's desktop browser — just navigate to:
```
file:///home/countermandaxis/screensaver/larry.html
```

---

## Updating Larry

Edit the file on the Pi directly:

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

Larry uses standard SVG animations and the Web Animations API. He works in any modern browser. He was specifically tested on Chromium on Pi OS Bookworm (Wayland).

- ✅ Chromium (Pi OS, Windows, macOS)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

---

## Technical Notes

- **No burn-in risk** — Larry never stays in one place. The bounding box bounces off all four screen edges using simple velocity reflection.
- **Frame-rate independent** — all animation timings use `dt` (delta time between frames) so Larry moves and scans at the same speed regardless of whether the Pi is running at 30fps or 60fps.
- **Self-contained** — the entire screensaver is one HTML file with no external requests. Safe to run fully offline.
- **Wayland compatible** — runs inside Chromium so it works on Wayland out of the box, unlike X11-only screensavers like xscreensaver.
