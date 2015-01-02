# -*- coding: utf-8 -*-
"""
-----------
volt.config
-----------

Volt configuration container module.

:copyright: (c) 2012-2014 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

import os
import sys
from os import path

from volt.exceptions import ConfigNotFoundError
from volt.utils import path_import, Loggable


DEFAULT_CONF_DIR = path.dirname(__file__)
DEFAULT_CONF = 'defaults'


class SiteConfigContainer(Loggable):

    """Reloadable, iterable lazy container for SiteConfig."""

    def __init__(self):
        self._loaded = None
        self._confs = None

    def __getattr__(self, name):
        if self._loaded is None:
            self._load()
        return getattr(self._loaded, name)

    def __setattr__(self, name, value):
        if name in ['_loaded', '_confs']:
            self.__dict__[name] = value
        else:
            if self._loaded is None:
                self._load()
            setattr(self._loaded, name, value)

    def __dir__(self):
        if self._loaded is None:
            self._load()
        return dir(self._loaded)

    def __iter__(self):
        if self._confs is None:
            self._confs = []
            for item in dir(self._loaded):
                # config objects are all caps
                # so we can shortcut the test instead of isinstance
                if item  == item.upper():
                    self._confs.append(getattr(self._loaded, item))
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        if self._loaded is None:
            self._load()
        try:
            return self._confs.pop()
        except IndexError:
            # reset for next iteration
            self._confs = None
            raise StopIteration

    def _load(self):
        self._loaded = SiteConfig()
        self.logger.debug('loaded: SiteConfig')

    def reset(self):
        if self._loaded is not None:
            self._loaded = None
            self._confs = None
            self.logger.debug('reset: SiteConfig')


class SiteConfig(Loggable):

    """Container class for storing all configurations used in a Volt site.

    SiteConfig unifies configuration values from volt.config.defaults
    and the user's voltapp.py.

    """

    def __init__(self):
        defaults = path_import(DEFAULT_CONF, DEFAULT_CONF_DIR)
        config = SiteConfig._load_config(defaults)

        user_dir = self.get_root_dir(config['_USER_FILE'])
        user_conf = config['_USER_FILE'].split('.')[0]
        user_mod = path_import(user_conf, user_dir)
        user_config = SiteConfig._load_config(user_mod)

        config.update(user_config, user_dir)
        config['_ROOT_DIR'] = user_dir

        self.__dict__ = config
        self.logger.debug('initialized: SiteConfig')

    @staticmethod
    def _adjust_config(config, user_dir):
        for key in config:
            if key.endswith('_DIR'):
                val = config[key]
                if user_dir:
                    val = val.lstrip(path.sep)
                config[key] = path.join(user_dir, val).rstrip(path.sep)
            elif key.endswith('URL'):
                config[key] = config[key].strip('/')
        return config

    @staticmethod
    def _load_config(mod):
        # TODO: remove Python2.6 compatibility
        return dict([(k, getattr(mod, k)) for k in dir(mod) if k.upper() == k])

    @staticmethod
    def _get_root_dir(conf_name, start_dir=None):
        """Returns the root directory of a Volt app.

        :param conf_name: user configuration filename
        :type conf_name: str
        :param start_dir: starting directory for configuration file lookup
        :type start_dir: str
        :returns: path to root directory of a Volt app
        :rtype: str

        Checks the current directory for a Volt config file. If it is not
        present, parent directories of the current directory is checked until
        a Volt settings file is found. If no Volt settings file is found up to
        '/', ConfigNotFoundError is raised.

        """
        if start_dir is None:
            start_dir = os.getcwd()

        # raise error if search goes all the way to root without any results
        if path.dirname(start_dir) == start_dir:
            raise ConfigNotFoundError("Failed to find Volt config file in "
                    "'{0}' or its parent directories.".format(os.getcwd()))

        # recurse if config file not found
        if not path.exists(path.join(start_dir, conf_name)):
            parent = path.dirname(start_dir)
            return SiteConfig._get_root_dir(conf_name, start_dir=parent)

        return start_dir
