# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Stefano Gottardo (plugin.autoupdatekodi)

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
import os
import time

import xbmc
import xbmcvfs
import xbmcgui

from resources.lib.globals import G
from urllib.request import urlretrieve

from resources.lib.helpers.kodi_ops import get_local_string
from resources.lib.helpers.logging import LOG


def download_file(url, dest_path, filename):
    start_time = time.time()
    dlg = xbmcgui.DialogProgress()
    dlg.create(G.ADDON_ID, get_local_string(30499))
    try:
        urlretrieve(url.rstrip('/'),
                    dest_path,
                    lambda num_blocks, block_size, file_size: reporthook(num_blocks, block_size, file_size,
                                                                         dlg, start_time, filename))
        return True
    except InterruptedError:
        LOG.error('Download interrupted by user')
    except Exception as exc:
        LOG.error('Download failed due to an error: {}', exc)
        raise Exception('Download failed') from exc
    finally:
        dlg.close()
    return False


def reporthook(num_blocks, block_size, file_size, dlg, start_time, filename):
    try:
        percent = min(num_blocks * block_size * 100 / file_size, 100)
        currently_downloaded = float(num_blocks) * block_size / (1024 * 1024)
        kbps_speed = num_blocks * block_size / (time.time() - start_time)
        eta = 0
        if kbps_speed > 0:
            eta = (file_size - num_blocks * block_size) / kbps_speed
            if eta < 0:
                eta = 0
        kbps_speed = kbps_speed / 1024
        eta = divmod(eta, 60)
        file_size_mb = float(file_size) / (1024 * 1024)
        status = '{:.02f} MB of {:.02f} MB '.format(currently_downloaded, file_size_mb)
        status += '{} {:.02f} Kb/s '.format(get_local_string(30501), kbps_speed)
        status += '{} {:02d}:{:02d}'.format(get_local_string(30502), int(eta[0]), int(eta[1]))
        dlg.update(int(percent), '{}[CR]{}[CR]{}'.format(get_local_string(30500), filename, status))
    except Exception as exc:
        LOG.error('[download_file] reporthook raised an error: {}', exc)
        dlg.update(100)
    if dlg.iscanceled():
        raise InterruptedError


def check_folder_path(path):
    """
    Check if folder path ends with path delimiter
    If not correct it (makes sure xbmcvfs.exists is working correct)
    """
    end = ''
    if '/' in path and not path.endswith('/'):
        end = '/'
    if '\\' in path and not path.endswith('\\'):
        end = '\\'
    return path + end


def folder_exists(path):
    """
    Checks if a given path exists
    :param path: The path
    :return: True if exists
    """
    return xbmcvfs.exists(check_folder_path(path))


def create_folder(path):
    """
    Create a folder if not exists
    :param path: The path
    """
    if not folder_exists(path):
        xbmcvfs.mkdirs(path)


def file_exists(file_path):
    """
    Checks if a given file exists
    :param file_path: File path to check
    :return: True if exists
    """
    return xbmcvfs.exists(xbmcvfs.translatePath(file_path))


def copy_file(from_path, to_path):
    """
    Copy a file to destination
    :param from_path: File path to copy
    :param to_path: Destination file path
    :return: True if copied
    """
    try:
        return xbmcvfs.copy(xbmcvfs.translatePath(from_path),
                            xbmcvfs.translatePath(to_path))
    finally:
        pass


def save_file_def(filename, content, mode='wb'):
    """
    Saves the given content under given filename, in the default add-on data folder
    :param filename: The filename
    :param content: The content of the file
    :param mode: optional mode options
    """
    save_file(os.path.join(G.DATA_PATH, filename), content, mode)


def save_file(file_path, content, mode='wb'):
    """
    Saves the given content under given filename path
    :param file_path: The filename path
    :param content: The content of the file
    :param mode: optional mode options
    """
    with xbmcvfs.File(xbmcvfs.translatePath(file_path), mode) as file_handle:
        file_handle.write(bytearray(content))


def load_file_def(filename, mode='rb'):
    """
    Loads the content of a given filename, from the default add-on data folder
    :param filename: The file to load
    :param mode: optional mode options
    :return: The content of the file
    """
    return load_file(os.path.join(G.DATA_PATH, filename), mode)


def load_file(file_path, mode='rb', encoder='utf-8'):
    """
    Loads the content of a given filename
    :param file_path: The file path to load
    :param mode: optional mode options
    :param encoder: the encoder
    :return: The content of the file
    """
    with xbmcvfs.File(xbmcvfs.translatePath(file_path), mode) as file_handle:
        return file_handle.readBytes().decode(encoder)


def delete_file_safe(file_path):
    if xbmcvfs.exists(file_path):
        try:
            xbmcvfs.delete(file_path)
        finally:
            pass


def delete_file(filename):
    file_path = xbmcvfs.translatePath(os.path.join(G.DATA_PATH, filename))
    try:
        xbmcvfs.delete(file_path)
    finally:
        pass


def list_dir(path):
    """
    List the contents of a folder
    :return: The contents of the folder as tuple (directories, files)
    """
    return xbmcvfs.listdir(path)


def delete_folder_contents(path, delete_subfolders=False):
    """
    Delete all files in a folder
    :param path: Path to perform delete contents
    :param delete_subfolders: If True delete also all subfolders
    """
    directories, files = list_dir(xbmcvfs.translatePath(path))
    for filename in files:
        xbmcvfs.delete(os.path.join(path, filename))
    if not delete_subfolders:
        return
    for directory in directories:
        delete_folder_contents(os.path.join(path, directory), True)
        # Give time because the system performs previous op. otherwise it can't delete the folder
        xbmc.sleep(80)
        xbmcvfs.rmdir(os.path.join(path, directory))


def delete_folder(path):
    """Delete a folder with all his contents"""
    delete_folder_contents(path, True)
    # Give time because the system performs previous op. otherwise it can't delete the folder
    xbmc.sleep(80)
    xbmcvfs.rmdir(xbmcvfs.translatePath(path))


def join_folders_paths(*args):
    """Join multiple folder paths in a safe way"""
    # Avoid the use of os.path.join, in some cases with special chars like % break the path
    return xbmcvfs.makeLegalFilename('/'.join(args))


def translate_path(path):
    return xbmcvfs.translatePath(path)
