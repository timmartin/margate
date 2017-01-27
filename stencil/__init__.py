"""
Compiled templates
"""

import os.path
from django.template import TemplateDoesNotExist
from django.template.backends.base import BaseEngine


class Template:
    def __init__(self, code, engine):
        self.code = code
        self.engine = engine

        super(Template, self).__init__()

    def render(self, context=None, request=None):
        return self.code


class FasterEngine(BaseEngine):
    app_dirname = 'compiled'

    def __init__(self, params):
        params.pop('OPTIONS')

        super(FasterEngine, self).__init__(params)

    def get_template(self, template_name):
        for template_dir in self.template_dirs:
            candidate_file = os.path.join(template_dir, template_name)
            if os.path.exists(candidate_file):
                with open(candidate_file, "r") as template_contents:
                    return Template(template_contents.read(), self)
        raise TemplateDoesNotExist("Template %s does not exist"
                                   % template_name)

    def from_string(self, template_code):
        return Template(template_code, self)
