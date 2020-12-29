# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Stefano Gottardo (plugin.autoupdatekodi)

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
import os
import subprocess
import time
from urllib.parse import quote, urlencode

from resources.lib.globals import G
from resources.lib.helpers.file_ops import join_folders_paths, load_file, save_file_def, translate_path


def build_url(pathitems=None, params=None, mode=None):
    """Build a plugin URL from pathitems and query parameters."""
    if not pathitems:
        raise ValueError('pathitems must be set.')
    path = '{netloc}/{path}/{qs}'.format(
        netloc=G.BASE_URL,
        path=_encode_path(mode, pathitems),
        qs=_encode_params(params))
    return path


def _expand_mode(mode):
    return [mode] if mode else []


def _encode_path(mode, pathitems):
    return quote(
        '/'.join(_expand_mode(mode) +
                 (pathitems or [])).encode('utf-8'))


def _encode_params(params):
    return ('?' + urlencode(params)) if params else ''


def run_manage_task(operation):
    """Create or delete the task"""
    # The "schtasks" command need the admin permissions to edit the tasks,
    # then we call windows API to elevate it as administrator (UAC will be prompt to the user)
    if operation == 'create':
        _generate_xml()
        args = '/create /xml "{xml_file_path}" /tn "Kodi_Install_NoUAC"'.format(
            xml_file_path=translate_path(join_folders_paths(G.DATA_PATH, 'Kodi_Install_NoUAC.xml')))
    else:
        args = '/delete /tn "Kodi_Install_NoUAC" /f'
    import ctypes
    shell32 = ctypes.windll.shell32
    # ShellExecuteW(
    #   HWND    hwnd,
    #   LPCWSTR lpOperation,
    #   LPCWSTR lpFile,
    #   LPCWSTR lpParameters,
    #   LPCWSTR lpDirectory,
    #   INT     nShowCmd)
    ret = shell32.ShellExecuteW(None, 'runas', 'schtasks', args, None, subprocess.SW_HIDE)
    if int(ret) <= 32:
        raise Exception('ShellExecuteW has failed')
    # The system need some time to apply the changes or the check_task will fail
    time.sleep(2)


def _generate_xml():
    # Read the original xml content
    content = load_file(join_folders_paths(G.ADDON_DATA_PATH, 'utils', 'Kodi_Install_NoUAC.xml'), encoder='utf-16-le')
    # Add the executable path
    content = content.replace('{}', join_folders_paths(G.INSTALLER_TEMP_PATH, G.INSTALLER_TEMP_NAME))
    # Save the new xml to user data
    save_file_def('Kodi_Install_NoUAC.xml', content.encode('utf-16-le'))


def check_task():
    """
    Check if the task is installed
    :return True if installed
    """
    with open(os.devnull, 'w') as dev_null:
        process = subprocess.Popen(
            ['schtasks', '/query', '/tn', 'Kodi_Install_NoUAC'],
            stdout=dev_null,
            stderr=dev_null,
            creationflags=subprocess.SW_HIDE)
        return_code = process.wait()
        return return_code == 0  # if 0 means the task is installed
