
from http.server import BaseHTTPRequestHandler, HTTPServer


class WERRequestHandler(BaseHTTPRequestHandler):
    """This class handles HTTP request for the WER service."""

    def do_GET(self):
        """Handles GET requests."""
        self.send_response(200)  # TODO: Replace with actual logic.
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"<h1>WER service online</h1>".encode('utf-8'))

    def do_POST(self):
        """Handles POST requests."""
        pass


if __name__ == "__main__":
    hostName = 'localhost'
    serverPort = 8888
    server = HTTPServer((hostName, serverPort), WERRequestHandler)
    print(f"Server started at {hostName}:{serverPort}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    print("Server stopped")
