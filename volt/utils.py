# -*- coding: utf-8 -*-
"""
----------
volt.utils
----------

Collection of general handy methods used throughout Volt.

:copyright: (c) 2012 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

from past.builtins import basestring

import imp
import logging
import os
import sys
from datetime import datetime


COLOR_MAP = {'black': '30', 'red': '31',
             'green': '32', 'yellow': '33',
             'blue': '34', 'violet': '35',
             'cyan': '36', 'grey': '37'}

BRIGHTNESS_MAP = {'normal': '00', 'bold': '01'}

logger = logging.getLogger('util')


def get_func_name(func):
    """Returns the name of the given function object.

    :param func: function object
    :type func: function
    :returns: function name
    :rtype: str

    """
    if sys.version_info[0] < 3:
        # Python2 stores function names in func_name
        return func.func_name
    # Python3 stores it in __name__
    return func.__name__


def cachedproperty(func):
    """Decorator for cached property loading."""
    attr_name = get_func_name(func)
    @property
    def cached(self):
        if not hasattr(self, '_cache'):
            setattr(self, '_cache', {})
        try:
            return self._cache[attr_name]
        except KeyError:
            result = self._cache[attr_name] = func(self)
            return result
    return cached


class Loggable(object):
    """Mixin for adding logging capabilities to classes."""
    @cachedproperty
    def logger(self):
        return logging.getLogger(type(self).__name__)


def time_string():
    """Returns string for logging time."""
    time = datetime.now()
    format = "%02d:%02d:%02d.%03.0f"
    return format % (time.hour, time.minute, time.second, \
            (time.microsecond / 1000.0 + 0.5))


def path_import(name, paths):
    """Imports a module from the specified path.

    name -- String denoting target module name.
    paths -- List of possible absolute directory paths or string of an
        absolute directory path that may contain the target module.

    """
    # convert to list if paths is string
    if isinstance(paths, basestring):
        paths = [paths]
    # force reload
    if name in sys.modules:
        del sys.modules[name]
    mod_tuple = imp.find_module(name, paths)
    return imp.load_module(name, *mod_tuple)


def console(string, format=None, color='grey', is_bright=False, log_time=True):
    """Formats the given string for console display.

    string -- String to display.
    format -- String to format the given string. Must include an extra '%s'
              for log_time() value if 'log_time' is True.
    color -- String indicating color.
    is_bright -- Boolean indicating whether to return a bright version of the
                 colored string or not.
    log_time -- Boolean indicating whether to log time or not.

    """
    if format is not None:
        if log_time:
            string = format % (time_string(), string)
        else:
            string = format % string

    if os.name != 'nt':
        brg = 'bold' if is_bright else 'normal'
        string = "\033[%s;%sm%s\033[m" % (BRIGHTNESS_MAP[brg], \
                COLOR_MAP[color], string)

    sys.stdout.write(string)


def write_file(file_path, text, bufsize=16384):
    """Writes the given text to a target file path.

    :param file_path: absolute file path of target file
    :type file_path: str
    :param text: text contents to write
    :type text: str
    :param bufsize: buffer size when writing to file (default: 16384)
    :type bufsize: int
    :returns: None

    """
    try:
        target = open(file_path, 'w', bufsize)
    except IOError:
        file_dir = os.path.dirname(file_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
            target = open(file_path, 'w', bufsize)
        else:
            raise

    # will only be reached when we get a writable target
    target.write(text)
    target.close()
    logger.debug("written: {0}".format(file_path))
