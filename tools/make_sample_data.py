"""Write fake monthly CSV data (same format as the capture scripts) for trying out the web page.

usage: make_sample_data.py <output dir> [days=400]
Writes <output dir>/rpi03-temperature/ and <output dir>/austin-78705/, a reading every 5 minutes,
with a gap and a spike thrown in so the chart's handling of both can be checked.
"""
import datetime
import math
import os
import random
import sys

HEADER = "time,temp_f\n"


def main(out, days):
    random.seed(1)
    end = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0, minute=0)
    start = end - datetime.timedelta(days=days)
    files = {}
    t = start
    step = datetime.timedelta(minutes=5)
    gap = (end - datetime.timedelta(days=3), end - datetime.timedelta(days=3) + datetime.timedelta(hours=7))
    spike = end - datetime.timedelta(days=10)
    while t <= end:
        doy = t.timetuple().tm_yday
        hour = t.hour + t.minute / 60.0
        season = 18 * math.sin((doy - 100) / 365.0 * 2 * math.pi)            # +/-18 F over the year
        outdoor = 68 + season + 12 * math.sin((hour - 9) / 24.0 * 2 * math.pi) + random.gauss(0, .4)
        inside = 76 + season * .5 + 3 * math.sin((hour - 11) / 24.0 * 2 * math.pi) + random.gauss(0, .15)
        if abs((t - spike).total_seconds()) < 600:
            inside += 14
        if not (gap[0] <= t <= gap[1]):
            for slug, val in (("rpi03-temperature", inside), ("austin-78705", outdoor)):
                folder = os.path.join(out, slug)
                os.makedirs(folder, exist_ok=True)
                path = os.path.join(folder, t.strftime("%Y-%m") + ".csv")
                if path not in files:
                    files[path] = open(path, "w")
                    files[path].write(HEADER)
                files[path].write("{0},{1:.1f}\n".format(t.strftime("%Y-%m-%dT%H:%M:%SZ"), val))
        t += step
    for f in files.values():
        f.close()
    print("wrote", len(files), "files under", out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 400)
