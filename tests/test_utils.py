# -*- coding: utf-8 -*-
"""
----------------
tests.test_utils
----------------

:copyright: (c) 2012-2014 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

import os
import stat
import sys
from datetime import datetime
from os import path
from tempfile import NamedTemporaryFile, gettempdir
from types import ModuleType
from uuid import uuid4

import pytest
from testfixtures import LogCapture, OutputCapture

from volt.utils import get_func_name, cachedproperty, Loggable, path_import, \
    console, write_file


# helper function for path_import testing
# returns a tuple of
# python file basename, NamedTemporaryFile object which does not auto-delete
def make_pyfile(contents=""):
    ntf = NamedTemporaryFile(mode='w', prefix='volt_', suffix='.py',
                             delete=False)
    ntf.write(contents)
    return path.basename(ntf.name).replace('.py', ''), ntf


def test_get_func_name():
    # mock function to test
    def myfunc(a):
        pass
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
    assert not hasattr(m, '_voltcache')
    assert m._cache_check == 0
    # test first call ~ cache initialized
    assert m.x == 1
    assert hasattr(m, '_voltcache')
    assert m._cache_check == 1
    # test second call ~ function not called (counter not incremented)
    assert m.x == 1
    assert m._cache_check == 1


def test_cachedproperty_get():

    # mock class with cachedproperty
    class CPTest(object):
        _cache_check = 0

        @cachedproperty
        def x(self):
            self._cache_check += 1
            return 1

    class CPTest2(CPTest):
        _cache_check_sub = 0

        @CPTest.x.getter
        def x(self):
            self._cache_check_sub += 1
            return 'a'

    m = CPTest2()
    # test before call ~ no cache
    assert not hasattr(m, '_voltcache')
    assert m._cache_check == 0
    assert m._cache_check_sub == 0
    # test first call ~ cache initialized but called from subclass
    assert m.x == 'a'
    assert hasattr(m, '_voltcache')
    print(m._voltcache)
    assert m._cache_check == 0
    assert m._cache_check_sub == 1
    # test second call ~ function not called (counter not incremented)
    assert m.x == 'a'
    assert m._cache_check == 0
    assert m._cache_check_sub == 1


def test_cachedproperty_only_get():
    class CPTest(object):
        @cachedproperty
        def x(self):
            return 1
    m = CPTest()
    with pytest.raises(AttributeError):
        m.x = 2
    with pytest.raises(AttributeError):
        del m.x


def test_cachedproperty_set():

    class CPTest(object):
        _x_set = 0

        @cachedproperty
        def x(self):
            return 1

        @x.setter
        def x(self, value):
            self._x_set += 1

    m = CPTest()
    assert m.x == 1
    assert m._voltcache['x'] == 1
    assert m._x_set == 0
    m.x = 2
    assert m.x == 2
    assert m._voltcache['x'] == 2
    assert m._x_set == 1


def test_cachedproperty_set_bypass():

    class CPTest(object):
        _x_get = 0

        @cachedproperty
        def x(self):
            self._x_get += 1
            return 1

        @x.setter
        def x(self, value):
            pass

    m = CPTest()
    # bypass getter by assigning value
    m.x = 99
    assert m.x == 99
    assert m._voltcache['x'] == 99
    assert m._x_get == 0


def test_cachedproperty_del():

    class CPTest(object):
        _x_del = 0

        @cachedproperty
        def x(self):
            return 1

        @x.deleter
        def x(self):
            self._x_del += 1

    m = CPTest()
    assert m.x == 1
    assert m._voltcache['x'] == 1
    del m.x
    assert 'x' not in m._voltcache
    assert m.x == 1


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
    with open(f.name, 'w') as target:
        target.write('x = 2\n')
    imported = path_import(mname, gettempdir())
    sys.dont_write_bytecode = False
    assert imported.x == 2
    os.unlink(f.name)


def test_console():
    time_fmt = '%H:%M:%S'
    with OutputCapture() as oc:
        console('x')
        console('y')
    captured = oc.captured.strip().split(os.linesep)
    assert len(captured) == 2
    time1, text1 = captured[0].split(' ')
    assert datetime.strptime(time1, time_fmt)
    assert text1 == 'x'
    time2, text2 = captured[1].split(' ')
    assert datetime.strptime(time2, time_fmt)
    assert text2 == 'y'


def test_console_custom_time():
    time_fmt = '%H:%M'
    with OutputCapture() as oc:
        console('x', time_fmt=time_fmt)
    captured = oc.captured.strip().split(os.linesep)
    assert len(captured) == 1
    time, text = captured[0].split(' ')
    assert datetime.strptime(time, time_fmt)
    assert text == 'x'


def test_console_no_log_time():
    with OutputCapture() as oc:
        console('a', log_time=False)
        console('b', log_time=False)
    oc.compare('\n'.join(['a', 'b']))


def test_console_bright():
    # disable time logging to make for easier comparison
    with OutputCapture() as oc:
        console('p', is_bright=True, log_time=False)
    oc.compare('\033[01;37mp\033[m')


def test_console_color():
    # disable time logging to make for easier comparison
    with OutputCapture() as oc:
        console('q', color='green', log_time=False)
    oc.compare('\033[00;32mq\033[m')


def test_write_file_existing_dir():
    f = path.join(gettempdir(), 'volt-' + str(uuid4()))
    try:
        write_file(f, 'a')
        with open(f, 'r') as src:
            assert src.read() == 'a'
    finally:
        if path.exists(f):
            os.unlink(f)


def test_write_file_nonexisting_dir():
    uuid = str(uuid4())
    f = path.join(gettempdir(), uuid, 'volt-' + uuid)
    assert not path.exists(path.dirname(f))
    try:
        write_file(f, 'a')
        with open(f, 'r') as src:
            assert src.read() == 'a'
    finally:
        if path.exists(f):
            os.unlink(f)


def test_write_file_nonmissing_ioerror():
    uuid = str(uuid4())
    d = path.join(gettempdir(), uuid)
    assert not path.exists(d)
    os.makedirs(d)
    # make dir read-only to trigger IOError not caused by missing file
    os.chmod(d, stat.S_IREAD)
    f = path.join(d, 'volt-' + uuid)
    with pytest.raises(IOError):
        write_file(f, 'a')
    os.rmdir(d)
