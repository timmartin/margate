"""
Code for interfacing Margate with Django
"""

from django.template import TemplateDoesNotExist
from django.template.utils import get_app_template_dirs
from django.template.loaders.filesystem import Loader as DjangoFileSystemLoader
from django.template.backends.base import BaseEngine

from margate.compiler import Compiler


class MargateLoader(DjangoFileSystemLoader):
    def get_dirs(self):
        return get_app_template_dirs('margate')


class MargateEngine(BaseEngine):
    app_dirname = "margate"

    def __init__(self, params):
        params = params.copy()

        try:
            params.pop('OPTIONS')
        except KeyError:
            pass

        super(MargateEngine, self).__init__(params)

        self.loader = MargateLoader(self)
        self.file_charset = 'utf-8'
        self.debug = False
        self.template_libraries = []
        self.template_builtins = []

    def get_template(self, template_name):
        compiler = Compiler()
        template_func = compiler.compile(self.find_template(template_name))
        return Template(template_func)

    def find_template(self, name):
        tried = []

        for source in self.loader.get_template_sources(name):
            try:
                contents = self.loader.get_contents(source)
            except TemplateDoesNotExist:
                tried.append((source, 'Source does not exist'))
            else:
                return contents

        raise TemplateDoesNotExist(name, tried=tried)


class Template:
    def __init__(self, template_func):
        self.template_func = template_func

    def render(self, context=None, request=None):
        return self.template_func(**context)
