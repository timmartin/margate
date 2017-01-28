"""
Compiler
"""

import io
from bytecode import Bytecode, Instr


class Compiler:
    def compile(self, source):
        bytecode = self._make_bytecode(source)

        def inner(**local_scope):
            local_scope["_output"] = io.StringIO()
            exec(bytecode, {}, local_scope)
            return local_scope['_output'].getvalue()

        return inner

    def _get_chunks(self, source):
        in_literal = True

        while True:
            next_start = source.find('{%')
            next_end = source.find('%}')

            if (next_start == -1) and (next_end == -1):
                yield Literal(source)
                break
            elif (next_start == -1):
                yield VariableExpansion(source[:next_end].strip())
                source = source[next_end + 2:]
            elif (next_end == -1):
                yield Literal(source[:next_start])
                source = source[next_start + 2:]
            else:
                if in_literal:
                    if next_end < next_start:
                        raise Exception("Syntax error")
                    yield Literal(source[:next_start])
                    in_literal = not in_literal
                    source = source[next_start + 2:]
                else:
                    if next_end > next_start:
                        raise Exception("Syntax error")
                    yield VariableExpansion(source[:next_end].strip())
                    in_literal = not in_literal
                    source = source[next_end + 2:]

    def _make_bytecode(self, source):
        instructions = []
        symbol_table = {
            "write_func": io.StringIO.write
        }

        for item in self._get_chunks(source):
            instructions += item.make_bytecode(symbol_table)

        bytecode = Bytecode(instructions + [Instr("LOAD_CONST", None),
                                            Instr("RETURN_VALUE")])
        return bytecode.to_code()


class Literal:
    def __init__(self, contents):
        self.contents = contents

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
