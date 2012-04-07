# -*- coding: utf-8 -*-
"""
--------------------
volt.engine.builtins
--------------------

Volt built-in base engines and units.

:copyright: (c) 2012 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

from __future__ import with_statement
import glob
import os

from volt.engine.core import _RE_DELIM, Engine, Unit
from volt.exceptions import ContentError
from volt.utils import lazyproperty


class TextUnit(Unit):

    """Class representation of text resources.

    This unit represents resources whose metadata (header) is contained
    in the same file as the content. Some examples of resources like this 
    is a single blog post or a single plain page. 

    """
    def __init__(self, fname, config):
        """Initializes TextUnit.

        fname -- Absolute path to the source file.
        config -- Config object containing unit options.

        """
        super(TextUnit, self).__init__(config)
        self._id = fname

        # parse header and content and check fields
        self.parse_source(self.id)
        self.check_required(self.config.REQUIRED)

    @property
    def id(self):
        return self._id

    def parse_source(self, file_path):
        """Parses the header and content from the source file.

        file_path -- Absolute path to source text file.

        """
        with self.open_text(file_path) as source:
            # open file and remove whitespaces
            read = filter(None, _RE_DELIM.split(source.read()))
            # header should be parsed into dict
            self.parse_header(read.pop(0))
            # content is everything else after header
            self.content = read.pop(0).strip()

        # if slug is not set in header, set it now
        if not hasattr(self, 'slug'):
            self.slug = self.slugify(self.title)

        # and set global values
        for field in self.config.GLOBAL_FIELDS:
            if not hasattr(self, field):
                setattr(self, field, self.config.GLOBAL_FIELDS[field])

    def parse_header(self, header_string):
        """Returns a dictionary of header field values.

        header_string -- String of header lines.

        """
        header_lines = [x.strip() for x in header_string.strip().split('\n')]
        for line in header_lines:
            if not ':' in line:
                    raise ContentError("Line '%s' in '%s' is not a proper "
                                       "header entry." % (line, self.id))
            field, value = [x.strip() for x in line.split(':', 1)]

            self.check_protected(field, self.config.PROTECTED)

            if field == 'slug':
                value = self.slugify(value)

            elif field in self.config.FIELDS_AS_LIST:
                value = self.as_list(value, self.config.LIST_SEP)

            elif field in self.config.FIELDS_AS_DATETIME:
                value = self.as_datetime(value, \
                        self.config.CONTENT_DATETIME_FORMAT)

            setattr(self, field.lower(), value)

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, os.path.basename(self.id))


class TextEngine(Engine):

    """Engine class for processing text units."""

    @lazyproperty
    def units(self):
        """Units whose source are text files in the filesystem."""
        # get absolute paths of content files
        targets = glob.iglob(os.path.join(self.config.CONTENT_DIR, '*'))
        files = (x for x in targets if os.path.isfile(x))
        units = [TextUnit(fname, self.config) for fname in files]

        return units
