"""This module contains the building blocks of the final template
function, in the form of bytecode generators.

"""

from bytecode import Instr, Label


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


class ForBlock:
    def __init__(self, for_node):
        self.variable = for_node.variable
        self.collection = for_node.collection
        self.sequence = Sequence()

    def __eq__(self, other):
        if not isinstance(other, ForBlock):
            return False

        return (self.variable == other.variable) \
            and (self.collection == other.collection) \
            and (self.sequence == other.sequence)

    def __repr__(self):
        return "<ForBlock %r in %r (%r)>" % (self.variable,
                                             self.collection,
                                             self.sequence)

    def make_bytecode(self, symbol_table):
        catch_block = Label()
        start_loop = Label()
        end_loop = Label()
        end_for = Label()
        end_of_function = Label()

        inner = [Instr("SETUP_EXCEPT", catch_block),
                 Instr("SETUP_LOOP", end_for),
                 Instr("LOAD_NAME", self.collection),
                 Instr("GET_ITER"),
                 start_loop,
                 Instr("FOR_ITER", end_loop),
                 Instr("STORE_NAME", self.variable)]

        for element in self.sequence.elements:
            inner += element.make_bytecode(symbol_table)

        inner += [Instr("JUMP_ABSOLUTE", start_loop),
                  end_loop,
                  Instr("POP_BLOCK"),
                  end_for,
                  Instr("POP_BLOCK"),
                  Instr("JUMP_FORWARD", end_of_function)]

        inner += [catch_block,
                  # In the catch block, we catch everything
                  # unconditionally (this is wrong, we should filter
                  # out just StopException, which is the only thing we
                  # have any business catching here).
                  #
                  # We pop (I think?) the exception and the stack
                  # frame data.
                  Instr("POP_TOP"),
                  Instr("POP_TOP"),
                  Instr("POP_TOP"),

                  # Pop the exception frame from the block stack.
                  Instr("POP_EXCEPT"),
                  Instr("JUMP_FORWARD", end_of_function),
                  Instr("END_FINALLY"),
                  end_of_function]

        return inner


class IfBlock:
    """The IfBlock generates code for a conditional expression.

    This currently only includes literal `True` and `False` as
    expressions, and doesn't support an `else` branch.
    """

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

    def make_bytecode(self, symbol_table):
        label_end = Label()
        inner = [Instr("LOAD_CONST", self.condition),
                 Instr("POP_JUMP_IF_FALSE", label_end)]

        for element in self.sequence.elements:
            inner += element.make_bytecode(symbol_table)

        inner += [label_end]

        return inner


class VariableExpansion:
    """A variable expansion takes the value of a variable and includes it
    into the template output. This should really take a full
    expression, not just a single variable.

    """

    def __init__(self, variable_name):
        self.variable_name = variable_name

    def make_bytecode(self, symbol_table):
        return [Instr("LOAD_CONST", symbol_table["write_func"]),
                Instr("LOAD_NAME", "_output"),
                Instr("LOAD_NAME", "str"),
                Instr("LOAD_NAME", self.variable_name),
                Instr("CALL_FUNCTION", 1),
                Instr("CALL_FUNCTION", 2),
                Instr("POP_TOP")]


class Literal:
    def __init__(self, contents):
        self.contents = contents

    def __eq__(self, other):
        if not isinstance(other, Literal):
            return False

        return other.contents == self.contents

    def __repr__(self):
        return "<Literal %r>" % self.contents

    def make_bytecode(self, symbol_table):
        return [Instr("LOAD_CONST", symbol_table["write_func"]),
                Instr("LOAD_NAME", "_output"),
                Instr("LOAD_CONST", self.contents),
                Instr("CALL_FUNCTION", 2),
                Instr("POP_TOP")]
