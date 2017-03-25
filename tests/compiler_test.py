import unittest
import unittest.mock
import io
from collections import namedtuple

from stencil.compiler import Compiler


class CompilerTest(unittest.TestCase):
    def test_compile_constant(self):
        compiler = Compiler()

        function = compiler.compile("Fish")
        self.assertEqual(function(),
                         "Fish")

    def test_compile_variable(self):
        compiler = Compiler()

        function = compiler.compile("Hello {{ whom }}")
        self.assertEquals(function(whom="world"),
                          "Hello world")

    def test_compile_two_variables(self):
        compiler = Compiler()

        function = compiler.compile(
            "Hello {{ you }}, I'm {{ me }}. Nice to meet you")

        self.assertEquals(
            function(you="Tim", me="an optimised template"),
            "Hello Tim, I'm an optimised template. Nice to meet you")

    def test_compile_if_block(self):
        compiler = Compiler()

        function = compiler.compile(
            "Conditional: {% if True %}true{% endif %}")

        self.assertEquals(
            function(),
            "Conditional: true")

        function = compiler.compile(
            "Conditional: {% if False %}true{% endif %}")

        self.assertEquals(
            function(),
            "Conditional: ")

    def test_compile_if_expression(self):
        compiler = Compiler()

        function = compiler.compile(
            "{% if x < 10 %}x is less than 10{% endif %}")

        self.assertEquals(
            function(x=5),
            "x is less than 10")

        self.assertEquals(
            function(x=20),
            "")

    def test_compile_for_loop(self):
        compiler = Compiler()

        function = compiler.compile(
            "Let's count: {% for i in numbers %} {{ i }} {% endfor %} done")

        self.assertEquals(
            function(numbers=range(3)),
            "Let's count:  0  1  2  done"
        )

    def test_for_if_nested(self):
        compiler = Compiler()

        function = compiler.compile(
            "Odd numbers: {% for i in numbers %}{% if i % 2 %}"
            "{{ i }} "
            "{% endif %}{% endfor %}")

        self.assertEquals(
            function(numbers=range(10)),
            "Odd numbers: 1 3 5 7 9 ")

    def test_object_member(self):
        Employee = namedtuple('Employee', ['name'])

        compiler = Compiler()

        function = compiler.compile(
            "member: {{ employee.name }}")

        self.assertEquals(
            function(employee=Employee("alice")),
            "member: alice")

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
