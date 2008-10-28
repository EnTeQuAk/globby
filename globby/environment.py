#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
    globby.environment
    ~~~~~~~~~~~~~~~~~~

    This module provides the command line interface
    and some minor functions.

    :copyright: 2006-2007 by Sebastian Koch and Christopher Grebs.
    :license: GNU GPL, see LICENSE for more details.
"""
import sys
import shutil
import os
from os.path import join, abspath, isdir, isfile, getmtime, exists
from tempfile import gettempdir
from threading import local, Lock
from jinja2 import Environment as JinjaEnvironment
from jinja2.loaders import FileSystemLoader
from jinja2.exceptions import TemplateNotFound
import globby
from globby.utils.text import read_file, write_file
from globby.exceptions import ProjectExists, ProjectNotFound, IsCurrentProject


FORBITTEN_PROJECT_THEMES_NAMES = ['.svn']
FORBITTEN_ENDSWITHES = ['~', '.bak']

#: helds all the thread local variables
#: currently those are:
#:
#: `env`:
#:      reference to the environment in the current thread
_locals = local()

#: the lock for the evironment setup
_setup_lock = Lock()

def setup_env(main_path, bind_to_thread=False, **std_args):
    """
    This returns a new Environment instance.

    Also the Environment class will be added to the
    _locals variable.

    If ``bind_to_thread`` is set to True the Environment will
    be set in this thread.
    """

    _setup_lock.acquire()
    try:
        # make sure this thread has access to the variable so just set
        # up a partial class and call __init__ later.
        _locals.env = env = object.__new__(Environment)
        env.__init__(main_path, **std_args)
    finally:
        # if there was no error when setting up the Environment instance
        # we should now have an attribute here to delete
        if hasattr(_locals, 'env') and not bind_to_thread:
            del _locals.env
        _setup_lock.release()
    return env

from globby import api


class ProjectEnvironment(object):
    """
    This object provides serveral methods
    to work with projects.
    It also represents the actual project.
    """
    def __init__(self, main_path, project_name='documentation',
                 projects_dir_name='projects', suffix='txt'):
        self.main_path = main_path
        self.name = project_name
        self.projects_dir_name = projects_dir_name
        self.suffix = suffix

        # the main projects path
        self.projects_path = join(
            abspath(self.main_path),
            self.projects_dir_name,
        )

        # the path to the choosen project
        self.path = join(
            self.projects_path,
            self.name
        )

        self.rendered_path = join(
                self.main_path,
                self.projects_dir_name,
                self.name,
                'rendered'
        )
        # some caches, so that we don't have to watch
        # the directorys for all projects or files
        self._all_projects_cache = []
        self._all_files_cache = []

    def set_project(self, name):
        """
        Set a new project as the actual one
        """
        #XXX: do we need to be able to set the other
        #     parameters, like prokects_dir_name and
        #     suffix?
        self.__init__(self.main_path, name,
                      self.projects_dir_name,
                      self.suffix)

    def make_new_project(self, name):
        """
        Create a new project and write the required
        ``menue.txt``
        """
        if name in self.all_projects:
            #XXX: exit silent?
            raise ProjectExists(
                _('%(project)s allready exists') % {'project': name}
            )
        new_project_pth = join(self.projects_path, name)
        os.mkdir(new_project_pth, 0777)
        menue_msg = _('#This menue file was automaticly generated for the '
                     'project "%(project)s"' % {'project': name})
        write_file(join(new_project_pth, 'menue.txt'), menue_msg)
        del self._all_projects_cache[:]

    def delete_project(self, name):
        """
        Remove an existing project from
        the filesystem.
        """
        if not name in self.all_projects:
            raise ProjectNotFound(
                _('%(project)s not found') % {'project': name}
            )
        if name == self.name:
            raise IsCurrentProject(
                _('%(project)s is the choosen project. You can\'t delete it')
                    % {'project': name}
            )
        pth = join(self.projects_path, name)
        shutil.rmtree(pth)
        del self._all_projects_cache[:]

    @property
    def all_projects(self):
        """return all projects"""
        names = []
        if self._all_projects_cache:
            # since we don't want to do this loop everytime,
            # we breake it if we already cached the files.
            names = self._all_projects_cache
        else:
            for fodn in os.listdir(self.projects_path):
                if isdir(join(self.projects_path, fodn)):
                    if not fodn in FORBITTEN_PROJECT_THEMES_NAMES:
                        names.append(fodn)
        self._all_projects_cache = names
        return names

    @property
    def all_files(self):
        """
        Return all files of the choosen project
        except SVN related and backup ones.
        We also split the file suffix and does not
        match the menue file.
        If you need the suffix or the menue file
        use ``all_files_unfiltered``.
        """
        files = []
        if self._all_files_cache:
            files = self._all_files_cache
        else:
            for root, dirs, filenames in os.walk(self.path):
                if '.svn' in root:
                    continue
                for fn in filenames:
                    if isfile(join(root, fn)):
                        if (not [x for x in FORBITTEN_ENDSWITHES if x in fn]
                                and fn.endswith(self.suffix)
                                and not fn in ['menue.txt']):
                            files.append(fn.split('.'+self.suffix)[0])
        self._all_files_cache = files
        return files

    @property
    def all_files_unfiltered(self):
        """
        Return all files from the actual project.
        This property does not filter the files
        except of backup files. They won't be matched.
        """
        files = []
        for root, dirs, filenames in os.walk(self.path):
            for fn in filenames:
                if isfile(join(self.path, fn)):
                    if not [x for x in FORBITTEN_ENDSWITHES if x in fn]:
                        # it's not compleatly unfiltered, because nobody needs
                        # backup files ;)
                        files.append(fn)
        return files

    def map_full_path(self, files=True):
        """
        Return the absolute path of all files or projects.

        on `files` == True, we return the full path of all files (default)
        on `files` == False, we return the full path of all projects
        """
        rv = []
        if files:
            for fn in self.all_files:
                rv.append(join(self.projects_path, fn))
        else:
            for pn in self.all_projects:
                rv.append(join(self.projects_path, pn))
        return rv


class ThemeEnvironment(FileSystemLoader):
    """
    The `ThemeEnvironment` provides serveral fuctions
    to work with globby themes.
    It also represents the actual choosen theme.
    """

    def __init__(self, main_path, theme_name='default',
                 themes_dir_name='themes', suffix='tmpl'):

        self.main_path = main_path
        self.themes_path = join(self.main_path, themes_dir_name)
        self.path = join(self.themes_path, theme_name)
        self.name = theme_name
        self.themes_dir_name = themes_dir_name
        self.suffix = suffix

        # some caches, so that we don't have to watch
        # the directorys for all projects or files
        self._all_themes_cache = []

    def set_theme(self, name):
        """
        set a new theme name
        and all other values inherits from
        the theme name
        """
        self.__init__(self.main_path,
                      name,
                      self.themes_dir_name,
                      self.suffix)

    @property
    def tmpl_name(self):
        #XXX: configurable
        return self.name + '.' + self.suffix

    @property
    def all_themes(self):
        """return all themes"""
        names = []
        if self._all_themes_cache:
            # since we don't want to do this loop everytime,
            # we breake it.
            names = self._all_themes_cache
        else:
            for theme in os.listdir(self.themes_path):
                if isdir(join(self.themes_path, theme)):
                    if not theme in FORBITTEN_PROJECT_THEMES_NAMES:
                        names.append(theme)
        self._all_themes_cache = names
        return names

    def get_source(self, jinja_environment, name):
        """
        return the source of the template named `name`

        used by Jinja
        """
        def check_source_changed():
            mtime = getmtime(filename)
            try:
                return getmtime(filename) == mtime
            except OSError:
                return False

        filename = join(self.path, name)
        if not exists(filename):
            raise TemplateNotFound(name)
        contents = read_file(filename)
        return contents, filename, check_source_changed


class Environment(object):
    """
    The runtime environment from globby.
    All properties are stored in the Environment
    to ensure that every component can use them
    as needed
    """

    def __init__(self, main_path, **std_args):
        self.std_args = std_args

        self.main_path = abspath(main_path)

        self.debug = self.std_args.get('debug', True)
        self.logger = globby.logger.Logger(join(
            self.main_path, 'logs'), self.debug)

        self.project = ProjectEnvironment(
            self.main_path,
            self.std_args.get('project', 'documentation'),
            'projects',
            self.std_args.get('suffix', 'txt'),
        )
        self.theme = ThemeEnvironment(
            self.main_path,
            self.std_args.get('theme', 'default'),
            'themes',
            self.std_args.get('template_suffix', 'tmpl')
        )
        self.jinja_env = JinjaEnvironment(loader=self.theme)
        #XXX clearify `charset`
        self.charset = self.std_args.get('charset', 'utf-8')
        self.accept_all = self.std_args.get('accept_all', False)

        self.pygments_style = self.std_args.get('pygments_style', 'default')

        self.builder_dct = dict(
            [(x.name, x) for x in api.get_all_units(globby.builder.Builder)]
        )
        self.builder = self.builder_dct[
            self.std_args.get('builder', 'project2html')
        ]



        processors = globby.markup.get_all_processors()[1]
        self.markup_processor = processors[
            self.std_args.get('markup_processor', 'woxt')]

        self.template_context = {
            'markup_processor': self.markup_processor,
            'suffix':           self.project.suffix,
            'theme':            self.theme.name,
            'debug':            self.debug,
            'project':          self.project.name,
            'charset':          self.charset,
            'main_path':        self.main_path,
            'projects_path':    self.project.projects_path,
            'themes_path':      self.theme.themes_path,
            'copyright':        ('This page was generated with '
                            '<a href="http://globby.webshox.org">Globby</a>'),
        }

        self.css_data = {}

    def init(self, main_path=None, **std_args):
        """
        You can pass new command line options
        and a new main_path to the Environment.
        Due this method it's possible to pass them
        in the runtime.
        """
        main_path = main_path or self.main_path
        self.__init__(main_path, **std_args)

    def load_template(self, template):
        return self.jinja_env.loader.load(self.jinja_env, template)

    def parse_template(self, template, ctx=None):
        """
        Parse a template with the Jinja template engine
        """
        ctx = ctx or self.template_context
        if isinstance(template, basestring):
            tmpl = self.load_template(template)
        else:
            from jinja2.exceptions import TemplateError
            raise TemplateError("can't render the given Template")
        return tmpl.render(ctx)

    def exit_globby(self):
        # close the log-file
        if not self.logger.log_file.closed:
            self.logger.log_file.close()
        sys.exit(0)
