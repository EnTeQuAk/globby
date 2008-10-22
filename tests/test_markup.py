#-*- coding: utf-8 -*-
"""
    unittests for the Globby Markup Engine
    ======================================

    :copyright: 2007 by Christopher Grebs
    :license: GNU GPL, see LICENSE for more details.
"""
import unittest

from os.path import dirname, abspath, join

from globby.markup.processors.woxt import WoxtProcessor
from globby.environment import Environment

env = Environment(abspath(dirname((__name__))))
env.project.path = join(env.main_path, "tests", "test-projects")

STYLES_TEST = '**bold**__underlined__//**bolditalic**//``monospaced``^^superscript^^,,subscript,,~~strike~~'
STYLES_TEST_RESULT = ('<strong>bold</strong><ins>underlined</ins>'
                      '<em><strong>bolditalic</strong></em><tt>monospaced</tt>'
                      '<sup>superscript</sup><sub>subscript</sub><del>strike</del>')
HEADLINES_TEST = ('=Headline1=\n==Headline2==\n===Headline3===\n====Headline4====\n'
                  '=====Headline5=====\n======Headline6======')
HEADLINES_TEST_RESULT = '''<h1 id="Headline1">Headline1 <a title="Link to Headline1" class="anchor" href="#Headline1">#</a></h1>
<h2 id="Headline2">Headline2 <a title="Link to Headline2" class="anchor" href="#Headline2">#</a></h2>
<h3 id="Headline3">Headline3 <a title="Link to Headline3" class="anchor" href="#Headline3">#</a></h3>
<h4 id="Headline4">Headline4 <a title="Link to Headline4" class="anchor" href="#Headline4">#</a></h4>
<h5 id="Headline5">Headline5 <a title="Link to Headline5" class="anchor" href="#Headline5">#</a></h5>
<h6 id="Headline6">Headline6 <a title="Link to Headline6" class="anchor" href="#Headline6">#</a></h6>'''



class TestWoxtProcessor(unittest.TestCase):

    def setUp(self):
        self.woxt = WoxtProcessor(env)

    def test_font_styles(self):
        self.assertEqual(
            self.woxt.to_html(STYLES_TEST),
            STYLES_TEST_RESULT
        )

    def test_headlines(self):
        self.assertEqual(
            self.woxt.to_html(HEADLINES_TEST),
            HEADLINES_TEST_RESULT
        )

    def test_links(self):
        self.assertEqual(
            self.woxt.to_html(u'[http://webshox.org]'),
            u'<a href="http://webshox.org">http://webshox.org</a>'
        )

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWoxtProcessor, 'test'))
    return suite


if __name__ == '__main__':
    unittest.main()
