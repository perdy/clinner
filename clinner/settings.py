# -*- coding: utf-8 -*-
"""
Settings.
"""
import os
from functools import partial
from functools import update_wrapper
from importlib import import_module

__all__ = ['settings']


class reset:  # noqa
    def __init__(self, func, *args, **kwargs):
        self.func = func
        update_wrapper(self, func)

    def __get__(self, instance, owner=None):
        self.instance = instance
        return partial(self, instance)

    def __call__(self, *args, **kwargs):
        self.instance.reset_default()
        self.func(*args, **kwargs)


class Settings:
    default_args = {}

    def __init__(self):
        self.reset_default()
        module_path = os.environ.get('CLINNER_SETTINGS')
        if module_path:
            self.build_from_module(module_path)

    def reset_default(self):
        """
        Reset settings to default values.
        """
        self.default_args = {}

    @staticmethod
    def import_settings(path):
        """
        Import a settings module that can be a module or an object.
        To import a module, his full path should be specified: *package.settings*.
        To import an object, his full path and object name should be specified: *project.settings:SettingsObject*.

        :param path: Settings full path.
        :return: Settings module or object.
        """
        try:
            try:
                m, c = path.rsplit(':', 1)
                module = import_module(m)
                s = getattr(module, c)
            except ValueError:
                s = import_module(path)
        except ImportError:
            raise ImportError("Settings not found '{}'".format(path))

        return s

    @staticmethod
    def get(s, key, default=None):
        """
        Get a settings value from key. Try to get key as it is, transforming to lower case and to upper case. If not
        found, a default value will be returned.

        :param s: Settings module or object.
        :param key: Settings key.
        :param default: Default value.
        :return: Settings value. Default value if key is not found.
        """
        return getattr(s, key, getattr(s, key.lower(), getattr(s, key.upper(), default)))

    @reset
    def build_from_django(self):
        from django.conf import settings as django_settings

        self.build_from_module(django_settings)

    @reset
    def build_from_module(self, module=None):
        if isinstance(module, str):
            module = self.import_settings(module)

        # Builder args
        self.default_args = self.get(module, 'clinner_default_args', {})

settings = Settings()
