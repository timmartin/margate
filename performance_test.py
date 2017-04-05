"""Run the same template through Django templates and through
margate, to give a crude performance comparison.

"""

import timeit

from django.template import Context, Engine

from margate.compiler import Compiler

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
margate_func = compiler.compile(expression)

engine = Engine()
template = engine.from_string(expression)
context = Context(variables)


def margate_render():
    return margate_func(**variables)


def django_render():
    return template.render(context)


def do_performance_test():
    assert margate_render() == django_render()

    iterations = 1000

    time_for_django = timeit.timeit(django_render, number=iterations)

    time_for_margate = timeit.timeit(margate_render, number=iterations)

    print("Django took {time} microseconds".format(
        time=round(time_for_django / iterations * 1000 * 1000,
                   2)))
    print("Margate took {time} microseconds".format(
        time=round(time_for_margate / iterations * 1000 * 1000,
                   2)))


if __name__ == '__main__':
    do_performance_test()
