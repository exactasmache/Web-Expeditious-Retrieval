from whoosh import index
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage


class Multiindex():
    def __init__(self, path):
        self._path = path
        self._storage = FileStorage(self._path)
        self._schema = Schema(url=TEXT(stored=True), content=TEXT)

    def _createIx(self, username):
        create_in(self._path, self._schema, indexname=username)

    def add_document(self, username, url, content):
        exists = self._storage.index_exists(username)

        if not exists:
            self._createIx(username)

        index = self._storage.open_index(username)

        writer = index.writer()
        writer.add_document(url=url, content=content)
        writer.commit()

    def search_word(self, username, word):
        exists = self._storage.index_exists(username)

        if not exists:
            return []

        index = self._storage.open_index(username)
        with index.searcher() as searcher:
            query = QueryParser("content", index.schema).parse(word)
            results = searcher.search(query)
            return (res for res in results)
