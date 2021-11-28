from whoosh import index
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage


class Multiindex():
    """
      Handles the index. Allows multiple indices in the same storage.
      Supports creating indexes, adding documents, and searching for words.

      The indices have only one schema allowed composed by an url, a title
      and a content. The content is not stored.
    """

    def __init__(self, path):
        """:param path: a path to an existent directory."""
        self._path = path
        self._storage = FileStorage(self._path)
        self._schema = Schema(
            url=TEXT(stored=True),
            title=TEXT(stored=True),
            content=TEXT
        )

    def createIx(self, username):
        """
          Creates an index in the storage path.

          :param username: name of the index to create or replace.
        """
        try:
            create_in(self._path, self._schema, indexname=username)
        except Exception as e:
            print(e)
            return False
        return True

    def add_document(self, username, url, title, content):
        """
          Creates an index in the storage path.

          :param username: name of the index.
          :param url: page url.
          :param title: page title.
          :param content: text to search from.

          Returns True if the document already exists or if
          it was added to the index.
          :rtype: bool
        """
        try:
            exists = self._storage.index_exists(username)

            if not exists:
                self.createIx(username)
            else:
                # Checks for the existence of the url in the index
                index = self._storage.open_index(username)
                with index.searcher() as searcher:
                    query = QueryParser("url", index.schema).parse(url)
                    results = searcher.search(query, limit=1)
                    if len(results) > 0:
                        return True

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
