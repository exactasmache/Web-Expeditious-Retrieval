
from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
from pprint import pformat
import json


class WERRequestHandler(BaseHTTPRequestHandler):
    """This class handles HTTP request for the WER service."""

    def do_GET(self):
        """Handles GET requests."""
        print(self.path)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"<h1>WER service online</h1>".encode('utf-8'))

    def do_POST(self):
        """Handles POST requests."""
        ctype, pdict = parse_header(self.headers.get('content-type'))
        postvars = {}
        try:
            if ctype == 'text/xml':
                length = int(self.headers.get('content-length'))
            elif ctype == 'multipart/form-data':
                postvars = parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.get('content-length'))
                postvars = parse_qs(
                  self.rfile.read(length), keep_blank_values=1)
            else:
                postvars = {}

            print(pformat(postvars))
            data = {
              'message': 'ok'
            }
            body = json.dumps(data)

            self.send_response(200)
            self.send_header(
              'Access-Control-Allow-Credentials', 'true')
            self.send_header(
              'Access-Control-Allow-Origin', '*')
            self.end_headers()

            self.wfile.write(body.encode('utf-8'))

        except Exception as e:
            print(e)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header(
            'Access-Control-Allow-Origin', '*')
        self.send_header(
            'Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header(
            "Access-Control-Allow-Headers", "content-type")
        self.end_headers()


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
