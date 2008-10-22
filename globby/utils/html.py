#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    globby.lib.utils.html
    ~~~~~~~~~~~~~~~~~~~~~

    Some help utilities for processing html.

    Some functions are taken from Trac and Genshi written by
    Edgewall Software.

    :copyright: 2006-2007 by Christopher Grebs, Edgewall Software.
    :license: GNU GPL, see LICENSE for more details.
"""

import re
import htmlentitydefs
from xml.sax.saxutils import quoteattr
from globby.utils.text import to_unicode
from globby.markup.lexer import RegexLexer
from globby.markup.datastructure import deque, MarkupToken


def escape_html(text):
    chars = [
        (u'&', u'&amp;'),
        (u'<', u'&lt;'),
        (u'>', u'&gt;'),
        (u'"', u'&quot;'),
        (u"'", u'&#39;')
    ]

    if not isinstance(text, unicode):
        text = to_unicode(text) # for security
    for char, repl in chars:
        text = text.replace(char, repl)
    return text


def unescape_html(text):
    chars = [
        (u'&#39;', u"'"),
        (u'&quot;', u'"'),
        (u'&gt;', u'>'),
        (u'&lt;', u'<'),
        (u'&amp;', u'&'),
    ]
    for char, repl in chars:
        text = text.replace(char, repl)
    return text

def plaintext(text, keeplinebreaks=True):
    """Returns the text as a `unicode` string with all entities and tags
    removed.

    >>> plaintext('<b>1 &lt; 2</b>')
    u'1 < 2'

    The `keeplinebreaks` parameter can be set to ``False`` to replace any line
    breaks by simple spaces:

    >>> plaintext('''<b>1
    ... &lt;
    ... 2</b>''', keeplinebreaks=False)
    u'1 < 2'

    :param text: the text to convert to plain text
    :param keeplinebreaks: whether line breaks in the text should be kept intact
    :return: the text with tags and entities removed
    """
    text = stripentities(striptags(text))
    if not keeplinebreaks:
        text = text.replace(u'\n', u' ')
    return text

_STRIPENTITIES_RE = re.compile(r'&(?:#((?:\d+)|(?:[xX][0-9a-fA-F]+));?|(\w+);)')
def stripentities(text, keepxmlentities=False):
    """Return a copy of the given text with any character or numeric entities
    replaced by the equivalent UTF-8 characters.

    >>> stripentities('1 &lt; 2')
    u'1 < 2'
    >>> stripentities('more &hellip;')
    u'more \u2026'
    >>> stripentities('&#8230;')
    u'\u2026'
    >>> stripentities('&#x2026;')
    u'\u2026'

    If the `keepxmlentities` parameter is provided and is a truth value, the
    core XML entities (&amp;, &apos;, &gt;, &lt; and &quot;) are left intact.

    >>> stripentities('1 &lt; 2 &hellip;', keepxmlentities=True)
    u'1 &lt; 2 \u2026'
    """
    def _replace_entity(match):
        if match.group(1): # numeric entity
            ref = match.group(1)
            if ref.startswith('x'):
                ref = int(ref[1:], 16)
            else:
                ref = int(ref, 10)
            return unichr(ref)
        else: # character entity
            ref = match.group(2)
            if keepxmlentities and ref in ('amp', 'apos', 'gt', 'lt', 'quot'):
                return u'&%s;' % ref
            try:
                return unichr(htmlentitydefs.name2codepoint[ref])
            except KeyError:
                if keepxmlentities:
                    return u'&amp;%s;' % ref
                else:
                    return ref
    return _STRIPENTITIES_RE.sub(_replace_entity, text)

_STRIPTAGS_RE = re.compile(r'<[^>]*?>')
def striptags(text):
    """Return a copy of the text with any XML/HTML tags removed.

    >>> striptags('<span>Foo</span> bar')
    'Foo bar'
    >>> striptags('<span class="bar">Foo</span>')
    'Foo'
    >>> striptags('Foo<br />')
    'Foo'

    :param text: the string to remove tags from
    :return: the text with tags removed
    """
    return _STRIPTAGS_RE.sub('', text)


class HTMLFormatter(RegexLexer):

    scan_re = [
        ('newline',         r'\n+', None),
        ('comment',         r'(<!--\s*.*?\s*-->)', None),
        ('standalone_tag',  r'<\s*([^<>]*?)\/>', 'st_tag_handler'),
        ('open_tag',        r'<\s*([^<>\/]*?)>', 'open_tag_handler'),
        ('closed_tag',      r'<\s*\/([^<>\/]*?)>', 'closed_tag_handler'),
    ]

    def __init__(self, source, ichar=' ', inum=2):
        super(HTMLFormatter, self).__init__(source)
        self.ichar = ichar
        self.inum = inum
        self.ctx['opened_tags'] = deque([])
        self.indent = 0
        self.text_buffer = deque([])
        self.linenum = 0
        self.last_line = 0

    def st_tag_handler(self, match_obj):
        yield MarkupToken('standalone_tag', match_obj.group(1).strip())

    def open_tag_handler(self, match_obj):
        name = match_obj.group(1).strip()
        self.ctx['opened_tags'].append(name)
        yield MarkupToken('open_tag', name)

    def closed_tag_handler(self, match_obj):
        name = match_obj.group(1).strip()
        if name in self.ctx['opened_tags']:
            self.ctx['opened_tags'].remove(name)
        yield MarkupToken('closed_tag', name)

    def format(self):
        if not self._parsed:
            self.tokenize()

        self.last_line = 0
        for token in self.stream:
            if token.name == 'standalone_tag':
                self.write(u'<%s />' % token.data)
                self.last_line = self.linenum

            elif token.name == 'open_tag':
                self.write(u'<%s>' % token.data)
                self.indent += self.inum
                self.last_line = self.linenum

            elif token.name == 'closed_tag':
                self.indent -= self.inum
                self.write(u'</%s>' % token.data)
                self.last_line = self.linenum

            elif token.name == 'newline':
                self.linenum += token.data.count('\n')
                self.write(token.data)

            else:
                self.write(token.data)
                self.last_line = self.linenum

    def write(self, data):
        if not self.last_line == self.linenum:
            data = u'%s%s' % (self.indent * self.ichar, data)
        self.text_buffer.append(data)

    def get_output(self):
        if not self.text_buffer:
            self.format()
        return u''.join(self.text_buffer)


test_html = u'''<html>
<head>
<title>lala</title>
</head>
<body>
This is only a <b style="display:bold;">test</b>
</body>
</html>
'''

def format_html(html):
    formatter = HTMLFormatter(html)
    return formatter.get_output()

if __name__ == '__main__':
    print format_html(test_html)
