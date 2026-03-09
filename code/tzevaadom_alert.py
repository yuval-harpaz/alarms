#!/usr/bin/env python3
"""
Tzeva Adom alert poller
- Polls https://api.tzevaadom.co.il/notifications every 100ms
- On alert: system notification (notify-send) + opens browser page
- Logs: first non-empty, up to 10 changes, last fetch before empty
"""

import json
import time
import subprocess
import webbrowser
import os
import tempfile
import requests
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────
URL         = "https://api.tzevaadom.co.il/notifications"
POLL_MS     = 100          # milliseconds between requests
LOG_FILE    = "alerts.log"
MAX_CHANGES = 10           # log up to this many changes after first non-empty
# ───────────────────────────────────────────────────────────────────────────

def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def log(msg, data=None):
    line = f"[{ts()}] {msg}"
    if data is not None:
        line += "\n  " + json.dumps(data, ensure_ascii=False)
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def fetch():
    """Return parsed JSON list, or None on error."""
    try:
        r = requests.get(URL, timeout=2, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            return data
        return None
    except Exception as e:
        print(f"[{ts()}] fetch error: {e}")
        return None

def payload_changed(old, new):
    """Detect any change in the JSON payload."""
    return json.dumps(old, sort_keys=True) != json.dumps(new, sort_keys=True)

    # ── Alternative change detectors (uncomment to use instead) ──
    # Detect change in cities only:
    # old_cities = {c for item in (old or []) for c in item.get("cities", [])}
    # new_cities = {c for item in (new or []) for c in item.get("cities", [])}
    # return old_cities != new_cities
    #
    # Detect new notificationId:
    # old_ids = {item.get("notificationId") for item in (old or [])}
    # new_ids = {item.get("notificationId") for item in (new or [])}
    # return not new_ids.issubset(old_ids)
    #
    # Detect change in threat level:
    # old_threats = {item.get("threat") for item in (old or [])}
    # new_threats = {item.get("threat") for item in (new or [])}
    # return old_threats != new_threats

# ── HTML alert page (written to temp file, opened in browser) ───────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>🚨 TZEVA ADOM</title>
  <style>
    body {{ background: #ff0000; color: white; font-family: sans-serif;
           display: flex; align-items: center; justify-content: center;
           min-height: 100vh; margin: 0; }}
    .box {{ background: rgba(0,0,0,0.6); padding: 2em; border-radius: 1em;
            max-width: 600px; text-align: center; }}
    h1 {{ font-size: 3em; margin: 0 0 0.5em; }}
    .cities {{ font-size: 1.4em; line-height: 1.8; }}
    .time {{ margin-top: 1em; opacity: 0.7; }}
  </style>
</head>
<body>
  <div class="box">
    <h1>🚨 צבע אדום 🚨</h1>
    <div class="cities">{cities}</div>
    <div class="time">{time}</div>
  </div>
  <script>
    // Play alert sound
    const ctx = new AudioContext();
    function beep(freq, start, dur) {{
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.connect(g); g.connect(ctx.destination);
      o.frequency.value = freq;
      g.gain.setValueAtTime(0.8, ctx.currentTime + start);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + start + dur);
      o.start(ctx.currentTime + start);
      o.stop(ctx.currentTime + start + dur + 0.05);
    }}
    beep(880, 0,   0.3);
    beep(660, 0.35, 0.3);
    beep(880, 0.7,  0.3);
    beep(660, 1.05, 0.5);
  </script>
</body>
</html>"""

_browser_tmpfile = None

def show_browser_alert(data):
    global _browser_tmpfile
    cities = []
    for item in data:
        cities.extend(item.get("cities", []))
    cities_html = "<br>".join(cities) if cities else "(unknown)"
    html = HTML_TEMPLATE.format(cities=cities_html, time=ts())

    # Reuse same temp file so we don't open 100 tabs
    if _browser_tmpfile is None:
        fd, path = tempfile.mkstemp(suffix=".html", prefix="tzevaadom_")
        os.close(fd)
        _browser_tmpfile = path

    with open(_browser_tmpfile, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open(f"file://{_browser_tmpfile}")

def show_system_notification(data):
    cities = []
    for item in data:
        cities.extend(item.get("cities", []))
    body = ", ".join(cities) if cities else "Alert!"
    try:
        subprocess.Popen(["notify-send", "-u", "critical", "-t", "10000",
                          "🚨 TZEVA ADOM", body])
    except FileNotFoundError:
        print("notify-send not found — install with: sudo apt install libnotify-bin")

# ── Main loop ───────────────────────────────────────────────────────────────
def main():
    print(f"[{ts()}] Starting poller → {URL} every {POLL_MS}ms")
    print(f"[{ts()}] Log file: {os.path.abspath(LOG_FILE)}")

    prev_data      = []      # last known payload
    in_alert       = False   # currently in a non-empty alert period
    change_count   = 0       # number of changes logged since alert started
    last_logged    = None    # last payload we logged

    interval = POLL_MS / 1000.0

    while True:
        t0   = time.monotonic()
        data = fetch()

        if data is None:
            # fetch error — just wait and retry
            time.sleep(interval)
            continue

        is_empty = len(data) == 0

        if not in_alert and not is_empty:
            # ── First non-empty message ──────────────────────────────────
            in_alert     = True
            change_count = 1
            last_logged  = data
            log("ALERT START (first non-empty)", data)
            show_system_notification(data)
            show_browser_alert(data)

        elif in_alert and not is_empty:
            if payload_changed(last_logged, data):
                if change_count <= MAX_CHANGES:
                    # ── Changed message (up to MAX_CHANGES) ─────────────
                    change_count += 1
                    last_logged   = data
                    log(f"ALERT CHANGE #{change_count}", data)
                    show_system_notification(data)
                    show_browser_alert(data)

        elif in_alert and is_empty:
            # ── Last fetch before empty ──────────────────────────────────
            log("ALERT END (last before empty)", last_logged)
            in_alert     = False
            change_count = 0
            last_logged  = None

        prev_data = data

        # Sleep for remainder of interval
        elapsed = time.monotonic() - t0
        sleep   = max(0, interval - elapsed)
        time.sleep(sleep)

if __name__ == "__main__":
    main()
