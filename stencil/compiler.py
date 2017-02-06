"""
Compiler
"""

import re
import io
from bytecode import Bytecode, Instr

from . import parser, block_parser, code_generation


class Parser:
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
                if self._starts_subsequence(token):
                    node = parser.parse_expression(
                        re.split(r'\s+',
                                 token.expression.strip()))

                    if isinstance(node, parser.IfNode):
                        block = code_generation.IfBlock(node.expression)
                    elif isinstance(node, parser.ForNode):
                        block = code_generation.ForBlock(node)

                    self._parse_into_sequence(block.sequence,
                                              token_iter,
                                              self._end_if_sequence)
                    sequence.add_element(block)
                else:
                    sequence.add_element(token)
        except StopIteration:
            return

    def _starts_subsequence(self, token):
        return isinstance(token, Execution)

    def _end_if_sequence(self, token):
        return isinstance(token, Execution)


class Compiler:
    def compile(self, source):
        bytecode = self._make_bytecode(source)

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

    def _make_bytecode(self, source):
        instructions = []
        symbol_table = {
            "write_func": io.StringIO.write
        }

        parser = Parser()
        sequence = parser.parse(self._get_chunks(source))

        for item in sequence.elements:
            instructions += item.make_bytecode(symbol_table)

        bytecode = Bytecode(instructions + [Instr("LOAD_CONST", None),
                                            Instr("RETURN_VALUE")])
        return bytecode.to_code()


class Execution:
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return "<Execution: %r>" % self.expression
