#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    globby.markup.woxt
    ~~~~~~~~~~~~~~~~~~

    This module provides the `woxt` Markup-Syntax.

    :copyright: 2006-2008 by Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""

import re, os
from os.path import join

from dmlt.machine import MarkupMachine, Directive, RawDirective, \
                         rule, bygroups
from dmlt.utils import parse_child_nodes
from globby.markup.processors.woxt import nodes
from globby.markup import BaseProcessor
from globby.utils.html import escape_html, plaintext
from globby.utils.text import strip_ext

__all__ = ['WoxtProcessor']

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import HtmlFormatter
    from pygments.util import ClassNotFound


    # we define our own formatter, to have
    # a better output
    class CodeFormatter(HtmlFormatter):
        def wrap(self, source, outfile):
            return self._wrap_code(source)

        def _wrap_code(self, source):
            yield 0, '<pre%s%s>' % (
                (self.cssclass and ' class="%s"' % self.cssclass or ''),
                (self.cssstyles and ' style="%s"' % self.cssstyles or '')
            )
            for i, t in source:
                yield i, t
            yield 0, '</pre>'

    PYGMENTS_INSTALLED = True
except ImportError:
    PYGMENTS_INSTALLED = False




class TextDirective(RawDirective):
    name = 'text'

    def parse(self, stream):
        return nodes.Text(stream.expect('text').value)


class SimpleMarkupDirective(Directive):
    __directive_node__ = None

    def parse(self, stream):
        dn = self.rule.enter
        begin, end = '%s_begin' % dn, '%s_end' % dn
        stream.expect(begin)
        children = parse_child_nodes(stream, self, end)
        stream.expect(end)
        return self.__directive_node__(children)


class EmphasizedDirective(SimpleMarkupDirective):
    __directive_node__ = nodes.Emphasized
    rule = rule(r"''", enter='emphasized')


class StrongDirective(SimpleMarkupDirective):
    __directive_node__ = nodes.Strong
    rule = rule(r'\*\*', enter='strong')


class UnderlineDirective(SimpleMarkupDirective):
    __directive_node__ = nodes.Underline
    rule = rule(r'__', enter='underline')


class SubscriptDirective(SimpleMarkupDirective):
    __directive_node__ = nodes.Sub
    rule = rule(r',,\(|\),,', enter='sub')


class SuperscriptDirective(SimpleMarkupDirective):
    __directive_node__ = nodes.Sup
    rule = rule(r'\^\^\(|\)\^\^', enter='sup')


class BigDirective(SimpleMarkupDirective):
    __directive_node__ = nodes.Big
    rule = rule(r'\+~\(|\)~\+', enter='big')


class SmallDirective(SimpleMarkupDirective):
    __directive_node__ = nodes.Small
    rule = rule(r'-~\(|\)~-', enter='small')


class WoxtMarkupMachine(MarkupMachine):
    directives = [EmphasizedDirective, StrongDirective, UnderlineDirective,
                  SubscriptDirective, SuperscriptDirective, BigDirective,
                  SmallDirective]
    special_directives = [TextDirective]



