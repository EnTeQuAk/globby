#-*- coding: utf-8 -*-
"""
    globby.markup.processors.other
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Serveral simple wrappers around some
    third party markup processors.

    :copyright: 2007 by Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""

from globby.markup import BaseProcessor

__all__ = ['MarkdownProcessor', 'TextileProcessor']

class MarkdownProcessor(BaseProcessor):
    name = 'markdown'

    def to_html(self, text):
        try:
            from markdown import markdown
        except ImportError:
            raise ImportError('Please install the "markdown" library first!')
        return markdown(text.encode('utf-8')).decode('utf-8')


class TextileProcessor(BaseProcessor):
    name = 'textile'

    def to_html(self, text):
        try:
            from textile import textile
        except ImportError:
            raise ImportError('Please install the "textile" library first!')
        # the original Textile-Processor can't handle `unicode` data
        # so we have to convert the data to a processable codec (utf-8)
        text = text.encode('utf-8')
        data = textile(text, head_offset=0, validate=0, sanitize=0)
        # reconvert to unicode for internal use
        return data.decode('utf-8')
