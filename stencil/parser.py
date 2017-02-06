"""The parser converts the template language into a usable structured
form.

There are two layers to the parsing: breaking the template down into
blocks, and parsing the expressions that appear in the execution
blocks within the template.

"""

import re
from collections import namedtuple


IfNode = namedtuple('IfNode', ['expression'])
ForNode = namedtuple('ForNode', ['variable', 'collection'])


def parse_expression(expression):
    from funcparserlib.parser import a, skip, some

    def true_val(x): return True

    def false_val(x): return False

    variable_name = some(lambda x: re.match(r'[a-zA-Z_]+', x))

    boolean = (a('True') >> true_val) | (a('False') >> false_val)

    if_expression = skip(a('if')) + boolean

    for_expression = (
        skip(a('for'))
        + (variable_name >> str)
        + skip(a('in'))
        + (variable_name >> str))

    def make_for_node(x): return ForNode(*x)

    return (if_expression >> IfNode
            | for_expression >> make_for_node).parse(expression)
