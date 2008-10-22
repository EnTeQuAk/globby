#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    globby.builder
    ~~~~~~~~~~~~~~

    Builder Unit. This unit is used to
    build the projects to websites.

    Since globby is at most modularized it's also possible
    to do other things with the project.
    Just implement your own Unit, that inherits from `Builder`.

    :copyright: 2006-2007 Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""

import errno
import os
from os.path import join

from globby import Unit
from globby.exceptions import FileParserError
from globby.utils.menue import MenueParser, MenueLexer
from globby.utils.text import read_file, write_file


class Builder(Unit):
    name = None

    def __init__(self, env):
        self.env = env
        self.logger = env.logger

    def parse_project(self):
        """
        This method will parse the project files
        and generate the output.
        This output can be serveral things, like
        HTML files, PDF or Latex.
        """
        raise NotImplementedError


class Project2HTML(Builder):
    name = 'project2html'

    def __init__(self, env):
        super(Project2HTML, self).__init__(env)

        self.project = self.env.project
        self.charset = self.env.charset
        self.theme = self.env.theme
        self.menue = self.generate_menue()
        self.processor = self.env.markup_processor(self.env)

        self.template_ctx = self.env.template_context
        self.template_ctx['project_files'] = self.project.all_files
        self.template_ctx['menue'] = self.menue

    def generate_menue(self):
        if os.path.isfile(join(
                self.project.path,
                ('menue.'+self.project.suffix))):
            # a menue file was found in the project directory so use it.
            menue_file_data = read_file(join(
                    self.project.path,
                    ('menue.'+self.project.suffix)
                )
            )
            menue_file_data = menue_file_data
        else:
            # if no menue file exists:
            #     generate a menue with all files in the project directory
            menue_file_data = u'\n'.join(self.project.all_files)

        return MenueParser(MenueLexer(menue_file_data)).get_output()

    def parse_project(self):
        try:
            os.mkdir(self.project.rendered_path)
            self.logger.info_msg(
                _('created ...%s') % self.project.rendered_path
            )
        except OSError, err:
            if err.errno == errno.EEXIST:
                self.logger.info_msg(_('I\'ll overwrite %s') % err.filename)
        # write the CSS, to be shure that we write it only once
        self.logger.debug_msg(_('reading CSS-Data...'))
        self.env.css_data['main_css'] = '\n/*Theme specific CSS*/\n'
        self.env.css_data['main_css'] += read_file(
                '%s/themes/%s/%s.css' %(
                    self.env.main_path,
                    self.theme.name,
                    self.theme.name), charset=self.charset)
        for data_file in self.project.all_files:
            if data_file != 'menue':
                try:
                    data_file = data_file + '.' + self.project.suffix
                    self.logger.debug_msg(
                        _('reading datafile %(fn)s ...') % {'fn': data_file}
                    )
                    # read the content of the `data_file`
                    data = read_file(
                        join(self.project.path, data_file),
                        charset=self.charset
                    )

                    # parse the content
                    self.logger.debug_msg(_('parsing datafile %(fn)s...')
                                            % {'fn': data_file})

                    data = self.processor.to_html(data)

                    # write the theme
                    self.logger.debug_msg(
                        _('rendering data with the choosen theme "%s"')
                            % self.theme.name
                    )
                    # parse the theme
                    tmpl = self.env.parse_template(
                        join(self.env.main_path, 'themes', self.theme.name, self.theme.tmpl_name),
                        self.template_ctx.update({
                            'content': data,
                            'title': '%s | %s' % (
                                self.project.name,
                                data_file.split('.')[0].capitalize()
                            )
                        })
                    )
                    # write parsed content to self.rendered_path
                    self.logger.debug_msg(
                        _('writing rendered data to %s')
                            %('%s.html' % (
                                join(
                                    self.project.rendered_path,
                                    data_file.split('.')[0]
                                )
                            )
                        )
                    )
                    write_file('%s.html' % (join(
                        self.project.rendered_path,
                        data_file.split('.')[0]
                    )), tmpl, charset=self.charset)

                except IOError, err:
                    raise FileParserError(err)
            else:
                pass
            self.logger.debug_msg(_('write CSS-Data'))
            write_file(join(
                    self.project.rendered_path,
                    'style.css'
                    ),
                u'\n'.join([x for x in self.env.css_data.values()]),
                charset=self.charset
            )
        self.logger.info_msg(_('All done!\n\n'))
