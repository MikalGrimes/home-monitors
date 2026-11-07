# home-monitors
Raspberry Pi temperature monitor. Readings are appended to monthly CSV files
(month boundaries and timestamps are UTC) that a static web page can load directly.

    data/<slug>/YYYY-MM.csv      time,temp_f   e.g. 2026-11-07T15:20:00Z,72.4

Crontab (every 5 minutes; use python3):

    */5 * * * * python3 ~/home-monitors/capture_temperature.py rpi03-temperature
    */5 * * * * python3 ~/home-monitors/capture_outdoor.py austin-78705 30.298 -97.742

Set `HOME_MONITORS_DATA` to store data somewhere other than `./data`.
Outdoor temperature comes from [Open-Meteo](https://open-meteo.com) (free for non-commercial use, no key).

## Web page

`web/index.html` is a static, dependency-free chart page (local-time axis, 1d to All ranges,
drag to zoom, hover for values). It reads `web/config.json` (copy to `web/config.local.json` to
customize per Pi without touching git) and loads only the month files it needs.

`deploy/server.py` is the small static server run by systemd. Serve it from `~/pages` and link in:

    ln -s ~/home-monitors/web  ~/pages/monitors
    ln -s ~/home-monitors/data ~/pages/monitors-data

then browse to `http://<pi>:8080/monitors/`.

Try it without a Pi: `python3 tools/make_sample_data.py /tmp/site/data` and serve `/tmp/site`
with the same two links.
