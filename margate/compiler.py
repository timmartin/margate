"""
Compiler
"""

import re
import io
from bytecode import Bytecode, Instr

from . import parser, block_parser, code_generation


class UnsupportedElementException(Exception):
    pass


class Parser:
    """The Parser is responsible for turning a template in "tokenised"
    form into a tree structure from which it is straightforward to
    generate bytecode.

    The input is in the form of a flat list of atomic elements of the
    template, where literal text (of any length) is a single element,
    and a {% %} or {{ }} expression is a single element.

    Figuring out nesting of starting and ending of loops happens
    within the parser.

    """

    def __init__(self, template_locator=None):

        def _get_related_template(template_name):
            template = template_locator.find_template(template_name)
            if not template:
                raise FileNotFoundError()
            with open(template) as template_file:
                compiler = Compiler(template_locator)
                return compiler._get_chunks(template_file.read())

        self._sub_template_locator = _get_related_template

    def parse(self, tokens):
        sequence = code_generation.Sequence()

        self._parse_into_sequence(sequence, tokens)

        return sequence

    def _parse_into_sequence(self, sequence, tokens,
                             termination_condition=None):
        token_iter = iter(tokens)

        try:
            while True:
                token = next(token_iter)
                if termination_condition and termination_condition(token):
                    return

                if isinstance(token, code_generation.Execution):
                    # An execution node always starts a subsequence
                    # (i.e. a node in the tree with its own
                    # children). Since we've ruled out the case where
                    # this is the termination of an existing block,
                    # any Execution node is the start of a new block.
                    block = self._parse_subsequence(token, token_iter)
                    sequence.add_element(block)
                else:
                    sequence.add_element(token)
        except StopIteration:
            return

    def _parse_subsequence(self, token, token_iter):
        node = parser.parse_expression(
            re.split(r'\s+',
                     token.expression.strip()))

        if isinstance(node, parser.IfNode):
            block = code_generation.IfBlock(node.expression)
            inner_termination_condition = self._end_sequence("endif")
        elif isinstance(node, parser.ForNode):
            block = code_generation.ForBlock(node)
            inner_termination_condition = self._end_sequence("endfor")
        elif isinstance(node, parser.ExtendsNode):
            if self._sub_template_locator is None:
                raise UnsupportedElementException(
                    "Parser is not configured to support "
                    "extending other templates")

            content = self._sub_template_locator(
                node.template_name)
            parsed = self.parse(content)
            block = code_generation.ExtendsBlock(parsed)
            inner_termination_condition = None
        elif isinstance(node, parser.BlockNode):
            block = code_generation.ReplaceableBlock(
                node.block_name)
            inner_termination_condition = self._end_sequence("endblock")
        else:
            raise Exception("Unrecognised block type")

        self._parse_into_sequence(block.sequence,
                                  token_iter,
                                  inner_termination_condition)

        return block

    def _end_sequence(self, end_token):
        def is_end_token(token):
            return (isinstance(token, code_generation.Execution)
                    and token.expression == end_token)

        return is_end_token


class TemplateLocator:
    def find_template(self, template_name):
        pass


class Compiler:
    """The Compiler takes a template in string form and returns bytecode
    that implements the template.
    """

    def __init__(self, template_locator=None):
        if template_locator is None:
            template_locator = TemplateLocator()

        self._template_locator = template_locator

    def compile(self, source):
        """Compile the template source code into a callable function."""
        bytecode = self._make_bytecode(source, self._template_locator)

        def inner(**local_scope):
            local_scope["_output"] = io.StringIO()
            exec(bytecode, {}, local_scope)
            return local_scope['_output'].getvalue()

        return inner

    def _get_chunks(self, source):
        state = block_parser.LiteralState(source)

        while state:
            match = re.search(r"\{\{|\}\}|\{%|%\}",
                              state.text)
            if match is None:
                (state, chunk) = state.accept_end_input()
            else:
                separator = match.group(0)

                if separator == "{{":
                    action = state.accept_open_expression
                elif separator == "}}":
                    action = state.accept_close_expression
                elif separator == "{%":
                    action = state.accept_open_execution
                elif separator == "%}":
                    action = state.accept_close_execution
                else:
                    raise Exception("Unrecognised separator")

                (state, chunk) = action(match.start(0),
                                        len(match.group(0)))

            yield chunk

    def _make_bytecode(self, source, template_locator):
        instructions = []
        symbol_table = {
            "write_func": io.StringIO.write
        }

        parser = Parser(self._template_locator)
        sequence = parser.parse(self._get_chunks(source))

        for item in sequence.elements:
            instructions += item.make_bytecode(symbol_table)

        bytecode = Bytecode(instructions + [Instr("LOAD_CONST", None),
                                            Instr("RETURN_VALUE")])
        return bytecode.to_code()
