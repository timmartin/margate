"""Run the same template through Django templates and through
stencil, to give a crude performance comparison.

"""

import timeit

from django.template import Context, Engine

from stencil.compiler import Compiler

expression = """
Hello {{ name }}, I am a {{ whom }}

I'm going to count:
{% for i in numbers %}
next: {{ i }}
{% endfor %}
"""

# Give some variables to print. Note that we have to convert the
# numbers to string ahead of time, because Django wants to do
# l10n-specific stuff with numbers and barfs if you attempt to display
# a number without having settings set up.
variables = {
    'name': 'world',
    'whom': 'template',
    'numbers': [str(i) for i in range(200)]
}

compiler = Compiler()
stencil_func = compiler.compile(expression)

engine = Engine()
template = engine.from_string(expression)
context = Context(variables)


def stencil_render():
    return stencil_func(**variables)


def django_render():
    return template.render(context)


def do_performance_test():
    assert stencil_render() == django_render()

    iterations = 1000

    time_for_django = timeit.timeit(django_render, number=iterations)

    time_for_stencil = timeit.timeit(stencil_render, number=iterations)

    print("Django took {time} microseconds".format(
        time=round(time_for_django / iterations * 1000 * 1000,
                   2)))
    print("Stencil took {time} microseconds".format(
        time=round(time_for_stencil / iterations * 1000 * 1000,
                   2)))


if __name__ == '__main__':
    do_performance_test()
