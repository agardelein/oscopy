#!/usr/bin/python


from gi.repository import GObject
from gi.repository import Gtk
import signal
import os
import sys
import readline
import subprocess
import configparser
import dbus, dbus.service, dbus.glib
from math import log10, sqrt
from xdg import BaseDirectory
#from matplotlib.widgets import SpanSelector
import IPython

import oscopy

from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
from . import gui
from .gtk_figure import IOscopy_GTK_Figure

IOSCOPY_COL_TEXT = 0
IOSCOPY_COL_X10 = 1
IOSCOPY_COL_VIS = 2 # Text in graphs combobox visible

# Note: for crosshair, see Gdk.GC / function = Gdk.XOR

def report_error(parent, msg):
    dlg = Gtk.MessageDialog(parent,
                            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                            Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, msg)
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

    def __init__(self, bus_name, object_path='/org/freedesktop/Oscopy', ctxt=None, ip=None):
        if bus_name is not None:
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

        # Might be moved to a dedicated app_figure class one day...
        self._btns = {}
        self._cbxs = {}
        self._cbx_stores = {}

        self._TARGET_TYPE_SIGNAL = 10354
        self._from_signal_list = [("oscopy-signals", Gtk.TargetFlags.SAME_APP,\
                                       self._TARGET_TYPE_SIGNAL)]
        self._to_figure = [("oscopy-signals", Gtk.TargetFlags.SAME_APP,\
                                self._TARGET_TYPE_SIGNAL)]
        self._to_main_win = [("text/plain", 0,
                                self._TARGET_TYPE_SIGNAL),
                             ('STRING', 0,
                              self._TARGET_TYPE_SIGNAL),
                             ('application/octet-stream', 0,
                              self._TARGET_TYPE_SIGNAL),
                             # For '*.raw' formats
                             ('application/x-panasonic-raw', 0,
                              self._TARGET_TYPE_SIGNAL),
                             # For '*.ts' formats
                             ('video/mp2t', 0,
                              self._TARGET_TYPE_SIGNAL),
                             ]

        if ctxt is None:
            self._ctxt = oscopy.Context()
        else:
            self._ctxt = ctxt        
            
        self._store = Gtk.TreeStore(GObject.TYPE_STRING, GObject.TYPE_PYOBJECT,
                                    GObject.TYPE_BOOLEAN)
        self._create_widgets()
        #self._app_exec('read demo/irf540.dat')
        #self._app_exec('read demo/ac.dat')
        #self._add_file('demo/res.dat')

        # From IPython/demo.py
        self.shell = ip

    SECTION = 'oscopy_ui'
    OPT_NETLISTER_COMMANDS = 'netlister_commands'
    OPT_SIMULATOR_COMMANDS = 'simulator_commands'
    OPT_RUN_DIRECTORY = 'run_directory'

    #
    # Actions
    #
    def _action_add_file(self, action):
        dlg = Gtk.FileChooserDialog(_('Add file(s)'), parent=self._mainwindow,
                                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                             Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        dlg.set_select_multiple(True)
        resp = dlg.run()
        if resp == Gtk.ResponseType.ACCEPT:
            for filename in dlg.get_filenames():
                self._app_exec('oread ' + filename)
        dlg.destroy()

    def _action_update(self, action):
        self._ctxt.update()

    def _action_new_math(self, action):
        dlg = Gtk.Dialog(_('New math signal'), parent=self._mainwindow,
                         buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                  Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

        # Label and entry
        hbox = Gtk.HBox()
        label = Gtk.Label(label=_('Expression:'))
        hbox.pack_start(label, True, True, 0)
        entry = Gtk.Entry()
        hbox.pack_start(entry, True, True, 0)
        dlg.vbox.pack_start(hbox, True, True, 0)

        dlg.show_all()
        resp = dlg.run()
        if resp == Gtk.ResponseType.ACCEPT:
            expr = entry.get_text()
            self._app_exec('%s' % expr)
            self._app_exec('oimport %s' % expr.split('=')[0].strip())
        dlg.destroy()

    def _action_execute_script(self, action):
        dlg = Gtk.FileChooserDialog(_('Execute script'), parent=self._mainwindow,
                                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                             Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        resp = dlg.run()
        filename = dlg.get_filename()
        dlg.destroy()
        if resp == Gtk.ResponseType.ACCEPT:
            self._app_exec('oexec ' + filename)

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
        Gtk.main_quit()
        sys.exit()

    def _action_figure(self, action, w, fignum):
        if not (w.flags() & Gtk.VISIBLE):
            w.show()
        else:
            w.window.show()
        self._app_exec('%%oselect %d-1' % fignum)

    #
    # UI Creation functions
    #
    def _create_menubar(self):
        # tuple format:
        # (name, stock-id, label, accelerator, tooltip, callback)
        actions = [
            ('File', None, _('_File')),
            ('Add file(s)...', Gtk.STOCK_ADD, _('_Add file(s)...'), None, None,
             self._action_add_file),
            ('Update files', Gtk.STOCK_REFRESH, _('_Update'), None, None,
             self._action_update),
            ('Execute script...', Gtk.STOCK_MEDIA_PLAY, _('_Execute script...'),
             None, None, self._action_execute_script),
            ("New Math Signal...", Gtk.STOCK_NEW, _('_New Math Signal'), None,
             None, self._action_new_math),
            ("Run netlister and simulate...", Gtk.STOCK_MEDIA_FORWARD,\
                 _("_Run netlister and simulate..."), None, None,\
                 self._action_netlist_and_simulate),
            ('Windows', None, _('_Windows')),
            ('Quit', Gtk.STOCK_QUIT, _('_Quit'), None, None,
             self._action_quit),
            ]

        actiongroup = self._actiongroup = Gtk.ActionGroup('App')
        actiongroup.add_actions(actions)

        uimanager = self._uimanager = Gtk.UIManager()
        uimanager.add_ui_from_string(self.__ui)
        uimanager.insert_action_group(actiongroup, 0)
        return uimanager.get_accel_group(), uimanager.get_widget('/MenuBar')

    def _create_treeview(self):
        celltext = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn(_('Signal'), celltext, text=0)
        tv = Gtk.TreeView()
        col.set_cell_data_func(celltext, self._reader_name_in_bold)
        col.set_expand(True)
        tv.append_column(col)
        tv.set_model(self._store)
        tv.connect('row-activated', self._row_activated)
        tv.connect('drag_data_get', self._drag_data_get_cb)
        tv.connect('button-press-event', self._treeview_button_press)
        tv.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,\
                               self._from_signal_list,\
                               Gdk.DragAction.COPY)
        self._togglecell = Gtk.CellRendererToggle()
        self._togglecell.set_property('activatable', True)
        self._togglecell.connect('toggled', self._cell_toggled, None)
        colfreeze = Gtk.TreeViewColumn(_('Freeze'), self._togglecell)
        colfreeze.add_attribute(self._togglecell, 'active', 2)
        tv.append_column(colfreeze)
        tv.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
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

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(self._treeview)

        vbox = Gtk.VBox()
        vbox.pack_start(self._menubar, False)
        vbox.pack_start(sw, True, True, 0)

        w = self._mainwindow = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        w.set_title(_('IOscopy'))
        w.add(vbox)
        w.add_accel_group(accel_group)
        w.connect('destroy', lambda w, e: w.hide() or True)
        w.connect('delete-event', lambda w, e: w.hide() or True)
        w.set_default_size(400, 300)
        w.show_all()
        w.drag_dest_set(Gtk.DestDefaults.MOTION |\
                        Gtk.DestDefaults.HIGHLIGHT |\
                        Gtk.DestDefaults.DROP,
                        self._to_main_win, Gdk.DragAction.COPY)
        w.connect('drag_data_received', self._drag_data_received_main_cb)

    def _create_figure_popup_menu(self, figure, graph):
        figmenu = gui.menus.FigureMenu()
        return figmenu.create_menu(figure, graph, self._app_exec)

    def show_all(self):
        self._mainwindow.show()

    #
    # Event-triggered functions
    #
    def _treeview_button_press(self, widget, event):
        if event.button == 3:
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
            def add_sig_func(tm, p, iter):
                name = tm.get_value(iter, 0)
                signals[name] = self._ctxt.signals[name]
            sel.selected_foreach(add_sig_func)
            tvmenu = gui.menus.TreeviewMenu(self.create)
            menu = tvmenu.make_menu(self._ctxt.figures, signals)
            menu.show_all()
            menu.popup(None, None, None, event.button, event.time)
            return True
        if event.button == 1:
            # It is not _that_ trivial to keep the selection when user start
            # to drag. The default handler reset the selection when button 1
            # is pressed. So we use this handler to store the selection
            # until drag has been recognized.
            tv = widget
            sel = tv.get_selection()
            rows = sel.get_selected_rows()[1]
            self._rows_for_drag = rows
            return False

    def _row_activated(self, widget, path, col):
        if len(path) == 1:
            return

        row = self._store[path]
        self._app_exec('ocreate %s' % row[0])

    def _axes_enter(self, event):
        self._figure_enter(event)
        self._current_graph = event.inaxes

        axes_num = event.canvas.figure.axes.index(event.inaxes) + 1
        fig_num = self._ctxt.figures.index(self._current_figure) + 1
        self._app_exec('%%oselect %d-%d' % (fig_num, axes_num))

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
        self._app_exec('%%oselect %d-%d' % (fig_num, axes_num))

    def _figure_leave(self, event):
#        self._current_figure = None
        pass

    def _cell_toggled(self, cellrenderer, path, data):
        if len(path) == 3:
            # Single signal
            if self._store[path][1].freeze:
                cmd = 'ounfreeze'
            else:
                cmd = 'ofreeze'
            self._app_exec('%s %s' % (cmd, self._store[path][0]))
        elif len(path) == 1:
            # Whole reader
            parent = self._store.get_iter(path)
            freeze = not self._store.get_value(parent, 2)
            if self._store[path][2]:
                cmd = 'ounfreeze'
            else:
                cmd = 'ofreeze'
            self._store.set_value(parent, 2, freeze)
            iter = self._store.iter_children(parent)
            while iter:
                self._app_exec('%s %s' % (cmd, self._store.get_value(iter, 0)))
                iter = self._store.iter_next(iter)

    #
    # Callbacks for App
    #
    def create(self, sigs):
        """ Instanciate the window widget with the figure inside, set the
        relevant events and add it to the 'Windows' menu.
        Finally, select the first graph of this figure.

        The figure has been instanciated by the application
        and is assumed to be the last one in Context's figure list
        """

        fignum = len(self._ctxt.figures) + 1
        fig = IOscopy_GTK_Figure(sigs, None,
                                 _('Figure %d') % fignum)
        self._ctxt.create(fig)

        fig.window.connect('drag_data_received', fig.drag_data_received_cb,
                           self._ctxt.signals)
        fig.canvas.mpl_connect('axes_enter_event', self._axes_enter)
        fig.canvas.mpl_connect('axes_leave_event', self._axes_leave)
        fig.canvas.mpl_connect('figure_enter_event', self._figure_enter)
        fig.canvas.mpl_connect('figure_leave_event', self._figure_leave)

        # Add it to the 'Windows' menu
        actions = [('Figure %d' % fignum, None, _('Figure %d') % fignum,
                    None, None, self._action_figure)]
        self._actiongroup.add_actions(actions, (fig.window, fignum))
        ui = "<ui>\
        <menubar name=\"MenuBar\">\
          <menu action=\"Windows\">\
            <menuitem action=\"Figure %d\"/>\
          </menu>\
        </menubar>\
        </ui>" % fignum
        merge_id = self._uimanager.add_ui_from_string(ui)
        self._fignum_to_merge_id[fignum] = merge_id
        self._app_exec('%%oselect %d-1' % fignum)
        return fig

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
                    .signals.items():
                self._store.append(it, (name, sig, sig.freeze))

    def update_readers(self):
        # Parse self._store to find deleted or new signals.
        # Shall be called subsequently to an update of reasers.
        iter = self._store.get_iter_root()
        while iter:
            rname = self._store.get_value(iter, 0)
            # Check for deleted signals
            citer = self._store.iter_children(iter)
            while citer:
                s = self._store.get_value(citer, 1)
                if s.name not in list(self._ctxt.readers[rname].signals.keys()):
                    self._store.remove(citer)
                    if not self._store.iter_is_valid(citer):
                        citer = None
                else:
                    citer = self._store.iter_next(citer)
            # Add new signals
            for sn, s in self._ctxt.readers[rname].signals.items():
                citer = self._store.iter_children(iter)
                while citer:
                    if self._store.get_value(citer, 1).name == sn:
                        break
                    citer = self._store.iter_next(citer)
                if not citer:
                    self._store.append(iter, (sn, s, s.freeze))
            iter = self._store.iter_next(iter)

    #
    # Callbacks for drag and drop
    #
    def _drag_data_received_main_cb(self, widget, drag_context, x, y, selection,
                                    target_type, time):
        name = selection.data
        if type(name) == str and name.startswith('file://'):
            print(name[7:].strip())
            self._app_exec('%%oread %s' % name[7:].strip())
                
    def _drag_data_get_cb(self, widget, drag_context, selection, target_type,\
                              time):
        if target_type == self._TARGET_TYPE_SIGNAL:
            tv = widget
            sel = tv.get_selection()
            (model, pathlist) = sel.get_selected_rows()
            iter = self._store.get_iter(pathlist[0])
            # Use the path list stored while button 1 has been pressed
            # See self._treeview_button_press()
            data = ' '.join([self._store[x][1].name for x in self._rows_for_drag])
            selection.set(selection.target, 8, data)
            return True
    #
    # Configuration-file related functions
    #
    def _init_config(self):
        # initialize configuration stuff
        path = BaseDirectory.save_config_path('oscopy')
        self.config_file = os.path.join(path, 'gui')
        self.hist_file = os.path.join(path, 'history')
        section = App.SECTION
        self.config = configparser.RawConfigParser()
        self.config.add_section(section)
        # defaults
        self.config.set(section, App.OPT_NETLISTER_COMMANDS, '')
        self.config.set(section, App.OPT_SIMULATOR_COMMANDS, '')
        self.config.set(section, App.OPT_RUN_DIRECTORY, '.')

    def _sanitize_list(self, lst):
        return [x for x in [x.strip() for x in lst] if len(x) > 0]

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
        GObject.idle_add(self._activate_net_and_sim)

    @dbus.service.method('org.freedesktop.OscopyIFace')
    def dbus_running(self):
        return

    # Misc functions
    def update_from_usr1(self):
        self._ctxt.update()

    def update_from_usr2(self):
        GObject.idle_add(self._activate_net_and_sim)

    def _activate_net_and_sim(self):
        if self._actiongroup is not None:
            action = self._actiongroup.get_action("Run netlister and simulate...")
            action.activate()

    def _run_ext_command(self, cmd, run_dir):
        old_dir = os.getcwd()
        os.chdir(run_dir)
        try:
            status, output = subprocess.getstatusoutput(cmd)
            if status:
                msg = _("Executing command '%s' failed.") % cmd
                report_error(self._mainwindow, msg)
            return status == 0
        finally:
            os.chdir(old_dir)

    def _app_exec(self, line):
        (first, last) = line.split(' ', 1)
        if first.startswith('%') or self.shell.find_magic(first.split()[0]) is not None:
            name = first.lstrip('%')
            self.shell.run_line_magic(name, last.strip())
        else:
            self.shell.ex(line)
    
def usr1_handler(signum, frame):
    app.update_from_usr1()

def usr2_handler(signum, frame):
    app.update_from_usr2()