'''

def list_filter(stream):
    """
    A simple filter, that adds the 'list_firststart'
    and 'list_fullend' tokens to the TokenStream.
    """
    in_list = False
    for token in stream:
        n = token.name
        if n == 'list' and not in_list:
            in_list = True
            yield Token('list_firststart', u'', token.opts)
            yield token
        elif n in ['paragraph', 'newline'] and in_list:
            if stream.look().name.startswith('list'):
                # we are still in a list.
                yield Token('text', token.data)
                continue
            else:
                if stream.look().data:
                    if re.compile(r'\s{4,}.+').match(stream.look().data):
                        continue
                in_list = False
                yield Token('list_fullend', u'', token.opts)
                yield token
        else:
            yield token

def style_filter(stream):
    """
    some style cleanups, they're hard to parse
    but easy to handle in the scanner
    """
    oc_escaped = {}
    for token in stream:
        data = token.data
        name = token.name
        if (data and data[0] == u'!' and not name in ['newline']
                and not name.startswith('list') or name == 'style'):
            # the markup is escaped.
            if name == 'style':
                if data.startswith(u'!'):
                    #first style token, wich can be escaped
                    oc_escaped[name] = True
                    yield Token('text', data[1:])
                elif oc_escaped.get(name, False):
                    #the second token, wich doesn't have to be escaped
                    d = data.startswith(u'!') and data[1:] or data
                    yield Token('text', d)
                else:
                    #can't handle... just yield it
                    yield token
            else:
                yield Token('text', data[1:])
        else:
            yield token

def code_block_filter(stream):
    block_buffer = []
    in_block = False
    for token in stream:
        name = token.name
        if name.startswith('code'):
            state = name.split('/')[1]
            if state == 'endblock':
                data = u''.join(block_buffer)

                if data[0] == '\n':
                    yield Token('code', data[1:], style='pre')
                elif data[0] == '#':
                    yield Token('code', data, style='code')
                else:
                    yield Token('code', data, style='tt')

                del block_buffer[:]
                in_block = False
            elif state == 'startblock':
                in_block = True
            elif state == 'text':
                if token.data is not None:
                    block_buffer.append(token.data)
            else:
                #XXX
                yield token
            continue

        if in_block:
            if token.data is not None: block_buffer.append(token.data)
        else:
            yield token

class WoxtLexer(RegexLexer):

    filters = [style_filter, list_filter, code_block_filter]
    scan_re = [
        ('newline',         r'\n+', 'nl_handler'),
        ('style',           r'!?(\*\*|__|\/\/|\`\`|\^\^|,,|\~\~)', None),
        ('lower',           r'!?\-\~(.+)\~\-', 'lower_handler'),
        ('bigger',          r'!?\+\~(.+)\~\+', 'bigger_handler'),
        ('headline',        (r'^!?(?P<hlevel>={1,6})(?P<txt>.+)(?P=hlevel)'
                             r'(?P<anchor>\s*\#[^#\n]*)?\s*$(?m)'), None),
        ('macro',           r'!?#(?P<mn>[a-z]+)\[(?P<ma>.*?)\]',
                                'handle_macro'),
        ('link',            (r'!?(\[(?P<link>[^\s]+?\S)'
                             '(?P<txt>\s+(.+?))?\])'), None),
        ('html_link',       (r'!?((?:http|ftp|nntp|news|mailto|aim|icq|telnet'
                                 r'|sftp|sip)\:[^\s\'"]+\S)'), None),
        ('email',           r'!?([-\w._+]+\@[\w.-]+)', None),
        ('code',            r'!?(\{\{\{)|(\}\}\})(?sm)', 'code_handler'),
        ('list',            (r'^(?P<ldepth>\s+)'
                                r'(?:[-*]|\d+\.|[a-zA-Z]\.|[ivxIVX]{1,5}\.)'
                                r'(?m)'), None),
        ('hr',              r'!?^(\-|_|/|\#){4,}(?m)', None),
    ]

    def nl_handler(self, match_obj):
        #FIXME: there are still some problems... try to analyze them
        if len(match_obj.group(0)) > 1:
            yield Token('paragraph', u'\n\n')
            if (len(match_obj.group(0)) -2) > 0:
                # we yield only one paragraph and all other NEWLINEs
                # in the paragraph will
                # be represented throught `<br />`s
                for i in xrange((len(match_obj.group(0))-2)):
                    yield Token('newline', u'\n')
        else:
            # there are not enought NEWLINE symbols to create a new paragraph.
            yield Token('newline', u'\n')

    def code_handler(self, match_obj):
        opened = self.ctx.get('open_code_blocks', 0)
        data = match_obj.group()
        state = data == u'{{{' and 'start' or 'close'
        if state == 'close' and opened > 1:
            opened -= 1
            yield Token('code/text', data)
        elif state == 'close' and opened == 1:
            # it's just one block
            opened = 0
            yield Token('code/endblock')
        elif state == 'start' and not opened:
            # the first brackets of a new block
            opened = 1
            yield Token('code/startblock')
        elif state == 'start' and opened:
            opened += 1
            yield Token('code/text', data)
        self.ctx['open_code_blocks'] = opened


    def handle_macro(self, match_obj):
        name = match_obj.group('mn')
        argument = match_obj.group('ma')
        data = match_obj.group()
        if not data.startswith(u'!'):
            yield Token('macro', data, macro_name=name, argument=argument)
        else:
            yield self.get_text_token(data[1:])

    def lower_handler(self, match_obj):
        data = match_obj.group(1)
        yield Token('lower', u'-~')
        for token in self.retokenize(data):
            yield token
        yield Token('lower', u'~-')

    def bigger_handler(self, match_obj):
        data = match_obj.group(1)
        yield Token('bigger', u'+~')
        for token in self.retokenize(data):
            yield token
        yield Token('bigger', u'~+')


#shortcut
p = ParsedData

class WoxtParser(TokenStreamParser):

    def __init__(self, environment, lexer):
        super(WoxtParser, self).__init__(lexer)
        self.env = environment
        # some needed attributes for lists
        self._list_stack = []
        self._tabstops = []

        # to save the used heading anchors
        self._anchors = {}

        # all open tags
        self._open_tags = []

    def text(self, token):
        self.push(p('text', escape_html(token.data)))

    def paragraph(self, token):
        if (not self.last.name in ['headline', 'list_fullend']
                and not self.check_open_state('in_list')):
            self.rev_state(token.name)
            if not self.check_open_state(token.name):
                self.close_tag(token.name)
            else:
                self.open_tag(token.name, u'\n<p>\n', u'\n</p>\n')

    def newline(self, token):
        if (not self.last.name in ['headline', 'list_fullend']
                and not self.check_open_state('in_list')):
            self.push(p('br', u'<br />'))
        self.push(p('nl', u'\n'))

    def style(self, token):
        styles = {
            u'**': 'strong',
            u',,': 'sub',
            u'//': 'em',
            u'^^': 'sup',
            u'__': 'ins',
            u'``': 'tt',
            u'~~': 'del'
        }
        style = styles.get(token.data, u'')
        if style:
            self.rev_state(style)
            if not self.check_open_state(style):
                self.close_tag(style)
            else:
                self.open_tag(style)

    def lower(self, token):
        self.rev_state('lower')
        if not self.check_open_state('lower'):
            self.close_tag('lower')
        else:
            self.open_tag(
                'lower', u'<span style="font-size: x-small;">', '</span>'
            )

    def bigger(self, token):
        self.rev_state('bigger')
        if not self.check_open_state('bigger'):
            self.close_tag('bigger')
        else:
            self.open_tag(
                'bigger', u'<span style="font-size: x-large;">', '</span>'
            )

    def headline(self, token):
        self.close_paragraph()
        # strip only *one* leading whitespace, if possible.
        text = strip_ext(token.match.group('txt'), num=1)
        anchor = token.match.group('anchor') or u''
        if anchor:
            anchor = escape_html(anchor.strip()[1:])
        else:
            # we have to create an automatic generated anchor
            anchor = escape_html(text)
        sans_markup = plaintext(anchor, keeplinebreaks=False)
        anchor = re.compile(r'[^\w:.-]+').sub(u'', sans_markup)
        i = 1
        while anchor in self._anchors:
            anchor += str(i)
            i += 1
        self._anchors[anchor] = True
        level = len(token.match.group('hlevel'))
        self.push(p('headline', u'<h%d id="%s">%s %s</h%d>' % (
            level, anchor, escape_html(text),
            self.format_anchor_link(anchor), level
            )
        ))

    def format_anchor_link(self, anchor):
        return (
            u'<a title="Link to %s" class="anchor" href="#%s">#</a>'
                % (anchor, anchor))

    def link(self, token):
        link = token.match.group('link')
        style = 'external'
        # check the kind of the link
        if link in self.env.project.all_files:
            # the link is an internal
            style = 'internal'
            link = link.split(self.env.project.suffix)[0]+u'.html'
        link_text = token.match.groupdict().get('txt') or link
        self.push(p('%s-link' % style, u'<a href="%s">%s</a>' % (
            link, escape_html(link_text).strip()
            )
        ))

    def html_link(self, token):
        link_text = token.match.group(1)
        self.push(p('html_link', u'<a href="%s">%s</a>' % (
            link_text, escape_html(link_text))
        ))

    def email(self, token):
        email_text = token.match.group(1)
        self.push(p('email', u'<a href="mailto:%s">%s</a>' % (
            email_text, escape_html(email_text)
            )
        ))

    def code(self, token):
        self.close_paragraph()
        data = token.data
        if data[0] == u'#' and token.opts['style'] == 'code':
            sdata = data.split(u'\n')
            lname =  sdata[0][1:]
            data = u'\n'.join(sdata[1:])
            if PYGMENTS_INSTALLED:
                try:
                    lexer = get_lexer_by_name(lname)
                except ClassNotFound:
                    try:
                        lexer = guess_lexer(data)
                    except ClassNotFound:
                        # fallback to the `text` lexer
                        lexer = get_lexer_by_name('text')
                formatter = CodeFormatter(
                    linenos=False, cssclass='code', nobackground=True,
                    style=self.env.pygments_style
                )
                data = highlight(data, lexer, formatter)
                self.env.logger.debug_msg(
                    _('Write additional CSS to %s') % join(
                        self.env.project.rendered_path,
                        'style.css'
                    )
                )
                if not 'pygments' in self.env.css_data:
                    self.env.css_data['pygments'] = u'\n/* autogenerated Pygments CSS */\n'
                    self.env.css_data['pygments'] += formatter.get_style_defs()
            else:
                self.env.logger.info_msg(_('Need "pygments" for highlightning'))
                data = escape_html(data)
        else:
            data = escape_html(data)

        if token.opts['style'] == 'tt':
            # one line codes should be displayed also at one line
            self.push(p('code/start', u'<tt>'))
            self.push(p('text', data))
            self.push(p('code/end', u'</tt>'))
        elif token.opts['style'] == 'code':
            self.push(p('rendered_code', data))
        else:
            self.push(p('code/start', u'<pre class="code">'))
            self.push(p('text', data))
            self.push(p('code/end', u'</pre>'))

    def hr(self, token):
        self.close_paragraph()
        if len(token.data) <= 4:
            self.push(p('hr', u'<hr />'))
        else:
            #XXX: the size attribute is not valid for `hr`
            size = len(token.data) - 2
            self.push(p('hr', u'<hr class="hrs%d" />' % (
                size < 5 and size or 5
            )))

    def macro(self, token):
        name = token.opts['macro_name']
        argument = token.opts['argument']
        if name == 'br':
            self.push(p('br', u'<br />'))
        elif name == 'comment':
            self.push(p('comment', u'<!-- %s -->' % escape_html(argument)))
        else:
            # try to find a macro handler:
            if hasattr(self, 'handle_%s_macro' % name):
                getattr(self, 'handle_%s_macro' % name)(name, argument)
            else:
                # can't handle this macro
                self.push(p('text', u'#%s[%s]' % (name, argument)))

    def handle_image_macro(self, name, argument):
        m = re.compile(r'(?P<l>[^\s]+\S)(?P<t>\s.*)?(?s)').match(argument)
        path, alt = m.groupdict().get('l'), (
            m.groupdict().get('t') or m.groupdict().get('l')
        )
        if (os.path.isabs(path) or
                path.split('/')[-1] in self.env.project.all_files_unfiltered):
            from shutil import copy as shcopy
            self.env.logger.info_msg(
                _('Copy the image %(img)s to %(rendered_path)s') % {
                    'img': path,
                    'rendered_path': self.env.project.rendered_path
            })
            shcopy(
                join(
                    self.env.project.path, path
                ),
                self.env.project.rendered_path
            )
            path = path.split('/')[-1]
        self.push(p('macro/image', u'<img src="%s" alt="%s" />' % (
            path, escape_html(alt.strip())
        )))

    # Generic indentation (as defined by lists)
    def _set_tab(self, depth):
        """
        Append a new tab if needed and truncate tabs deeper than `depth`
        """
        tabstops = []
        for ts in self._tabstops:
            if ts >= depth:
                break
            tabstops.append(ts)
        tabstops.append(depth)
        self._tabstops = tabstops

    # Lists
    # This implementation is based on the Trac ones
    # Tanks to the project!

    def list_firststart(self, token):
        self.open_state('in_list')

    def list_fullend(self, token):
        self.close_list()
        self.close_state('in_list')

    def list(self, token):
        ldepth = len(token.match.group('ldepth'))
        listid = token.data[ldepth]
        self.ctx['in_list_item'] = True
        class_ = start = None
        if listid in u'-*':
            type_ = 'ul'
        else:
            type_ = 'ol'
            idx = '01iI'.find(listid)
            if idx >= 0:
                class_ = ('arabiczero', None, 'lowerroman', 'upperroman')[idx]
            elif listid.isdigit():
                start = token.data[ldepth:token.data.find('.')]
            elif listid.islower():
                class_ = 'loweralpha'
            elif listid.isupper():
                class_ = 'upperalpha'
        self._set_list_depth(ldepth, type_, class_, start)

    def _get_list_depth(self):
        """Return the space offset associated to the deepest opened list."""
        return self._list_stack and self._list_stack[-1][1] or 0

    def _set_list_depth(self, depth, new_type, list_class, start):
        def open_list():
            self.close_paragraph()
            self._list_stack.append((new_type, depth))
            self._set_tab(depth)
            class_attr = list_class and (u' class="%s"' % list_class) or u''
            start_attr = (start and ' start="%s"' % start) or ''
            self.push(p('list/tag/open', u'<'+new_type+class_attr+start_attr+u'><li>'))
        def close_list(tp):
            self._list_stack.pop()
            self.push(p('list/tag/close', u'</li></%s>' % tp))

        # depending on the indent/dedent, open or close lists
        if depth > self._get_list_depth():
            open_list()
        else:
            while self._list_stack:
                deepest_type, deepest_offset = self._list_stack[-1]
                if depth >= deepest_offset:
                    break
                close_list(deepest_type)
            if depth > 0:
                if self._list_stack:
                    old_type, old_offset = self._list_stack[-1]
                    if new_type and old_type != new_type:
                        close_list(old_type)
                        open_list()
                    else:
                        if old_offset != depth: # adjust last depth
                            self._list_stack[-1] = (old_type, depth)
                        self.push(p('li/open', u'</li>'))
                        self.push(p('li/close', u'<li>'))
                else:
                    open_list()

    def close_list(self):
        self._set_list_depth(0, None, None, None)

    def close_paragraph(self):
        if self.check_open_state('paragraph'):
            self.close_state('paragraph')
            self.close_tag('paragraph')

    def open_tag(self, name, tag=None, close_tag=None):
        tag = tag or u'<%s>' % name
        close_tag = close_tag or u'</%s>' % name
        self._open_tags.append((name, tag, close_tag))
        self.push(p(
            '%s/%s' % (name, 'open'),
            tag,
        ))

    def close_tag(self, name):
        last_tag = None
        while last_tag != name:
            if not self._open_tags:
                return
            tmp = self._open_tags.pop()
            self.push(p(
                '%s/close' % tmp[0],
                tmp[2]
            ))
            last_tag = tmp[0]

    def get_output(self):
        p = ParsedData
        if not self.out_stream:
            self.parse()
        self.close_tag(True)
        return u''.join([x.data for x in self.out_stream if x.data])


class WoxtProcessor(BaseProcessor):
    name = 'woxt'

    def to_html(self, text):
        lexer = WoxtLexer(text)
        parser = WoxtParser(self.env, lexer)
        return parser.get_output()
'''

if __name__ == '__main__':
    text = u'''
Just some \\''cool\\'' new paragraph.

escaped: \\\\\\
emphasized: ''text''
strong: **text**
underline: __underline__
subscript: ,,(subscript),,
superscript: ^^(Super!)^^
big: +~(big)~+
small: -~(small)~-
'''
    print WoxtMarkupMachine(text).render(enable_escaping=True)
