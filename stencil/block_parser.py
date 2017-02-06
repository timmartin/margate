from . import code_generation


class LiteralState:
    """The literal state is the state the block parser is in when it is
    processing anything that will be included in the template output
    as a literal. The template starts out in literal state and
    transitions back into it every time a block is closed.
    """

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
                code_generation.Literal(self.text[:offset]))

    def accept_open_execution(self, offset, length):
        return (ExecutionState(self.text[offset + length:]),
                code_generation.Literal(self.text[:offset]))

    def accept_close_expression(self, offset, length):
        raise Exception("Syntax error")

    def accept_close_execution(self, offset, length):
        raise Exception("Syntax error")

    def accept_end_input(self):
        return (None, code_generation.Literal(self.text))


class ExecutionState:
    """Execution state is the state when any kind of code execution is
    occurring. This includes the start and ends of blocks.
    """

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
                code_generation.Execution(self.text[:offset]))

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
                code_generation.VariableExpansion(self.text[:offset].strip()))

    def accept_end_input(self):
        raise Exception("Syntax error")
