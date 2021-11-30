
from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
from pprint import pformat
import json

from indexHandler import Multiindex


def build_response(res: list = None):
    """
      Creates an html response with the listed results

      :param res: list of results of the searching.
      Every element must be a dictionary containing an url and a title.

      Returns the html code.
      :rtype: str
    """

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

    def do_return_error(self, code: int = 500, message: str = None):
        """Returns an error response

          :param code: error code.
          :param message: error message.
        """
        self.send_response(code)

        if message:
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(message.encode('utf-8'))

        else:
            self.end_headers()

    def do_available(self):
        """
          Handles the /search request.

          Returns true if the server is running, and if /index is appended to
          the path, it also checks whether the index exists.
        """
        path = self.path
        subpaths = path.split('/')

        if len(subpaths) not in [2, 3]:
            self.do_return_error(code=400)
            pass

        msg = "Resource not available."
        ret = self._index is not None
        if subpaths[-1] == 'index':
            ret = ret and self._index.available(self._default_usr)
            msg = "Index not available."
        else:
            ret = ret and self._index.available()

        if ret:
            self.send_response(200)

        else:
            body = {'message': msg}
            self.do_return_error(code=503)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(body.encode('utf-8'))

    def do_search(self):
        """Handles the /search request."""
        path = self.path
        subpaths = path.split('/')

        if len(subpaths) != 3:
            self.do_return_error(code=400)
            pass

        word = parse_qs(subpaths[-1])
        if 'q' not in word or word['q'] == []\
                or len(word['q']) > 1:
            self.do_return_error(code=400)
            pass

        print(" > Searching", word['q'][0])
        try:
            res = self._index.search_word(self._default_usr, word['q'][0])
            if res is False:
                self.do_return_error(code=500)
                pass

        except Exception as e:
            print(e)
            self.do_return_error(code=500)
            pass

        print("Result:", [r for r in res])
        body = build_response(res)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def do_store(self, postvars: dict):
        """Saves the document in the index _index

          :param postvars: dictionary with the url title and text of the
          document to be added.
        """
        res = self._index.add_document(
            self._default_usr, postvars['url'],
            postvars['title'],
            postvars['text']
        )
        if not res:
            self.do_return_error(code=500)
            pass

        data = {'message': 'Saved'}
        body = json.dumps(data)

        self.send_response(200)
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def do_GET(self):
        """Handles GET requests."""
        path = self.path

        if (not isinstance(path, bytes) and not isinstance(path, str)):
            self.do_return_error(code=442)
            pass

        if path.startswith('/available'):
            self.do_available()

        if path.startswith('/search'):
            self.do_search()

        elif path.startswith('/favicon.ico'):
            self.send_response(200)
            self.end_headers()

        else:
            self.do_return_error(code=403)

    def do_POST(self):
        """Handles POST requests."""
        ctype, _ = parse_header(self.headers.get('content-type'))
        path = self.path
        postvars = {}

        if ctype == 'application/json':
            try:
                length = int(self.headers.get('content-length'))
                bytes_val = self.rfile.read(length)
                my_json = bytes_val.decode('utf8')
                postvars = json.loads(my_json)
            except Exception as e:
                print(e)
                self.do_return_error(code=500)

            if path.startswith('/store'):
                if not postvars or 'url' not in postvars.keys() or \
                        'text' not in postvars.keys() or \
                        'title' not in postvars.keys():
                    self.do_return_error(code=400)
                    pass
                try:
                    self.do_store(postvars)
                except Exception as e:
                    print(e)
                    self.do_return_error(code=500)

            if path.startswith('/newindex'):
                if self._index.createIx(self._default_usr):
                    self.send_response(201)
                else:
                    self.send_response(200)
                self.end_headers()
        else:
            self.do_return_error(code=406)

    def do_OPTIONS(self):
        """Handles OPTIONS request."""
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
