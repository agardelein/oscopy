from gi.repository import Gtk, Gio, Gdk

IOSCOPY_SIGNAL_LIST_UI = 'oscopy/signal-list.ui'


class IOscopyAppWin(Gtk.ApplicationWindow):
    def __init__(self, app, uidir=None):
        Gtk.ApplicationWindow.__init__(self, title='IOscopy', application=app)
        self.app = app

        self.TARGET_TYPE_SIGNAL = 10354
        self.from_signal_list = [Gtk.TargetEntry.new("oscopy-signals",
                                                      Gtk.TargetFlags.SAME_APP,
                                                      self.TARGET_TYPE_SIGNAL)]

        self.to_main_win = [Gtk.TargetEntry.new("text/plain", 0,
                                                self.TARGET_TYPE_SIGNAL),
                            Gtk.TargetEntry.new('STRING', 0,
                                                self.TARGET_TYPE_SIGNAL),
                            Gtk.TargetEntry.new('application/octet-stream', 0,
                                                self.TARGET_TYPE_SIGNAL),
                            # For '*.raw' formats
                            Gtk.TargetEntry.new('application/x-panasonic-raw', 0,
                                                self.TARGET_TYPE_SIGNAL),
                            # For '*.ts' formats
                            Gtk.TargetEntry.new('video/mp2t', 0,
                                                self.TARGET_TYPE_SIGNAL),
                            ]

        self.builder = Gtk.Builder()
        self.builder.expose_object('store', self.app.store)
        self.builder.add_from_file('/'.join((self.app.uidir, IOSCOPY_SIGNAL_LIST_UI)))
        self.add(self.builder.get_object('scwin'))
        self.set_default_size(400, 300)
        handlers = {'row_activated': self.row_activated,
                    'drag_data_get': self.drag_data_get,
                    'tv_button_pressed': self.treeview_button_press,
                    'cell_toggled': self.cell_toggled,
                    }
        self.builder.connect_signals(handlers)
        # Bold font for file names
        col = self.builder.get_object('tvc')
        col.set_cell_data_func(self.builder.get_object('tvcrt'), self.reader_name_in_bold)        
        # Drag setup
        tv = self.builder.get_object('tv')
        tv.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,\
                               self.from_signal_list,\
                               Gdk.DragAction.COPY)
        # Drop setup
        self.drag_dest_set(Gtk.DestDefaults.MOTION |\
                        Gtk.DestDefaults.HIGHLIGHT |\
                        Gtk.DestDefaults.DROP,
                        self.to_main_win, Gdk.DragAction.COPY)
        self.connect('drag_data_received', self.drag_data_received)

        # Just hide, don't destroy window
        self.connect('destroy', lambda w, e: w.hide() or True)
        self.connect('delete-event', lambda w, e: w.hide() or True)

    def reader_name_in_bold(self, column, cell, model, iter, data=None):
        if len(model.get_path(iter)) == 1:
            cell.set_property('markup', "<b>" + model.get_value(iter, 0) +\
                                  "</b>")
        else:
            cell.set_property('text', model.get_value(iter, 0))

    def row_activated(self, widget, path, col):
        if len(path) == 1:
            return

        row = self.app.store[path]
        self.app.exec_str('ocreate %s' % row[0])

    def treeview_button_press(self, widget, event):
        if event.button == 3:
            print('treeview button press')
            return
            # FIXME : Display menu on button 3 click
            tv = widget
            ret = tv.get_path_at_pos(int(event.x), int(event.y))
            if ret is None: return True
            path, tvc, x, y = ret
            if len(path) == 1:
                # Not supported to add a full file
                return True
            sel = tv.get_selection()
            if path not in sel.get_selected_rows()[1]:
                # Click in another path than the one selected
                sel.unselect_all()
                sel.select_path(path)
            signals = {}
            def add_sig_func(tm, p, iter, data):
                name = tm.get_value(iter, 0)
                signals[name] = self._ctxt.signals[name]
            sel.selected_foreach(add_sig_func, None)
            tvmenu = gui.menus.TreeviewMenu(self.create)
            menu = tvmenu.make_menu(self._ctxt.figures, signals)
#            menu = self._uimanager.get_widget('/PopupMenu')
#            menu.show_all()
            print(menu)
            menu.popup(None, None, None, None, event.button, event.time)
            return True

        if event.button == 1:
            # It is not _that_ trivial to keep the selection when user start
            # to drag. The default handler reset the selection when button 1
            # is pressed. So we use this handler to store the selection
            # until drag has been recognized.
            tv = widget
            sel = tv.get_selection()
            rows = sel.get_selected_rows()[1]
            self.rows_for_drag = rows
            return False

    def cell_toggled(self, cellrenderer, path):
        if len(path) == 3:
            # Single signal
            if self.app.store[path][1].freeze:
                cmd = 'ounfreeze'
            else:
                cmd = 'ofreeze'
            self.app.exec_str('%s %s' % (cmd, self.app.store[path][0]))
        elif len(path) == 1:
            # Whole reader
            parent = self.app.store.get_iter(path)
            freeze = not self.app.store.get_value(parent, 2)
            if self.app.store[path][2]:
                cmd = 'ounfreeze'
            else:
                cmd = 'ofreeze'
            self.app.store.set_value(parent, 2, freeze)
            iter = self.app.store.iter_children(parent)
            while iter:
                self.app.exec_str('%s %s' % (cmd, self.app.store.get_value(iter, 0)))
                iter = self.app.store.iter_next(iter)

    def drag_data_get(self, widget, drag_context, data, target_type,\
                              time):
        if target_type == self.TARGET_TYPE_SIGNAL:
            tv = widget
            sel = tv.get_selection()
            (model, pathlist) = sel.get_selected_rows()
            iter = self.app.store.get_iter(pathlist[0])
            # Use the path list stored while button 1 has been pressed
            # See self._treeview_button_press()
            siglist = ' '.join([self.app.store[x][1].name for x in self.rows_for_drag])
            print(siglist)
            data.set_text(siglist, -1)
            return True
        print('drag data get')

    def drag_data_received(self, widget, drag_context, x, y, data,
                           target_type, time):
        name = data.get_text()
        if type(name) == str and name.startswith('file://'):
            self.app.exec_str('%%oread %s' % name[7:].strip())

