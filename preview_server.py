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
}


APP_ROUTES = {"/help", "/privacy", "/terms", "/disclaimer", "/about",
              "/contact", "/feedback", "/credits", "/accessibility"}


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        clean = self.path.split("?", 1)[0].split("#", 1)[0]
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

    def log_message(self, fmt, *args):
        import sys
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("127.0.0.1", 8791), Handler).serve_forever()
