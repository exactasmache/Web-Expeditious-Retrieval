
from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
from pprint import pformat
import json
from indexHandler import Multiindex


def build_response(res):
    body = """ <!DOCTYPE html>
              <html>
                <head>
                  <title>Results</title>
                </head>
                <body>
                <h1>Results</h1>
            """
    if not res:
        body += "<p>Sorry, no page was found using that word.</p>"

    else:
        body += "<ul>"
        for r in res:
            body += f'<a href=\"{r["url"]}\"><li>{r["title"]}</li></a>'
        body += "</ul>"

    body += """</body>
            </html>
          """
    return body


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

            print(" > Searching", word['q'][0])
            try:
                res = self._index.search_word(self._default_usr, word['q'][0])
                if res is False:
                    return self.error(500)

            except Exception as e:
                print(e)
                return self.error(500)

            print("Result:", [r for r in res])
            body = build_response(res)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(body.encode('utf-8'))

        elif path.startswith('/favicon.ico'):
            self.send_response(200)
            self.end_headers()

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

                if not postvars or 'url' not in postvars.keys() or \
                        'text' not in postvars.keys() or \
                        'title' not in postvars.keys():
                    self.error(400)

            try:
                res = self._index.add_document(
                    self._default_usr, postvars['url'],
                    postvars['title'],
                    postvars['text']
                )

                if not res:
                    return self.error(500)

                data = {'message': 'Saved'}
                body = json.dumps(data)

                self.send_response(200)
                self.send_header('Access-Control-Allow-Credentials', 'true')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body.encode('utf-8'))

            except Exception as e:
                print(e)
                self.error(500)

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
