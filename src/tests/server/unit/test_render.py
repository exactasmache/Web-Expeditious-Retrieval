__author__ = "Marcelo Bianchetti"
__email__ = "mbianchetti@dc.uba.ar"

import re
import unittest
from server.render import Render


class TestRender(unittest.TestCase):
    def setUp(self):
        self.render = Render()

    def tearDown(self):
        self.render = None

    def test_render_creation(self):
        assert self.render is not None

    def test_render_builder_empty(self):
        """
          Checks the html generated when receiving an empty list.
          We should check whether it is a valid html.
        """
        empty_list = []

        ret = self.render.build_list_response(empty_list)
        html = "<!DOCTYPE html>" \
               "<html><head><title>Results</title></head>" \
               "<body><h1>Results</h1>" \
               "<p>Sorry, no page was found using that word.</p>" \
               "</body></html>"

        ret = re.sub('\s+', ' ', ret.strip())
        ret = re.sub('> <', '><', ret)

        assert ret == html

    def test_render_builder_one(self):
        """
          Checks the html generated when receiving a list with only one
          element. We should check whether it is a valid html.
        """
        elem = {
            'url': "http://localhost:8888",
            'title': "Server"
          }
        one_element_list = [elem]

        ret = self.render.build_list_response(one_element_list)
        html = "<!DOCTYPE html>" \
               "<html><head><title>Results</title></head>" \
               "<body><h1>Results</h1>" \
               "<ul>"\
               f'<a href=\"{elem["url"]}\"><li>{elem["title"]}</li></a>'\
               "</ul>"\
               "</body></html>"

        ret = re.sub('\s+', ' ', ret.strip())
        ret = re.sub('> <', '><', ret)

        assert ret == html

    def test_render_builder_one(self):
        """
          Checks the html generated when receiving a list with more than
          one element. We should check whether it is a valid html.
        """
        elem1 = {
            'url': "http://localhost:8888",
            'title': "Server"
          }
        elem2 = {
            'url': "http://localhost:8888",
            'title': "Server"
          }
        elem3 = {
            'url': "http://localhost:8888",
            'title': "Server"
          }
        one_element_list = [elem1, elem2, elem3]

        ret = self.render.build_list_response(one_element_list)
        html = "<!DOCTYPE html>" \
               "<html><head><title>Results</title></head>" \
               "<body><h1>Results</h1>" \
               "<ul>"\
               f'<a href=\"{elem1["url"]}\"><li>{elem1["title"]}</li></a>'\
               f'<a href=\"{elem2["url"]}\"><li>{elem2["title"]}</li></a>'\
               f'<a href=\"{elem3["url"]}\"><li>{elem3["title"]}</li></a>'\
               "</ul>"\
               "</body></html>"

        ret = re.sub('\s+', ' ', ret.strip())
        ret = re.sub('> <', '><', ret)

        assert ret == html


if __name__ == '__main__':
    unittest.main()
