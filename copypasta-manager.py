#!/usr/bin/python
# -*- coding: utf-8 -*-

#       Copyright 2010 Nils Dagsson Moskopp // erlehmann

#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from __future__ import with_statement

import gtk
import os

class CopypastaManager:
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("Interface.GtkBuilder")
        builder.connect_signals(self)

        self.window = builder.get_object("window")

        self.statusbar = builder.get_object("statusbar")

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
        self.print_status("file import", "Importiert: %s" % self.pastapath)

    def main(self):
        self.window.show_all()
        gtk.main()

    def on_button_copy_clicked(self, button):
        start, end = self.pastabuffer.get_bounds()
        text = self.pastabuffer.get_text(start, end)

        clipboard = gtk.clipboard_get()
        clipboard.set_text(text)
        clipboard.store()

    def on_button_delete_clicked(self, button):
        iter = self.pastaselection.get_selected()[1]
        abspath = self.pastastore.get_value(iter, 2)

        if os.path.isfile(abspath):
            try:
                os.remove(abspath)
                self.pastastore.remove(iter)
                self.print_status("file delete", "Gelöscht: %s" % abspath)
            except OSError, e:
                self.print_status("file delete", "Löschen fehlgeschlagen: %s" % e)
        elif os.path.isdir(abspath):
            self.print_status("file delete", "Löschen fehlgeschlagen: Ist ein Verzeichnis.")
        
    def on_button_new_clicked(self, button):
        iter = self.pastaselection.get_selected()[1]

        try:
            abspath = self.pastastore.get_value(iter, 2)
        except TypeError:
            abspath = self.pastapath

        if os.path.isdir(abspath):
            dir = abspath
        elif os.path.isfile(abspath):
            dir = os.path.dirname(abspath)
            iter = None

        title = "Neue Kopierpaste"
        newfile = os.path.join(dir, title)

        if not os.path.isfile(newfile):
            try:
                with open(newfile, 'w') as file:
                    pass
                self.pastastore.append(iter, [title, "", newfile])
            except:
                self.print_status("file creation", "Dateierstellung fehlgeschlagen: %s" % abspath)
        else:
            self.print_status("file creation", "Dateierstellung fehlgeschlagen: „%s“ existiert bereits." % title)

    def on_pastabuffer_changed(self, buffer):
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end)

        iter = self.pastaselection.get_selected()[1]
        self.pastastore.set(iter, 1, text)

        abspath = self.pastastore.get_value(iter, 2)
        if os.path.isfile(abspath):
            try:
                with open(abspath, 'w') as file:
                    file.write(text)
            except IOError:
                self.print_status("file open", "Aktualisierung fehlgeschlagen: %s" % abspath)

    def on_renderer_edited(self, cell, path, text, model):
        try:
            oldname = model[path][2]
            newname = os.path.join(os.path.dirname(model[path][2]),text)

            if not oldname == newname:
                if not os.path.exists(newname):
                    os.rename(oldname, newname)
                    model[path][0] = text
                    model[path][2] = newname
                else:
                    self.print_status("file rename", "Umbenennen fehlgeschlagen: Datei %s existiert." % newname)

        except OSError, e:
            self.print_status("file rename", "Umbenennen fehlgeschlagen: Wakarimasen lol.")

    def on_row_changed(self, treeselection):
        iter = treeselection.get_selected()[1]
        if iter:
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
            if not filename.startswith("."):
                abspath = os.path.join(path, filename)
    
                if os.path.isfile(abspath):
                    try:
                        with open(abspath) as file:
                            content = file.read()
                            self.pastastore.append(iter, [filename, content, abspath])
                    except IOError:
                        pass
                if os.path.isdir(abspath):
                    parent = self.pastastore.append(iter, [filename, "", abspath])
                    self.populate_pastatree(treestore, abspath, parent)

    def print_status(self, context, message):
        cid = self.statusbar.get_context_id(context)
        self.statusbar.push(cid, message)

if __name__ == '__main__':
    cm = CopypastaManager()
    cm.main()
