# -*- coding: utf-8 -*-
"""
--------------------
volt.config.defaults
--------------------

Volt default configuration values.

:copyright: (c) 2012-2014 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

# Changing values in this Config is possible but not recommended


## Volt configurations

# User config file name
# Used to determine project root
_USER_CONF = 'voltapp.py'

# Directory paths for content files, templates, assets
# and generated site relative to a project root
_CONTENT_DIR = 'contents'
_TEMPLATE_DIR = 'templates'
_ASSET_DIR = 'assets'
_SITE_DIR = 'site'


## Default site configurations

# Site URL, used for generating absolute URLs
SITE_URL = 'http://localhost:8000'

# Engines used in generating the site
# Defaults to none
ENGINES = []

# Extra pages to write that are not controlled by an engine
# Examples: 404.html, index.html (if not already written by an engine)
# The tuple should list template names of these pages, which should
# be present in the default template directory
SITE_PAGES = {}

# Boolean to set if output file names should all be 'index.html' or vary
# according to the last token in its self.permalist attribute
# index.html-only outputs allows for nice URLS without fiddling too much
# with .htaccess
INDEX_HTML_ONLY = True

# Logging level
# If set to 10, Volt will write logs to a file
# 30 is logging.WARNING
LOG_LEVEL = 30

# String replacement scheme for slugs
# Dictionary, key is the string to replace, value is the replacement string
# This is used to replace non-ascii consonants or vowels in a slug with
# their ascii equivalents, so the slug meaning is preserved.
# For example {u'ß': 'ss'}, would transfrom the slug "viel-Spaß" to
# "viel-spass" instead of "viel-spa", preserving its meaning
SLUG_CHAR_MAP = {}

# Jinja2 filter functions
FILTERS = []

# Jinja2 test functions
TESTS = []
