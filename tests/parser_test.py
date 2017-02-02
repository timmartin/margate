import unittest

from stencil.compiler import (Parser, LiteralState, ExecutionState,
                              Sequence, IfBlock, parse_expression)


class ParserTest(unittest.TestCase):
    def test_simple_sequence(self):
        parser = Parser()

        sequence = parser.parse([LiteralState("Foo"),
                                 LiteralState("Bar")])

        self.assertEquals(2, len(sequence.elements))

    def test_parse_if_block(self):
        parser = Parser()

        sequence = parser.parse([LiteralState("Foo"),
                                 ExecutionState("if True"),
                                 LiteralState("Bar"),
                                 ExecutionState("endif"),
                                 LiteralState("Baz")])

        expected_sequence = Sequence()
        expected_sequence.add_element(LiteralState("Foo"))

        block = IfBlock(condition=True)
        block.sequence = Sequence()
        block.sequence.add_element(LiteralState("Bar"))
        expected_sequence.add_element(block)

        expected_sequence.add_element(LiteralState("Baz"))

        self.assertEquals(sequence.elements,
                          expected_sequence.elements)

    def test_parse_if_expressions(self):
        foo = parse_expression(["if", "True"])
        self.assertEquals(True,
                          foo)
