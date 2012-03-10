# -*- coding: utf-8 -*-
"""
-----------------
volt.engine.plain
-----------------

Volt Plain Engine.

The plain engine takes text files as resources and writes single web pages.

:copyright: (c) 2012 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""


from volt.config import CONFIG
from volt.engines import Engine


__name__ = 'plain'


class PlainEngine(Engine):
    """Class for processing plain web pages.
    """

    def activate(self):
        # parse plain page units
        self.units = self.process_text_units(CONFIG.PLAIN, CONFIG.PLAIN.CONTENT_DIR)

    def dispatch(self):
        # write them according to template
        self.write_units(CONFIG.PLAIN.UNIT_TEMPLATE_FILE)
