__author__ = "Marcelo Bianchetti"
__version__ = "1.0.0"
__email__ = "mbianchetti@dc.uba.ar"
__status__ = "Testing"


class Render():
    """
      A class to render responses.
      For now it returns just a harcoded html for the list.
    """

    def build_list_response(self, res: list = None):
        """
          Creates an html response with the listed results

          :param res: list of results of the searching.
          Every element must be a dictionary containing an url and a title.

          Returns the html code.
          :rtype: str
        """

        body = """<!DOCTYPE html>
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
