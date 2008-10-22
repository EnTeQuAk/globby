#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    globby.markup.datastructure
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Serveral datastructures for storing data.

    :copyright: 2006-2007 by Christopher Grebs
    :license: GNU GPL, see LICENSE for more details.
"""

# we use deque as the datacollection for the TokenStream
# and the TokenStack instead of generator objects
try:
    from collections import deque
    deque.remove
except (ImportError, AttributeError):
    # python versions < 2.4 doesn't support deque. So we define
    # a simple subclass of `list`, that provides the deque
    # features
    class deque(list):
        def appendleft(self, item): list.insert(self, 0, item)
        def popleft(self): return list.pop(self, 0)
        def clear(self): del self[:]
        def remove(self, item): list.remove(self, item)


class TokenError(Exception):
    pass

class EndOfStream(Exception):
    pass

class TokenMeta(type):
    """
    Token metaclass that ensures that nobody subclasses
    the only token class.
    """

    def __new__(mcs, name, bases, cls_dict):
        if bases != (object,):
            raise TypeError('subclassing Token isn\'t possible')
        return type.__new__(mcs, name, bases, cls_dict)


class MarkupToken(object):
    """
    It's used to store Data in the TokenStack or
    the TokenStream. The `UndefinedToken` is a little
    shortcut for an empty `MarkupToken`.

    :param name:         The name of the token, used for describing the token value.
    :param data:        The value of the token. Defaults to ``None``.
    :param match:        The match object of the token. Defaults to ``None``.
    :param opts:         Sereral options. Here you can define anything you want to.
    """

    __metaclass__ = TokenMeta
    __slots__ = ('name', 'data', 'match', 'opts')

    def __init__(self, name, data=None, match=None, **opts):
        self.name = name
        self.data = data
        self.match = match
        self.opts = opts

    def __repr__(self):
        return '<%s: %r (%r)>' % (
            self.__class__.__name__,
            self.name,
            self.data
        )

class UndefinedToken(object):
    """
    An UndefinedToken is used to store an
    undefined (e.g inital or empty) token in the
    TokenStack or TokenStream.
    It's defined as a MarkupToken and like
    it it's not possible to subclass an UndefinedToken.
    """

    __metaclass__ = TokenMeta
    __slots__ = ('name', 'data', 'match', 'opts')

    def __init__(self):
        self.name = ''
        self.data = None
        self.match = None
        self.opts = {}

    def __repr__(self):
        return '<%s: %r (%r)>' % (
            self.__class__.__name__,
            self.name,
            self.data
        )


class ParsedData(object):
    """
    This class is used to represent data, that's
    parsed from the TokenStream. With a list
    of `ParsedData` tokens it's possible
    to create the final output.
    """

    __metaclass__ = TokenMeta
    __slots__ = ('name', 'data')

    def __init__(self, name, data=None):
        self.name = name
        self.data = data

    def __repr__(self):
        return '<%s: %r (%r)>' % (
            self.__class__.__name__,
            self.name,
            self.data
        )


class TokenStack(object):
    """
    The TokenStack provide some functions
    to push new tokens to the stack and
    to get some informations about the TokenStack.
    It's used by the `Lexer` to hold dynamic data
    and to ease the lexing process.
    """
    def __init__(self):
        self._token_stack = deque()
        self._text_buffer = deque()

    def __repr__(self):
        return '<%s (%r)>' % (
            self.__class__.__name__,
            self._token_stack
        )

    @property
    def current_token(self):
        """Return the current token from the stack"""
        return self._token_stack[-1]

    @property
    def last_token(self):
        """Return the last used token from the stack"""
        return self._token_stack[-2]

    def flatten(self):
        """
        Return the token buffer without touch
        the text buffer or the token stack.
        so it can be used to lookup the actual TokenStack.

        :return: a TokenStream instance
        """
        if self._text_buffer:
            self._token_stack.append(u''.join(self._text_buffer))
        return TokenStream(self._token_stack)

    def pop(self):
        """
        Return the last token from the TokenStack and
        delete it. It raises a `TokenError` if the stack
        is empty
        """
        if len(self._token_stack) > 0:
            return self._token_stack.pop()
        raise TokenError('TokenStack is empty!')

    def push(self, token):
        """
        Append a token (*must* be an instance of `MarkupToken`)
        to the token stack.
        """
        # append text tokens
        self.flush_text()
        # for security reasons ;)
        if isinstance(token, MarkupToken):
            self._token_stack.append(token)
        else:
            #FIXME: does we need support for UndefinedTokens in the stack?
            raise TokenError('%s isn\'t a \'MarkupToken\' instance!' % token)

    def write_text(self, char):
        """write text into the text buffer """
        self._text_buffer.append(char)

    def flush_text(self):
        """
        Join the content from the text buffer
        and add a new text token to the stack.
        """
        if self._text_buffer:
            data = u''.join(self._text_buffer)
            self._text_buffer.clear()
            self.push(MarkupToken('text', data))

    def flush(self):
        """
        Return the whole token stack
        and delete it.
        """
        self.flush_text()
        stack = [x for x in self._token_stack]
        self._token_stack.clear()
        return TokenStream(stack)


class TokenStream(object):
    """
    The TokenStream works like a normal generator just that
    it supports pushing tokens back to the stream.
    It also supports look forward and fetching a stream
    of tokens.
    The TokenStream needs to get an iterable. It doesn't matter
    if it's a tuple, a list or a generator object.
    We move the iterable into a `deque` object, so we can handle
    all iterables on the same way.
    """

    def __init__(self, iterable):
        self.stack = deque(list(iterable))
        self._pushed = []
        self.last = UndefinedToken()

    def __iter__(self):
        """Return self in order to mark this is iterator."""
        return self

    def __nonzero__(self):
        """Are we at the end of the tokenstream?"""
        if self._pushed:
            return True
        try:
            self.feed(self.next())
        except StopIteration:
            return False
        return True

    eos = property(lambda x: not x.__nonzero__(), doc=__nonzero__.__doc__)

    def __contains__(self, item):
        if isinstance(item, MarkupToken):
            for token in self.stack:
                if token is item:
                    return True
        else:
            return item in self.stack
        return False

    def __len__(self):
        return len(self.stack)+len(self._pushed)

    def next(self):
        """Return the next token from the stream."""
        if self._pushed:
            rv = self._pushed.pop()
        else:
            try:
                rv = self.stack.popleft()
            except IndexError:
                raise StopIteration()
        self.last = rv
        return rv

    def look(self):
        """Pop and push a token, return it."""
        if not self.eos:
            token = self.next()
            self.feed(token)
            return token
        return UndefinedToken()

    def look_until(self, num=1):
        """Pop and push `num` tokens, return all tokens"""
        tokens = []
        for i in xrange(num):
            try:
                tokens.insert(0, self.next())
            except StopIteration:
                continue
        self._pushed.extend(tokens)
        return TokenStream(tokens)

    def fetch_until(self, num=1):
        """
        Fetch `num` tokens from the Stream.

        :return: TokenStream object, with all fetched
                 tokens, until the `StopIteration`
                 exception.
        """
        fetched_tokens = []
        for i in xrange(num):
            try:
                fetched_tokens.append(self.next())
            except StopIteration:
                raise EndOfStream('end of stream')
        return TokenStream(fetched_tokens)

    def feed(self, token):
        """Push a yielded token back to the stream."""
        self._pushed.append(token)
    push = feed
