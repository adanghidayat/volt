# -*- coding: utf-8 -*-
"""
-----------------
volt.config.tests
-----------------

Default Jinja2 tests.

:copyright: (c) 2012-2014 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

from past.builtins import basestring


def activatedin(name, config):
    """Jinja2 test for checking whether an engine, plugin, or widget is active.

    :param name: Name or list of names of engine, plugin, or widget
    :type name: str or [str]
    :param config: UnifiedConfigContainer instance, passed as an argument at
        render time so the values are already primed
    :type config: UnifiedConfigContainer
    :returns: activation status of the given engine, plugin, or widget
    :rtype: bool

    Example usage:
        {{ if "css_minifier" is activatedin CONFIG }}
            <p>CSS Minifier plugin is active</p>
        {{ endif }}

    or, to check whether several engines/plugins/widgets are active:
        {{ if ["css_minifier", "blog"] is activatedin CONFIG }}
            <p>CSS Minifier plugin and Blog engine are active</p>
        {{ endif }}
    """
    # no need to collect _actives if it's already set
    try:
        actives = config._actives
    # _actives not set, then compute it and do a setattr
    except AttributeError:
        engines = config.SITE.ENGINES
        plugins = config.SITE.PLUGINS
        widgets = config.SITE.WIDGETS

        for conf in config:
            # we don't care if the Config object doesn't have any plugins
            # or widgets (e.g. CONFIG.VOLT), so we default to an empty tuple
            plugins += getattr(conf, 'PLUGINS', tuple())
            widgets += getattr(conf, 'WIDGETS', tuple())

        actives = set(engines + plugins + widgets)
        setattr(config, '_actives', actives)

    if isinstance(name, basestring):
        return any([name in x for x in actives])

    results = []
    for item in name:
        results.append(any([item in x for x in actives]))
    return all(results)

