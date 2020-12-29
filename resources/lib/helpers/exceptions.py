# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Stefano Gottardo (plugin.autoupdatekodi)

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""


class InvalidPathError(Exception):
    """The requested path is invalid and could not be routed"""


class InvalidFileId(Exception):
    """Invalid FileId"""
