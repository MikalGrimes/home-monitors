"""Shared helper: append one reading to a monthly CSV data file.

Layout:  <data root>/<slug>/YYYY-MM.csv   (month boundaries are UTC)
Row:     2026-11-07T15:20:00Z,72.4        (UTC timestamp, degrees F)

The data root defaults to ./data next to this file; set HOME_MONITORS_DATA
to put it somewhere else (for example, the directory your web server serves).
"""
import datetime
import os

HEADER = "time,temp_f\n"


def data_root():
    default = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    return os.environ.get("HOME_MONITORS_DATA", default)


def append_reading(slug, temp_f, when=None):
    """Append (utc time, temp_f) to the current UTC month's file for `slug`."""
    if when is None:
        when = datetime.datetime.now(datetime.timezone.utc)
    when = when.astimezone(datetime.timezone.utc).replace(microsecond=0)

    folder = os.path.join(data_root(), slug)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, when.strftime("%Y-%m") + ".csv")

    row = "{0},{1:.1f}\n".format(when.strftime("%Y-%m-%dT%H:%M:%SZ"), temp_f)
    new_file = not os.path.exists(path)
    with open(path, "a") as f:
        if new_file:
            f.write(HEADER)
        f.write(row)  # one short write in append mode, so readers never see half a line
    return path, row.strip()
