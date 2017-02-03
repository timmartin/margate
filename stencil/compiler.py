"""
Compiler
"""

import re
import io
from bytecode import Bytecode, Instr


def parse_expression(expression):
    from funcparserlib.parser import a, skip

    def true_val(x): return True

    def false_val(x): return False

    boolean = (a('True') >> true_val) | (a('False') >> false_val)

    if_expression = skip(a('if')) + boolean
    return if_expression.parse(expression)


class LiteralState:
    def __init__(self, text):
        self.text = text

    def __eq__(self, other):
        if not isinstance(other, LiteralState):
            return False

        return self.text == other.text

    def __repr__(self):
        return "<LiteralState %r>" % self.text

    def accept_open_expression(self, offset, length):
        return (ExpressionState(self.text[offset + length:]),
                Literal(self.text[:offset]))

    def accept_open_execution(self, offset, length):
        return (ExecutionState(self.text[offset + length:]),
                Literal(self.text[:offset]))

    def accept_close_expression(self, offset, length):
        raise Exception("Syntax error")

    def accept_close_execution(self, offset, length):
        raise Exception("Syntax error")

    def accept_end_input(self):
        return (None, Literal(self.text))


class ExecutionState:
    def __init__(self, text):
        self.text = text

    def accept_open_expression(self, offset, length):
        raise Exception("Syntax error")

    def accept_open_execution(self, offset, length):
        raise Exception("Syntax error")

    def accept_close_expression(self, offset, length):
        raise Exception("Syntax error")

    def accept_close_execution(self, offset, length):
        return (LiteralState(self.text[offset + length:]),
                Execution(self.text[:offset]))

    def accept_end_input(self):
        raise Exception("Syntax error")


class ExpressionState:
    def __init__(self, text):
        self.text = text

    def accept_open_expression(self, offset, length):
        raise Exception("Syntax error: opened expression inside expression")

    def accept_open_execution(self, offset, length):
        raise Exception("Syntax error")

    def accept_close_execution(self, offset, length):
        raise Exception("Syntax error")

    def accept_close_expression(self, offset, length):
        return (LiteralState(self.text[offset + length:]),
                VariableExpansion(self.text[:offset].strip()))

    def accept_end_input(self):
        raise Exception("Syntax error")


class Sequence:
    def __init__(self):
        self.elements = []

    def __eq__(self, other):
        if not isinstance(other, Sequence):
            return False

        return self.elements == other.elements

    def __repr__(self):
        return "<Sequence %r>" % self.elements

    def add_element(self, element):
        self.elements.append(element)


class Parser:
    def parse(self, tokens):
        sequence = Sequence()

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
                    block = IfBlock(parse_expression(re.split(r'\s+',
                                                              token.text)))
                    self._parse_into_sequence(block.sequence,
                                              token_iter,
                                              self._end_if_sequence)
                    sequence.add_element(block)
                else:
                    sequence.add_element(token)
        except StopIteration:
            return

    def _starts_subsequence(self, token):
        return isinstance(token, ExecutionState)

    def _end_if_sequence(self, token):
        return isinstance(token, ExecutionState)


class Compiler:
    def compile(self, source):
        bytecode = self._make_bytecode(source)

        def inner(**local_scope):
            local_scope["_output"] = io.StringIO()
            exec(bytecode, {}, local_scope)
            return local_scope['_output'].getvalue()

        return inner

    def _get_chunks(self, source):
        state = LiteralState(source)

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


class Literal:
    def __init__(self, contents):
        self.contents = contents

    def __str__(self):
        return "<Literal %r>" % self.contents

    def make_bytecode(self, symbol_table):
        return [Instr("LOAD_CONST", symbol_table["write_func"]),
                Instr("LOAD_NAME", "_output"),
                Instr("LOAD_CONST", self.contents),
                Instr("CALL_FUNCTION", 2),
                Instr("POP_TOP")]


class VariableExpansion:
    def __init__(self, variable_name):
        self.variable_name = variable_name

    def make_bytecode(self, symbol_table):
        return [Instr("LOAD_CONST", symbol_table["write_func"]),
                Instr("LOAD_NAME", "_output"),
                Instr("LOAD_NAME", self.variable_name),
                Instr("CALL_FUNCTION", 2),
                Instr("POP_TOP")]


class Execution:
    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return "<Execution: %r>" % self.expression

    def make_bytecode(self, symbol_table):
        return []


class IfBlock:
    def __init__(self, condition):
        self.condition = condition
        self.sequence = Sequence()

    def __eq__(self, other):
        if not isinstance(other, IfBlock):
            return False

        return (self.sequence == other.sequence) \
            and (self.condition == other.condition)

    def __repr__(self):
        return "<IfBlock %r, %r>" % (self.condition, self.sequence)
