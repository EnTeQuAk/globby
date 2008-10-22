#-*- coding: utf-8 -*-
"""
    globby.markup.processors.rst
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Simple wrapper around the docutils ReStructedText module

    :copyright: 2007 by Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""
from globby.markup import BaseProcessor

__all__ = ['RstProcessor']


try:
    from docutils.core import publish_parts
    from docutils import nodes
    from docutils.parsers.rst import directives
    DOCUTILS_IMPORTED = True
except ImportError:
    DOCUTILS_IMPORTED = False

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
    def pygments_directive(name, arguments, options, content, lineno,
                   content_offset, block_text, state, state_machine):
        try:
            lexer = get_lexer_by_name(arguments[0])
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = get_lexer_by_name('text')
        normal_fmter = HtmlFormatter()
        lineno_fmter = HtmlFormatter(linenos=True)
        formatter = ('linenos' in options) and lineno_fmter or normal_fmter
        parsed = highlight(u'\n'.join(content), lexer, formatter)
        return [nodes.raw('', parsed, format='html')]
    PYGMENTS_IMPORTED = True
except ImportError:
    PYGMENTS_IMPORTED = False



class RstProcessor(BaseProcessor):
    name = 'rst'

    def check_installed(self):
        if not DOCUTILS_IMPORTED:
            raise ImportError('Please install the "docutils" library first')

    def to_html(self, text):
        self.check_installed()
        if PYGMENTS_IMPORTED:
            pygments_directive.arguments = (1, 0, 1)
            pygments_directive.content = 1
            pygments_directive.options = {'linenos': directives.flag}
            directives.register_directive('sourcecode', pygments_directive)
        parts = publish_parts(source=text, writer_name='html')
        # write only the HTML-Body
        data = parts['fragment'].strip()
        return data
