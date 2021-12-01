__author__ = "Marcelo Bianchetti"
__email__ = "mbianchetti@dc.uba.ar"

import os
import unittest
from server.indexHandler import Multiindex


TESTPATH = os.path.join(os.getcwd(), "testindex/")
INDEXNAME = "Testing"


class TestMultiindex(unittest.TestCase):
    def setUp(self):
        """
          Creates a multiindex of name INDEXNAME within the directory
          TESTPATH.
        """
        self.indexname = INDEXNAME
        self.index = Multiindex(TESTPATH)

    def tearDown(self):
        """Removes the multiindex, i.e., the whole directory."""
        self.index.remove_index()

    def test_index_creation(self):
        """
          Checks if the multiindex was properly created.
          Creates an index within the multiindex.
          Checks its availability and, after removing it, checks its
          unavailability.
        """
        assert self.index is not None

        self.index.createIx(self.indexname)
        assert self.index.available(self.indexname) is True

        self.index.remove_index(self.indexname)
        assert self.index.available(self.indexname) is False


if __name__ == '__main__':
    unittest.main()
