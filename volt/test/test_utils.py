# -*- coding: utf-8 -*-
"""
--------------------
volt.test.test_utils
--------------------

Tests for the volt.utils module.

:copyright: (c) 2012 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

import os
import sys
import unittest
from inspect import getabsfile

from volt.utils import path_import, get_func_name
from volt.test import INSTALL_DIR, USER_DIR


class PathImportCases(unittest.TestCase):

    def test_path_import_string(self):
        path = os.path.join(INSTALL_DIR, 'engine', 'builtins')
        mod = path_import('in_install', path)
        mod_path = os.path.join(INSTALL_DIR, 'engine', 'builtins', 'in_install.py')
        self.assertEqual(getabsfile(mod), mod_path)

    def test_path_import_list(self):
        user_path = os.path.join(USER_DIR, 'engines')
        install_path = os.path.join(INSTALL_DIR, 'engine', 'builtins')
        paths = [user_path, install_path]
        mod = path_import('in_both', paths)
        mod_path = os.path.join(USER_DIR, 'engines', 'in_both.py')
        self.assertEqual(getabsfile(mod), mod_path)


class GetFuncNameCases(unittest.TestCase):

    def test_get_func_name(self):
        def myfunc(): pass
        self.assertEqual(get_func_name(myfunc), 'myfunc')
