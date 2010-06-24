#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2010 Nils Dagsson Moskopp

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

# see also 

from __future__ import with_statement

import gtk
import os

class CopypastaManager:
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("Interface.GtkBuilder")
        builder.connect_signals(self)

        self.window = builder.get_object("window")

        self.pastaview = builder.get_object("textview_pasta")

        self.pastabuffer = builder.get_object("textbuffer_pasta")
        self.pastabuffer.connect('changed', self.on_pastabuffer_changed)

        self.pastastore = builder.get_object("treestore_pasta")

        renderer = gtk.CellRendererText()
        renderer.set_property( 'editable', True )
        renderer.connect('edited', self.on_renderer_edited, self.pastastore)

        titlecolumn = gtk.TreeViewColumn("Copypasta", renderer)
        titlecolumn.set_attributes(renderer, text=0)

        self.pastatree = builder.get_object("treeview_pasta")
        self.pastatree.append_column(titlecolumn)

        self.pastaselection = self.pastatree.get_selection()
        self.pastaselection.connect('changed', self.on_row_changed)

        self.pastapath = os.path.join(os.getcwd(),"pastas")
        self.populate_pastatree(self.pastatree, self.pastapath)

    def main(self):
        self.window.show_all()
        gtk.main()

    def on_button_copy_clicked(self, button):
        start, end = self.pastabuffer.get_bounds()
        text = self.pastabuffer.get_text(start, end)

        clipboard = gtk.clipboard_get()
        clipboard.set_text(text)
        clipboard.store()

    def on_button_new_clicked(self, button):
        self.pastastore.append(None, ["Neue Kopierpaste", "", ""])

    def on_pastabuffer_changed(self, buffer):
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end)

        iter = self.pastaselection.get_selected()[1]
        self.pastastore.set(iter, 1, text)

        abspath = self.pastastore.get_value(iter, 2)
        with open(abspath, 'w') as file:
            #file.seek(0)
            file.write(text)

    def on_renderer_edited(self, cell, path, text, model):
        try:
            oldname = model[path][2]
            newname = os.path.join(os.path.dirname(model[path][2]),text)
            os.rename(oldname, newname)
            model[path][0] = text
            model[path][2] = newname
        except OSError:
            pass

    def on_row_changed(self, treeselection):
        iter = treeselection.get_selected()[1]
        content = self.pastastore.get_value(iter, 1)
        self.pastabuffer.set_text(content)

    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()

    def populate_pastatree(self, treestore, path, iter=None):
        try:
            dirlist = os.listdir(path)
            dirlist.sort()
        except OSError: # no directory
            pass

        for filename in dirlist:
            abspath = os.path.join(path, filename)

            try:                
                with open(abspath) as file:
                    content = file.read()
                    self.pastastore.append(iter, [filename, content, abspath])
            except IOError:
                parent = self.pastastore.append(iter, [filename, "", abspath])
                self.populate_pastatree(treestore, abspath, parent)

if __name__ == '__main__':
    cm = CopypastaManager()
    cm.main()
