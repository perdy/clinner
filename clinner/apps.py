# -*- coding: utf-8 -*-
"""Django application config module.
"""
try:
    from django.apps import AppConfig
except ImportError:
    AppConfig = object

from clinner.settings import settings


class Clinner(AppConfig):
    name = 'clinner'
    verbose_name = 'Clinner'

    def ready(self):
        settings.build_from_django()
