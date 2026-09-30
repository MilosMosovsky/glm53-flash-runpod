"""Health check shim for RunPod load-balancer endpoints.

The load balancer treats any health response other than 200 (ready) or 204
(initializing) as unhealthy and terminates workers that stay unhealthy for
about 8 minutes. llama-server answers nothing while the model downloads and
503 while it loads, which takes longer than that for large models. This shim
serves on PORT_HEALTH and reports 204 until llama-server's /health is 200.

Usage: python lb_health.py <llama-server port> <health port>
"""

import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = f"http://127.0.0.1:{sys.argv[1]}/health"


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            with urllib.request.urlopen(UPSTREAM, timeout=2) as response:
                code = 200 if response.status == 200 else 204
        except Exception:
            code = 204
        self.send_response(code)
        self.end_headers()

    def log_message(self, *args):
        pass


ThreadingHTTPServer(("0.0.0.0", int(sys.argv[2])), HealthHandler).serve_forever()
