# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Stefano Gottardo (plugin.autoupdatekodi)

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
import resources.lib.helpers.kodi_ops as kodi_ops
from resources.lib.globals import G
from resources.lib.helpers.exceptions import InvalidPathError
from resources.lib.helpers.logging import LOG


def route(pathitems):
    """Route to the appropriate handler"""
    LOG.debug('Routing navigation request')
    root_handler = pathitems[0] if pathitems else G.MODE_DIRECTORY
    if root_handler == G.MODE_INSTALL:
        from resources.lib.navigation.install import install
        install(pathitems[1:], G.REQUEST_PARAMS)
    else:
        nav_handler = _get_nav_handler(root_handler, pathitems)
        _execute(nav_handler, pathitems[1:], G.REQUEST_PARAMS)
    return True


def _get_nav_handler(root_handler, pathitems):
    nav_handler = None
    if root_handler == G.MODE_DIRECTORY:
        from resources.lib.navigation.directory import Directory
        nav_handler = Directory
    if root_handler == G.MODE_ACTION:
        from resources.lib.navigation.actions import ActionsExecutor
        nav_handler = ActionsExecutor
    if not nav_handler:
        raise InvalidPathError('No root handler for path {}'.format('/'.join(pathitems)))
    return nav_handler


def _execute(executor_type, pathitems, params):
    """Execute an action as specified by the path"""
    try:
        executor = executor_type(params).__getattribute__(pathitems[0] if pathitems else 'root')
    except AttributeError as exc:
        raise InvalidPathError('Unknown action {}'.format('/'.join(pathitems))) from exc
    LOG.debug('Invoking action: {}', executor.__name__)
    executor(pathitems=pathitems[1:])


def run(argv):
    # Initialize globals right away to avoid stale values from the last addon invocation.
    # Otherwise Kodi's reuseLanguageInvoker will cause some really quirky behavior!
    # PR: https://github.com/xbmc/xbmc/pull/13814
    G.init_globals(argv)
    LOG.info('Started (Version {})'.format(G.VERSION_RAW))
    LOG.info('URL is {}'.format(G.URL))
    success = False
    try:
        pathitems = [part for part in G.REQUEST_PATH.split('/') if part]
        success = route(pathitems)
    except Exception as exc:
        import traceback
        LOG.error(traceback.format_exc())
        kodi_ops.dlg_ok('AutoUpdateKodi',
                        kodi_ops.get_local_string(30700).format(
                            '[{}] {}'.format(exc.__class__.__name__, exc)))
    if not success:
        from xbmcplugin import endOfDirectory
        endOfDirectory(handle=G.PLUGIN_HANDLE, succeeded=False)
    LOG.log_time_trace()
