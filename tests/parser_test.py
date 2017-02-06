import unittest

from stencil.parser import parse_expression, IfNode, ForNode
from stencil.compiler import Parser
from stencil.code_generation import (Literal, Sequence, IfBlock,
                                     ForBlock, Execution)


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

    def test_parse_for_loop(self):
        parser = Parser()

        sequence = parser.parse([Execution("for x in things"),
                                 Literal("bar"),
                                 Execution("endfor")])

        expected_sequence = Sequence()
        block = ForBlock(ForNode('x', 'things'))
        block.sequence.add_element(Literal("bar"))
        expected_sequence.add_element(block)

        self.assertEquals(sequence.elements,
                          expected_sequence.elements)

    def test_parser(self):
        foo = parse_expression(["if", "True"])
        self.assertEqual(foo, IfNode(True))

        foo = parse_expression(["for", "var", "in", "collection"])
        self.assertEqual(foo, ("var", "collection"))
