#!/usr/bin/env python
"""
    globby.markup.parser
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: 2006-2007 by Christopher Grebs
    :license: GNU GPL, see LICENSE for details.
"""

from globby.markup.datastructure import TokenStream, ParsedData, MarkupToken
from globby.utils.html import escape_html

class TokenError(Exception):
    pass

class HandlerNotFound(Exception):
    pass


class TokenStreamParser(object):

    # tags, must be closed before generate the output:
    # {'name': '</closetag>'}
    tags_tc = {}

    # ('handler_name', 'token_name_to_handle')
    handlers = []

    def __init__(self, lexer):
        self._lexer = lexer
        self.stream = TokenStream(self._lexer.get_stream())
        self.out_stream = []
        self.ctx = {}
        self.last = ParsedData('initial', 'initial')
        self._open_tags = []

    def parse(self):
        handler_names = []
        if self.handlers:
            for entry in self.handlers:
                name = entry[0]
                if not hasattr(self, name):
                    raise HandlerNotFound('Can\'t find the handler %r in %r' % (
                        name, self.__class__.__name__
                    ))
                handler_names.append(name)
            hitn = False
        else:
            hitn = True

        for token in self.stream:
            if not isinstance(token, MarkupToken):
                raise TokenError(
                    '%r is no instance of \'MarkupToken\'' % token
                )
            if token.name in handler_names or hitn:
                if hitn:
                    handler = token.name
                else:
                    handler = self.handlers[handler_names.index(token.name)]
                if hasattr(self, handler):
                    getattr(self, handler)(token)
                else:
                    raise HandlerNotFound('Can\'t find the handler %r in %r' % (
                        handler, self.__class__.__name__
                    ))
            else:
                self.push(ParsedData('text', escape_html(token.data)))

    def push(self, token):
        if token:
            if not isinstance(token, ParsedData):
                raise TokenError(
                    '%r is no instance of \'ParsedData\'' % token
                )
            self.out_stream.append(token)
            self.last = self.out_stream[-1]

    def pushmany(self, token_list):
        for token in token_list:
            self.push(token)

    def peek(self):
        return self.stream.look()

    def peekmany(self, num=1):
        tokens = self.stream.fetch_until(num)
        for tok in tokens:
            self.stream.feed(tok)
        return tokens

    # some functions we use for handling open and closing
    # tags
    def open_state(self, name):
        if not name in self.ctx:
            self.ctx[name] = True
        else:
            #FIXME: should we raise an error?
            pass

    def close_state(self, name):
        if name in self.ctx:
            self.ctx[name] = False

    def rev_state(self, name):
        self.ctx[name] = not self.ctx.get(name, False)

    def check_open_state(self, name):
        return self.ctx.get(name, False)

    def get_output(self, text):
        raise NotImplementedError
