import gobject
import gtk

from oscopy.readers.detect_reader import DetectReader
from oscopy import Figure
import oscopy

from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar

def report_error(parent, msg):
    dlg = gtk.MessageDialog(parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
    dlg.set_title(parent.get_title())
    dlg.run()
    dlg.destroy()

class App(object):
    __ui = '''<ui>
    <menubar name="MenuBar">
      <menu action="File">
        <menuitem action="Add file"/>
        <menuitem action="Quit"/>
      </menu>
    </menubar>
    </ui>'''

    def __init__(self):
        self._scale_to_str = {'lin': 'Linear', 'logx': 'LogX', 'logy': 'LogY',\
                                  'loglog': 'Loglog'}
        self._layout_to_str = {'horiz': 'Horizontal', 'vert':'Vertical',\
                                   'quad':'Quad'}
        self._ctxt = oscopy.Context()
        self._store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        self._create_widgets()
        #self._add_file('demo/irf540.dat')
        #self._add_file('demo/ac.dat')
        #self._add_file('demo/res.dat')
        self._figcount = 0
        self._windows_to_figures = {}
        self._current_graph = None
        self._current_figure = None

    def _add_file(self, filename):
        try:
            self._ctxt.read(filename)
        except NotImplementedError:
            report_error(self._mainwindow,
                         'Could not find a reader for %s' % filename)
            return
        it = self._store.append(None, (filename, None))
        for name, sig in self._ctxt.readers[filename].signals.iteritems():
            self._store.append(it, (name, sig))

    def _action_add_file(self, action):
        dlg = gtk.FileChooserDialog('Add file', parent=self._mainwindow,
                                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        resp = dlg.run()
        filename = dlg.get_filename()
        dlg.destroy()
        if resp == gtk.RESPONSE_ACCEPT:
            self._add_file(filename)

    def _action_quit(self, action):
        main_loop.quit()

    def _create_menubar(self):
        # tuple format:
        # (name, stock-id, label, accelerator, tooltip, callback)
        actions = [
            ('File', None, '_File'),
            ('Add file', gtk.STOCK_ADD, '_Add file', None, None,
                self._action_add_file),
            ('Quit', gtk.STOCK_QUIT, '_Quit', None, None,
                self._action_quit),
                ]
        actiongroup = gtk.ActionGroup('App')
        actiongroup.add_actions(actions)

        uimanager = gtk.UIManager()
        uimanager.add_ui_from_string(self.__ui)
        uimanager.insert_action_group(actiongroup, 0)
        return uimanager.get_accel_group(), uimanager.get_widget('/MenuBar')

    def _create_treeview(self):
        col = gtk.TreeViewColumn('Signal', gtk.CellRendererText(), text=0)
        tv = gtk.TreeView()
        tv.append_column(col)
        tv.set_model(self._store)
        tv.connect('row-activated', self._row_activated)
        return tv

    def _create_widgets(self):
        accel_group, self._menubar = self._create_menubar()
        self._treeview = self._create_treeview()

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self._treeview)

        vbox = gtk.VBox()
        vbox.pack_start(self._menubar, False)
        vbox.pack_start(sw)

        w = self._mainwindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        w.set_title('Oscopy GUI')
        w.add(vbox)
        w.add_accel_group(accel_group)
        w.connect('destroy', lambda *x: self._action_quit(None))
        w.set_default_size(400, 300)
        w.show_all()

    def _create_units_window(self, fig):
        if self._current_graph is None:
            return
        dlg = gtk.Dialog('Enter graph units',\
                             buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,\
                                          gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        # Label and entry for X axis
        hbox_x = gtk.HBox()
        label_xunits = gtk.Label('X axis unit:')
        hbox_x.pack_start(label_xunits)
        entry_xunits = gtk.Entry()
        entry_xunits.set_text(self._current_graph.unit[0])
        hbox_x.pack_start(entry_xunits)
        dlg.vbox.pack_start(hbox_x)

        # Label and entry for Y axis
        hbox_y = gtk.HBox()
        label_yunits = gtk.Label('Y axis unit:')
        hbox_y.pack_start(label_yunits)
        entry_yunits = gtk.Entry()
        entry_yunits.set_text(self._current_graph.unit[1])
        hbox_y.pack_start(entry_yunits)
        dlg.vbox.pack_start(hbox_y)

        dlg.show_all()
        resp = dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            self._current_graph.set_unit((entry_xunits.get_text(),\
                                             entry_yunits.get_text()))
            if fig.canvas is not None:
                fig.canvas.draw()
        dlg.destroy()

    def _units_menu_item_activated(self, menuitem, user_data):
        fig = user_data
        self._create_units_window(fig)

    def _create_range_window(self, fig):
        if self._current_graph is None:
            return
        dlg = gtk.Dialog('Enter graph range',\
                             buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,\
                                          gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        [xmin, xmax], [ymin, ymax] = self._current_graph.get_range()
        # Label and entry for X axis
        hbox_x = gtk.HBox()
        label_xmin = gtk.Label('Xmin:')
        hbox_x.pack_start(label_xmin)
        entry_xmin = gtk.Entry()
        entry_xmin.set_text(str(xmin))
        hbox_x.pack_start(entry_xmin)
        label_xmax = gtk.Label('Xmax:')
        hbox_x.pack_start(label_xmax)
        entry_xmax = gtk.Entry()
        entry_xmax.set_text(str(xmax))
        hbox_x.pack_start(entry_xmax)
        dlg.vbox.pack_start(hbox_x)

        # Label and entry for Y axis
        hbox_y = gtk.HBox()
        label_ymin = gtk.Label('Ymin:')
        hbox_y.pack_start(label_ymin)
        entry_ymin = gtk.Entry()
        entry_ymin.set_text(str(ymin))
        hbox_y.pack_start(entry_ymin)
        label_ymax = gtk.Label('Ymax:')
        hbox_y.pack_start(label_ymax)
        entry_ymax = gtk.Entry()
        entry_ymax.set_text(str(ymax))
        hbox_y.pack_start(entry_ymax)
        dlg.vbox.pack_start(hbox_y)

        dlg.show_all()
        resp = dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            r = [float(entry_xmin.get_text()),\
                     float(entry_xmax.get_text()),\
                     float(entry_ymin.get_text()),\
                     float(entry_ymax.get_text())]
            self._current_graph.set_range(r)
            if fig.canvas is not None:
                fig.canvas.draw()
        dlg.destroy()

    def _range_menu_item_activated(self, menuitem, user_data):
        fig = user_data
        self._create_range_window(fig)

    def _signals_menu_item_activated(self, menuitem, user_data):
        fig, parent_it, it = user_data
        name, sig = self._store.get(it, 0, 1)
        print 'Adding signal %s to %s' % (name, fig)
        if not fig.graphs:
            fig.add({name:sig})
        else:
            if self._current_graph is not None:
                self._current_graph.insert({name: sig})
        if fig.canvas is not None:
            fig.canvas.draw()

    def _graph_menu_item_activated(self, menuitem, user_data):
        fig = user_data
        fig.add()
        fig.canvas.draw()

    def _scale_menu_item_activated(self, menuitem, user_data):
        fig, scale = user_data
        self._current_graph.set_scale(scale)
        if fig.canvas is not None:
            fig.canvas.draw()

    def _layout_menu_item_activated(self, menuitem, user_data):
        fig, layout = user_data
        fig.layout = layout
        if fig.canvas is not None:
            fig.canvas.draw()

    def _delete_graph_menu_item_activated(self, menuitem, user_data):
        fig = user_data
        if self._current_graph is not None:
            idx = fig.graphs.index(self._current_graph)
            fig.delete(idx + 1)
            self._current_graph = None
            if fig.canvas is not None:
                fig.canvas.draw()

    def _remove_signal_menu_item_activated(self, menuitem, user_data):
        fig, signals = user_data
        if self._current_graph is None:
            return
        self._current_graph.remove(signals)
        if fig.canvas is not None:
            fig.canvas.draw()

    def _create_scale_menu(self, fig):
        menu = gtk.Menu()
        for scale in self._scale_to_str.keys():
            item = gtk.CheckMenuItem(self._scale_to_str[scale])
            item.set_active(self._current_graph.scale == scale)
            item.connect('activate', self._scale_menu_item_activated,
                         (fig, scale))
            menu.append(item)
        return menu

    def _create_layout_menu(self, fig):
        menu = gtk.Menu()
        for layout in self._layout_to_str.keys():
            item = gtk.CheckMenuItem(self._layout_to_str[layout])
            item.set_active(fig.layout == layout)
            item.connect('activate', self._layout_menu_item_activated,
                         (fig, layout))
            menu.append(item)
        return menu

    def _create_remove_signal_menu(self, fig):
        menu = gtk.Menu()
        if self._current_graph is None:
            item_nograph = gtk.MenuItem('No graph selected')
            menu.append(item_nograph)
            return menu
        for name, signal in self._current_graph.signals.iteritems():
            item = gtk.MenuItem(name)
            item.connect('activate', self._remove_signal_menu_item_activated,
                         (fig, {name: signal}))
            menu.append(item)
        return menu

    def _create_graph_menu(self, fig):
        menu = gtk.Menu()
        item_range = gtk.MenuItem('Range...')
        item_range.connect('activate', self._range_menu_item_activated, (fig))
        menu.append(item_range)
        item_units = gtk.MenuItem('Units...')
        item_units.connect('activate', self._units_menu_item_activated, (fig))
        menu.append(item_units)
        item_scale = gtk.MenuItem('Scale')
        item_scale.set_submenu(self._create_scale_menu(fig))
        menu.append(item_scale)
        item_add = gtk.MenuItem('Insert signal')
        item_add.set_submenu(self._create_filename_menu(fig))
        menu.append(item_add)
        item_remove = gtk.MenuItem('Remove signal')
        item_remove.set_submenu(self._create_remove_signal_menu(fig))
        menu.append(item_remove)
        return menu

    def _create_figure_menu(self, fig):
        menu = gtk.Menu()
        item_add = gtk.MenuItem('Add graph')
        item_add.connect('activate', self._graph_menu_item_activated,
                         (fig))
        menu.append(item_add)
        item_delete = gtk.MenuItem('Delete graph')
        item_delete.connect('activate', self._delete_graph_menu_item_activated,
                            (fig))
        menu.append(item_delete)
        item_layout = gtk.MenuItem('Layout')
        item_layout.set_submenu(self._create_layout_menu(fig))
        menu.append(item_layout)
        return menu

    def _create_signals_menu(self, fig, parent_it):
        menu = gtk.Menu()
        it = self._store.iter_children(parent_it)
        while it is not None:
            name = self._store.get_value(it, 0)
            item = gtk.MenuItem(name)
            item.connect('activate', self._signals_menu_item_activated,
                         (fig, parent_it, it))
            menu.append(item)
            it = self._store.iter_next(it)
        return menu

    def _create_filename_menu(self, fig):
        it = self._store.get_iter_root()
        if it is None:
            return gtk.Menu()

        menu = gtk.Menu()
        while it is not None:
            filename = self._store.get_value(it, 0)
            item = gtk.MenuItem(filename)
            item.set_submenu(self._create_signals_menu(fig, it))
            menu.append(item)
            it = self._store.iter_next(it)
        return menu

    def _create_figure_popup_menu(self, fig):
        menu = gtk.Menu()
        if self._current_graph is None:
            item_nograph = gtk.MenuItem('No graph selected')
            menu.append(item_nograph)
            return menu
        item_figure = gtk.MenuItem('Figure')
        item_figure.set_submenu(self._create_figure_menu(fig))
        menu.append(item_figure)
        item_graph = gtk.MenuItem('Graph')
        item_graph.set_submenu(self._create_graph_menu(fig))
        menu.append(item_graph)
        return menu

    def _button_press(self, widget, event):
        if event.button == 3:
            window = widget.parent.parent
            fig = self._windows_to_figures[window]
            menu = self._create_figure_popup_menu(fig)
            menu.show_all()
            menu.popup(None, None, None, event.button, event.time)

    #TODO: _windows_to_figures consistency...
    # think of a better way to map events to Figure objects
    def _row_activated(self, widget, path, col):
        if len(path) == 1:
            return

        row = self._store[path]
        self._ctxt.create({row[0]: row[1]})
        fig = self._ctxt.figures[len(self._ctxt.figures) - 1]

        w = gtk.Window()
        self._figcount += 1
        self._windows_to_figures[w] = fig
        w.set_title('Figure %d' % self._figcount)
        vbox = gtk.VBox()
        w.add(vbox)
        canvas = FigureCanvas(fig)
        canvas.connect('button-press-event', self._button_press)
        canvas.mpl_connect('axes_enter_event', self._axes_enter)
        canvas.mpl_connect('axes_leave_event', self._axes_leave)
        canvas.mpl_connect('figure_enter_event', self._figure_enter)
        canvas.mpl_connect('figure_leave_event', self._figure_leave)
        vbox.pack_start(canvas)
        toolbar = NavigationToolbar(canvas, w)
        vbox.pack_start(toolbar, False, False)
        w.resize(400, 300)
        w.show_all()

    def _axes_enter(self, event):
        self._current_graph = event.inaxes

    def _axes_leave(self, event):
        # Unused for better user interaction
#        self._current_graph = None
        pass

    def _figure_enter(self, event):
        self._current_figure = event.canvas.figure

    def _figure_leave(self, event):
#        self._current_figure = None
        pass

if __name__ == '__main__':
    app = App()
    main_loop = gobject.MainLoop()
    main_loop.run()

