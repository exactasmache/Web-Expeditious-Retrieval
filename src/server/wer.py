__author__ = "Marcelo Bianchetti"
__version__ = "1.0.0"
__email__ = "mbianchetti@dc.uba.ar"
__status__ = "Testing"

from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
from pprint import pformat
import json
from functools import partial

from indexHandler import Multiindex
from render import Render

import base64

"""
  We are using a quite simple authentication schema, for which it is enough
  just to have some credentials shared between the server and the client.

  We assume we do not want to ask the client to get logged in before starting
  using the extension. In which case we should receive a pair username/password
  and return a kind of token, which should be stored in the client. Since we do
  not distinguish among clients we are assuming that step is already done, and
  we have the same token for every client. The user:password that generates the
  token is test:test, and the token is the one stored as CREDENTIALS.

  We should use an external library such as auth0 or a more powerful framework,
  such as Flask or Django.

  Note that we are not using HTTPS neither, so the security is almost
  non-existent.
"""
USER = 'test'
PASS = 'test'
B64 = base64.b64encode(f"{USER}:{PASS}".encode("UTF-8"))
CREDENTIALS = f'Basic {B64.decode(encoding="UTF-8")}'


class WERRequestHandler(BaseHTTPRequestHandler):
    """This class handles HTTP request for the WER service."""

    def __init__(self, ix_path, default_idx, *args, **kwargs):
        self._ix_path = ix_path
        self._index = Multiindex(self._ix_path)
        self._default_idx = default_idx
        self._render = Render()

        # BaseHTTPRequestHandler calls do_GET **inside** __init__ !!!
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

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
        pass

    def do_available(self):
        """
          Handles the /search request.

          Returns true if the server is running and,, if '/index' is appended
          to the path, it also checks whether the index exists.
        """
        path = self.path
        subpaths = path.split('/')

        if len(subpaths) not in [2, 3]:
            self.do_return_error(code=400)
            pass

        msg = "Index available."
        status = "AVAILABLE"
        ret = self._index is not None
        if subpaths[-1] == 'index':
            ret = ret and self._index.available(self._default_idx)
        else:
            ret = ret and self._index.available()

        if not ret:
            msg = "Index not available."
            status = "UNAVAILABLE"

        body = json.dumps({'message': msg, 'status': status})
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))
        pass

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
            res = self._index.search_word(self._default_idx, word['q'][0])
            if res is False:
                self.do_return_error(code=500)
                pass

        except Exception as e:
            print(e)
            self.do_return_error(code=500)
            pass

        print("Result:", [r for r in res])
        body = self._render.build_list_response(res)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))
        pass

    def do_store(self, postvars: dict):
        """Saves the document in the index _index

          :param postvars: dictionary with the url title and text of the
          document to be added.
        """
        res = self._index.add_document(
            self._default_idx, postvars['url'],
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
        pass

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        """Handles GET requests."""
        path = self.path
        if (not isinstance(path, bytes) and not isinstance(path, str)):
            self.do_return_error(code=442)
            pass

        auth = self.headers.get('Authorization')

        if auth is None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received'.encode('utf-8'))
            pass

        elif auth == CREDENTIALS:
            if path.startswith('/available'):
                self.do_available()

            elif path.startswith('/search'):
                self.do_search()

            elif path.startswith('/favicon.ico'):
                self.send_response(200)
                self.end_headers()
                pass

            else:
                self.do_return_error(code=403)
        else:
            self.do_AUTHHEAD()
            self.wfile.write(auth.encode('utf-8'))
            self.wfile.write('not authenticated'.encode('utf-8'))
            pass

    def do_POST(self):
        """Handles POST requests."""
        ctype, _ = parse_header(self.headers.get('content-type'))
        path = self.path
        postvars = {}

        auth = self.headers.get('Authorization')

        if auth is None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received'.encode('utf-8'))
            pass

        elif auth == CREDENTIALS:
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
                    if self._index.createIx(self._default_idx):
                        self.send_response(201)
                    else:
                        self.send_response(200)
                    self.end_headers()
                    pass
            else:
                self.do_return_error(code=406)
        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.get('Authorization'))
            self.wfile.write('not authenticated'.encode('utf-8'))
            pass

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

    indexDir = 'indexdir'
    defaultIdx = 'Anonimous'

    # partially applies the first two arguments to the Handler
    handler = partial(WERRequestHandler, indexDir, defaultIdx)

    # .. then pass it to HTTPHandler as normal:
    server = HTTPServer((hostName, serverPort), handler)
    print(f"Server started at {hostName}:{serverPort}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    print("Server stopped")
