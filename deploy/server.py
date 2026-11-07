"""Tiny static file server for the Pi (systemd runs this; it replaces the old pool-controller server).

Serves ROOT (default ~/pages) on port 8080. Link the monitor page and data into it:

    ln -s ~/home-monitors/web  ~/pages/monitors
    ln -s ~/home-monitors/data ~/pages/monitors-data

usage: server.py [root] [port]
"""
import functools
import http.server
import os
import socketserver
import sys


class Handler(http.server.SimpleHTTPRequestHandler):
    def address_string(self):
        return self.client_address[0]      # no reverse DNS lookup

    def end_headers(self):
        # Revalidate on every load: unchanged files come back as a cheap 304,
        # and the current month's CSV is never served stale.
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    root = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/pages")
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    Server(("", port), functools.partial(Handler, directory=root)).serve_forever()
