# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Stefano Gottardo (plugin.autoupdatekodi)

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
# Everything that is to be globally accessible must be defined in this module.
# Using the Kodi reuseLanguageInvoker feature, only the code in the addon.py or service.py module
# will be run every time the addon is called.
# All other modules (imports) are initialized only on the first invocation of the add-on.
from urllib.parse import parse_qsl, unquote, urlparse

import xbmcaddon


class GlobalVariables(object):
    """Encapsulation for global variables to work around quirks with
    Kodi's reuseLanguageInvoker behavior"""
    # pylint: disable=attribute-defined-outside-init
    # pylint: disable=invalid-name, too-many-instance-attributes

    MIRROR_BASE_URL = 'http://mirrors.kodi.tv/'

    MODE_DIRECTORY = 'directory'
    MODE_ACTION = 'actions'
    MODE_INSTALL = 'install'

    def __init__(self):
        """Do nothing on constructing the object"""
        # The class initialization (GlobalVariables) will only take place at the first initialization of this module
        # on subsequent add-on invocations (invoked by reuseLanguageInvoker) will have no effect.
        # Define here also any other variables necessary for the correct loading of the other project modules
        self.IS_ADDON_FIRSTRUN = None
        self.ADDON = None
        self.ADDON_DATA_PATH = None
        self.DATA_PATH = None
        self.FILES_LIST = []

    def init_globals(self, argv):
        """Initialized globally used module variables. Needs to be called at start of each plugin instance!"""
        # IS_ADDON_FIRSTRUN: specifies if the add-on has been initialized for the first time
        #                    (reuseLanguageInvoker not used yet)
        self.IS_ADDON_FIRSTRUN = self.IS_ADDON_FIRSTRUN is None
        # xbmcaddon.Addon must be created at every instance otherwise it does not read any new changes to the settings
        self.ADDON = xbmcaddon.Addon()
        self.URL = urlparse(argv[0])
        self.REQUEST_PATH = unquote(self.URL[2][1:])
        try:
            self.PARAM_STRING = argv[2][1:]
        except IndexError:
            self.PARAM_STRING = ''
        self.REQUEST_PARAMS = dict(parse_qsl(self.PARAM_STRING))
        if self.IS_ADDON_FIRSTRUN:
            # Global variables that do not need to be generated at every instance
            self.ADDON_ID = self.ADDON.getAddonInfo('id')
            self.PLUGIN = self.ADDON.getAddonInfo('name')
            self.VERSION_RAW = self.ADDON.getAddonInfo('version')
            self.VERSION = remove_ver_suffix(self.VERSION_RAW)
            self.ICON = self.ADDON.getAddonInfo('icon')
            self.ADDON_DATA_PATH = self.ADDON.getAddonInfo('path')  # Add-on folder
            self.DATA_PATH = self.ADDON.getAddonInfo('profile')  # Add-on user data folder
            try:
                self.PLUGIN_HANDLE = int(argv[1])
                self.IS_SERVICE = False
                self.BASE_URL = '{scheme}://{netloc}'.format(scheme=self.URL[0],
                                                             netloc=self.URL[1])
            except IndexError:
                self.PLUGIN_HANDLE = 0
                self.IS_SERVICE = True
                self.BASE_URL = '{scheme}://{netloc}'.format(scheme='plugin',
                                                             netloc=self.ADDON_ID)
        # Initialize the log
        from resources.lib.helpers.logging import LOG
        LOG.initialize(self.ADDON_ID, self.PLUGIN_HANDLE,
                       self.ADDON.getSettingString('debug_log_level'),
                       self.ADDON.getSettingBool('enable_timing'))
        # Temporary file path (use to download and run the installer)
        from resources.lib.helpers.file_ops import translate_path
        self.INSTALLER_TEMP_PATH = translate_path(G.DATA_PATH) + 'temp/'
        self.INSTALLER_TEMP_NAME = 'KodiInstaller.exe'  # Mush be equal to all scripts
        self.DOWNLOADS_PATH = translate_path(G.DATA_PATH) + 'downloads/'


def remove_ver_suffix(version):
    """Remove the codename suffix from version value"""
    import re
    pattern = re.compile(r'\+\w+\.\d$')  # Example: +matrix.1
    return re.sub(pattern, '', version)


# We initialize an instance importable of GlobalVariables from run_addon.py and run_service.py,
# where G.init_globals() MUST be called before you do anything else.
G = GlobalVariables()
