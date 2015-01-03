# -*- coding: utf-8 -*-
"""
-----------
volt.config
-----------

Volt configuration container module.

:copyright: (c) 2012-2014 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

from future.standard_library import install_aliases
install_aliases()

import os
from os import path
from collections import UserDict

from volt.exceptions import ConfigNotFoundError
from volt.utils import path_import, Loggable


DEFAULT_CONF_DIR = path.dirname(__file__)
DEFAULT_CONF = 'defaults'


class SiteConfigContainer(Loggable):

    """Reloadable lazy container for SiteConfig."""

    def __init__(self):
        self._loaded = None

    def __getitem__(self, key):
        if self._loaded is None:
            self._load()
        return self._loaded[key]

    def __setitem__(self, key, value):
        if self._loaded is None:
            self._load()
        self._loaded[key] = value

    def __delitem__(self, key):
        if self._loaded is None:
            self._load()
        del self._loaded[key]

    def __contains__(self, key):
        if self._loaded is None:
            self._load()
        return key in self._loaded

    def _load(self):
        self._loaded = SiteConfig()
        self.logger.debug('loaded: SiteConfig')

    def reset(self):
        """Unloads all loaded configuration values."""
        if self._loaded is not None:
            self._loaded = None
            self.logger.debug('reset: SiteConfig')


class SiteConfig(UserDict, Loggable):

    """Container class for storing all configurations used in a Volt site.

    SiteConfig unifies configuration values from volt.config.defaults
    and the user's voltapp.py.

    """

    def __init__(self, default_conf=DEFAULT_CONF,
                 default_conf_dir=DEFAULT_CONF_DIR):
        """Initializes SiteConfig.

        :param default_conf: Base file name of default configurations file.
                             Defaults to `defaults`.
        :type default_conf: str
        :param default_conf_dir: Directory where the default configurations
                                 file is located.
        :type default_conf_dir: str

        """
        defaults = path_import(default_conf, default_conf_dir)
        config = SiteConfig._load_config(defaults)

        user_dir = SiteConfig._get_root_dir(config['_USER_CONF'])
        user_conf = config['_USER_CONF'].split('.')[0]
        user_mod = path_import(user_conf, user_dir)
        user_config = SiteConfig._load_config(user_mod)

        config.update(user_config)
        print(config.keys())
        config['_ROOT_DIR'] = user_dir

        UserDict.__init__(self, config)
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
            raise ConfigNotFoundError("Failed to find Volt config file.")

        # recurse if config file not found
        if not path.exists(path.join(start_dir, conf_name)):
            parent = path.dirname(start_dir)
            return SiteConfig._get_root_dir(conf_name, start_dir=parent)

        return start_dir
