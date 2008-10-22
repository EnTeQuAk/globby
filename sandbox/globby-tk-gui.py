#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    globby.gui.tk-interface
    ~~~~~~~~~~~~~~~~~~~~~~~

    This file implements a very simple
    but power- and featurefull GUI for
    the Globby Webpagegenerator

    :copyright: 2003 by Iuri Wickert, 2007 by Sebastian Koch.
    :license: GNU GPL, see LICENSE for more details.


"""
# TODO:
#
# Hintergrundfarbe ausgewählter Tab und hintergrundfarbe dazugehöriger Frame abgeleichen


import Tkinter as tk
from ScrolledText import ScrolledText
from tkMessageBox import showinfo, askyesno
import tkSimpleDialog
from time import sleep
import thread
import os
import shutil
import codecs
#import sys
#sys.path.append('/home/sabba/svn/globby/trunk/globby')
#sys.path.append(os.path.dirname(os.getcwd()))




class notebook:
    # initialization. receives the master widget
    # reference and the notebook orientation
    def __init__(self, master, side=tk.LEFT):

        self.active_fr = None
        self.count = 0
        self.choice = tk.IntVar(0)
        self.current_hotkeys = None

        # allows the TOP and BOTTOM
        # radiobuttons' positioning.
        if side in (tk.TOP, tk.BOTTOM):
            self.side = tk.LEFT
        else:
            self.side = tk.TOP

        # creates notebook's frames structure
        self.rb_fr = tk.Frame(master, borderwidth=1, relief=tk.RAISED)
        self.rb_fr.pack(side=side, fill=tk.X)
        self.screen_fr = tk.Frame(master, relief=tk.FLAT)
        self.screen_fr.pack(fill=tk.BOTH, expand=1)


    # return a master frame reference for the external frames (screens)
    def __call__(self):
        return self.screen_fr


    # add a new frame (screen) to the (bottom/left of the) notebook
    def add_screen(self, fr, title):
        b = tk.Radiobutton(self.rb_fr, text=title, indicatoron=0,
                    variable=self.choice, value=self.count,
                    command=lambda: self.display(fr),borderwidth=1,padx=10)
        b.pack(fill=tk.BOTH, side=self.side)

        # ensures the first frame will be
        # the first selected/enabled
        if not self.active_fr:
            fr.pack(fill=tk.BOTH, expand=1)
            self.active_fr = fr

        self.count += 1

        # returns a reference to the newly created
        # radiobutton (allowing its configuration/destruction)
        return b


    # hides the former active frame and shows
    # another one, keeping its reference
    def display(self, fr):

        self.active_fr.forget()
        fr.pack(fill=tk.BOTH, expand=1)
        self.active_fr = fr
        print "fr", fr
        print "self.choice", self.choice
        print "self.count", self.count


    def set_hotkeys(self, hotkeys, frame2bind):
        """Will (re)set hotkeys. Is called on init and on Tab change.
        Values:
            hotkeys:
                contains the hotkey and the corresponding action (Type = List)
            frame2bind:
                contains the frame to bind the Hotkeys
        """
        print "reset Hotkeys"




class Globby_Text_Editor(tk.Frame):
    def __init__(self, parent_widget, settings):
        # some initial values
        # TODO this Values are obsolete since Project_Settings covers them
        # --> self.settings.projects_path
        self.hash_opened_filename = None
        self.opened_filename = None
        self.settings = settings

        self.edit_button_list=[
            {'text':'new page', 'cmd':self.on_new_page,
                'keytxt':'CTRL+n','hotkey':'<Control-n>'},
            {'text':'del page', 'cmd':self.on_del_page,
                'keytxt':'CTRL+n','hotkey':'<DELETE>'} ,
            {'text':'save', 'cmd':self.on_save,
                'keytxt':'CTRL+s','hotkey':'<Control-s>'},
            {'text':'undo', 'cmd':self.on_undo,
                'keytxt':'CTRL+z','hotkey':'<Control-z>'},
            {'text':'redo', 'cmd':self.on_redo,
                'keytxt':'CTRL+y','hotkey':'<Control-y>'}]

        self.syntax_button_list=[
            {'text':'**bold**', 'cmd':self.on_tag_insert, 'open_tag':'**',
                'close_tag':'**','keytxt':'CTRL+b','hotkey':'<Control-b>'},
            {'text':'//italic//', 'cmd':self.on_tag_insert, 'open_tag':'//',
                'close_tag':'//', 'keytxt':'CTRL+i','hotkey':'<Control-i>'},
            {'text':'__underline__', 'cmd':self.on_tag_insert, 'open_tag':'__',
                'close_tag':'__', 'keytxt':'CTRL+u','hotkey':'<Control-u>'},
            {'text':'[Link]', 'cmd':self.on_tag_insert, 'open_tag':'[',
                'close_tag':']', 'keytxt':'CTRL+l','hotkey':'<Control-l>'},
            {'text':'¸¸sub¸¸', 'cmd':self.on_tag_insert, 'open_tag':'¸¸',
                'close_tag':'¸¸', 'keytxt':'CTRL+d','hotkey':'<Control-d>'},
            {'text':'^^upper^^', 'cmd':self.on_tag_insert, 'open_tag':'^^',
                'close_tag':'^^', 'keytxt':'CTRL+q','hotkey':'<Control-q>'},
            {'text':'-~smaller~-', 'cmd':self.on_tag_insert, 'open_tag':'-~',
                'close_tag':'~-', 'keytxt':'CTRL+w','hotkey':'<Control-w>'},
            {'text':'+~bigger~+', 'cmd':self.on_tag_insert, 'open_tag':'+~',
                'close_tag':'~+', 'keytxt':'CTRL+e','hotkey':'<Control-e>'},
            {'text':'~~strike_thru~~', 'cmd':self.on_tag_insert, 'open_tag':'~~',
                'close_tag':'~~', 'keytxt':'CTRL+t','hotkey':'<Control-t>'} ]

        # build Widgets
        tk.Frame.__init__(self, parent_widget)
        self.pack(fill=tk.BOTH, expand=tk.YES)

        #self.baseframe = tk.Frame(parent_widget)
        #self.baseframe.pack(fill=tk.BOTH, expand=tk.YES)
        self.editor()
        self.button_frame()

        # start tracking text changes inside the editfield
        thread.start_new_thread(self.on_txt_changes, ('',))



    def editor(self):
        """ combine some Widgets to an enhanced editor (incl. Scrollbar)

        --> self.text
                the text widget itself

        --> self.opened_file_label
                Label on top of the editfield to show the name of the current
                opened File
                It can be used to show textchanges
        """
        # build widgets
        self.txtfrm = tk.Frame(self)
        self.txtfrm.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.YES)
        self.opened_file_label = tk.Label(self.txtfrm, text="No File chosen")
        self.opened_file_label.pack(fill=tk.X)
        self.text = ScrolledText(self.txtfrm, bg="white",
                                undo=1, maxundo=30,
                                wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT)
        self.text.insert(1.0, u"Please open a File to edit")

        # build first(reference -- new name??) hash for comparison on changes
        self.hash_opened_filename = hash(self.text.get(1.0,tk.END))

        # Set focus on textwidget and move cursor to the upper left
        self.text.focus_set()
        self.text.mark_set(tk.INSERT, '0.0')      # goto line
        self.text.see(tk.INSERT)                  # scroll to line


    def label_button_row(self, parent_widget=None,
                            btnlst=None, start_count=0):
        """Build a 2 column table with a label beside each button in a row.
        Bind a keyboard sequence to the button command.
        Display this keyboard sequence on the label.

        todo:
            - think about a parameter for the widget to bind the Hotkeys
            - rename to: labled_button_row, draw_labled_button_row

        Parameter:
        --> parent_widget:
                Parent widget to place the table

        --> btnlst:
                Type: List of dicts representing a button
                Example:
                    {'text':'**bold**',     # displayed on the Button (string)
                    'cmd':self.on_tag_insert,   # command
                    'open_tag':'**',        # chars representing the beginning
                                            # of a tag for inserting (string)
                    'close_tag':'**',       # chars representing the end
                                            # of a tag for inserting (string)
                    'keytxt':'CTRL+b',      # displayed on the Label (string)
                    'hotkey':'<Control-b>'} # keyboard sequence (string)
                Note:
                    The existence of 'open_tag' and 'close_tag' in btnlst
                    decides which command is bound to the Button.
                    If they aren't there 'cmd' must be a function without
                    parameters!!!
                    otherwise 'cmd' needs following parameters:
                        otag = btn['open_tag']
                        ctag = btn['close_tag']
                        event = None  # Placeholder for a keysequence

        --> start_count:
                Type: int

                Description:
                    The table is relized with tkinter grid layout manager.
                    start_count is used if there is already a grid
                    (with a Label beside a button).
                    start_count can add the automatic genrated
                    buttons under the existing.
                    In Globby_Editor it is used to put a label_button_row
                    under a Tkinter menubutton(file choose, headlines).
        """
        i = start_count
        for btn in btnlst:
            try:
                otag = btn['open_tag']
                ctag = btn['close_tag']
                event = None
                doit = lambda e=event, o=otag, c=ctag:self.on_tag_insert(e,o,c)
                tk.Button(parent_widget, text=btn['text'], command=doit,
                        relief=tk.RIDGE
                        ).grid(column=0, row=i, sticky=tk.W+tk.E)
                self.text.bind(btn['hotkey'],doit)
            except KeyError:
                tk.Button(parent_widget, text=btn['text'], command=btn['cmd'],
                        relief=tk.RIDGE
                        ).grid(column=0, row=i, sticky=tk.W+tk.E)
            tk.Label(parent_widget, text=btn['keytxt'], relief=tk.FLAT
                ).grid(column=1, row=i, sticky=tk.W)
            i +=1


    def button_frame(self):
        """draws a frame to hold a edit- and syntax-buttons under each other
        """
        self.btnfrm = tk.Frame(self)
        self.btnfrm.pack(fill=tk.BOTH, side=tk.LEFT)
        self.edit_buttons()
        self.syntax_buttons()


    def edit_buttons(self):
        """draws a frame with buttons for editing (save, undo, redo, open)
        """

        # genrate a labelframe
        self.efrm = tk.LabelFrame(self.btnfrm, text="Edit Buttons")
        self.efrm.pack(fill=tk.BOTH, padx=5, pady=5)

        # generate a button with a pulldown menue to open a file to edit
        self.file_open_mbtn = tk.Menubutton(self.efrm, text='Open File')
        # generate the pulldown menue
        self.file_open_menu = tk.Menu(self.file_open_mbtn,
                                        postcommand=self.gen_file2edit_menu)
        # bind the pulldown menue to the menubutton
        self.file_open_mbtn.config(menu=self.file_open_menu, relief=tk.RIDGE)


        self.file_open_mbtn.grid(column=0,row=0, sticky=tk.W+tk.E)

        # label beside the Button to display the associated keyboard shortcut
        self.file_open_lbl = tk.Label(self.efrm, text='CTRL+o', relief=tk.FLAT)
        self.file_open_lbl.grid(column=1, row=0, sticky=tk.W+tk.E)


        # generate buttons as described in self.edit_button_list
        self.label_button_row(self.efrm, self.edit_button_list, 2)


        # bind keyboard shortcut to the menue
        self.text.bind('<Control-o>',
                lambda e: self.file_open_menu.tk_popup(e.x_root, e.y_root))


    def gen_file2edit_menu(self):
        """generates a (new) menu bound to the file chooser button
        so every time when a project is created or deleted
        gen_choose_project_menu should be called
        """
        # delete all existing menue entrys
        self.file_open_menu.delete(0,tk.END)
        proj_path = os.path.join(self.settings.projects_path,
                                self.settings.current_project )
        print "proj_path", proj_path
        for this_file in os.listdir(proj_path):
            splitted = os.path.splitext(this_file)
            if splitted[1] == ".txt" and splitted[0] != "menue":
                #print "this_file",this_file
                open_file = os.path.join(proj_path, this_file)
                do_it = lambda bla = open_file:self.on_open(bla)
                self.file_open_menu.add_command(label=splitted, command=do_it)




    def syntax_buttons(self):
        """draws a frame with buttons for insert (wiki)markup

        idea: new parameter for on_tag_insert()
            jump_in_between=True/False so a pulldown list for different levels
            of headlines arn't necessary
        """

        # genrate a labelframe
        self.sfrm = tk.LabelFrame(self.btnfrm, text="Syntax Buttons")
        self.sfrm.pack(fill=tk.BOTH, padx=5, pady=5)

        # generate a button with a pulldown menue für headline Syntax
        self.headln_menubtn = tk.Menubutton(self.sfrm, text='= Headlines =')
        # generate the pulldown menue
        self.headln_menu = tk.Menu(self.headln_menubtn)
        # bind the pulldown menue to the menubutton
        self.headln_menubtn.config(menu=self.headln_menu, relief=tk.RIDGE)
        # generate menue entrys
        i=1
        for entry in ('h1','h2','h3','h4','h5','h6'):
            otag = '\n\n'+'='*i+' '
            ctag = ' '+'='*i+'\n\n'
            doit = lambda event=None, o=otag, c=ctag:self.on_tag_insert(event,o,c)
            self.headln_menu.add_command(label=entry, command=doit)
            i+=1
        self.headln_menubtn.grid(column=0,row=0, sticky=tk.W+tk.E)

        # label beside the Button to display the associated keyboard shortcut
        self.headln_lbl = tk.Label(self.sfrm, text='CTRL+h', relief=tk.FLAT)
        self.headln_lbl.grid(column=1, row=0, sticky=tk.W+tk.E)

        # generate buttons as described in self.edit_button_list
        self.label_button_row(self.sfrm, self.syntax_button_list, 1)

        # bind keyboard shortcut to the menue
        self.text.bind('<Control-h>',
                lambda e: self.headln_menu.tk_popup(e.x_root, e.y_root))


    def on_txt_changes(self, dummy_value=tk.NONE):
        """ tracks text changes inside the editfield by comparing hash values
        new name: visualize_txt_changes???
        """
        while True:
            new_hash = hash(self.text.get(1.0, tk.END))
            if new_hash != self.hash_opened_filename:
                #print "changes"
                self.opened_file_label.configure(fg="red")
            else:
                #print "no changes"
                self.opened_file_label.configure(fg="black")
            sleep(0.2)


    def on_open(self, file_to_open=None):
        """- opens a *.txt file from project folder
        - generates a reference hash.
        - Brings the cursor to the upper left and show this position
          in the textfield

        Parameter:
        --> file_to_open:
                complete path for file to open
        idea:
            - rename file_to_open to openfile or file_to_open
        """
        self.opened_file_to_open = file_to_open
        self.opened_file_label.configure(text=file_to_open)
        self.text.delete(1.0, tk.END)

        self.opened_filename = os.path.basename(file_to_open)


        # write file content into the editfield
        editfile = codecs.open(file_to_open,'r', 'utf-8')
        self.text.insert(1.0, editfile.read())
        editfile.close()

        # generate reference hash for a comparison to track text changes
        self.hash_opened_filename = hash(self.text.get(1.0,tk.END))

        self.text.edit_reset()                  # clear tk's undo/redo stacks
        self.text.focus_set()                   # focus to textfield
        self.text.mark_set(tk.INSERT, '0.0')    # place cursor to upper left
        self.text.see(tk.INSERT)                # and display this line


    def on_save(self):
        """ Safes the current edited file"""
        if self.opened_filename:
            print "on_safe_"
            print "  self.opened_filename",self.opened_filename

            self.hash_opened_filename = hash(self.text.get(1.0,tk.END))


            path_to_safe_file = os.path.join(self.settings.projects_path,
                                    self.settings.current_project,
                                    self.opened_filename)

            safefile = codecs.open(path_to_safe_file,'w', 'utf-8')
            safefile.write(self.text.get(1.0,tk.END))
            safefile.close()
            self.text.edit_reset()        #clear tk's undo/redo stacks
        else:
            showinfo('Globby Text Editor','No File to save \n\n'
                    'You need to choose a File before editing')


    def on_undo(self):
        try:                                    # tk8.4 keeps undo/redo stacks
            self.text.edit_undo( )              # exception if stacks empty
        except tk.TclError:
            showinfo('Globby Text Editor', 'Nothing to undo')


    def on_redo(self):
        print "redo"
        try:                                  # tk8.4 keeps undo/redo stacks
            self.text.edit_redo()             # exception if stacks empty
        except tk.TclError:
            showinfo('Globby Text Editor', 'Nothing to redo')


    def on_new_page(self):
        """ Ask the user to name the new File, create a blank File and load it
        into the Editorwidget

        TODO:   check if file with the new filename allready exists
                check if Filename contains Specialchars
        """
        print "on_new_page"
        nfile_name = tkSimpleDialog.askstring("New File Name",
                                    "Fill in a new File Name")
        proj_path = os.path.join(self.settings.projects_path,
                                self.settings.current_project)
        nfile_name = os.path.join(proj_path, nfile_name.strip()+'.txt')
        nfile = codecs.open(nfile_name, 'w', 'utf-8')

        current_project = self.settings.current_project
        infostring1 = u'# Diese Datei wurde automatisch mit '
        infostring2 = u'dem Projekt "%s" erstellt' % current_project
        nfile.write(infostring1+infostring2 )
        nfile.close()

        self.on_open(nfile_name)

    def on_del_page(self):
        """"""
        print "del page"
        # self.settings.current_project
        del_file = os.path.join(self.settings.projects_path,
                                    self.settings.current_project,
                                    self.opened_filename)

        del_page = askyesno("Do you really want to delete ", del_file)

        if del_page:
            #self.set_project(self.new_project_name)
            print "%s geloescht" % del_file
            os.remove(del_file)


    def on_tag_insert(self, event=None, open_tag=None, close_tag=None):
        """ inserts a (wiki)tag to the current cursor position.

        If there is no text marked in the editfield, open_tag and close_tag
        are inserted to the current cursor position behind each other and the
        cursor jumps in between.
        Otherwise the marked string is enclosed by open_tag and close_tag and
        inserted to the current cursor position. Here the new cursor position
        is right behind the complete inserted string with tags.

        At this moment this behavior is quite buggy :-(

        idea:
            - new parameter for on_tag_insert()
              jump_in_between=True/False so a pulldown list for different levels
              of headlines arn't necessary
            - rename to: on_insert_tag?? on_tag_insert

        Parameter:
        --> event                       # keyboard shortcut
        --> open_tag                    # string
        --> close_tag                   # string

        """
        #print 'event',event
        #print 'open_tag',open_tag
        #print 'close_tag',close_tag

        ## when no String is selected:
        if not self.text.tag_ranges(tk.SEL):
            print "no String is selected"
            insert_point = self.text.index('insert')
            insertline = insert_point.split('.')[0]
            addit = 1
            if event != None:
                print "event not None"
                addit = 2
            insertrow = str(int(insert_point.split('.')[1])+len(open_tag)+addit)
            new_insert_point = insertline+'.'+ insertrow
            self.text.insert(insert_point, open_tag+''+close_tag)
            # place cursor to insert_point
            self.text.mark_set(tk.INSERT, new_insert_point)
            # display this position on the editfield
            self.text.see(tk.INSERT)

        ## when a String is selected:
        else:
            #print "im else"
            marked_text = self.text.get(self.text.index(tk.SEL_FIRST),
                                        self.text.index(tk.SEL_LAST))
            replace_index = self.text.index(tk.SEL_FIRST)
            print "replace_index in selected", replace_index
            self.text.delete(self.text.index(tk.SEL_FIRST),
                            self.text.index(tk.SEL_LAST))
            self.text.insert(replace_index, open_tag+marked_text+close_tag)




class Project_Settings(tk.Frame):
    def __init__(self, parent_widget=None):
        """Builds the Interface for Project Settings"""
        #TODO: raise error if path does not exist
        #TODO: think about an extra Function for paths
        self.projects_path = os.path.join(os.path.dirname(os.getcwd()),'projects')
        self.current_project = 'documentation'


        #print os.path.join(os.path.dirname(os.getcwd()),'projects')

        tk.Frame.__init__(self, parent_widget)
        self.pack(fill=tk.BOTH, expand=tk.YES)


        self.choose_project_frame()
        self.new_project_frame()
        self.del_project_frame()

    def choose_project_frame(self):
        # genrate a labelframe
        self.project_frame = tk.LabelFrame(self, text="Choose a Project to work with")
        self.project_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        # generate Label to show the current project name
        self.project_name_label = tk.Label(self.project_frame,
                                            bg="white",
                                            text=self.current_project)
        self.project_name_label.grid(column=0,row=0, sticky=tk.W+tk.E)

        # generate a button with a pulldown menue to open a file to edit
        self.project_delete_mbtn = tk.Menubutton(self.project_frame, text='Change Project')
        # generate the pulldown menue
        self.project_delete_menu = tk.Menu(self.project_delete_mbtn)
        # bind the pulldown menue to the menubutton
        self.project_delete_mbtn.config(menu=self.project_delete_menu, relief=tk.RIDGE)
        # generate menue entrys
        self.gen_choose_project_menu()
        self.project_delete_mbtn.grid(column=1,row=0, sticky=tk.W+tk.E)

        # label beside the Button to display the associated keyboard shortcut
        self.project_delete_lbl = tk.Label(self.project_frame, text='CTRL+p', relief=tk.FLAT)
        self.project_delete_lbl.grid(column=2, row=0, sticky=tk.W+tk.E)

    def gen_choose_project_menu(self):
        """generates a (new) menu bound to the project chooser button
        so every time when a project is created or deleted
        gen_choose_project_menu should be called
        """
        # delete all existing menue entrys
        self.project_delete_menu.delete(0,tk.END)

        for entry in os.listdir(self.projects_path):
            entry_incl_path = os.path.join(self.projects_path,entry)
            #print entry_incl_path
            if os.path.isdir(entry_incl_path) and entry != ".svn":
                do_it = lambda bla = entry:self.set_project(bla)
                self.project_delete_menu.add_command(label=entry, command=do_it)

    def new_project_frame(self):
        # genrate a labelframe
        self.new_project_frame = tk.LabelFrame(self, text="Create a new Project")
        self.new_project_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        self.choose_button = tk.Button(self.new_project_frame,
                                        text="Enter a Name for your new Project",
                                        command=self.add_new_project)
        self.choose_button.grid(column=0,row=0, sticky=tk.W+tk.E)

        self.new_name_hotkey_label = tk.Label(self.new_project_frame,
                                            text='CTRL+n')
        self.new_name_hotkey_label.grid(column=1,row=0, sticky=tk.W+tk.E)



    def del_project_frame(self):
        # genrate a labelframe
        self.del_project_frame = tk.LabelFrame(self, text="Delete a Project")
        self.del_project_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        # generate a button with a pulldown menue to open a file to edit
        delbuttontxt = 'Choose Project to completely delete'
        self.del_project_delete_mbtn = tk.Menubutton(self.del_project_frame,
                                                    text = delbuttontxt)
        # generate the pulldown menue
        self.del_project_delete_menu = tk.Menu(self.del_project_delete_mbtn)
        # bind the pulldown menue to the menubutton
        self.del_project_delete_mbtn.config(menu=self.del_project_delete_menu,
                                            relief=tk.RIDGE)
        # generate menue entrys
        # Todo: regenerate menue on changes in project folder
        self.gen_delete_project_menu()
        self.del_project_delete_mbtn.grid(column=0,row=0, sticky=tk.W+tk.E)

        # label beside the Button to display the associated keyboard shortcut
        self.del_project_delete_lbl = tk.Label(self.del_project_frame,
                                                text='CTRL+d', relief=tk.FLAT)
        self.del_project_delete_lbl.grid(column=1, row=0, sticky=tk.W+tk.E)

    def gen_delete_project_menu(self):
        """generates a (new) menu bound to the project delete button
        so every time when a project is created or deleted
        gen_delete_project_menu should be called
        """
        # delete all existing menue entrys
        self.del_project_delete_menu.delete(0,tk.END)

        not_deletable_projects = ["documentation", "debug", ".svn"]
        for entry in os.listdir(self.projects_path):
            is_a_dir = os.path.isdir(os.path.join(self.projects_path,entry))
            if is_a_dir and entry not in not_deletable_projects:
                do_it = lambda bla = entry:self.delete_project(bla)
                self.del_project_delete_menu.add_command(label=entry, command=do_it)


    def set_project(self, project_name=None):
        """rename to choose working project"""
        self.current_project = project_name
        if project_name == None:
            self.project_name_label.configure(text="No Project Chosen")
        else:
            self.project_name_label.configure(text=project_name)


    def add_new_project(self):
        "dummy"
        print "new project"

        # TODO:
        # make it impossible to use special chars like german "Umlauts"

        # Hier wird der Dialog aufgerufen. Beim Drücken auf OK
        # wird der Inhalt des Entys in email gespeichert
        self.new_project_name = tkSimpleDialog.askstring("New Project Name",
                                    "Fill in a new Project Name")
        if self.new_project_name:
            new_proj_folder = os.path.join( self.projects_path,
                                            self.new_project_name)
            os.mkdir(new_proj_folder,0777)
            menue_txt = file(os.path.join(new_proj_folder, 'menue.txt'), 'w')
            infostring1 = '# Diese Datei wurde automatisch mit '
            infostring2 = 'dem Projekt "%s" erstellt' % self.new_project_name
            menue_txt.write(infostring1+infostring2 )
            menue_txt.close()

            # regenerate pulldown menues
            self.gen_choose_project_menu()
            self.gen_delete_project_menu()

            infotxt = ("Do you want to choose this new Projekt:"
                      "\n\n%s\n\n"
                      "as current working Projekt?")% self.new_project_name
            set_proj_as_current = askyesno("Set current Project",infotxt)

            if set_proj_as_current:
                self.set_project(self.new_project_name)

    def delete_project(self, deleteable_project):
        """Delete a Project(folder) incl all Subfolders, all Files and redraws
         - choose_project_menu
         - delete_project_menu

        NOTE: Currently no Errorhandling on not fitting rights (to delete)
        """

        delinfo = "Do you really want to delete this Project:\n\n%s" % deleteable_project
        shure_to_delete = askyesno("Delete Project",delinfo)

        if shure_to_delete:
            shutil.rmtree(os.path.join(self.projects_path, deleteable_project))
            # regenerate pulldown menues
            self.gen_choose_project_menu()
            self.gen_delete_project_menu()

            if self.current_project == deleteable_project:
                self.set_project()
                print "self.current_project == deleteable_project"


class Generate_HTML(tk.Frame):
    def __init__(self, parent_widget=None):
        """Builds the Interface for Project Settings"""
        self.themes_path = os.path.join(os.path.dirname(os.getcwd()),'themes')
        self.current_theme = 'default'

        tk.Frame.__init__(self, parent_widget)
        self.pack(fill=tk.BOTH, expand=tk.YES)

        self.choose_theme_frame()

    def choose_theme_frame(self):
        # genrate a labelframe

        self.theme_frame = tk.LabelFrame(self, text="Choose a Theme")
        self.theme_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        # generate Label to show the current project name
        self.theme_name_label = tk.Label(self.theme_frame,
                                            bg="white",
                                            text=self.current_theme)
        self.theme_name_label.grid(column=0,row=0, sticky=tk.W+tk.E)

        # generate a button with a pulldown menue to open a file to edit
        themebuttontxt = 'Choose Theme for your website'
        self.theme_delete_mbtn = tk.Menubutton(self.theme_frame,
                                                    text = themebuttontxt)
        # generate the pulldown menue
        self.theme_delete_menu = tk.Menu(self.theme_delete_mbtn)
        # bind the pulldown menue to the menubutton
        self.theme_delete_mbtn.config(menu=self.theme_delete_menu,
                                            relief=tk.RIDGE)
        # generate menue entrys
        for entry in os.listdir(self.themes_path):
            entry_incl_path = os.path.join(self.themes_path,entry)
            if os.path.isdir(entry_incl_path) and entry != ".svn":
                do_it = lambda bla = entry:self.set_theme(bla)
                self.theme_delete_menu.add_command(label=entry, command=do_it)
        self.theme_delete_mbtn.grid(column=1,row=0, sticky=tk.W+tk.E)

        # label beside the Button to display the associated keyboard shortcut
        self.theme_delete_lbl = tk.Label(self.theme_frame,
                                                text='CTRL+t', relief=tk.FLAT)
        self.theme_delete_lbl.grid(column=2, row=0, sticky=tk.W+tk.E)

    def set_theme(self, theme_name=None):
        "dummy"
        print "TODO Write Docstring"
        self.current_theme = theme_name
        self.theme_name_label.configure(text=theme_name)



class Main_GUI:
    def __init__(self, parent_widget=None):
        """Builds the Tabbed Notebook Interface"""
        n = notebook(parent_widget, tk.TOP)

        project_frame = Project_Settings(n())

        editor_frame = Globby_Text_Editor(n(), project_frame)

        menu_edit_frame = tk.Frame(n())
        b6 = tk.Button(menu_edit_frame, text='menu_edit_frame', command=self.dummy_funct)
        b7 = tk.Button(menu_edit_frame, text='Beep 2', command=self.dummy_funct)
        b6.pack(fill=tk.BOTH, expand=1)
        b7.pack(fill=tk.BOTH, expand=1)

        gen_html_frame = Generate_HTML(n())

        upload_frame = tk.Frame(n())
        b10 = tk.Button(upload_frame, text='upload_frame', command=self.dummy_funct)
        b11 = tk.Button(upload_frame, text='Beep 2', command=self.dummy_funct)
        b10.pack(fill=tk.BOTH, expand=1)
        b11.pack(fill=tk.BOTH, expand=1)

        help_frame = tk.Frame(n())
        b10 = tk.Button(help_frame, text='help_frame', command=self.dummy_funct)
        b11 = tk.Button(help_frame, text='Beep 2', command=self.dummy_funct)
        b10.pack(fill=tk.BOTH, expand=1)
        b11.pack(fill=tk.BOTH, expand=1)

        n.add_screen(project_frame, "choose / create Project F1")
        n.add_screen(editor_frame, "edit a Page F2")
        n.add_screen(menu_edit_frame, "edit Menue F3")
        n.add_screen(gen_html_frame, "generate website F4")
        n.add_screen(upload_frame, "upload website F5")
        n.add_screen(help_frame, "Help / Info F12")


        # workaround for wrongly displayed frames
        # last called Frame is displayed on all frames until last called Frame
        # has been activated)
        #
        # TODO: why is it so?
        n.display(editor_frame)
        n.display(menu_edit_frame)
        n.display(gen_html_frame)
        n.display(upload_frame)
        n.display(help_frame)
        n.display(project_frame)

    def dummy_funct(self):
        print "dummy - WERDE ICH NOCH GEBRAUCHT?"



if __name__ == "__main__":
    a = tk.Tk()
    Main_GUI(a)
    a.mainloop()
