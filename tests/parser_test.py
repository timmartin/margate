import unittest

from stencil.compiler import (Parser, Literal, Execution,
                              Sequence, IfBlock, parse_expression)


class ParserTest(unittest.TestCase):
    def test_simple_sequence(self):
        parser = Parser()

        sequence = parser.parse([Literal("Foo"),
                                 Literal("Bar")])

        self.assertEquals(2, len(sequence.elements))

    def test_parse_if_block(self):
        parser = Parser()

        sequence = parser.parse([Literal("Foo"),
                                 Execution("if True"),
                                 Literal("Bar"),
                                 Execution("endif"),
                                 Literal("Baz")])

        expected_sequence = Sequence()
        expected_sequence.add_element(Literal("Foo"))

        block = IfBlock(condition=True)
        block.sequence = Sequence()
        block.sequence.add_element(Literal("Bar"))
        expected_sequence.add_element(block)

        expected_sequence.add_element(Literal("Baz"))

        self.assertEquals(sequence.elements,
                          expected_sequence.elements)

    def test_parse_if_expressions(self):
        foo = parse_expression(["if", "True"])
        self.assertEquals(True,
                          foo)
