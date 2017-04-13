"""The compiler module contains the public interface to the library.

"""

import re
import io
from bytecode import Bytecode, Instr

from . import parser, block_parser


class TemplateLocator:
    """The template locator abstracts the details of locating templates
    when one template extends another (such as with the ``{% extends %}``
    tag)self.
    """

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
        """Compile the template source code into a callable function.

        :return: A callable function that returns rendered content as
          a string when called.
        """
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

        parser_obj = parser.Parser(self._template_locator)
        sequence = parser_obj.parse(self._get_chunks(source))

        for item in sequence.elements:
            instructions += item.make_bytecode(symbol_table)

        bytecode = Bytecode(instructions + [Instr("LOAD_CONST", None),
                                            Instr("RETURN_VALUE")])
        return bytecode.to_code()
