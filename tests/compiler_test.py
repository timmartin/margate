import unittest

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