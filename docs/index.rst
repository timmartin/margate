
Welcome to Margate's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   django
   todo_list
   reference

Introduction
------------

Margate is a templating engine for Python that compiles templates down
to Python bytecode. It is mostly Django-compatible in spirit, though
it falls short of being a drop-in replacement for Django templates.

Early performance testing suggests that it is around 10 times faster
than regular Django templates.

Example
-------

Simply instantiate a :py:class:`~margate.compiler.Compiler` and call
its :py:meth:`~margate.compiler.Compiler.compile()` method with the
template source::

  template_source = """
  <p>Hello {{ person }}, my name is {{ me }}
  """

  compiler = margate.compiler.Compiler()
  template_function = compiler.compile(template_source)

You now have a function that can be called to yield the rendered
content. Pass variable values in keyword arguments::

  print(template_function(person="alice",
                          me="a template"))

FAQ
---

Why oh why?
'''''''''''

Mostly to learn about Python bytecode.

You don't really expect the speed benefit to be worth it, do you?
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Template rendering is extremely unlikely to be the bottleneck in your
web application. Optimising it will at best save a constant overhead
from each page view, and will have a proportionately lower impact on
your slowest pages.

On the other hand, it's free speed. It can probably save you a few
milliseconds per page view, which might help when you're trying to get
your landing page to load as fast as possible. Assuming the templating
language has all the same features, why wouldn't you? Template
expansion probably can't be parallelised with anything else your web
app is doing, so miliseconds here contribute directly to the bottom
line.

What's with the name?
'''''''''''''''''''''

The library was originally called Stencil, but it turns out that lots
of people call their templating library Stencil, so I had to change.

I hate spending time thinking of names for projects, so when I get
stuck I just use the name of an English seaside town. There are plenty
of them and they are reasonably unique and memorable names.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
