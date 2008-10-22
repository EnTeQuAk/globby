#-*- coding: utf-8 -*-
"""
    globby.api
    ~~~~~~~~~~

    API implementations

    :copyright: 2007 by Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""

from globby.environment import _locals, setup_env


def get_all_units(unitcls):
    """return a list of all units from `unitcls`"""
    if hasattr(unitcls, '__metaclass__'):
        unit_metacls = unitcls.__metaclass__
        unitdct = unit_metacls.unit2sub
        name = unitcls.__name__
        units = []
        if name in unitdct:
            for subunit in unitdct[name].values():
                units.append(subunit)
        return units
    return []


def get_environment():
    if hasattr(_locals, 'env'):
        return _locals.env
    return None


__all__ = list(x for x in locals() if not x.startswith('_'))
