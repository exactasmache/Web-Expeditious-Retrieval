__author__ = "Marcelo Bianchetti"
__email__ = "mbianchetti@dc.uba.ar"

import os
import re
import unittest
from server.indexHandler import Multiindex


TESTPATH = os.path.join(os.getcwd(), "testindex/")


class TestMultiindex(unittest.TestCase):
    def setUp(self):
        self.indexname = "Testing"
        self.index = Multiindex(TESTPATH)

    def tearDown(self):
        self.index.remove_index()

    def test_index_creation(self):
        assert self.index is not None

        self.index.createIx(self.indexname)
        assert self.index.available(self.indexname) is True

        self.index.remove_index(self.indexname)
        assert self.index.available(self.indexname) is False


if __name__ == '__main__':
    unittest.main()
