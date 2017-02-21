Stencil
=======

Stencil is a library that provides a Django-compatible template engine
where the templates compile to raw Python bytecode. In theory, this
will make them expand faster. This is at a very early stage and is
experimental.

Performance tests
-----------------

I've only done minimal performance tests so far, but on a couple of
simple cases Stencil is 10 times faster than "real" Django
templates.

See `performance_test.py` for the details.
