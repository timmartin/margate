"""The parser converts the template language into a usable structured
form.

There are two layers to the parsing: breaking the template down into
blocks (which is done by the :py:mod:`~margate.block_parser` module),
and parsing the expressions that appear in the execution blocks within
the template.

The parser in this module uses a combination of ad hoc parsing,
`funcparserlib <https://pypi.python.org/pypi/funcparserlib>`_ and
`ast.parse
<https://docs.python.org/3/library/ast.html#ast.parse>`_. The
top-level rules in the language (``if``, ``for``, ``endif`` etc.) are
handled ad hoc since they are not recursive. However, the expression
that is given as an argument to ``if`` is an arbitrary expression and
parsed

"""

import re
import ast
from collections import namedtuple
import funcparserlib.parser

from . import code_generation, compiler

IfNode = namedtuple('IfNode', ['expression'])
ForNode = namedtuple('ForNode', ['variable', 'collection'])
ExtendsNode = namedtuple('ExtendsNode', ['template_name'])
BlockNode = namedtuple('BlockNode', ['block_name'])


class UnsupportedElementException(Exception):
    pass


def parse_expression(expression):
    """Parse an expression that appears in an execution node, i.e. a
    block delimited by ``{% %}``.

    This can be a compound expression like a ``for`` statement with
    several sub-expressions, or it can just be a single statement such
    as ``endif``.

    :param list expression: Tokenised expression.

    """
    from funcparserlib.parser import a, skip, some

    # For if expressions, we rely on the Python parser to process the
    # expression rather than using our own parser.
    if expression[0] == 'if':
        return IfNode(ast.parse(' '.join(expression[1:]), mode="eval"))

    variable_name = some(lambda x: re.match(r'[a-zA-Z_]+', x))

    # TODO We use the same function twice, first to match the token
    # and then to extract the value we care about from the token
    # (namely the contents of the quoted string). This smells wrong.
    def extract_quoted_string(x):
        result = re.match(r'\"([^\"]*)\"', x)
        if result:
            return result.groups(1)

    quoted_string = some(extract_quoted_string)

    for_expression = (
        skip(a('for'))
        + (variable_name >> str)
        + skip(a('in'))
        + (variable_name >> str))

    extends_expression = (
        skip(a('extends'))
        + (quoted_string >> extract_quoted_string))

    block_expression = (
        skip(a('block'))
        + (variable_name >> str))

    def make_for_node(x): return ForNode(*x)

    def make_extends_node(x): return ExtendsNode(*x)

    parser = ((for_expression >> make_for_node)
              | (extends_expression >> make_extends_node)
              | (block_expression >> BlockNode))

    try:
        return parser.parse(expression)
    except funcparserlib.parser.NoParseError as e:
        raise Exception("Invalid expression '%s'" % expression)


class Parser:
    """The Parser is responsible for turning a template in "tokenised"
    form into a tree structure from which it is straightforward to
    generate bytecode.

    The input is in the form of a flat list of atomic elements of the
    template, where literal text (of any length) is a single element,
    and a ``{% %}`` or ``{{ }}`` expression is a single element.

    Figuring out nesting of starting and ending of loops happens
    within the parser.

    """

    def __init__(self, template_locator=None):

        def _get_related_template(template_name):
            template = template_locator.find_template(template_name)
            if not template:
                raise FileNotFoundError()
            with open(template) as template_file:
                compiler_obj = compiler.Compiler(template_locator)
                return compiler_obj._get_chunks(template_file.read())

        self._sub_template_locator = _get_related_template

    def parse(self, tokens):
        """Parse a token sequence into a
        :py:class:`~margate.code_generation.Sequence` object.

        """

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
        node = parse_expression(
            re.split(r'\s+',
                     token.expression.strip()))

        if isinstance(node, IfNode):
            block = code_generation.IfBlock(node.expression)
            inner_termination_condition = self._end_sequence("endif")
        elif isinstance(node, ForNode):
            block = code_generation.ForBlock(node)
            inner_termination_condition = self._end_sequence("endfor")
        elif isinstance(node, ExtendsNode):
            if self._sub_template_locator is None:
                raise UnsupportedElementException(
                    "Parser is not configured to support "
                    "extending other templates")

            content = self._sub_template_locator(
                node.template_name)
            parsed = self.parse(content)
            block = code_generation.ExtendsBlock(parsed)
            inner_termination_condition = None
        elif isinstance(node, BlockNode):
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
