import unittest

from stencil.compiler import (Parser, LiteralState, ExecutionState,
                              Sequence, IfBlock)


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
        expected_sequence.add_element(IfBlock())
        expected_sequence.add_element(LiteralState("Baz"))

        self.assertEquals(sequence.elements,
                          expected_sequence.elements)
