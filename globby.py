#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os, sys
from os.path import abspath, dirname, join, pardir, isfile
from optparse import OptionParser, Option
import time

try:
    from pygments.styles import get_all_styles
    PYGMENTS_IMPORTED = True
except ImportError:
    PYGMENTS_IMPORTED = False

import globby
from globby.api import setup_env, get_all_units
from globby.builder import Builder
from globby.cli import do_validate_opts, OptionHelpFormatter
from globby.cli.colors import nocolor, underline
from globby.markup import get_all_processors


# The I18N factory

LOCALE_PATH = join(abspath(dirname(globby.cli.__file__)), 'locale')
# the name of the gettext domain.
GETTEXT_DOMAIN = 'globby'

# set up the gettext system and locales
import gettext
import locale

gettext.install(GETTEXT_DOMAIN)

lang = 'en'
# choose language
for i, item in enumerate(sys.argv[1:]):
    if item == '-l':
        lang = sys.argv[i+2]
    elif item.startswith('--language='):
        lang = sys.argv[i].replace('--language=')
gettext_lang = gettext.translation(GETTEXT_DOMAIN, LOCALE_PATH, languages=[lang])

# register the gettext function for the whole interpreter as "_"
import __builtin__
__builtin__._ = gettext_lang.gettext
# a helper that ensures that the string is marked as translatable
# but that string will be translated later in the programm
__builtin__.N_ = lambda s: s


main_path = os.path.abspath(os.path.dirname(__file__))
# How to build a CLI-Option:
# The Options are parsed thought the builtin ``optparse`` module.
# BUT: We changed the help-system a little bit, so you still can use
#      all options you know about ``optparse`` but the argument `help`
#      can be a list, a tuple or a simple string.
#      for every tuple/list entry the Help-System will use a NEWLINE.
#      A string will be handled as a list with only one entry.
CLI_OPTION_LIST = [
        Option(
            #long-opt:
            '--project',
            #short-opt:
            '-p',
            #optional arguments:
            dest = 'project',
            help = N_('Set the value for the name of the project'),
        ),
        Option(
            #long-opt:
            '--theme',
            #short-opt:
            '-t',
            #optional arguments:
            dest = 'theme',
            default='default',
            help = N_('Set the name of the theme'),
        ),
        Option(
            #long-opt:
            '--suffix',
            #optional arguments:
            dest = 'suffix',
            default = 'txt',
            help = N_('The suffix of the files in "globby/projects/PROJECT/"'),
        ),
        Option(
            #long-opt:
            '--debug',
            #short-opt:
            '-d',
            #optional arguments:
            dest = 'debug',
            help = (N_('Set automaticly the following vars:'),
                    N_('theme: default'),
                    N_('project:  debug'),
                    N_('accept_all: True')),
            action = 'store_true',
        ),
        Option(
            #long-opt:
            '--charset',
            #short-opt:
            '-c',
            #optional arguments:join
            dest = 'charset',
            help = N_('Define the charset for the generated HTML-Files'),
            default = 'utf-8',
        ),
        Option(
            #long-opt:
            '--markup',
            #optional arguments:
            dest = 'markup_processor',
            default = 'woxt',
            help = (N_('Choose a markup, witch to use for rendering the project'),
                    N_('(it defaults to \'woxt\')'),
                    N_('choose one of: %s') % ', '.join(
                                [x for x in get_all_processors()[1]])),
        ),
        Option(
            '--builder',
            dest = 'builder',
            default = 'project2html',
            help = (N_('Choose the Builder wich generates your output.'),
                    N_('(it defaults to \'project2html\')'),
                    N_('Choose one of: %s') % ', '.join(
                    [x.name for x in get_all_units(Builder)]
                    )),
        ),
        Option(
            #long-opt:
            '--accept_all',
            #short-opt:
            '-a',
            #optional aruguments:
            dest = 'accept_all',
            action = 'store_true',
            help = N_('accept all queries'),
        ),
        # needed to avoid an error if the user will
        # choose a language. (because it's changed
        # in an earlier state of the Globby application)
        Option(
            '--language',
            '-l',
            dest = 'language',
            help = N_('set a specific language'),
        ),
        Option(
            #long-opt:
            '--help',
            #short-opt:
            '-h',
            #optional aruguments:
            action = 'help',
            help = N_('show this help message and exit'),
        ),
        Option(
            #long-opt:
            '--version',
            #short-opt:
            '-v',
            #optional aruguments:
            action = 'version',
            help = N_('show the program\'s version number and exit'),
        ),
]
if PYGMENTS_IMPORTED:
    CLI_OPTION_LIST.append(
        Option(
            '--pygments-style',
            dest = 'pygments_style',
            default = 'default',
            help = (N_('If you\'re using Pygments, choose here the used style'),
                    N_('(defaults to \'default\')'),
                    N_('choose one of: %s') % ', '.join(
                                list(get_all_styles()))),
        )
    )

def parse_cli(env):
    """parse the command line"""
    parser = OptionParser(
        option_list = CLI_OPTION_LIST,
        formatter = OptionHelpFormatter(),
        usage = N_("python globby.py [options]"),
        # *must* be `False`. Except, our CLI-Help doesn't work!
        add_help_option=False
    )
    # replace the `print_help` message because `optparse` tries
    # to encode it with ASCII but in some translations (e.g german)
    # it doesn't work propertly.
    parser.print_help = lambda x=sys.stdout: x.write(parser.format_help())
    cl_opts, args = parser.parse_args(sys.argv[1:])
    cl_opts = do_validate_opts(env, cl_opts.__dict__)
    return cl_opts, args


def main():
    t_1 = time.time()
    env = setup_env(main_path)
    cl_opts, args = parse_cli(env)
    env.init(**cl_opts)
    if sys.platform[:3] == 'win':
        # Windows doesn't support colorized CMD-Output
        nocolor()
    if not env.debug and not env.accept_all:
        print _('Please validate all given options:')
    else:
        print _('You\'ve entered the following options.'
               '\nGlobby will use them to render the project:')
    print
    print '%20s: %s' % (_('option'), _('value'))
    print
    for opt in cl_opts.keys():
        print '%20s: %s' % (opt, (cl_opts[opt] or _('not given or set')))

    if not env.debug and not env.accept_all:
        print _('\nIf all Values are correct, type "y" to generate your page')
        print _('otherwise type "n" to abort '
                '(NOTE: it aborts on any key except "y")')
        choice = raw_input(_('Run parser? (y|n): ')).lower()
        while True:
            if choice.startswith('y') or choice.startswith('j'):
                break
            else:
                env.exit_globby()
    print '\n'
    builder = env.builder(env)
    builder.parse_project()
    env.exit_globby()


if __name__ == '__main__':
    main()
