# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Stefano Gottardo (plugin.autoupdatekodi)

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
import xbmcplugin

from resources.lib.globals import G

CONTENT_FOLDER = 'files'


def add_sort_methods(sort_type):
    if sort_type == 'sort_nothing':
        xbmcplugin.addSortMethod(G.PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_NONE)
    if sort_type == 'sort_label':
        xbmcplugin.addSortMethod(G.PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
    if sort_type == 'sort_label_ignore_folders':
        xbmcplugin.addSortMethod(G.PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
    if sort_type == 'sort_episodes':
        xbmcplugin.addSortMethod(G.PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_EPISODE)
        xbmcplugin.addSortMethod(G.PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(G.PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_VIDEO_TITLE)


def finalize_directory(items, content_type=CONTENT_FOLDER, sort_type='sort_nothing', title=None):
    """Finalize a directory listing. Add items, set available sort methods and content type"""
    if title:
        xbmcplugin.setPluginCategory(G.PLUGIN_HANDLE, title)
    xbmcplugin.setContent(G.PLUGIN_HANDLE, content_type)
    add_sort_methods(sort_type)
    xbmcplugin.addDirectoryItems(G.PLUGIN_HANDLE, items)


def end_of_directory(dir_update_listing, succeeded=True):
    # If dir_update_listing=True overwrite the history list, so we can get back to the main page
    xbmcplugin.endOfDirectory(G.PLUGIN_HANDLE,
                              succeeded=succeeded,
                              updateListing=dir_update_listing,
                              cacheToDisc=False)

