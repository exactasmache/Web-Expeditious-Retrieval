
from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
from pprint import pformat
import json
from indexHandler import Multiindex


class WERRequestHandler(BaseHTTPRequestHandler):
    """This class handles HTTP request for the WER service."""
    _ix_path = 'indexdir'
    _index = Multiindex(_ix_path)
    _default_usr = 'Anonimous'

    def error(self, code=500, message=None):
        self.send_response(code)

        if message:
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(message.encode('utf-8'))

        else:
            self.end_headers()

    def do_GET(self):
        """Handles GET requests."""
        path = self.path

        if (not isinstance(path, bytes) and not isinstance(path, str)):
            return self.error(442)

        if path.startswith('/search'):
            subpaths = path.split('/')

            if len(subpaths) != 3:
                return self.error(400)

            word = parse_qs(subpaths[-1])

            if 'q' not in word or word['q'] == []\
                    or len(word['q']) > 1:
                return self.error(400)

            print("Searching", word['q'][0])
            try:
                res = self._index.search_word(self._default_usr, "hola")
            except Exception as e:
                print(e)
                return self.error(500)

            print("Result:", [r for r in res])
            body = f"<h1>Sorry, no page was found using that word.</h1>"
            if res:
                body = "<ol>"
                for r in res:
                    body += f"<li>{r}</li>"
                body = "</ol>"

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(body.encode('utf-8'))
        else:
            self.error(403)

    def do_POST(self):
        """Handles POST requests."""
        ctype, _ = parse_header(self.headers.get('content-type'))

        try:
            postvars = {}
            if ctype == 'application/json':
                length = int(self.headers.get('content-length'))
                bytes_val = self.rfile.read(length)
                my_json = bytes_val.decode('utf8')
                postvars = json.loads(my_json)
                print(type(postvars))
                if 'url' not in postvars.keys() or \
                        'text' not in postvars.keys():
                    self.error(400)

            try:
                print(postvars)
                # TODO: Store the texts in the index.
                # print(pformat(postvars))

                data = {'message': 'Saved'}
                body = json.dumps(data)

                self.send_response(200)
                self.send_header('Access-Control-Allow-Credentials', 'true')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body.encode('utf-8'))

            except Exception as e:
                print(e)
                self.send_response(500)
                self.end_headers()

        except Exception as e:
            print(e)
            self.error(500)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "content-type")
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
