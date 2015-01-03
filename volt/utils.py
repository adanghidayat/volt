# -*- coding: utf-8 -*-
"""
----------
volt.utils
----------

Collection of general handy methods used throughout Volt.

:copyright: (c) 2012-2014 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

from __future__ import print_function
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

    :param func: Function object
    :type func: function
    :returns: Function name
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
        """Logger for this object's instance."""
        return logging.getLogger(type(self).__name__ + '-' + str(id(self)))


def path_import(name, paths):
    """Imports a module from the specified path.

    :param name: Target module name
    :type name: str
    :param paths: Absolute directory path(s) to look for the import
    :type paths: str or [str]
    :returns: Imported module

    """
    # convert to list if paths is string
    if isinstance(paths, basestring):
        paths = [paths]
    # force reload
    if name in sys.modules:
        del sys.modules[name]
    mod_tuple = imp.find_module(name, paths)
    return imp.load_module(name, *mod_tuple)


def console(text, fmt=None, color='grey', is_bright=False, log_time=True,
            time_fmt='{H:02d}:{M:02d}:{S:02d}.{f:03.0f}'):
    """Formats the given string for console display.

    :param text: Text to display
    :type text: str
    :param fmt: Format string (with `.format`). Must contain '{text}' as text
                placeholder. If ``log_time`` is True, must also contain
                '{time}' as time placeholder.
    :type fmt: str
    :param color: Color to display. Possible values are black, red, green,
                  yellow, blue, violet, cyan, or grey.
    :type color: str
    :param is_bright: Whether to display bright text or not
    :type is_bright: bool
    :param log_time: Whether to include time information in or not
    :type log_time: bool
    :param time_fmt: Format of the time string
    :type time_fmt: str
    :returns: Colored text for console display
    :rtype: str
    :raises ValueError: if '{text}' placeholder is missing and/or '{time}'
                        placeholder is missing when ``log_time`` is True

    """
    if format is not None:
        if '{text}' not in text:
            raise ValueError("Missing '{text}' placeholder for console "
                             "display.")
        if log_time:
            if '{time}' not in text:
                raise ValueError("Missing '{time}' placeholder for console "
                                 "display.")
            now = datetime.now()
            time_str = time_fmt.format(H=now.hour, M=now.minute, S=now.second,
                                       f=now.microsecond / 1000.0 + 0.5)
            string = fmt.format(time=time_str, text=text)
        else:
            string = fmt.format(text=text)

    if os.name != 'nt':
        brg = 'bold' if is_bright else 'normal'
        text = "\033[{0};{1}m{2}\033[m".format(BRIGHTNESS_MAP[brg], \
                                                 COLOR_MAP[color], string)

    print(text, file=sys.stdout)


def write_file(file_path, text, bufsize=16384):
    """Writes the given text to a target file path.

    :param file_path: Absolute file path of target file
    :type file_path: str
    :param text: Text contents to write
    :type text: str
    :param bufsize: Buffer size when writing to file (default: 16384)
    :type bufsize: int

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
