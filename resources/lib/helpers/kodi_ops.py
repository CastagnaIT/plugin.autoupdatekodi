# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Stefano Gottardo (plugin.autoupdatekodi)

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
import json
from contextlib import contextmanager
from functools import wraps

import xbmc
import xbmcgui

from resources.lib.globals import G
from resources.lib.helpers.logging import LOG


def json_rpc(method, params=None):
    """
    Executes a JSON-RPC in Kodi

    :param method: The JSON-RPC method to call
    :type method: string
    :param params: The parameters of the method call (optional)
    :type params: dict
    :returns: dict -- Method call result
    """
    request_data = {'jsonrpc': '2.0', 'method': method, 'id': 1,
                    'params': params or {}}
    request = json.dumps(request_data)
    LOG.debug('Executing JSON-RPC: {}', request)
    raw_response = xbmc.executeJSONRPC(request)
    # debug('JSON-RPC response: {}'.format(raw_response))
    response = json.loads(raw_response)
    if 'error' in response:
        raise IOError('JSONRPC-Error {}: {}'
                      .format(response['error']['code'],
                              response['error']['message']))
    return response['result']


def get_local_string(string_id):
    """Retrieve a localized string by its id"""
    src = xbmc if string_id < 30000 else G.ADDON
    return src.getLocalizedString(string_id)


def show_notification(msg, title='AutoUpdateKodi', time=3000):
    """Show a notification"""
    xbmc.executebuiltin('Notification({}, {}, {}, {})'
                        .format(title, msg, time, G.ICON))


def dlg_confirm(title, message):
    """Ask the user to confirm an operation"""
    return xbmcgui.Dialog().yesno(title, message)


def dlg_ok(title, message):
    return xbmcgui.Dialog().ok(title, message)


@contextmanager
def show_busy_dialog():
    """Context to show the busy dialog on the screen"""
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')


def show_busy_dialog_decorator(func):
    """Decorator to show the busy dialog on the screen"""
    # pylint: disable=missing-docstring
    @wraps(func)
    def busy_dialog_wrapper(*args, **kwargs):
        with show_busy_dialog():
            return func(*args, **kwargs)
    return busy_dialog_wrapper


def run_plugin_action(path, block=False):
    """Create an action that can be run with xbmc.executebuiltin in order to run a Kodi plugin specified by path.
    If block is True (default=False), the execution of code will block until the called plugin has finished running."""
    return 'RunPlugin({}, {})'.format(path, block)
