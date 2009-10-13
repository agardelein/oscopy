import gobject
import gtk
import signal
import commands

import oscopy

from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
import gui

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
        <menuitem action="Update files"/>
        <menuitem action="New Math Signal..."/>
        <menuitem action="Run netlister and simulate..."/>
        <menuitem action="Quit"/>
      </menu>
    </menubar>
    </ui>'''

    def __init__(self):
        self._scale_to_str = {'lin': 'Linear', 'logx': 'LogX', 'logy': 'LogY',\
                                  'loglog': 'Loglog'}
        self._figcount = 0
        self._windows_to_figures = {}
        self._current_graph = None
        self._current_figure = None
        self._TARGET_TYPE_SIGNAL = 10354
        self._from_signal_list = [("oscopy-signals", gtk.TARGET_SAME_APP,\
                                       self._TARGET_TYPE_SIGNAL)]
        self._to_figure = [("oscopy-signals", gtk.TARGET_SAME_APP,\
                                self._TARGET_TYPE_SIGNAL)]
        self._ctxt = oscopy.Context()
        self._store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        self._create_widgets()
        self._add_file('demo/irf540.dat')
        #self._add_file('demo/ac.dat')
        #self._add_file('demo/res.dat')

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

    def _action_update(self, action):
        self._ctxt.update()

    def _action_new_math(self, action):
        dlg = gtk.Dialog('New math signal', parent=self._mainwindow,
                         buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                  gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        # Label and entry
        hbox = gtk.HBox()
        label = gtk.Label('Expression:')
        hbox.pack_start(label)
        entry = gtk.Entry()
        hbox.pack_start(entry)
        dlg.vbox.pack_start(hbox)

        dlg.show_all()
        resp = dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            expr = entry.get_text()
            try:
                self._ctxt.math(expr)
            except ReadError, e:
                report_error(self._mainwindow,
                             'Could not find a reader for %s' % expr)
                return
            it = self._store.append(None, (expr, None))
            for name, sig in self._ctxt.readers[expr].signals.iteritems():
                self._store.append(it, (name, sig))

        dlg.destroy()
        

    def _action_quit(self, action):
        main_loop.quit()

    def _create_menubar(self):
        # tuple format:
        # (name, stock-id, label, accelerator, tooltip, callback)
        actions = [
            ('File', None, '_File'),
            ('Add file', gtk.STOCK_ADD, '_Add file', None, None,
             self._action_add_file),
            ('Update files', gtk.STOCK_REFRESH, '_Update', None, None,
             self._action_update),
            ("New Math Signal...", gtk.STOCK_NEW, '_New Math Signal', None,
             None, self._action_new_math),
            ("Run netlister and simulate...", gtk.STOCK_MEDIA_FORWARD,\
                 "_Run netlister and simulate...", None, None,\
                 self._action_netlist_and_simulate),
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
        tv.connect('button-press-event', self._treeview_button_press)
        tv.connect('drag_data_get', self._drag_data_get_cb)
        tv.drag_source_set(gtk.gdk.BUTTON1_MASK,\
                               self._from_signal_list,\
                               gtk.gdk.ACTION_COPY)
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


    def _create_figure_popup_menu(self, figure, graph):
        figmenu = gui.menus.FigureMenu()
        return figmenu.create_menu(self._store, figure, graph)

    def _create_treeview_popup_menu(self, signals):
        menu = gtk.Menu()
        if not signals:
            item_none = gtk.MenuItem("No signal selected")
            menu.append(item_none)
            return menu
        for name, signal in signals.iteritems():
            item_freeze = gtk.CheckMenuItem("Freeze %s" % name)
            item_freeze.set_active(signal.freeze)
            item_freeze.connect('activate',\
                                    self._signal_freeze_menu_item_activated,\
                                    (signal))
        menu.append(item_freeze)
        return menu

    def _signal_freeze_menu_item_activated(self, menuitem, signal):
        signal.freeze = not signal.freeze
        # Modify also the signal in the treeview
        # (italic font? gray font color? a freeze column?)

    def _treeview_button_press(self, widget, event):
        if event.button == 3:
            tv = widget
            path, tvc, x, y = tv.get_path_at_pos(int(event.x), int(event.y))
            if len(path) == 1:
                return
            tv.set_cursor(path)
            row = self._store[path]
            signals = {row[0]: row[1]}
            menu = self._create_treeview_popup_menu(signals)
            menu.show_all()
            menu.popup(None, None, None, event.button, event.time)

    def _button_press(self, event):
        if event.button == 3:
            menu = self._create_figure_popup_menu(event.canvas.figure, event.inaxes)
            menu.show_all()
            menu.popup(None, None, None, event.button, event.guiEvent.time)

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
        canvas.mpl_connect('button_press_event', self._button_press)
        canvas.mpl_connect('axes_enter_event', self._axes_enter)
        canvas.mpl_connect('axes_leave_event', self._axes_leave)
        canvas.mpl_connect('figure_enter_event', self._figure_enter)
        canvas.mpl_connect('figure_leave_event', self._figure_leave)
        w.connect("drag_data_received", self._drag_data_received_cb)
        w.drag_dest_set(gtk.DEST_DEFAULT_MOTION |\
                                 gtk.DEST_DEFAULT_HIGHLIGHT |\
                                 gtk.DEST_DEFAULT_DROP,
                             self._to_figure, gtk.gdk.ACTION_COPY)
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

    def update_from_usr1(self):
        self._ctxt.update()

    def _action_netlist_and_simulate(self, action):
        dialog = gtk.Dialog("Run netlister and simulate",\
                                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,\
                                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        vbox_netl = gtk.VBox()
        ckbutton_netl = gtk.CheckButton("Run netlister")
        ckbutton_netl.set_active(True)
        vbox_netl.pack_start(ckbutton_netl)
        entry_netl = gtk.Entry()
        entry_netl.set_text("gnetlist -s -o demo.cir -g spice-sdb demo.sch")
        vbox_netl.pack_start(entry_netl)
        dialog.vbox.pack_start(vbox_netl)
        vbox_netl = gtk.VBox()

        vbox_sim = gtk.VBox()
        ckbutton_sim = gtk.CheckButton("Run simulator")
        ckbutton_sim.set_active(True)
        vbox_sim.pack_start(ckbutton_sim)
        entry_sim = gtk.Entry()
        entry_sim.set_text("gnucap -b demo.cir")
        vbox_sim.pack_start(entry_sim)
        dialog.vbox.pack_start(vbox_sim)
        ckbutton_upd = gtk.CheckButton("Update readers")
        ckbutton_upd.set_active(True)
        dialog.vbox.pack_start(ckbutton_upd)
        dialog.show_all()
        resp = dialog.run()
        if resp == gtk.RESPONSE_ACCEPT:
            if ckbutton_netl.get_active():
                res = commands.getstatusoutput(entry_netl.get_text())
                if res[0]:
                    report_error(self._mainwindow, res[1])
                print res[1]
            if ckbutton_sim.get_active():
                res = commands.getstatusoutput(entry_sim.get_text())
                if res[0]:
                    report_error(self._mainwindow, res[1])
                print res[1]
            if ckbutton_upd.get_active():
                self._ctxt.update()
        dialog.destroy()

    def _drag_data_get_cb(self, widget, drag_context, selection, target_type,\
                              time):
        if target_type == self._TARGET_TYPE_SIGNAL:
            tv = widget
            (path, col) = tv.get_cursor()
            row = self._store[path]
            print row[0]
            selection.set(selection.target, 8, row[0])

    def _drag_data_received_cb(self, widget, drag_context, x, y, selection,\
                                   target_type, time):
        if target_type == self._TARGET_TYPE_SIGNAL:
            if self._current_graph is not None:
                signals = {selection.data: self._ctxt.signals[selection.data]}
                self._current_graph.insert(signals)
                if self._current_figure.canvas is not None:
                    self._current_figure.canvas.draw()
        
def usr1_handler(signum, frame):
    app.update_from_usr1()

if __name__ == '__main__':
    app = App()
    main_loop = gobject.MainLoop()
    signal.signal(signal.SIGUSR1, usr1_handler)
    main_loop.run()

