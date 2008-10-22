#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
from os.path import join, dirname, abspath, pardir
import pygtk
pygtk.require('2.0')
import pango
import gtk
import gtk.glade

try:
    import globby
except ImportError:
    pth = abspath(join(abspath(dirname(__file__)), pardir, pardir))
    sys.path.insert(0, pth)

from globby.environment import Environment
from globby.exceptions import ProjectIsActual, ProjectExists
from globby.exceptions import ProjectNotFound
from utils import * #XXX III

#TODO:
#   ** Project Edit **
#        * Let the following Buttons work: `New`
#        * Implement a Undo and Redo System
#        * Implement the Syntax Buttons
#        * Syntax Highlightning for the Sourcecode (Maybe use a Live Preview)

class GlobbyGTK(object):
    def __init__(self):
        # the Globby Environment
        self.env = Environment(main_path)

        # include the glade file
        glade_file = 'globby.glade'

        # activate our glade widgets and connect the delete event
        self.widgets = gtk.glade.XML(glade_file)
        self.widgets.signal_autoconnect(self)
        self.window = self.widgets.get_widget('window')
        self.window.connect('delete-event', self.on_quit)

        # the statusbar
        self.statusbar = self.widgets.get_widget('main_statusbar')

        # the combo box to change the active project
        self.projects_combo = self.widgets.get_widget('projects_combo')
        self.projects_store = gtk.ListStore(str)
        cell = gtk.CellRendererText()
        self.projects_combo.pack_start(cell, True)
        self.projects_combo.add_attribute(cell, 'text', 0)
        self.projects_combo.set_model(self.projects_store)
        # add all projects to the table
        for p in self.env.project.all_projects:
            miter = self.projects_combo.append_text(p)
        self.projects_combo.set_active(0)
        self.env.project.set_project(self.projects_combo.get_active_text())
        self.projects_combo.set_title('All projects')

        # for the text editor
        self.actual_project_file = None

        # text view and buffer for the project page editor
        self.text_view = self.widgets.get_widget('page_text')
        self.text_buffer = self.text_view.get_buffer()

        self.set_statusbar_msg('initial message', 'globbyGTK initialized')

    # **** Choose/Create Project Notebook label ****
    def on_project_changed(self, sender, arg=None):
        active = self.projects_combo.get_active_text()
        if active:
            self.env.project.set_project(active)
            self.set_statusbar_msg('changed project',
                'changed actual working project to %s' % active
            )

    def on_project_create_btn(self, sender, arg=None):
        text_widget = self.widgets.get_widget('new_project_name')
        name = text_widget.get_text()
        if name:
            ask_user = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                                        type=gtk.MESSAGE_QUESTION,
                                        buttons=gtk.BUTTONS_YES_NO)
            ask_user.set_markup('Do you really want to create the Project')
            ask_user.format_secondary_text(name)
            if ask_user.run() == gtk.RESPONSE_YES:
                try:
                    self.env.project.make_new_project(name)
                    self.set_statusbar_msg('created project',
                        '%s successfull created' % name)
                except ProjectExists:
                    info_dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                        type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK,
                        message_format='The Project %r allready exists.' % name)
                    info_dialog.format_secondary_text(
                        'Please delete it before create a new project named %r'
                        % name
                    )
                    if info_dialog.run():
                        info_dialog.destroy()
            ask_user.destroy()
        else:
            self.set_statusbar_msg('create project', 'No project name given')

    def on_project_delete_btn(self, sender, arg=None):
        text_widget = self.widgets.get_widget('delete_project_name')
        name = text_widget.get_text()
        if name:
            ask_user = gtk.MessageDialog(None,
                gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,
                gtk.BUTTONS_YES_NO)
            ask_user.set_markup('Do you really want to delete the Project')
            ask_user.format_secondary_text(name)
            if ask_user.run() == gtk.RESPONSE_YES:
                try:
                    self.env.project.delete_project(name)
                    self.set_statusbar_msg('delete project',
                        '%s successfull deleted' % name)
                except (ProjectNotFound, ProjectIsActual), err:
                    info_dialog = gtk.MessageDialog(
                        None, gtk.DIALOG_MODAL,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                        err.message
                    )
                    info_dialog.format_secondary_text(
                        'Please resolv the problem and try again')
                    if info_dialog.run():
                        info_dialog.destroy()
            ask_user.destroy()
        else:
            self.set_statusbar_msg('delete project', 'No project name given')

    # ******* Editor Window ******
    def on_open_project_file(self, sender, arg=None):
        dialog = gtk.FileChooserDialog(
            title='Select a Project',
            parent=self.window,
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        )
        dialog.set_current_folder(self.env.project.path)
        dialog.set_default_response(gtk.RESPONSE_OK)

        if dialog.run() != gtk.RESPONSE_OK:
            return dialog.destroy()

        filename = dialog.get_filename()
        if filename != self.actual_project_file:
            self.save_changes()
        self.actual_project_file = filename
        dialog.destroy()
        try:
            f = file(filename)
        except IOError, err:
            return self.show_error(str(err))
        try:
            text = f.read()
        finally:
            f.close()
        self.set_statusbar_msg('text_editor', 'opened %s' % filename.split('/')[-1])
        self.text_buffer.set_text(text)

    def on_save_changes(self, sender, arg=None):
        self.save_changes()

    def save_changes(self):
        if self.actual_project_file is None:
            return
        try:
            f = file(self.actual_project_file, 'w')
        except IOError, err:
            return self.show_error(str(err))
        try:
            text = self.text_buffer.get_text(
                self.text_buffer.get_start_iter(),
                self.text_buffer.get_end_iter()
            )
            f.write(text)
            self.set_statusbar_msg('text_editor',
                _('Wrote %s lines to %s') % (
                    self.text_buffer.get_line_count(),
                    self.actual_project_file.split('/')[-1]
            ))
        finally:
            f.close()

    # ******* Main Window related methods *******

    def set_statusbar_msg(self, desc, msg):
        ctx = self.statusbar.get_context_id(desc)
        id = self.statusbar.push(ctx, '  ' + msg + '...')
        return (id, ctx)

    def on_about(self, sender, arg=None):
        """Show the about dialog"""
        dialog = gtk.AboutDialog()
        dialog.set_name('globbyGTK')
        dialog.set_version('.'.join(map(str, VERSION)))
        dialog.set_copyright(get_copyright())
        dialog.set_authors(AUTHORS)
        dialog.set_translator_credits('\n'.join(TRANSLATORS))
        dialog.set_license(LICENSE)
        #logo
        logo = gtk.gdk.pixbuf_new_from_file("logo.png")
        dialog.set_logo(logo)
        dialog.set_comments('GTK application with a simple user interface '
                              'for the Globby website generator.')
        dialog.set_website('http://globby.webshox.org')
        if dialog.run():
            dialog.destroy()

    def dummy(self, sender, arg=None):
        self.set_statusbar_msg(
            'dummy', 'DUMMY call from %r :: args: %s'
            % (sender, arg)
        )

    def show_error(self, message, title=None):
        """Show an error window."""
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                   message)
        if title is None:
            title = _('Error')
        dialog.set_title(title)
        if dialog.run():
            dialog.destroy()

    def on_quit(self, sender, arg=None):
        self.save_changes()
        gtk.main_quit()

    def run(self):
        """start the application"""
        self.window.show()
        gtk.main()


def main():
    """application entrypoint."""
    try:
        app = GlobbyGTK()
        app.run()
    except KeyboardInterrupt:
        pass
    return 0
if __name__ == "__main__":
    main()
