# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Stefano Gottardo (plugin.autoupdatekodi)

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
import json
import re
from urllib.request import Request, urlopen

import xbmcgui

import resources.lib.helpers.kodi_ops as kodi_ops
import resources.lib.helpers.misc as misc
from resources.lib.globals import G
from resources.lib.helpers.file_ops import delete_folder_contents
from resources.lib.helpers.logging import LOG


class ActionsExecutor(object):
    """Execute add-on actions"""

    def __init__(self, params):
        LOG.debug('Initializing "ActionsExecutor" with params: {}', params)
        self.params = params

    def add_task(self, pathitems=None):  # pylint: disable=unused-argument
        if not kodi_ops.dlg_confirm(kodi_ops.get_local_string(30050),
                                    kodi_ops.get_local_string(30042)):
            return
        with kodi_ops.show_busy_dialog():
            if misc.check_task():
                self.delete_task()
            misc.run_manage_task('create')
            if not misc.check_task():
                # Task creation failed
                kodi_ops.dlg_ok(kodi_ops.get_local_string(30050), kodi_ops.get_local_string(30045))
                return
            kodi_ops.show_notification(kodi_ops.get_local_string(30044))

    def delete_task(self, pathitems=None):  # pylint: disable=unused-argument
        if not kodi_ops.dlg_confirm(kodi_ops.get_local_string(30051),
                                    kodi_ops.get_local_string(30043)):
            return
        with kodi_ops.show_busy_dialog():
            if misc.check_task():
                misc.run_manage_task('delete')
            if misc.check_task():
                # Task deletion failed
                kodi_ops.show_notification(kodi_ops.get_local_string(30047))
                return
            kodi_ops.show_notification(kodi_ops.get_local_string(30046))

    def delete_downloads(self, pathitems=None):  # pylint: disable=unused-argument
        if kodi_ops.dlg_confirm(kodi_ops.get_local_string(30074),
                                kodi_ops.get_local_string(30075)):
            with kodi_ops.show_busy_dialog():
                delete_folder_contents(G.DOWNLOADS_PATH, delete_subfolders=True)

    def get_git_history(self, pathitems=None):
        # Query github data
        filename = pathitems[0]
        data = _get_git_history(filename)
        # Generate list from github data
        list_items = []
        for commit_data in reversed(data['commits']):
            # Show only "Merge" commits
            if not commit_data['commit']['message'].startswith('Merge'):
                continue
            list_item = xbmcgui.ListItem(label=_generate_label_from_commit(commit_data),
                                         offscreen=True)
            list_item.setContentLookup(False)
            list_items.append(list_item)
        # Show dialog
        index = 0
        while index != -1:
            # Show "Merged PR's of: ..." dialog
            index = xbmcgui.Dialog().select(kodi_ops.get_local_string(30081).format(filename),
                                            list_items,
                                            preselect=index)
            if not index == -1:
                # Get PR number
                pr_number = re.findall(r'#(\d+)', list_items[index].getLabel())
                xbmcgui.Dialog().textviewer(list_items[index].getLabel(), _get_pr_details(pr_number))

    def use_task_info(self, pathitems=None):  # pylint: disable=unused-argument
        xbmcgui.Dialog().ok(kodi_ops.get_local_string(30040), kodi_ops.get_local_string(30041))


def _generate_label_from_commit(data):
    list_header_text = data['commit']['message'].split('\n')
    # Get PR number
    pr_number = re.findall(r'#(\d+)', list_header_text[0])
    return '#{} {}'.format(pr_number[0], list_header_text[2])


@kodi_ops.show_busy_dialog_decorator
def _get_pr_details(pr_number):
    commits_childs_headers = []
    text = ''
    if pr_number:
        # Get PR data
        url = 'https://api.github.com/repos/xbmc/xbmc/pulls/{}'.format(pr_number[0])
        page_response = make_http_request(url)
        pr_data = json.loads(page_response.decode())
        text = pr_data['title'] + '[CR][CR]'
        text += 'DESCRIPTION:[CR]'
        desc = re.sub(r'<!--.*-->', '', pr_data['body'])  # delete hidden comments
        text += desc + '[CR][CR]'
        # Get commits data
        url = 'https://api.github.com/repos/xbmc/xbmc/pulls/{}/commits'.format(pr_number[0])
        page_response = make_http_request(url)
        commits = json.loads(page_response.decode())
        for commit_data in reversed(commits):
            commits_childs_headers.append(commit_data['commit']['message'].split('\n')[0])
    text += 'COMMITS:[CR]'
    text += '[CR]'.join(commits_childs_headers)
    return text


@kodi_ops.show_busy_dialog_decorator
def _get_git_history(selected_file):
    selected_commit_sha = _get_commit_sha(selected_file)
    try:
        previous_file = G.FILES_LIST[G.FILES_LIST.index(selected_file) + 1]
    except (ValueError, IndexError):
        previous_file = None
    if previous_file:
        previous_commit_sha = _get_commit_sha(previous_file)
    else:
        previous_commit_sha = 'HEAD'
    url = 'https://api.github.com/repos/xbmc/xbmc/compare/{}...{}'.format(previous_commit_sha, selected_commit_sha)
    page_response = make_http_request(url)
    return json.loads(page_response.decode())


def _get_commit_sha(filename):
    return filename.split('-')[2]


def make_http_request(url):
    LOG.debug('Execute HTTP request to: {}', url)
    return urlopen(Request(url), timeout=10).read()
