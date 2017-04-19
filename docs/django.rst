Using from Django
=================

Language compatibility
----------------------

The Margate language is very similar in style to the built-in Django
template engine, but differs in a number of important details.

Most importantly, ``{{ }}`` expressions (and expressions in ``for``
loop commands etc.) are treated as arbitrary Python code. This means
that they are more flexible than Django template language, but
prevents you from taking advantage of the shortcuts that automatically
convert object attributes into dictionary member lookup.

For example, instead of writing::

  {% for tag in blog_post.tags %}
  ...
  {% endfor %}

if ``blog_post`` is a dictionary, you will need to write::

  {% for tag in blog_post["tags"] %}
  ...
  {% endfor %}

Another limitation is that none of the built-in filters are currently
supported.

Configuring Django to use the engine
------------------------------------

To enable Margate in Django, simply add it to the ``TEMPLATES`` in
``settings.py``::

  TEMPLATES = [
    {
      'BACKEND': 'margate.django.MargateEngine',
      'DIRS': [],
      'APP_DIRS': True
    }
  ]

Limitations
-----------
  
Currently templates are compiled on-demand and discarded immediately
afterwards rather than being cached. This means that there is unlikely
to be any speed advantage to using Margate in a Django app.
