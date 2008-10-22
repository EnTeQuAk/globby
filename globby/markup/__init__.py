#-*- coding: utf-8 -*-
"""
    globby.markup
    ~~~~~~~~~~~~~

    Serveral modules for the Markup processing.

    :copyright: 2006-2007 by Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""

import os
import sys


class BaseProcessor(object):
    def __init__(self, env):
        self.env = env

    def to_html(self, text):
        """
        This method will use a markup lexer
        and a markup parser, to get the parsed
        HTML data.
        """
        raise NotImplementedError

    def to_pdf(self, text):
        """
        This method will render the `TokenStream`
        to a PDF document
        """
        raise NotImplementedError

    def to_latex(self, text):
        """
        This method will render the `TokenStream`
        to Latex
        """
        raise NotImplementedError


def get_all_processors():
    found_processors = {}
    imports = []
    mpth = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, os.path.join(mpth, '..', '..'))
    ns = globals()
    for filename in os.listdir(os.path.join(mpth, 'processors')):
        if filename.endswith('.py') and not filename.startswith('_'):
            module_name = 'globby.markup.processors.%s' % filename[:-3]
            module = __import__(module_name, None, None, [''])
            for pname in module.__all__:
                pobj = getattr(module, pname)
                imports.append((module_name, pname, pobj))
                found_processors[pobj.name] = pobj

    imports.sort()
    return (imports, found_processors)


ns = globals()
PROCESSORS = get_all_processors()[0]
for pimp in PROCESSORS:
    ns[pimp[1]] = pimp[2]
