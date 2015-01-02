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
        """Unloads all loaded configuration values."""
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
        """Adjusts the values of keys contained in config for consistency.

        The adjustments are:

        * All keys ending with `_DIR` are made into absolute directory paths
          by prefixing them the ``user_dir``. If the key value is already an
          absolute path, ``user_dir`` has no effect.

        * All keys ending with `URL` are stripped of their preceding and
          succeeding slash ('/').

        :param config: Configuration key-value pairs
        :type config: dict
        :param user_dir: Absolute path to Volt root directory
        :type user_dir: str
        :returns: Adjusted configuration
        :rtype: dict

        """
        for key, val in config.items():
            if key.endswith('_DIR'):
                if not path.isabs(val):
                    val = path.join(user_dir, val)
                config[key] = val.rstrip(path.sep)
            elif key.endswith('URL'):
                config[key] = val.strip('/')
        return config

    @staticmethod
    def _load_config(mod):
        """Loads all config values from the given module.

        Config values are contained in all uppercase keys.

        :param mod: Module to load configurations from
        :type mod: module object
        :returns: Configuration key-value pairs
        :rtype: dict

        """
        # TODO: remove Python2.6 compatibility
        return dict([(k, getattr(mod, k)) for k in dir(mod) if k.upper() == k])

    @staticmethod
    def _get_root_dir(conf_name, start_dir=None):
        """Computes the root directory of a Volt app.

        Checks the current directory for a Volt config file. If it is not
        present, parent directories of the current directory is checked until
        a Volt configuration file is found.

        :param conf_name: user configuration filename
        :type conf_name: str
        :param start_dir: starting directory for configuration file lookup
        :type start_dir: str
        :returns: path to root directory of a Volt app
        :rtype: str
        :raises ConfigNotFoundError: if no Volt configuration file is found
                                     up to the root filesystem directory

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
