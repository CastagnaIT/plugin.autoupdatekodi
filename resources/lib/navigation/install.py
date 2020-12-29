# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Stefano Gottardo (plugin.autoupdatekodi)

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
from resources.lib.globals import G
from resources.lib.helpers.file_ops import (join_folders_paths, download_file, folder_exists, create_folder, copy_file,
                                            file_exists)
from resources.lib.helpers.logging import LOG
import resources.lib.helpers.kodi_ops as kodi_ops
import resources.lib.helpers.misc as misc

import time
import subprocess


def install(pathitems, params):
    LOG.info('Start install Kodi "{}" (params "{}")', pathitems[-1], params)
    use_task_scheduler = G.ADDON.getSettingBool('usetaskscheduler')
    save_downloads = G.ADDON.getSettingBool('save_downloads')
    # Download the file
    if not kodi_ops.dlg_confirm(kodi_ops.get_local_string(30070),
                                kodi_ops.get_local_string(30071).format(pathitems[-1])):
        return
    # Check if the task is installed
    if use_task_scheduler and not misc.check_task():
        kodi_ops.dlg_ok(kodi_ops.get_local_string(30070),
                        kodi_ops.get_local_string(30072))
        return
    # Check if destination path exist
    if not folder_exists(G.INSTALLER_TEMP_PATH):
        create_folder(G.INSTALLER_TEMP_PATH)
    # Check if the setup installer is already downloaded
    dwn_filepath = join_folders_paths(G.DOWNLOADS_PATH, '/'.join(pathitems[:-1]), pathitems[-1])
    # Temp file path will be used by the Windows Task scheduled
    temp_filepath = join_folders_paths(G.INSTALLER_TEMP_PATH, G.INSTALLER_TEMP_NAME)
    if params.get('is_local', 'False') == 'True':
        # Get the file to install from "downloads" folder
        if not file_exists(dwn_filepath):
            raise FileExistsError('The file {] not exists'.format(pathitems[:-1]))
        copy_file(dwn_filepath, temp_filepath)
    else:
        # Download the file
        if save_downloads and file_exists(dwn_filepath):
            # Copy the existing file to the temp file path
            copy_file(dwn_filepath, temp_filepath)
        else:
            # Download the setup installer file
            url_file_path = '/'.join(pathitems)
            if not download_file(G.MIRROR_BASE_URL + url_file_path,
                                 temp_filepath,
                                 pathitems[-1]):
                # Download cancelled
                kodi_ops.show_notification(kodi_ops.get_local_string(30073))
                return
            # Save the setup installer file
            if save_downloads:
                copy_file(temp_filepath, dwn_filepath)
    with kodi_ops.show_busy_dialog():
        # Run the "AutoUpdateWorker" bash script
        _run_auto_update_worker(use_task=use_task_scheduler)
        # Wait a bit before close Kodi,
        # the bash script have to read the executable path from the Kodi process before continue
        time.sleep(2)
        kodi_ops.json_rpc('Application.Quit')


def _run_auto_update_worker(use_task=False):
    arg = 'useTask' if use_task else join_folders_paths(G.INSTALLER_TEMP_PATH, G.INSTALLER_TEMP_NAME)
    auw_path = join_folders_paths(G.ADDON_DATA_PATH, 'utils', 'AutoUpdateWorker.bat')
    # CREATE_NEW_CONSOLE allow run the process separately and release immediately python
    subprocess.Popen([auw_path, arg], creationflags=subprocess.CREATE_NEW_CONSOLE)
