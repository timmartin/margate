Reference
=========

The process of building a template into a function has the following
steps:

* The template is broken down into blocks (such as literal text and
  code execution) that are treated differently. This is handled by
  :py:mod:`the block parser <margate.block_parser>`.
* The resultant sequence of blocks is passed to the
  :py:class:`~margate.compiler.Parser` to be turned into a parse tree.
* The parse tree is processed by :py:mod:`code generation
  <margate.code_generation>` to make Python bytecode.

Compiler
--------

.. automodule:: margate.compiler

.. autoclass:: Compiler
   :members:

.. autoclass:: Parser
   :members:

.. autoclass:: TemplateLocator

Code generation
---------------

.. automodule:: margate.code_generation

.. autoclass:: Sequence
   :members:

.. autoclass:: ForBlock
   :members:

.. autoclass:: IfBlock
   :members:

.. autoclass:: ExtendsBlock
   :members:

.. autoclass:: ReplaceableBlock
   :members:

.. autoclass:: VariableExpansion
   :members:

.. autoclass:: Literal
   :members:

.. autoclass:: Execution
   :members:

Block parser
------------

.. automodule:: margate.block_parser

.. autoclass:: LiteralState
   :members:

.. autoclass:: ExecutionState
   :members:

.. autoclass:: ExpressionState
   :members:

Parser
------

.. automodule:: margate.parser

.. autofunction:: parse_expression
