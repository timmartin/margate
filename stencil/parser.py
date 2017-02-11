"""The parser converts the template language into a usable structured
form.

There are two layers to the parsing: breaking the template down into
blocks, and parsing the expressions that appear in the execution
blocks within the template.

"""

import re
import ast
from collections import namedtuple


IfNode = namedtuple('IfNode', ['expression'])
ForNode = namedtuple('ForNode', ['variable', 'collection'])


def parse_expression(expression):
    """
    Parse an expression that appears in an execution node.

    :param list expression: Tokenised expression.
    """
    from funcparserlib.parser import a, skip, some

    if expression[0] == 'if':
        return IfNode(ast.parse(' '.join(expression[1:]), mode="eval"))

    def true_val(x): return True

    def false_val(x): return False

    variable_name = some(lambda x: re.match(r'[a-zA-Z_]+', x))

    for_expression = (
        skip(a('for'))
        + (variable_name >> str)
        + skip(a('in'))
        + (variable_name >> str))

    def make_for_node(x): return ForNode(*x)

    return (for_expression >> make_for_node).parse(expression)
