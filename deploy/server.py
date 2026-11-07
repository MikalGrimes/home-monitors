"""Tiny static file server for the Pi (run it from systemd). Works on Python 3.5.

Only three directories are reachable, so the repos' .git folders and source stay private:

    /                -> --pages     (default ~/code/pages, the pool controller site)
    /monitors/       -> --monitors  (default ~/code/home-monitors/web)
    /monitors-data/  -> --data      (default ~/data/home-monitors, where the capture scripts write)

usage: server.py [--pages DIR] [--monitors DIR] [--data DIR] [--port 8080]
"""
import argparse
import functools
import http.server
import os
import posixpath
import socketserver
import urllib.parse


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, root, mounts, **kwargs):
        self.root = root
        self.mounts = mounts               # {"monitors": dir, "monitors-data": dir}
        super().__init__(*args, **kwargs)

    def address_string(self):
        return self.client_address[0]      # no reverse DNS lookup

    def translate_path(self, path):
        # Same job as the stdlib version (which on 3.5 can only serve the current directory),
        # but the first path segment may select a different base directory.
        path = path.split("?", 1)[0].split("#", 1)[0]
        trailing_slash = path.rstrip().endswith("/")
        words = [w for w in posixpath.normpath(urllib.parse.unquote(path)).split("/") if w]
        base = self.root
        if words and words[0] in self.mounts:
            base = self.mounts[words[0]]
            words = words[1:]
        result = base
        for w in words:
            if w.startswith("."):
                return os.path.join(base, "no-such-file")   # hide .git and other dot files (404)
            if os.path.dirname(w):
                continue                   # never let a segment climb out of its base
            result = os.path.join(result, w)
        return result + "/" if trailing_slash else result

    def end_headers(self):
        # Revalidate on every load: unchanged files come back as a cheap 304,
        # and the current month's CSV is never served stale.
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pages", default="~/code/pages")
    ap.add_argument("--monitors", default="~/code/home-monitors/web")
    ap.add_argument("--data", default="~/data/home-monitors")
    ap.add_argument("--port", type=int, default=8080)
    a = ap.parse_args()

    def full(p):
        return os.path.abspath(os.path.expanduser(p))

    handler = functools.partial(Handler, root=full(a.pages),
                                mounts={"monitors": full(a.monitors), "monitors-data": full(a.data)})
    Server(("", a.port), handler).serve_forever()


if __name__ == "__main__":
    main()
