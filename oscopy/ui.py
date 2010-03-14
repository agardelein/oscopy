#!/usr/bin/python
from __future__ import with_statement

import gobject
import gtk
import signal
import os
import readline
import commands
import ConfigParser
import dbus, dbus.service, dbus.glib
from xdg import BaseDirectory
import IPython

import oscopy

from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
import gui

# Note: for crosshair, see gtk.gdk.GC / function = gtk.gdk.XOR

def report_error(parent, msg):
    dlg = gtk.MessageDialog(parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
    dlg.set_title(parent.get_title())
    dlg.run()
    dlg.destroy()

class App(dbus.service.Object):
    __ui = '''<ui>
    <menubar name="MenuBar">
      <menu action="File">
        <menuitem action="Add file(s)..."/>
        <menuitem action="Update files"/>
        <menuitem action="Execute script..."/>
        <menuitem action="New Math Signal..."/>
        <menuitem action="Run netlister and simulate..."/>
        <menuitem action="Quit"/>
      </menu>
      <menu action="Windows">
      </menu>
    </menubar>
    </ui>'''

    def __init__(self, bus_name, object_path='/org/freedesktop/Oscopy', ctxt=None):
        dbus.service.Object.__init__(self, bus_name, object_path)
        self._scale_to_str = {'lin': _('Linear'), 'logx': _('LogX'), 'logy': _('LogY'),\
                                  'loglog': _('Loglog')}
        self._windows_to_figures = {}
        self._fignum_to_windows = {}
        self._fignum_to_merge_id = {}
        self._current_graph = None
        self._current_figure = None
        self._prompt = "oscopy-ui>"
        self._init_config()
        self._read_config()

        self._TARGET_TYPE_SIGNAL = 10354
        self._from_signal_list = [("oscopy-signals", gtk.TARGET_SAME_APP,\
                                       self._TARGET_TYPE_SIGNAL)]
        self._to_figure = [("oscopy-signals", gtk.TARGET_SAME_APP,\
                                self._TARGET_TYPE_SIGNAL)]

        if ctxt is None:
            self._ctxt = oscopy.Context()
        else:
            self._ctxt = ctxt        
            
        self._store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT,
                                    gobject.TYPE_BOOLEAN)
        self._create_widgets()
        #self._app_exec('read demo/irf540.dat')
        #self._app_exec('read demo/ac.dat')
        #self._add_file('demo/res.dat')

        # From IPython/demo.py
        self.shell = __IPYTHON__

    SECTION = 'oscopy_ui'
    OPT_NETLISTER_COMMANDS = 'netlister_commands'
    OPT_SIMULATOR_COMMANDS = 'simulator_commands'
    OPT_RUN_DIRECTORY = 'run_directory'

    #
    # Actions
    #
    def _action_add_file(self, action):
        dlg = gtk.FileChooserDialog(_('Add file(s)'), parent=self._mainwindow,
                                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dlg.set_select_multiple(True)
        resp = dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            for filename in dlg.get_filenames():
                self._app_exec("read " + filename)
        dlg.destroy()

    def _action_update(self, action):
        self._ctxt.update()

    def _action_new_math(self, action):
        dlg = gtk.Dialog(_('New math signal'), parent=self._mainwindow,
                         buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                  gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        # Label and entry
        hbox = gtk.HBox()
        label = gtk.Label(_('Expression:'))
        hbox.pack_start(label)
        entry = gtk.Entry()
        hbox.pack_start(entry)
        dlg.vbox.pack_start(hbox)

        dlg.show_all()
        resp = dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            expr = entry.get_text()
            self._app_exec('math %s' % expr)

        dlg.destroy()

    def _action_execute_script(self, action):
        dlg = gtk.FileChooserDialog(_('Execute script'), parent=self._mainwindow,
                                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        resp = dlg.run()
        filename = dlg.get_filename()
        dlg.destroy()
        if resp == gtk.RESPONSE_ACCEPT:
            self._app_exec("exec " + filename)

    def _action_netlist_and_simulate(self, action):
        dlg = gui.dialogs.Run_Netlister_and_Simulate_Dialog()
        dlg.display(self._actions)
        actions = dlg.run()
        if actions is None:
            return
        self._actions = actions
        run_dir = actions['run_from']
        if actions['run_netlister'][0]:
            if not self._run_ext_command(actions['run_netlister'][1][0], run_dir):
                return
        if actions['run_simulator'][0]:
            if not self._run_ext_command(actions['run_simulator'][1][0], run_dir):
                return
        if actions['update']:
            self._ctxt.update()

    def _action_quit(self, action):
        self._write_config()
        readline.write_history_file(self.hist_file)

    def _action_figure(self, action, w, fignum):
        if not (w.flags() & gtk.VISIBLE):
            w.show()
        else:
            w.window.show()
        self._app_exec('%%select %d-1' % fignum)

    #
    # UI Creation functions
    #
    def _create_menubar(self):
        # tuple format:
        # (name, stock-id, label, accelerator, tooltip, callback)
        actions = [
            ('File', None, _('_File')),
            ('Add file(s)...', gtk.STOCK_ADD, _('_Add file(s)...'), None, None,
             self._action_add_file),
            ('Update files', gtk.STOCK_REFRESH, _('_Update'), None, None,
             self._action_update),
            ('Execute script...', gtk.STOCK_MEDIA_PLAY, _('_Execute script...'),
             None, None, self._action_execute_script),
            ("New Math Signal...", gtk.STOCK_NEW, _('_New Math Signal'), None,
             None, self._action_new_math),
            ("Run netlister and simulate...", gtk.STOCK_MEDIA_FORWARD,\
                 _("_Run netlister and simulate..."), None, None,\
                 self._action_netlist_and_simulate),
            ('Windows', None, _('_Windows')),
            ('Quit', gtk.STOCK_QUIT, _('_Quit'), None, None,
             self._action_quit),
            ]

        actiongroup = self._actiongroup = gtk.ActionGroup('App')
        actiongroup.add_actions(actions)

        uimanager = self._uimanager = gtk.UIManager()
        uimanager.add_ui_from_string(self.__ui)
        uimanager.insert_action_group(actiongroup, 0)
        return uimanager.get_accel_group(), uimanager.get_widget('/MenuBar')

    def _create_treeview(self):
        celltext = gtk.CellRendererText()
        col = gtk.TreeViewColumn(_('Signal'), celltext, text=0)
        tv = gtk.TreeView()
        col.set_cell_data_func(celltext, self._reader_name_in_bold)
        col.set_expand(True)
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
        colfreeze = gtk.TreeViewColumn(_('Freeze'), self._togglecell)
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
        w.set_title(_('Oscopy GUI'))
        w.add(vbox)
        w.add_accel_group(accel_group)
        w.connect('destroy', lambda w, e: w.hide() or True)
        w.connect('delete-event', lambda w, e: w.hide() or True)
        w.set_default_size(400, 300)
        w.show_all()

    def _create_figure_popup_menu(self, figure, graph):
        figmenu = gui.menus.FigureMenu()
        return figmenu.create_menu(self._store, figure, graph, self._app_exec)

    def show_all(self):
        self._mainwindow.show()

    #
    # Event-triggered functions
    #
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

    def _axes_enter(self, event):
        self._figure_enter(event)
        self._current_graph = event.inaxes
        axes_num = event.canvas.figure.axes.index(event.inaxes) + 1
        fig_num = self._ctxt.figures.index(self._current_figure) + 1
        self._app_exec('%%select %d-%d' % (fig_num, axes_num))

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
        self._app_exec('%%select %d-%d' % (fig_num, axes_num))

    def _figure_leave(self, event):
#        self._current_figure = None
        pass

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

    #
    # Callbacks for App
    #
    def create(self):
        fig = self._ctxt.figures[len(self._ctxt.figures) - 1]
        fignum = len(self._ctxt.figures)

        w = gtk.Window()
        self._windows_to_figures[w] = fig
        self._fignum_to_windows[fignum] = w
        w.set_title(_('Figure %d') % fignum)
        vbox = gtk.VBox()
        w.add(vbox)
        canvas = FigureCanvas(fig)
        canvas.mpl_connect('button_press_event', self._button_press)
        canvas.mpl_connect('axes_enter_event', self._axes_enter)
        canvas.mpl_connect('axes_leave_event', self._axes_leave)
        canvas.mpl_connect('figure_enter_event', self._figure_enter)
        canvas.mpl_connect('figure_leave_event', self._figure_leave)
        w.connect("drag_data_received", self._drag_data_received_cb)
        w.connect('delete-event', lambda w, e: w.hide() or True)
        w.drag_dest_set(gtk.DEST_DEFAULT_MOTION |\
                                 gtk.DEST_DEFAULT_HIGHLIGHT |\
                                 gtk.DEST_DEFAULT_DROP,
                             self._to_figure, gtk.gdk.ACTION_COPY)
        vbox.pack_start(canvas)
        toolbar = NavigationToolbar(canvas, w)
        vbox.pack_start(toolbar, False, False)
        w.resize(400, 300)
        w.show_all()

        # Add it to the 'Windows' menu
        actions = [(_('Figure %d') % fignum, None, _('Figure %d') % fignum,
                    None, None, self._action_figure)]
        self._actiongroup.add_actions(actions, (w, fignum))
        ui = "<ui>\
        <menubar name=\"MenuBar\">\
          <menu action=\"Windows\">\
            <menuitem action=\"Figure %d\"/>\
          </menu>\
        </menubar>\
        </ui>" % fignum
        merge_id = self._uimanager.add_ui_from_string(ui)
        self._fignum_to_merge_id[fignum] = merge_id
        self._app_exec('%%select %d-1' % fignum)

    def destroy(self, num):
        if not num.isdigit() or int(num) > len(self._ctxt.figures):
            return
        else:
            fignum = int(num)
        action = self._uimanager.get_action('/MenuBar/Windows/Figure %d' %
                                            fignum)
        if action is not None:
            self._actiongroup.remove_action(action)
            self._uimanager.remove_ui(self._fignum_to_merge_id[fignum])
            self._fignum_to_windows[fignum].destroy()

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

    def freeze(self, signals):
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

    def add_file(self, filename):
        if filename.strip() in self._ctxt.readers:
            it = self._store.append(None, (filename.strip(), None, False))
            for name, sig in self._ctxt.readers[filename.strip()]\
                    .signals.iteritems():
                self._store.append(it, (name, sig, sig.freeze))

    #
    # Callbacks for drag and drop
    #
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

    #
    # Configuration-file related functions
    #
    def _init_config(self):
        # initialize configuration stuff
        path = BaseDirectory.save_config_path('oscopy')
        self.config_file = os.path.join(path, 'gui')
        self.hist_file = os.path.join(path, 'history')
        section = App.SECTION
        self.config = ConfigParser.RawConfigParser()
        self.config.add_section(section)
        # defaults
        self.config.set(section, App.OPT_NETLISTER_COMMANDS, '')
        self.config.set(section, App.OPT_SIMULATOR_COMMANDS, '')
        self.config.set(section, App.OPT_RUN_DIRECTORY, '.')

    def _sanitize_list(self, lst):
        return filter(lambda x: len(x) > 0, map(lambda x: x.strip(), lst))

    def _actions_from_config(self, config):
        section = App.SECTION
        netlister_commands = config.get(section, App.OPT_NETLISTER_COMMANDS)
        netlister_commands = self._sanitize_list(netlister_commands.split(';'))
        simulator_commands = config.get(section, App.OPT_SIMULATOR_COMMANDS)
        simulator_commands = self._sanitize_list(simulator_commands.split(';'))
        actions = {
            'run_netlister': (True, netlister_commands),
            'run_simulator': (True, simulator_commands),
            'update': True,
            'run_from': config.get(section, App.OPT_RUN_DIRECTORY)}
        return actions

    def _actions_to_config(self, actions, config):
        section = App.SECTION
        netlister_commands = ';'.join(actions['run_netlister'][1])
        simulator_commands = ';'.join(actions['run_simulator'][1])
        config.set(section, App.OPT_NETLISTER_COMMANDS, netlister_commands)
        config.set(section, App.OPT_SIMULATOR_COMMANDS, simulator_commands)
        config.set(section, App.OPT_RUN_DIRECTORY, actions['run_from'])

    def _read_config(self):
        self.config.read(self.config_file)
        self._actions = self._actions_from_config(self.config)

    def _write_config(self):
        self._actions_to_config(self._actions, self.config)
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    # DBus routines
    @dbus.service.method('org.freedesktop.OscopyIFace')
    def dbus_update(self):
        gobject.idle_add(self._activate_net_and_sim)

    @dbus.service.method('org.freedesktop.OscopyIFace')
    def dbus_running(self):
        return

    # Misc functions
    def update_from_usr1(self):
        self._ctxt.update()

    def update_from_usr2(self):
        gobject.idle_add(self._activate_net_and_sim)

    def _activate_net_and_sim(self):
        if self._actiongroup is not None:
            action = self._actiongroup.get_action("Run netlister and simulate...")
            action.activate()

    def _run_ext_command(self, cmd, run_dir):
        old_dir = os.getcwd()
        os.chdir(run_dir)
        try:
            status, output = commands.getstatusoutput(cmd)
            if status:
                msg = _("Executing command '%s' failed.") % cmd
                report_error(self._mainwindow, msg)
            return status == 0
        finally:
            os.chdir(old_dir)

    def _app_exec(self, line):
        self.shell.runlines(line)
    
def usr1_handler(signum, frame):
    app.update_from_usr1()

def usr2_handler(signum, frame):
    app.update_from_usr2()
