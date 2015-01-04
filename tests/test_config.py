# -*- coding: utf-8 -*-
"""
-----------------
tests.test_config
-----------------

:copyright: (c) 2012-2014 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

import os
import shutil
import sys
import tempfile
from os import path
from types import ModuleType
from uuid import uuid4

import pytest

from volt.exceptions import ConfigNotFoundError
from volt.config import SiteConfigContainer, SiteConfig


# helper method for setting up config tests
def setup_mock_dirs(conf_contents=''):
    uuid = str(uuid4())
    d = path.join(tempfile.gettempdir(), 'volt-' + uuid)
    assert not path.exists(d)
    os.makedirs(d)
    old_dir = os.getcwd()
    os.chdir(d)
    f = path.join(d, 'voltapp.py')
    with open(f, 'w') as target:
        target.write(conf_contents)
    return old_dir, f


def test_siteconfigcontainer():
    # setup files and directories
    old_dir, f = setup_mock_dirs('X = 1\n')
    d = path.dirname(f)
    # actual testing
    scc = SiteConfigContainer()
    assert scc['X'] == 1
    # cleanup
    os.chdir(old_dir)
    shutil.rmtree(d)


def test_siteconfigcontainer_setitem():
    # setup files and directories
    old_dir, f = setup_mock_dirs('X = 1\n')
    d = path.dirname(f)
    # actual testing
    scc = SiteConfigContainer()
    scc['X'] = 2
    assert scc['X'] == 2
    # cleanup
    os.chdir(old_dir)
    shutil.rmtree(d)


def test_siteconfigcontainer_delitem():
    # setup files and directories
    old_dir, f = setup_mock_dirs('X = 1\n')
    d = path.dirname(f)
    # actual testing
    scc = SiteConfigContainer()
    del scc['X']
    with pytest.raises(KeyError):
        scc['X']
    # cleanup
    os.chdir(old_dir)
    shutil.rmtree(d)


def test_siteconfigcontainer_contains():
    # setup files and directories
    old_dir, f = setup_mock_dirs('X = 1\n')
    d = path.dirname(f)
    # actual testing
    scc = SiteConfigContainer()
    assert 'X' in scc
    # cleanup
    os.chdir(old_dir)
    shutil.rmtree(d)


def test_siteconfigcontainer_reset():
    # setup files and directories
    old_dir, f = setup_mock_dirs('X = 1\n')
    d = path.dirname(f)
    sys.dont_write_bytecode = True
    # actual testing
    scc = SiteConfigContainer()
    assert scc['X'] == 1
    with open(f, 'w') as target:
        target.write('X = 2\n')
    scc.reset()
    assert scc['X'] == 2
    # cleanup
    sys.dont_write_bytecode = False
    os.chdir(old_dir)
    shutil.rmtree(d)


def test_siteconfig():
    # setup files and directories
    old_dir, f = setup_mock_dirs('X = 1\n')
    d = path.dirname(f)
    # actual testing
    from volt.config import defaults
    sc = SiteConfig()
    assert sc['X'] == 1
    assert sc['_ROOT_DIR'] == path.dirname(f)
    assert sc['SITE_URL'] == defaults.SITE_URL
    # cleanup
    os.chdir(old_dir)
    shutil.rmtree(d)


@pytest.mark.parametrize('config,user_dir,expected', [
    ({'a': 1}, '/tmp',
        {'a': 1}),
    ({'a': 1, 'URL': 'http://site.com/'}, '/tmp',
        {'a': 1, 'URL': 'http://site.com'}),
    ({'a': 1, 'MY_URL': 'http://site.com/'}, '/tmp',
        {'a': 1, 'MY_URL': 'http://site.com'}),
    ({'a': 1, 'OUT_DIR': 'site'}, '/tmp/',
        {'a': 1, 'OUT_DIR': '/tmp/site'}),
    ({'a': 1, 'OUT_DIR': 'site/'}, '/tmp/',
        {'a': 1, 'OUT_DIR': '/tmp/site'}),
    ({'a': 1, 'OUT_DIR': '/my/own/path/'}, '/tmp/',
        {'a': 1, 'OUT_DIR': '/my/own/path'}),
    ({'a': 1, 'OUT_DIR': '/my/own/path'}, '/tmp/',
        {'a': 1, 'OUT_DIR': '/my/own/path'}),
])
def test_siteconfig_adjust_config(config, user_dir, expected):
    assert SiteConfig._adjust_config(config, user_dir) == expected


def test_siteconfig_load_config():
    mock_mod = ModuleType("mock_mod")
    mock_entries = {
        'A': 1, '_B': 'string', 'C': {2: 3}, 'D': [4], '_E': None,
        '_a': 0, '_b': '',
    }
    for key, value in mock_entries.items():
        setattr(mock_mod, key, value)
    expected = {
        'A': 1, '_B': 'string', 'C': {2: 3}, 'D': [4], '_E': None,
    }
    assert SiteConfig._load_config(mock_mod) == expected


def test_siteconfig_get_root_dir():
    # setup files and directories
    old_dir, f = setup_mock_dirs('X = 1\n')
    d = path.dirname(f)
    with open(f, 'w') as target:
        target.write('x = 1\n')
    assert SiteConfig._get_root_dir('voltapp.py') == d
    os.chdir(old_dir)
    shutil.rmtree(d)


def test_siteconfig_get_root_dir_two_levels():
    uuid = str(uuid4())
    d = path.join(tempfile.gettempdir(), 'volt-' + uuid)
    d2 = path.join(d, 'a', 'b')
    assert not path.exists(d)
    os.makedirs(d2)
    f = path.join(d, 'voltapp.py')
    with open(f, 'w') as target:
        target.write('x = 1\n')
    assert SiteConfig._get_root_dir('voltapp.py', d2) == d
    shutil.rmtree(d)


def test_siteconfig_get_root_dir_missing():
    uuid = str(uuid4())
    d = path.join(tempfile.gettempdir(), 'volt-' + uuid)
    assert not path.exists(d)
    os.makedirs(d)
    with pytest.raises(ConfigNotFoundError) as exc:
        SiteConfig._get_root_dir('voltapp.py', d) == d
    assert str(exc.value) == 'Failed to find Volt config file.'
    shutil.rmtree(d)
