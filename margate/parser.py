"""The parser converts the template language into a usable structured
form.

There are two layers to the parsing: breaking the template down into
blocks (which is done by the :py:mod:`~margate.block_parser` module),
and parsing the expressions that appear in the execution blocks within
the template.

"""

import re
import ast
from collections import namedtuple
import funcparserlib.parser


IfNode = namedtuple('IfNode', ['expression'])
ForNode = namedtuple('ForNode', ['variable', 'collection'])
ExtendsNode = namedtuple('ExtendsNode', ['template_name'])
BlockNode = namedtuple('BlockNode', ['block_name'])


def parse_expression(expression):
    """
    Parse an expression that appears in an execution node.

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
