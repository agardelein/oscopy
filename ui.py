import gobject
import gtk
import signal
import os
import readline
import commands
import ConfigParser
from xdg import BaseDirectory

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

class OscopyAppUI(oscopy.OscopyApp):
    def __init__(self, context):
        oscopy.OscopyApp.__init__(self, context)
        self._callbacks = {}
        self._autorefresh = True
        
    def connect(self, event, func, data):
        if not isinstance(event, str):
            return
        if hasattr(self, 'do_'+event):
            self._callbacks[event] = {func: data}

    def postcmd(self, stop, line):
        oscopy.OscopyApp.postcmd(self, stop, line)
        if not line:
            return
        event = line.split()[0].strip()
        if len(line.split()) > 1:
            args = line.split(' ', 1)[1].strip()
        else:
            args = ''
        if self._callbacks.has_key(event):
            for func, data in self._callbacks[event].iteritems():
                func(event, args, data)
        if self._autorefresh and self._current_figure is not None and\
                self._current_figure.canvas is not None:
            self._current_figure.canvas.draw()

    def help_refresh(self):
        print 'refresh FIG#|on|off|current|all'
        print '  on|off       toggle auto refresh of current figure'
        print '  current|all  refresh either current figure or all'
        print '  FIG#         figure to refresh'
        print 'without arguments refresh current figure'
    def do_refresh(self, args):
        if args == 'on':
            self._autorefresh = True
        elif args == 'off':
            self._autorefresh = False
        elif args == 'current' or args == '':
            if self._current_figure is not None and\
                    self._current_figure.canvas is not None:
                self._current_figure.canvas.draw()
        elif args == 'all':
            for fig in self._ctxt.figures:
                if fig.canvas is not None:
                    fig.canvas.draw()
        elif args.isdigit():
            fignum = int(args) - 1
            if fignum >= 0 and fignum < len(self._ctxt.figures):
                if self._ctxt.figures[fignum].canvas is not None:
                    print 'refreshing'
                    self._ctxt.figures[fignum].canvas.draw()

    def do_pause(self, args):
        print "Pause command disabled in UI"

    def do_plot(self, line):
        print "Plot command disabled in UI"

