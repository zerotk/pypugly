from __future__ import absolute_import
from django.template.loaders.base import Loader


class Loader(Loader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        from pypugly import generate
        source = generate(template_name, template_dirs or [])
        return source, template_name
