"""Tiny static file server for the Pi (run it from systemd).

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
import socketserver
import urllib.parse


class Handler(http.server.SimpleHTTPRequestHandler):
    mounts = {}                            # "/prefix" -> directory, filled in by main()

    def address_string(self):
        return self.client_address[0]      # no reverse DNS lookup

    def translate_path(self, path):
        clean = urllib.parse.unquote(urllib.parse.urlsplit(path).path)
        for prefix, directory in self.mounts.items():
            if clean == prefix or clean.startswith(prefix + "/"):
                self.directory = directory          # a handler instance serves one request
                return super().translate_path(clean[len(prefix):] or "/")
        return super().translate_path(path)

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

    Handler.mounts = {
        "/monitors": os.path.abspath(os.path.expanduser(a.monitors)),
        "/monitors-data": os.path.abspath(os.path.expanduser(a.data)),
    }
    root = os.path.abspath(os.path.expanduser(a.pages))
    Server(("", a.port), functools.partial(Handler, directory=root)).serve_forever()


if __name__ == "__main__":
    main()
