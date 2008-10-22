#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    globby.exceptions
    ~~~~~~~~~~~~~~~~~

    Privide some Globby specific error classes
    to handle exceptions.

    :copyright: 2006-2008 by Sebastian Koch and Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""


class GlobbyException(Exception):
    """
    Base class for exceptions caused
    by Globby.
    """


class FileParserError(GlobbyException):
    """Error, raised while file parsing process."""


class ProjectNotFound(GlobbyException, ValueError):
    """Raised if a project file could not be found"""


class ProjectExists(GlobbyException):
    """
    Raised if globby tries to create a project
    but it exists allready.
    """


class IsCurrentProject(GlobbyException):
    """
    Raised if the project that will be deleted
    is currently used.
    """


class MenueBroken(GlobbyException, RuntimeError):
    """
    The menue is broken and we can't parse it...
    """
