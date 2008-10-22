#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    globby.lib.utils.text
    ~~~~~~~~~~~~~~~~~~~~~

    Some help utilities for text processing.

    :copyright: 2006-2007 by Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""

import locale, re


def read_file(filename, charset='utf-8'):
    f = open(filename, 'rb')
    try:
        data = to_unicode(
            re.sub(r'\r\n|\r|\n', '\n', f.read()),
            charset)
    finally:
        f.close()
    return data


def write_file(filename, data, charset='utf-8'):
    f = open(filename, 'w')
    if not isinstance(data, unicode):
        # wtf? -- if this happens... I kill myself ;)
        data = to_unicode(data)
    try:
        f.write(data.encode(charset))
    finally:
        f.close()


def to_unicode(text, charset=None):
    if isinstance(text, unicode):
        # the string isn't a 'str' instance... then it is a 'unicode' one
        return text
    if charset:
        # try to decode with the given 'charset'
        return text.decode(charset, 'replace')
    else:
        try:
            # decode with 'charset' doesn't work... try 'utf-8'
            return text.decode('utf-8')
        except UnicodeError:
            try:
                # 'utf-8' still not work? -- try the local preferred encoding
                return text.decode(locale.getpreferredencoding(), 'replace')
            except UnicodeError:
                # it nothing work... fallback to 'iso-8859-15'
                return text.decode('iso-8859-15', 'replace')


def rstrip_ext(text, chars, num=None):
    """
    rstrip_ext(s [,chars, num]) -> string

    Return a copy of the string s with trailing chars removed.
    If chars is given and not None, remove characters in chars instead.
    If num is given and not None, remove max. num characters if given, whitespaces
    if not.
    """
    if chars is None:
        chars = ' '

    if num is not None:
        result = list(text)
        for i, c in enumerate(reversed(text)):
            if c in chars and i < num:
                result.pop()
        result = ''.join(result)
    else:
        result = text.rstrip(chars)
    return result

def lstrip_ext(text, chars, num=None):
    """
    lstrip_ext(s [,chars, num]) -> string

    Return a copy of the string s with leading chars removed.
    If chars is given and not None, remove characters in chars instead.
    If num is given and not None, remove max. num characters if given, whitespaces
    if not.
    """
    if chars is None:
        chars = ' '

    if num is not None:
        result = list(text)
        for i, c in enumerate(text):
            if c in chars and i < num:
                result.pop(0)
        result = ''.join(result)
    else:
        result = text.lstrip(chars)
    return result

def strip_ext(text, chars=None, num=None):
    """
    strip_ext(s [,chars, num]) -> string

    Return a copy of the string s with leading and trailing
    chars removed.
    If chars is given and not None, remove characters in chars instead.
    If num is given and not None, remove max. num characters if given, whitespaces
    if not.
    """
    if chars is None:
        chars = ' '

    if not isinstance(chars, basestring):
        raise TypeError('\'chars\' must be a unicode, str or None value')

    if num:
        r = rstrip_ext(text, chars, num)
        result = lstrip_ext(r, chars, num)
    else:
        result = text.strip(chars)
    return result
