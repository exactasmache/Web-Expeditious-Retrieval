__author__ = "Marcelo Bianchetti"
__version__ = "1.0.0"
__email__ = "mbianchetti@dc.uba.ar"
__status__ = "Testing"

import os
import shutil

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
        """
          :param path: a path to a directory. If the directory does not exist,
          it is created.
        """
        self._path = path
        if not os.path.isdir(self._path):
            os.mkdir(self._path)

        self._storage = FileStorage(self._path)
        self._schema = Schema(
            url=TEXT(stored=True),
            title=TEXT(stored=True),
            content=TEXT
        )

    def available(self, indexname=None):
        """
          Checks for the multiindex availability. If an indexname is
          given, then it also check for the particular index
          availability

          :param indexname: name of the index from which you want
          to check availability.

          :rtype: bool
        """
        ret = self._path is not None and \
            self._storage is not None and \
            self._schema is not None

        if indexname is not None:
            return ret and self._storage.index_exists(indexname)

        return ret

    def createIx(self, indexname: str, ovewrite: bool = False):
        """
          Creates an index in the storage path.

          :param indexname: name of the index to create or replace.
          :param ovewrite: indicates if the index must be overwritten.

          Returns True if the index was created, otherwise False.
          :rtype: bool
        """
        if not ovewrite and self._storage.index_exists(indexname):
            return False

        try:
            create_in(self._path, self._schema, indexname=indexname)
        except Exception as e:
            print(e)
            return False
        return True

    def add_document(self, indexname: str, url: str, title: str, content: str):
        """
          Adds a document to the index named indexname located at the storage
          path.

          :param indexname: name of the index.
          :param url: page url.
          :param title: page title.
          :param content: text to search from.

          Returns True if the document already exists or if
          it was added to the index, otherwise False.
          :rtype: bool
        """
        exists = self._storage.index_exists(indexname)

        if not exists:
            created = self.createIx(indexname)
            if not created:
                return False

        else:
            # Checks for the existence of the url in the index
            try:
                index = self._storage.open_index(indexname)
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
            index = self._storage.open_index(indexname)
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

    def search_word(self, indexname: str, word: str):
        """
          Searches for the word whithin the documents stored in the index
          named indexname located at the storage path.

          :param indexname: name of the index.
          :param word: sentence to search.

          Returns the list of diccionaries
          {title: title, url: url}
          for each document containing the word.
          Otherwise it returns an empty list.
          :rtype: list
        """
        exists = self._storage.index_exists(indexname)

        if not exists:
            return []

        try:
            index = self._storage.open_index(indexname)
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

    def remove_index(self, indexname=None):
        """
          Removes all the files in the subtree self._path that starts with
          indexname or f'_{indexname}'. If no indexname is given, then it
          removes the whole index directory.

          :param indexname: name of the index to remove.
        """
        dir = self._path
        if indexname is not None:
            exists = self._storage.index_exists(indexname)

            if exists:
                for file in os.listdir(dir):
                    if file.startswith(indexname) or \
                            file.startswith(f'_{indexname}'):

                        path = os.path.join(dir, file)
                        try:
                            shutil.rmtree(path)
                        except OSError:
                            os.remove(path)

        elif os.path.isdir(dir):
            for file in os.listdir(dir):
                path = os.path.join(dir, file)
                try:
                    shutil.rmtree(path)
                except OSError:
                    os.remove(path)
            print("remove", dir)
            os.rmdir(dir)