class App(object):
    __ui = '''<ui>
    <menubar name="MenuBar">
      <menu action="File">
        <menuitem action="Add file"/>
        <menuitem action="Update files"/>
        <menuitem action="Execute script..."/>
        <menuitem action="New Math Signal..."/>
        <menuitem action="Run netlister and simulate..."/>
        <menuitem action="Show terminal"/>
        <menuitem action="Quit"/>
      </menu>
    </menubar>
    </ui>'''

    def __init__(self):
        self._scale_to_str = {'lin': 'Linear', 'logx': 'LogX', 'logy': 'LogY',\
                                  'loglog': 'Loglog'}
        self._configfile = "gui"
        self._figcount = 0
        self._windows_to_figures = {}
        self._current_graph = None
        self._current_figure = None
        self._term_win = None
        self._prompt = "oscopy-ui>"
        # History file
        self.hist_file = ".oscopy_hist"

        self._TARGET_TYPE_SIGNAL = 10354
        self._from_signal_list = [("oscopy-signals", gtk.TARGET_SAME_APP,\
                                       self._TARGET_TYPE_SIGNAL)]
        self._to_figure = [("oscopy-signals", gtk.TARGET_SAME_APP,\
                                self._TARGET_TYPE_SIGNAL)]
        self._ctxt = oscopy.Context()
        self._app = OscopyAppUI(self._ctxt)
        self._app.connect('read', self._add_file, None)
        self._app.connect('math', self._add_file, None)
        self._app.connect('freeze', self._freeze, None)
        self._app.connect('unfreeze', self._freeze, None)
        self._app.connect('create', self._create, None)
        self._resource = "oscopy"
        self._read_config()
        self._store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT,
                                    gobject.TYPE_BOOLEAN)
        self._create_widgets()
        #self._app_exec('read demo/irf540.dat')
        #self._app_exec('read demo/ac.dat')
        #self._add_file('demo/res.dat')

    def _add_file(self, event, filename, data=None):
        it = self._store.append(None, (filename.strip(), None, False))
        for name, sig in self._ctxt.readers[filename.strip()]\
                .signals.iteritems():
            self._store.append(it, (name, sig, sig.freeze))

    def _action_add_file(self, action):
        dlg = gtk.FileChooserDialog('Add file', parent=self._mainwindow,
                                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        resp = dlg.run()
        filename = dlg.get_filename()
        dlg.destroy()
        if resp == gtk.RESPONSE_ACCEPT:
            self._app_exec("read " + filename)

    def _app_exec(self, line):
        line = self._app.precmd(line)
        stop = self._app.onecmd(line)
        self._app.postcmd(stop, line)

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
            self._app_exec('%s' % expr)

        dlg.destroy()

    def _action_show_terminal(self, action):
        self._create_terminal_window()

    def _action_execute_script(self, action):
        dlg = gtk.FileChooserDialog('Execute script', parent=self._mainwindow,
                                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        resp = dlg.run()
        filename = dlg.get_filename()
        dlg.destroy()
        if resp == gtk.RESPONSE_ACCEPT:
            self._app_exec("exec " + filename)

    def _action_quit(self, action):
        self._write_config()
        readline.write_history_file(self.hist_file)
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
            ('Execute script...', gtk.STOCK_MEDIA_PLAY, '_Execute script...',
             None, None, self._action_execute_script),
            ("New Math Signal...", gtk.STOCK_NEW, '_New Math Signal', None,
             None, self._action_new_math),
            ("Run netlister and simulate...", gtk.STOCK_MEDIA_FORWARD,\
                 "_Run netlister and simulate...", None, None,\
                 self._action_netlist_and_simulate),
            ("Show terminal", None, "_Show terminal", None, None,
             self._action_show_terminal),
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
        celltext = gtk.CellRendererText()
        col = gtk.TreeViewColumn('Signal', celltext, text=0)
        tv = gtk.TreeView()
        col.set_cell_data_func(celltext, self._reader_name_in_bold)
        tv.append_column(col)
        tv.set_model(self._store)
        tv.connect('row-activated', self._row_activated)
        tv.connect('drag_data_get', self._drag_data_get_cb)
        tv.drag_source_set(gtk.gdk.BUTTON1_MASK,\
                               self._from_signal_list,\
                               gtk.gdk.ACTION_COPY)
        self._togglecell = gtk.CellRendererToggle()
        self._togglecell.set_property('activatable', True)
        self._togglecell.connect('toggled', self._cell_toggled, None)
        colfreeze = gtk.TreeViewColumn('Freeze', self._togglecell)
        colfreeze.add_attribute(self._togglecell, 'active', 2)
        tv.append_column(colfreeze)
        tv.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        return tv

    def _reader_name_in_bold(self, column, cell, model, iter, data=None):
        if len(model.get_path(iter)) == 1:
            cell.set_property('markup', "<b>" + model.get_value(iter, 0) +\
                                  "</b>")
        else:
            cell.set_property('text', model.get_value(iter, 0))

    # Search algorithm from pygtk tutorial
    def _match_func(self, row, data):
        column, key = data
        return row[column] == key

    def _search(self, rows, func, data):
        if not rows: return None
        for row in rows:
            if func(row, data):
                return row
            result = self._search(row.iterchildren(), func, data)
            if result: return result
        return None

    def _freeze(self, event, signals, data=None):
        for signal in signals.split(','):
            match_row = self._search(self._store, self._match_func,\
                                         (0, signal.strip()))
            if match_row is not None:
                match_row[2] = match_row[1].freeze
                parent = self._store.iter_parent(match_row.iter)
                iter = self._store.iter_children(parent)
                freeze = match_row[2]
                while iter:
                    if not self._store.get_value(iter, 2) == freeze:
                        break
                    iter = self._store.iter_next(iter)
                if iter == None:
                    # All row at the same freeze value,
                    # set freeze for the reader
                    self._store.set_value(parent, 2, freeze)
                else:
                    # Set reader freeze to false
                    self._store.set_value(parent, 2, False)

    def _cell_toggled(self, cellrenderer, path, data):
        if len(path) == 3:
            # Single signal
            if self._store[path][1].freeze:
                cmd = 'unfreeze'
            else:
                cmd = 'freeze'
            self._app_exec('%s %s' % (cmd, self._store[path][0]))
        elif len(path) == 1:
            # Whole reader
            parent = self._store.get_iter(path)
            freeze = not self._store.get_value(parent, 2)
            if self._store[path][2]:
                cmd = 'unfreeze'
            else:
                cmd = 'freeze'
            self._store.set_value(parent, 2, freeze)
            iter = self._store.iter_children(parent)
            while iter:
                self._app_exec('%s %s' % (cmd, self._store.get_value(iter, 0)))
                iter = self._store.iter_next(iter)

    def _create_widgets(self):
        accel_group, self._menubar = self._create_menubar()
        self._treeview = self._create_treeview()
        self._create_terminal_window()

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

    def _create_terminal_window(self):
        if self._term_win is None:
            self._term_win = gui.dialogs.TerminalWindow(self._prompt,
                                                        self._app.intro,
                                                        self.hist_file,
                                                        self._app_exec)
        if not self._term_win.is_there:
            self._term_win.create()
        pass

    def _create_figure_popup_menu(self, figure, graph):
        figmenu = gui.menus.FigureMenu()
        return figmenu.create_menu(self._store, figure, graph, self._app_exec)

    def _treeview_button_press(self, widget, event):
        if event.button == 3:
            tv = widget
            path, tvc, x, y = tv.get_path_at_pos(int(event.x), int(event.y))
            if len(path) == 1:
                return
            tv.set_cursor(path)
            row = self._store[path]
            signals = {row[0]: row[1]}
            menu = self._create_treeview_popup_menu(signals, path)
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
        self._app_exec('create %s' % row[0])

    def _create(self, event, signals, data=None):
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
        self._app_exec('select %d-1' % len(self._ctxt.figures))

    def _axes_enter(self, event):
        self._current_graph = event.inaxes
        axes_num = event.canvas.figure.axes.index(event.inaxes) + 1
        fig_num = self._ctxt.figures.index(self._current_figure) + 1
        self._app_exec('select %d-%d' % (fig_num, axes_num))

    def _axes_leave(self, event):
        # Unused for better user interaction
#        self._current_graph = None
        pass

    def _figure_enter(self, event):
        self._current_figure = event.canvas.figure
        if hasattr(event, 'inaxes') and event.inaxes is not None:
            axes_num = event.canvas.figure.axes.index(event.inaxes) + 1
        else:
            axes_num = 1
        fig_num = self._ctxt.figures.index(self._current_figure) + 1
        self._app_exec('select %d-%d' % (fig_num, axes_num))

    def _figure_leave(self, event):
#        self._current_figure = None
        pass

    def update_from_usr1(self):
        self._ctxt.update()

    def _action_netlist_and_simulate(self, action):
        netnsimdlg = gui.dialogs.Run_Netlister_and_Simulate_Dialog()
        netnsimdlg.display(self._actions)
        actions = netnsimdlg.run()
        if actions is not None:
            self._actions = actions
            old_dir = os.getcwd()
            os.chdir(self._actions['run_from'])
            if self._actions['run_netlister'][0]:
                res = commands.getstatusoutput(self._actions['run_netlister'][1])
                if res[0]:
                    report_error(self._mainwindow, res[1])
                print res[1]
            if self._actions['run_simulator'][0]:
                res = commands.getstatusoutput(self._actions['run_simulator'][1])
                if res[0]:
                    report_error(self._mainwindow, res[1])
                print res[1]
            os.chdir(old_dir)
            if self._actions['update']:
                self._ctxt.update()

    def _drag_data_get_cb(self, widget, drag_context, selection, target_type,\
                              time):
        if target_type == self._TARGET_TYPE_SIGNAL:
            tv = widget
            sel = tv.get_selection()
            (model, pathlist) = sel.get_selected_rows()
            iter = self._store.get_iter(pathlist[0])
            data = " ".join(map(lambda x:self._store[x][1].name, pathlist))
            selection.set(selection.target, 8, data)
            # The multiple selection do work, but how to select signals
            # that are not neighbours in the list? Ctrl+left do not do
            # anything, neither alt+left or shift+left!

    def _drag_data_received_cb(self, widget, drag_context, x, y, selection,\
                                   target_type, time):
        if target_type == self._TARGET_TYPE_SIGNAL:
            if self._current_graph is not None:
                signals = {}
                for name in selection.data.split():
                    signals[name] = self._ctxt.signals[name]
                self._current_graph.insert(signals)
                if self._current_figure.canvas is not None:
                    self._current_figure.canvas.draw()

    def _read_config(self):
        cmdsec = 'Commands'
        netlopt = 'Netlister'
        simopt = 'Simulator'
        runfrom = "RunFrom"
        self._confparse = ConfigParser.SafeConfigParser()
        self._confparse.add_section(cmdsec)
        self._confparse.set(cmdsec, netlopt, '')
        self._confparse.set(cmdsec, simopt, '')
        self._confparse.set(cmdsec, runfrom, '.')
        path = BaseDirectory.load_first_config(self._resource)
        if path is not None:
            res = self._confparse.read('/'.join((path, self._configfile)))
        self._actions = {'run_netlister': (True,
                                           self._confparse.get(cmdsec, netlopt)),
                         'run_simulator': (True,
                                           self._confparse.get(cmdsec, simopt)),
                         'update': True,
                         'run_from': self._confparse.get(cmdsec, runfrom)}

    def _write_config(self):
        cmdsec = 'Commands'
        netlopt = 'Netlister'
        simopt = 'Simulator'
        runfrom = "RunFrom"
        self._confparse.set(cmdsec, netlopt, self._actions['run_netlister'][1])
        self._confparse.set(cmdsec, simopt, self._actions['run_simulator'][1])
        self._confparse.set(cmdsec, runfrom, self._actions['run_from'])
        path = BaseDirectory.save_config_path(self._resource)
        f = open('/'.join((path, self._configfile)), 'w')
        res = self._confparse.write(f)
        f.close()

        
def usr1_handler(signum, frame):
    app.update_from_usr1()

if __name__ == '__main__':
    app = App()
    main_loop = gobject.MainLoop()
    signal.signal(signal.SIGUSR1, usr1_handler)
    main_loop.run()

