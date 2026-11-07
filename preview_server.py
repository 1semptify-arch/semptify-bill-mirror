"""Local preview server — mimics the Cloudflare Worker's routing.

The worker serves repo-root files at /static/img/<name> and /static/js/<name>,
and resolves clean URLs (/bill, /bill/live, /your-voice) to the built *.html
files. python -m http.server can't do either, so this maps both. Preview
only — never deploy.
"""
import http.server
import pathlib

ROOT = pathlib.Path(__file__).parent

ALIASES = {
    "/": "bill.html",
    "/bill": "bill.html",
    "/bill/live": "live.html",
    "/live": "live.html",
    "/research": "research.html",
    "/bill/research": "research.html",
    "/what-the-bill-changes": "what-the-bill-changes.html",
    "/your-voice": "your-voice.html",
    "/voice": "your-voice.html",
    "/bill/history": "history.html",
    "/bill/providers": "providers.html",
    "/bill/brief": "brief.html",
    "/bill/classroom": "classroom.html",
    "/bill/press": "press.html",
    "/bill/myths": "myths.html",
}


APP_ROUTES = {"/help", "/privacy", "/terms", "/disclaimer", "/about",
              "/contact", "/feedback", "/credits", "/accessibility"}


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        clean = self.path.split("?", 1)[0].split("#", 1)[0]
        if clean.startswith("/api/"):
            self._proxy_api()
            return
        if clean == "/favicon.ico":
            self.send_response(302)
            self.send_header("Location", "/static/img/mn-flag.png")
            self.end_headers()
            return
        if clean in APP_ROUTES:
            self.send_response(302)
            self.send_header("Location", "https://semptify.org" + clean)
            self.end_headers()
            return
        super().do_GET()

    def translate_path(self, path):
        clean = path.split("?", 1)[0].split("#", 1)[0]
        if "/static/img/" in clean or "/static/js/" in clean:
            cand = ROOT / clean.rsplit("/", 1)[-1]
            if cand.exists():
                return str(cand)
        if clean in ALIASES:
            return str(ROOT / ALIASES[clean])
        if "." not in clean.rsplit("/", 1)[-1]:
            cand = ROOT / (clean.strip("/").replace("/", "-") + ".html")
            if cand.exists():
                return str(cand)
            cand = ROOT / (clean.strip("/") + ".html")
            if cand.exists():
                return str(cand)
        return super().translate_path(path)

    def _proxy_api(self):
        """Proxy /api/* to semptify.org so the board works in local preview
        (the Cloudflare worker does the same in prod)."""
        import urllib.request
        url = "https://semptify.org" + self.path
        try:
            req = urllib.request.Request(url, headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/130.0 Safari/537.36"})
            with urllib.request.urlopen(req, timeout=15) as r:
                body = r.read()
                self.send_response(r.status)
                self.send_header("Content-Type", r.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(('{"error":"preview api proxy failed","detail":%s}'
                              % repr(str(e))).encode())

    def log_message(self, fmt, *args):
        import sys
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("127.0.0.1", 8791), Handler).serve_forever()
