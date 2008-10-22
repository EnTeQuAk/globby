#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""simple testfile for the new menue generator"""
import re

from globby.markup.lexer import RegexLexer
from globby.markup.parser import TokenStreamParser
from globby.markup.datastructure import ParsedData, MarkupToken


def style_filter(stream):
    in_list = False
    for token in stream:
        n = token.name
        if n == 'list' and not in_list:
            in_list = True
            if n not in ['text', 'newline']: yield token
        elif n in ['text', 'newline'] and in_list:
            if stream.look().name.startswith('list'):
                # we are still in a list.
                continue
            else:
                if stream.look().data:
                    if re.compile(r'\s{4,}.+').match(stream.look().data):
                        continue
                in_list = False
                yield MarkupToken('list_fullend', token.data, token.opts)
                if n not in ['text', 'newline']: yield token
        else:
            if n not in ['text', 'newline']: yield token


class MenueLexer(RegexLexer):

    scan_re = [
        ('newline',     r'\n+', None),
        ('menue_entry', r'^(?P<lvl>\s*)(?P<other>.*)(?m)', 'menue_handler'),
    ]

    filters = [style_filter]

    def menue_handler(self, match_obj):
        opts = match_obj.groupdict()
        lvl = len(opts['lvl']) + 1
        m = re.compile(r'([^#]+)(\#.*)?').match(opts['other'])
        if m:
            comment = m.group(2)
            if comment:
                pass
            other = [x.strip(' ') for x in m.group(1).split('"')]
            if len(other) < 2:
                other.append(other[0])
            link, desc = other[0], other[1]
            yield MarkupToken('list', match=match_obj, level=lvl)
            yield MarkupToken('menue_entry', desc, link=link)


p = ParsedData
class MenueParser(TokenStreamParser):

    def __init__(self, lexer):
        super(MenueParser, self).__init__(lexer)
        self._list_stack = []
        self._tabstops = []

    def list_fullend(self, token):
        self.close_list()

    def _set_tab(self, depth):
        """Append a new tab if needed and truncate tabs deeper than `depth`
        """
        tabstops = []
        for ts in self._tabstops:
            if ts >= depth:
                break
            tabstops.append(ts)
        tabstops.append(depth)
        self._tabstops = tabstops

    def list(self, token):
        ldepth = token.opts['level']
        self._set_list_depth(ldepth)

    def _get_list_depth(self):
        """Return the space offset associated to the deepest opened list."""
        return self._list_stack and self._list_stack[-1] or 0

    def _set_list_depth(self, depth):
        def open_list():
            self._list_stack.append(depth)
            self._set_tab(depth)
            self.push(p('list/tag/open', '\n<ul>\n<li>'))
        def close_list():
            self._list_stack.pop()
            self.push(p('list/tag/close', '</li>\n</ul>\n'))

        # depending on the indent/dedent, open or close lists
        if depth > self._get_list_depth():
            open_list()
        else:
            while self._list_stack:
                deepest_offset = self._list_stack[-1]
                if depth >= deepest_offset:
                    break
                close_list()
            if depth > 0:
                if self._list_stack:
                    old_offset = self._list_stack[-1]
                    if old_offset != depth: # adjust last depth
                        self._list_stack[-1] = depth
                    self.push(p('li/open', '</li>\n'))
                    self.push(p('li/close', '<li>'))
                else:
                    open_list()

    def close_list(self):
        self._set_list_depth(0)

    def menue_entry(self, token):
        desc = token.data
        link = token.opts['link']
        if desc and link:
            self.push(p('li/content', u'<a href="%s.html">%s</a>' % (link, desc.strip())))
        elif desc and not link:
            self.push(p('li/content', u'<pre class="menue_section">%s</pre>' % desc.strip()))
        else:
            self.push(p('li/content', u'<a href="%s.html">%s</a>' % (link, link)))

    def get_output(self):
        from globby.utils.html import HTMLFormatter
        if not self.out_stream:
            self.parse()
        self.close_list()
        data = u''.join([x.data for x in self.out_stream if x])
        return data


TEST_MENUE = '''
# this is a simple comment
"Main"
    "undersection"
        link "Name"
    link2 "Name2"
    link3
link3 "Name" # comment
'''

if __name__ == '__main__':
    for token in MenueLexer(TEST_MENUE):
        if token.name == 'menue_entry':
            print "Menue_Entry: %s::%s" % (token.data, token.opts['link'])
        elif token.name == 'list':
            print "Level: %d, data: %s" % (token.opts['level'], token.data)
        else:
            print "Menue end"
    print MenueParser(MenueLexer(TEST_MENUE)).get_output()
