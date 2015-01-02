from types import ModuleType

import pytest

from volt.config import SiteConfig


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
        'A': 1, '_B': 'string', 'C': {2:3}, 'D': [4], '_E': None,
        '_a': 0, '_b': '',
    }
    for key, value in mock_entries.items():
        setattr(mock_mod, key, value)
    expected = {
        'A': 1, '_B': 'string', 'C': {2:3}, 'D': [4], '_E': None,
    }
    assert SiteConfig._load_config(mock_mod) == expected
