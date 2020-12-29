# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Stefano Gottardo (plugin.autoupdatekodi)

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
import os
import re
import xbmcgui

import resources.lib.helpers.kodi_ops as kodi_ops
from resources.lib.globals import G
from resources.lib.helpers.file_ops import folder_exists
from resources.lib.helpers.logging import LOG
from resources.lib.helpers.misc import build_url
from resources.lib.navigation.directory_helper import finalize_directory, end_of_directory

BUILDS = {
    'nightlies': 'Nightlies',
    'releases': 'Releases',
    'snapshots': 'Snapshots',
    'test-builds': 'Test builds'
}

ARCHITECTURES = {
    'win32': 'Windows 32 bit',
    'win64': 'Windows 64 bit'
}


class Directory(object):
    """Directory listings"""

    def __init__(self, params):
        LOG.debug('Initializing "Directory" with params: {}', params)
        self.params = params

    def is_local(self):
        return self.params.get('is_local', 'False') == 'True'

    def root(self, pathitems=None):  # pylint: disable=unused-argument
        self.builds()

    def builds(self, pathitems=None):  # pylint: disable=unused-argument
        directory_items = []
        for build_name, label in BUILDS.items():
            pathitems_value = ['architecture', build_name, 'windows']
            if self.is_local() and not _local_folder_exists(pathitems_value[1:]):
                continue
            directory_items.append(create_listitem(pathitems_value,
                                                   is_folder=True, label=label, is_local=self.is_local()))
        if not self.is_local():
            directory_items.append(create_listitem(['local_builds'],
                                                   is_folder=True, label='Downloaded', is_local=True,
                                                   art_thumb='DefaultAddonsRepo.png'))
        finalize_directory(directory_items, title='Builds')
        end_of_directory(False)

    # This is used only to differentiate the Kodi navigator path
    def local_builds(self, pathitems=None):
        self.builds(pathitems)

    def architecture(self, pathitems=None):
        directory_items = []
        for arch_name, label in ARCHITECTURES.items():
            pathitems_value = ['subfolder'] + pathitems + [arch_name]
            if self.is_local() and not _local_folder_exists(pathitems_value[1:]):
                continue
            directory_items.append(create_listitem(pathitems_value,
                                                   is_folder=True, label=label, is_local=self.is_local()))
        finalize_directory(directory_items, title='Architecture')
        end_of_directory(False)

    def subfolder(self, pathitems=None):
        G.FILES_LIST.clear()
        add_github_menu = 'master' in pathitems and 'nightlies' in pathitems and not self.is_local()
        folder_list = []
        file_list = []
        if self.is_local():
            current_path = G.DOWNLOADS_PATH + '\\'.join(pathitems)
            for item in os.listdir(current_path):
                if os.path.isfile(os.path.join(current_path, item)):
                    file_list.append(item)
                else:
                    folder_list.append(item)
        else:
            url = G.MIRROR_BASE_URL + '/'.join(pathitems) + '/'
            from urllib.request import Request, urlopen
            page_response = urlopen(Request(url), timeout=10).read()
            # Find the folders in the webpage
            folder_list = re.findall(r'href="([^\/"\.]+)\/"', page_response.decode())
            # Find the executables names in the webpage
            file_list = re.findall(r'href="([^"]*\.exe)"', page_response.decode())
        directory_items = []
        # Create the directory items
        for folder_name in folder_list:
            pathitems_value = ['subfolder'] + pathitems + [folder_name]
            directory_items.append(create_listitem(pathitems_value,
                                                   is_folder=True, label=folder_name, is_local=self.is_local()))
        # Create the directory file items
        for filename in file_list:
            # Memorize filename in to globals, allow to find other info from items for github operations
            G.FILES_LIST.append(filename)
            pathitems_value = pathitems + [filename]
            if add_github_menu:
                # Add "View github history" menu
                menu_item = [(kodi_ops.get_local_string(30080),
                             kodi_ops.run_plugin_action(
                                 build_url(['get_git_history', filename], mode=G.MODE_ACTION)))]
            else:
                menu_item = None
            directory_items.append(create_listitem(pathitems_value,
                                                   is_folder=False, label=filename, menu_items=menu_item,
                                                   is_local=self.is_local(),
                                                   art_thumb='DefaultAddon.png'))
        title = ARCHITECTURES.get(pathitems[-1], pathitems[-1])
        finalize_directory(directory_items, title=title)
        end_of_directory(False)


def create_listitem(pathitems=None, is_folder=False, label=None, menu_items=None, is_local=False, art_thumb=None):
    list_item = xbmcgui.ListItem(label=label, offscreen=True)
    list_item.setContentLookup(False)
    list_item.setInfo('video', {})
    properties = {
        'isFolder': is_folder
    }
    list_item.setProperties(properties)
    list_item.addContextMenuItems(menu_items or [])
    if art_thumb:
        list_item.setArt({'thumb': art_thumb})
    if is_local:
        params = {'is_local': True}
    else:
        params = None
    return build_url(pathitems=pathitems,
                     mode=G.MODE_DIRECTORY if is_folder else G.MODE_INSTALL,
                     params=params), list_item, is_folder


def _local_folder_exists(pathitems):
    return folder_exists(G.DOWNLOADS_PATH + '\\'.join(pathitems))
