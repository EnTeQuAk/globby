#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    Globby
    ~~~~~~

    :copyright: 2006-2008 by Sebastian Koch, Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""

__version__ = '0.2' # no dev, beta or what ever here!
__docformat__ = 'reStructuredText'
__license__ = 'GNU General Public License'

import sys


# some i18n variables
try:
    _
    N_
except NameError:
    # globby was imported from an other application
    # except the globby.py
    # Then we need to set the gettext variables
    # to avoid an exception
    import __builtin__
    __builtin__._ = lambda x: x
    __builtin__.N_ = lambda x: x


class UnitMeta(type):
    """
    Metaclass that appends every
    Unit to ``unit2sub`` and appends also
    every subclass to the ``unit2sub[base]``
    dictionary.
    """
    unit2sub = {}

    def __new__(mcs, name, bases, dct):
        obj = type.__new__(mcs, name, bases, dct)
        if bases == (object,):
            # `Component` itself
            return obj
        if Unit in bases:
            obj._isunit = True
            if name in UnitMeta.unit2sub:
                raise TypeError('Unit with name %r already exists' % name)
            UnitMeta.unit2sub[name] = {}
        else:
            obj._subunits = subunits = []
            for base in bases:
                UnitMeta.unit2sub[base.__name__].update({obj.__name__: obj})
                if '_isunit' in base.__dict__:
                    subunits.append(base)
                elif '_subunits' in base.__dict__:
                    subunits.extend(base._subunits)
        return obj


class Unit(object):
    """Base Unit class."""
    __metaclass__ = UnitMeta

    def __init__(self, env):
        self.env = env

# Lazy loading
# ------------

class _ModuleProxy(object):
    _module = None

    def __init__(self, name):
        self.__dict__['_module_name'] = name

    def __getattr__(self, name):
        try:
            return getattr(self._module, name)
        except AttributeError:
            if self._module is not None:
                raise

            import_name = 'globby.%s' % self._module_name
            __import__(import_name)
            module = sys.modules[import_name]
            globals()[self._module_name] = module
            return getattr(module, name)

    def __setattr__(self, name, value):
       try:
            setattr(self._module, name, value)
       except AttributeError:
            if self._module is not None:
                raise

            import_name = 'globby.%s' % self._module_name
            __import__(import_name)
            module = sys.modules[import_name]
            globals()[self._module_name] = module
            setattr(module, name, value)

#XXX: complete this list
api = _ModuleProxy('api')
builder = _ModuleProxy('builder')
environment = _ModuleProxy('environment')
template = _ModuleProxy('template')
cli = _ModuleProxy('cli')
utils = _ModuleProxy('utils')
markup = _ModuleProxy('markup')
logger = _ModuleProxy('utils.logger')
