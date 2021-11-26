from whoosh import index
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage


class Multiindex():
    def __init__(self, path):
        self._path = path
        self._storage = FileStorage(self._path)
        self._schema = Schema(
          url=TEXT(stored=True),
          title=TEXT(stored=True),
          content=TEXT
        )

    def _createIx(self, username):
        try:
            create_in(self._path, self._schema, indexname=username)
        except Exception as e:
            print(e)
            return False
        return True

    def add_document(self, username, url, title, content):
        try:
            exists = self._storage.index_exists(username)

            if not exists:
                self._createIx(username)

            index = self._storage.open_index(username)

            writer = index.writer()
            writer.add_document(url=url, title=title, content=content)
            writer.commit()

        except Exception as e:
            print(e)
            return False

        return True

    def search_word(self, username, word):
        try:
            exists = self._storage.index_exists(username)

            if not exists:
                return []

            index = self._storage.open_index(username)
            with index.searcher() as searcher:
                query = QueryParser("content", index.schema).parse(word)
                results = searcher.search(query, limit=None)
                return [{
                  "url": res["url"],
                  "title": res["title"]
                } for res in results]
        except Exception as e:
            print(e)
            return False
