import unittest
import unittest.mock
import io
from collections import namedtuple

from margate.compiler import Compiler


class CompilerTest(unittest.TestCase):

    def test_extend_template(self):
        template_locator = unittest.mock.MagicMock()
        template_locator.find_template.return_value = '/wherever/foo.html'

        mock_file = io.StringIO("Title: {% block title %}{% endblock %}")

        mock_open = unittest.mock.MagicMock(return_value=mock_file)

        with unittest.mock.patch('builtins.open', mock_open):
            compiler = Compiler(template_locator)

            function = compiler.compile(
                '{% extends "base.html" %}'
                '{% block title %}'
                'The title'
                '{% endblock %}')

        self.assertEquals(
            function(),
            "Title: The title")
