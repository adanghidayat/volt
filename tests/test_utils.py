# -*- coding: utf-8 -*-
"""
----------------
tests.test_utils
----------------

:copyright: (c) 2012-2014 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

import os
import sys
from os import path
from tempfile import NamedTemporaryFile, gettempdir
from types import ModuleType

from testfixtures import LogCapture

from volt.utils import get_func_name, cachedproperty, Loggable, path_import


# helper function for path_import testing
# returns a tuple of
# python file basename, NamedTemporaryFile object which does not auto-delete
def make_pyfile(contents=""):
    ntf = NamedTemporaryFile(mode='w', prefix='volt_', suffix='.py', delete=False)
    ntf.write(contents)
    return path.basename(ntf.name).replace('.py', ''), ntf


def test_get_func_name():
    # mock function to test
    def myfunc(a): pass
    assert get_func_name(myfunc) == 'myfunc'


def test_cachedproperty():
    # mock class with cachedproperty
    class CPTest(object):
        _cache_check = 0
        @cachedproperty
        def x(self):
            self._cache_check += 1
            return 1
    m = CPTest()
    # test before call ~ no cache
    assert not hasattr(m, '_cache')
    assert m._cache_check == 0
    # test first call ~ cache initialized
    assert m.x == 1
    assert hasattr(m, '_cache')
    assert m._cache_check == 1
    # test second call ~ function not called (counter not incremented)
    assert m.x == 1
    assert m._cache_check == 1


def test_loggable():
    l = Loggable()
    with LogCapture() as lc:
        l.logger.info('is info')
        l.logger.error('is error')
    logger_name = '{0}-{1}'.format(l.__class__.__name__, id(l))
    lc.check((logger_name, 'INFO', 'is info'),
             (logger_name, 'ERROR', 'is error'))


def test_path_import():
    mname, f = make_pyfile('x = 1\n')
    f.close()
    imported = path_import(mname, gettempdir())
    assert isinstance(imported, ModuleType)
    assert imported.x == 1
    os.unlink(f.name)


def test_path_import_multiple():
    mname, f = make_pyfile('x = 1\n')
    f.close()
    imported = path_import(mname, ["/tmp/maybe", gettempdir()])
    assert isinstance(imported, ModuleType)
    assert imported.x == 1
    os.unlink(f.name)


def test_path_import_reload():
    # first import
    mname, f = make_pyfile('x = 1\n')
    f.close()
    # NOTE: Disabling *.pyc creation since it interferes with our reloading
    #       In a non-test environment, we expect reimport is not done within
    #       such a short timespan that Python's import machinery detects the
    #       time difference and thus performs an actual reimport.
    sys.dont_write_bytecode = True
    imported = path_import(mname, gettempdir())
    assert imported.x == 1
    # second import ~ value changed
    with open(f.name, 'w') as target: target.write('x = 2\n')
    imported = path_import(mname, gettempdir())
    sys.dont_write_bytecode = False
    assert imported.x == 2
    os.unlink(f.name)
