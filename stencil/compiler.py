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
        while True:
            next_start = source.find('{{')
            next_end = source.find('}}')

            if (next_start == -1) and (next_end == -1):
                yield source
                break
            elif (next_start == -1):
                yield source[:next_end]
                source = source[next_end + 2:]
            elif (next_end == -1):
                yield source[:next_start]
                source = source[next_start + 2:]
            else:
                next_separator = min(next_start, next_end)
                yield source[:next_separator]
                source = source[next_separator + 2:]

    def _make_bytecode(self, source):
        in_literal = True
        instructions = []
        write_func = io.StringIO.write

        for item in self._get_chunks(source):
            if in_literal:
                instructions += [Instr("LOAD_CONST", write_func),
                                 Instr("LOAD_NAME", "_output"),
                                 Instr("LOAD_CONST", item),
                                 Instr("CALL_FUNCTION", 2),
                                 Instr("POP_TOP")]
            else:
                variable_name = item.strip()

                instructions += [Instr("LOAD_CONST", write_func),
                                 Instr("LOAD_NAME", "_output"),
                                 Instr("LOAD_NAME", variable_name),
                                 Instr("CALL_FUNCTION", 2),
                                 Instr("POP_TOP")]

            in_literal = not in_literal

        bytecode = Bytecode(instructions + [Instr("LOAD_CONST", None),
                                            Instr("RETURN_VALUE")])
        return bytecode.to_code()
