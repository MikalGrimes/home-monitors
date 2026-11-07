# home-monitors
Raspberry Pi temperature monitor. Readings are appended to monthly CSV files
(month boundaries and timestamps are UTC) that a static web page can load directly.

    data/<slug>/YYYY-MM.csv      time,temp_f   e.g. 2026-11-07T15:20:00Z,72.4

Crontab (every 5 minutes; use python3):

    HOME_MONITORS_DATA=/home/pi/data/home-monitors
    */5 * * * * cd ~/code/home-monitors && python3 capture_temperature.py rpi03-temperature
    */5 * * * * cd ~/code/home-monitors && python3 capture_outdoor.py austin-78705 30.298 -97.742

`HOME_MONITORS_DATA` is where data is stored (default: `./data` next to the scripts).
Outdoor temperature comes from [Open-Meteo](https://open-meteo.com) (free for non-commercial use, no key).

## Web page

`web/index.html` is a static, dependency-free chart page (local-time axis, 1d to All ranges,
drag to zoom, hover for values). It reads `web/config.json` (copy to `web/config.local.json` to
customize per Pi without touching git) and loads only the month files it needs.

`deploy/server.py` is the small static server run by systemd. It maps three URL prefixes to
directories, so nothing else (including the repos' `.git` folders) is reachable:

    /                -> ~/code/pages              (pool controller site)
    /monitors/       -> ~/code/home-monitors/web  (this page)
    /monitors-data/  -> ~/data/home-monitors      (readings written by the capture scripts)

Pi layout: repos in `~/code/`, readings in `~/data/home-monitors/`. Point the capture scripts at the
data directory with `HOME_MONITORS_DATA`, set once at the top of the crontab:

    HOME_MONITORS_DATA=/home/pi/data/home-monitors
    */5 * * * * cd ~/code/home-monitors && python3 capture_temperature.py rpi03-temperature
    */5 * * * * cd ~/code/home-monitors && python3 capture_outdoor.py austin-78705 30.298 -97.742

Target platform is a Pi Zero W on Raspbian Stretch with Python 3.5, so the scripts avoid newer Python features.

systemd (replaces `/home/pi/serve.py` in the `pool-page` service; `WorkingDirectory` no longer matters):

    ExecStart=/bin/sh -c 'exec /usr/bin/python3 -u /home/pi/code/home-monitors/deploy/server.py >> /var/log/pool-page.log 2>&1'

then `sudo systemctl daemon-reload && sudo systemctl restart pool-page`. Add `--pages`, `--monitors`,
`--data` or `--port` to override the defaults. Browse to `http://<pi>:8080/monitors/`; the pool page keeps
its existing URL. Dot-files and dot-folders (such as `.git`) are never served.

Try it without a Pi: `python3 tools/make_sample_data.py /tmp/sample` then
`python3 deploy/server.py --pages . --monitors web --data /tmp/sample` and open `http://localhost:8080/monitors/`.
