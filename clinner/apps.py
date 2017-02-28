# -*- coding: utf-8 -*-
"""Django application config module.
"""
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

from health_check.settings import settings


class Clinner(AppConfig):
    name = 'clinner'
    verbose_name = _('Clinner')

    def ready(self):
        settings.build_from_django()
