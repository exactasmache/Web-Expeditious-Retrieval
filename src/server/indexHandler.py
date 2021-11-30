from whoosh import index
from whoosh.index import create_in
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

    def __init__(self, path: str):
        """:param path: a path to an existent directory."""
        self._path = path
        self._storage = FileStorage(self._path)
        self._schema = Schema(
            url=TEXT(stored=True),
            title=TEXT(stored=True),
            content=TEXT
        )

    def available(self, username=None):
        """
          Checks for the multiindex availability. If an username is
          given, then it also check for the particular index
          availability

          :param username: name of the index from which you want
          to check availability.

          :rtype: bool
        """
        ret = self._path is not None and \
            self._storage is not None and \
            self._schema is not None

        if username is not None:
            return ret and self._storage.index_exists(username)

        return ret

    def createIx(self, username: str, ovewrite: bool = False):
        """
          Creates an index in the storage path.

          :param username: name of the index to create or replace.
          :param ovewrite: indicates if the index must be overwritten.

          Returns True if the index was created, otherwise False.
          :rtype: bool
        """
        if not ovewrite and self._storage.index_exists(username):
            return False

        try:
            create_in(self._path, self._schema, indexname=username)
        except Exception as e:
            print(e)
            return False
        return True

    def add_document(self, username: str, url: str, title: str, content: str):
        """
          Adds a document to the index named username located at the storage
          path.

          :param username: name of the index.
          :param url: page url.
          :param title: page title.
          :param content: text to search from.

          Returns True if the document already exists or if
          it was added to the index, otherwise False.
          :rtype: bool
        """
        exists = self._storage.index_exists(username)

        if not exists:
            created = self.createIx(username)
            if not created:
                return False

        else:
            # Checks for the existence of the url in the index
            try:
                index = self._storage.open_index(username)
                with index.searcher() as searcher:
                    query = QueryParser("url", index.schema).parse(url)
                    results = searcher.search(query, limit=1)
                    if len(results) > 0:
                        return True
            except Exception as e:
                print(e)
                return False

            finally:
                index.close()

        try:
            index = self._storage.open_index(username)
            writer = index.writer()
            writer.add_document(url=url, title=title, content=content)
            writer.commit()

        except Exception as e:
            if writer:
                writer.cancel()
            print(e)
            return False

        finally:
            index.close()

        return True

    def search_word(self, username: str, word: str):
        """
          Searches for the word whithin the documents stored in the index
          named username located at the storage path.

          :param username: name of the index.
          :param word: sentence to search.

          Returns the list of diccionaries
          {title: title, url: url}
          for each document containing the word.
          Otherwise it returns an empty list.
          :rtype: list
        """
        exists = self._storage.index_exists(username)

        if not exists:
            return []

        try:
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
            return []

        finally:
            index.close()
