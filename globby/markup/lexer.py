#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    globby.markup.lexer
    ~~~~~~~~~~~~~~~~~~~

    This module provides a component to scan
    a text for lexing serveral markup languages.

    :copyright: 2006-2007 by Christopher Grebs
    :license: GNU GPL, see LICENSE for more details.
"""

import re

from globby.markup.datastructure import TokenStream, TokenStack, MarkupToken

class TokenError(Exception):
    pass

class HandlerNotFound(Exception):
    pass


class RegexLexer(object):

    # Here the Markup Lexer must define the regular
    # expressions, and the optional match handler.
    # A scan_re should be build, based on the follow example:
    # ('tokentype', r'regular expression', 'handler'),
    #
    # Like you see, it's only a simple list of tuples.
    #
    # - The ``tokentype`` is the name of the token, added to the TokenStream.
    # - The ``regex`` is the regular expression, the `tokenize` function will
    #   search for
    # - The `handler` is the name of a function,
    #   that handles a matched object.
    #   This function should return a generator object, with all `Token`s
    #   needed for next stage. Parsing.
    scan_re = {}

    filters = []

    def __init__(self, text):
        self.max_length = len(text)
        self.pos = 0 # actual position in the text
        self.text = text
        self._end_pos = 0
        self._regex_cache = {}
        self._parsed = False
        self.stack = TokenStack()
        self.stream = None
        self.ctx = {}

    def match(self, regex):
        """
        This function returns the match object.
        We need a standalone function, because we
        cache the regular expressions. It's not that caching
        at all, but we check that we compile only once.
        """
        if not self._regex_cache.has_key(regex):
            self._regex_cache[regex] = re.compile(regex)

        m = self._regex_cache[regex].match(self.text, self.pos)
        if m is not None:
            self._end_pos = m.end()
        return m

    def tokenize(self):
        """
        Go through the text and tokenize it...
        This method goes through the text, and calls for
        every change of ``self.pos`` the whole ``self.scan_re``.
        Then it tries to match the text from ``self.pos`` to ``self.max``.
        If matched try to call a *match_handler*, to get a token stream.
        If no *match_handler* defined, add a standardized `MarkupToken` to the stack.
        If no regular expression matched on the text it handles it as
        text and produce a `MarkupToken` with the name "text".
        """
        while self.pos < self.max_length:
            for name, regex, handler in self.scan_re:
                m = self.match(regex)
                # if no match we try again with the next rule
                if not m:
                    continue

                self.stack.flush_text()
                if handler:
                    if hasattr(self, handler):
                        # try to handle the match with the `handler` method
                        stream = getattr(self, handler)(m)
                        if stream:
                            for token in stream:
                                if not isinstance(token, MarkupToken):
                                    raise TokenError(
                                        '%r is no instance `MarkupToken`'
                                            % token
                                    )
                                self.stack.push(token)
                    else:
                        raise HandlerNotFound('can not find %r in %r'
                            % (handler, self.__class__.__name__))
                else:
                    # push the standardized token to the stack
                    self.stack.push(
                        MarkupToken(name, m.group(), m, **m.groupdict())
                    )
                self.pos = self._end_pos
                break
            else:
                # no rex matched the text. send one char into the text buffer
                if self.pos < self.max_length:
                    self.stack.write_text(self.text[self.pos])
                else:
                    self.stack.flush_text()
                self.pos += 1
        self.stack.flush_text()
        self._parsed = True
        self.stream = self.filter(TokenStream(self.stack.flush()))
        return self.stream

    def filter(self, stream):
        """
        Apply some filters on the stream
        so we can modify the stream after the
        tokenize process.
        """
        for filter_func in self.filters:
            stream = TokenStream(filter_func(stream))
        return stream

    def get_stream(self):
        """
        Return the filtered TokenStream
        """
        return self.tokenize()

    def get_text_token(self, value=None):
        return MarkupToken('text', value)

    def retokenize(self, text):
        ilexer = self.__class__(text)
        return ilexer.get_stream()

    def __iter__(self):
        return iter(self.tokenize())

    def __repr__(self):
        return '<%s (%d/%d)>' % (
            self.__class__.__name__,
            self.pos,
            self.max_length
        )
