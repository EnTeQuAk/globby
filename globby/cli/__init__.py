#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    globby.cli
    ~~~~~~~~~~

    Add some help functions for the command line interface
    and provide a formatter for the ``optparse``-module

    :copyright: 2006-2007 by Sebastian Koch and Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""


import os
from optparse import HelpFormatter

from globby.cli import colors


# for the HelpFormatter
NO_DEFAULT = ("NO", "DEFAULT")

class OptionHelpFormatter(HelpFormatter):
    """
    HelpFormatter, for a better output for ``optparse``
    We overwrite the most of the output functions
    to implement a better Help-System, so
    Help-Messages looks nicer and are easier to implement.
    """
    def __init__(self,
                 indent_increment=0,
                 max_help_position=10,
                 width=None,
                 short_first=0
                 ):
        HelpFormatter.__init__(
            self,
            indent_increment,
            max_help_position,
            width, short_first
        )

    def expand_default(self, option):
        if self.parser is None or not self.default_tag:
            return option.help

        default_value = self.parser.defaults.get(option.dest)
        if default_value is NO_DEFAULT or default_value is None:
            default_value = self.NO_DEFAULT_VALUE

        help_list = []
        if not isinstance(option.help, str):
            for opt in option.help:
                if isinstance(opt, basestring):
                    # the `opt` is a string or a unicode
                    help_list.append(opt.replace(
                        self.default_tag, default_value)
                    )
                else:
                    # it should be a tuple or list, so try that
                    help_list.append('\n'.join([x for x in opt]).replace(
                        self.default_tag, default_value)
                    )
        else:
            # option.help is a string. We handle it as a iterable with one field
            help_list.append(option.help.replace(
                self.default_tag, default_value)
            )

        option.help = help_list
        return option.help

    def format_usage(self, usage):
        return colors.red(_('\nusage: %s\n') % usage)

    def format_heading(self, heading):
        return colors.bold('%*s%s:\n' % (self.current_indent, '', heading))

    def format_option(self, option):
        result = []

        opts = self.option_strings[option]
        # the help-string, where all available options
        # will be printed (long and short options)
        opts = colors.bold('\n%s\n' % (opts))

        result.append(opts)

        if option.help:
            help_lines = self.expand_default(option)
            for help_line in help_lines:
                result.append(colors.blue('%*s%s\n' % (4, ' ', _(help_line))))
        return ''.join(result)


def ask_user(env, param, opts, directory_list=None, output_str=None):
    """ask the user for `param` to fill ``opts[param]``"""

    if output_str:
        # for better controling about the CLI-Output
        output_str = output_str
    else:
        output_str = param

    assert directory_list is not None # needed ;)

    print _('\nThe following %s, found by Globby:\n') % _(output_str)
    i = 0
    for sub_directory in directory_list:
        i += 1
        print '(%d) -- %s' % (i, sub_directory)
    print _('\nNow fill in the number of the %s') % _(output_str)
    print colors.bold(_('To exit Globby fill in "END"!'))
    users_choice = raw_input(_('Choice: '))
    if users_choice.lower().startswith('e'):
        env.exit_globby()

    while True:
        try:
            users_choice = int(users_choice)
            if users_choice != 0:
                opts[param] = directory_list[users_choice-1]
                print _('You choose "%s"') % opts[param]
                break
        except (ValueError, IndexError):
            #the user entered a string instead of a integer
            if users_choice in directory_list:
                opts[param] = users_choice
                print _('You choose "%s"') % opts[param]
                break

        # this only happens if we **dont** break before, so the user entered
        # something wrong....
        print _('\nSorry, this %s does not exist!') % _(output_str)
        print (_('fill in "%(end)s" to exit Globby \n'
               'or fill in the correct %(out_str)s\n') % {
                   'end': colors.bold(_('END')), 'out_str': _(output_str)})
        users_choice = raw_input(_('new choice: '))


def do_validate_opts(env, opts):
    """validate all options and fill them, if needed"""

    if opts.has_key('debug') and opts['debug'] is not None:
        opts['theme'] = 'default'
        opts['project'] = 'debug'
        opts['accept_all'] = True
    else:
        if not opts['builder'] in env.builder_dct:
            print colors.red(_("The builder %r is not defined") % opts['builder'])
            env.exit_globby()
        if opts['project'] is None:
            projects = env.project.all_projects
            ask_user(env, 'project', opts, projects, N_('projects'))

        if opts['theme'] is None or opts['theme'] == 'default':
            if opts['theme'] == 'default' and not opts['accept_all']:
                print _("\nYou've choosen the default theme.\n"
                       "If this is your choice accept with 'y' otherwise apply a 'n'.")
                if not raw_input(_("your Choice (y/n): ")) in ['j', 'y']:
                    themes = env.theme.all_themes
                    ask_user(env, 'theme', opts, themes, N_('themes'))
        print '\n'
    return opts
