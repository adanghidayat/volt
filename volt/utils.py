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


class cachedproperty(object):

    """Decorator for cached property loading.

    Based on the descriptor protocol as noted in
    https://docs.python.org/3.4/howto/descriptor.html#descriptor-protocol

    This decorator is designed to cache results from a getter function
    without the need to explicitly declare hidden variables.

    Note that this means the deleter function only removes the computed
    value from the cache. Thus, :meth:`hasattr` will never return `False`
    for the decorator as on subsequent access the getter recomputes the
    deleted value and fill the cache again.

    """
    # NOTE: making fget non-optional
    # no use case for caching if value is non-readable
    def __init__(self, fget, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        func_name = get_func_name(self.fget)
        if not hasattr(obj, '_voltcache'):
            setattr(obj, '_voltcache', {})
        if func_name not in obj._voltcache:
            obj._voltcache[func_name] = self.fget(obj)
        return obj._voltcache[func_name]

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError('can\'t set attribute')
        func_name = get_func_name(self.fset)
        if not hasattr(obj, '_voltcache'):
            setattr(obj, '_voltcache', {})
        self.fset(obj, value)
        obj._voltcache[func_name] = value

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError('can\'t delete attribute')
        func_name = get_func_name(self.fdel)
        del obj._voltcache[func_name]
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)


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


def console(text, color=None, is_bright=False, log_time=True,
            time_fmt='%H:%M:%S'):
    """Formats the given string for console display.

    If ``log_time`` is True, a time string (according to ``time_fmt``) is
    prepended to the given text.

    :param text: Text to display
    :type text: str
    :param color: Color to display. Possible values are black, red, green,
                  yellow, blue, violet, cyan, or grey.
    :type color: str
    :param is_bright: Whether to display bright text or not
    :type is_bright: bool
    :param log_time: Whether to include time information or not
    :type log_time: bool
    :param time_fmt: Format of the time string (following the directives of
                     :meth:`~datetime.datetime.strftime`)
    :type time_fmt: str
    :returns: Colored text for console display
    :rtype: str

    """
    if log_time:
        time_str = datetime.now().strftime(time_fmt)
        text = time_str + ' ' + text

    if is_bright and color is None:
        color = 'grey'

    if os.name != 'nt' and color is not None:
        brg = 'bold' if is_bright else 'normal'
        text = '\033[{bg};{fg}m{text}\033[m'.format(bg=BRIGHTNESS_MAP[brg],
                                                    fg=COLOR_MAP[color],
                                                    text=text)
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
