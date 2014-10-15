from gi.repository import GObject
from gi.repository import Gtk, Gio, GLib
from gi.repository import Gdk
import os, signal
import sys
import readline
import subprocess
import configparser
from math import log10, sqrt
from xdg import BaseDirectory
#from matplotlib.widgets import SpanSelector
import IPython

import oscopy

from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backend_bases import LocationEvent
#from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
from . import gui
from .gui.gtk_figure import IOscopy_GTK_Figure

IOSCOPY_COL_TEXT = 0
IOSCOPY_COL_X10 = 1
IOSCOPY_COL_VIS = 2 # Text in graphs combobox visible

IOSCOPY_UI = 'oscopy/ioscopy.ui'
IOSCOPY_NEW_MATH_SIGNAL_UI = 'oscopy/new_math_signal_dlg.glade'
IOSCOPY_RUN_NETNSIM_UI = 'oscopy/run_netnsim_dlg.glade'

DEFAULT_NETLISTER_COMMAND = 'gnetlist -g spice-sdb -O sort_mode -o %s.net %s.sch'
DEFAULT_SIMULATOR_COMMAND = 'gnucap -b %s.net'

# Note: for crosshair, see Gdk.GC / function = Gdk.XOR

def report_error(parent, msg):
    dlg = Gtk.MessageDialog(parent,
                            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                            Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, msg)
    dlg.set_title(parent.get_title())
    dlg.run()
    dlg.destroy()

class IOscopyApp(Gtk.Application):
    def __init__(self, ctxt = None, ip = None, uidir=None):
        Gtk.Application.__init__(self)
        # TODO: Validate uidir
        self.uidir = uidir
        self.builder = None
        self.shell = ip
        self.ctxt = ctxt
        self.config = None
        self.actions = {}
        self.windows_to_figures = {}
        self.fignum_to_windows = {}
        self.current_graph = None
        self.current_figure = None
        self.store = Gtk.TreeStore(GObject.TYPE_STRING, GObject.TYPE_PYOBJECT,
                                    GObject.TYPE_BOOLEAN)

    SECTION = 'oscopy_ui'
    OPT_NETLISTER_COMMANDS = 'netlister_commands'
    OPT_SIMULATOR_COMMANDS = 'simulator_commands'
    OPT_RUN_DIRECTORY = 'run_directory'

    def do_activate(self):
        w = gui.appwin.IOscopyAppWin(self, self.uidir)
        w.show_all()
        self.w = w

    def do_startup(self):
        Gtk.Application.do_startup(self)
        # Add and connect actions
        a = Gio.SimpleAction.new('quit', None)
        a.connect('activate', self.quit_activated)
        self.add_action(a)

        a = Gio.SimpleAction.new('add_file', None)
        a.connect('activate', self.add_file_activated)
        self.add_action(a)

        a = Gio.SimpleAction.new('update_files', None)
        a.connect('activate', self.update_files_activated)
        self.add_action(a)

        a = Gio.SimpleAction.new('exec_script', None)
        a.connect('activate', self.exec_script_activated)
        self.add_action(a)

        a = Gio.SimpleAction.new('new_math', None)
        a.connect('activate', self.new_math_signal_activated)
        self.add_action(a)

        a = Gio.SimpleAction.new('run_netnsim', None)
        a.connect('activate', self.run_netnsim_activated)
        self.add_action(a)

        a = Gio.SimpleAction.new('show_sigwin', None)
        a.connect('activate', self.show_sigwin_activated)
        self.add_action(a)

        a = Gio.SimpleAction.new('show_figure', GLib.VariantType.new('s'))
        a.connect('activate', self.show_figure_activated)
        self.add_action(a)

        a = Gio.SimpleAction.new('insert_signal', GLib.VariantType.new('(sst)'))
        a.connect('activate', self.insert_signal_activated)
        self.add_action(a)

        self.builder = Gtk.Builder()
        self.builder.expose_object('store', self.store)
        self.builder.add_from_file('/'.join((self.uidir, IOSCOPY_UI)))
        self.set_app_menu(self.builder.get_object('appmenu'))
        self.init_config()
        self.read_config()
        signal.signal(signal.SIGUSR1, self.sigusr1_handler)
        signal.signal(signal.SIGUSR2, self.sigusr2_handler)

    def quit_activated(self, action, param):
#        self._write_config()
#        readline.write_history_file(self.hist_file)
        Gtk.main_quit()
        sys.exit()

    def add_file_activated(self, action, param):
        dlg = Gtk.FileChooserDialog(_('Add file(s)'), parent=self.w,
                                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                             Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        dlg.set_select_multiple(True)
        resp = dlg.run()
        if resp == Gtk.ResponseType.ACCEPT:
            for filename in dlg.get_filenames():
                self.exec_str('oread ' + filename)
        dlg.destroy()

    def update_files_activated(self, action, param):
        self.ctxt.update()

    def exec_script_activated(self, action, param):
        dlg = Gtk.FileChooserDialog(_('Execute script'), parent=self.w,
                                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                             Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        resp = dlg.run()
        filename = dlg.get_filename()
        dlg.destroy()
        if resp == Gtk.ResponseType.ACCEPT:
            self.exec_str('oexec ' + filename)

    def new_math_signal_activated(self, action, param):
        builder = Gtk.Builder()
        builder.add_from_file('/'.join((self.uidir, IOSCOPY_NEW_MATH_SIGNAL_UI)))

        dlg = builder.get_object('new_math_signal_dlg')
        dlg.show_all()

        resp = dlg.run()
        if resp:
            entry = builder.get_object('math_entry')
            expr = entry.get_text()
            self.exec_str('%s' % expr)
            self.exec_str('oimport %s' % expr.split('=')[0].strip())
        dlg.destroy()

    def run_netnsim_activated(self, action, param):
        builder = Gtk.Builder()
        helper = gui.dialogs.run_netnsim_dlg_helper()
        dlg = helper.build_dialog(builder,
                         '/'.join((self.uidir, IOSCOPY_RUN_NETNSIM_UI)),
                         self.actions,
                         DEFAULT_NETLISTER_COMMAND,
                         DEFAULT_SIMULATOR_COMMAND
                         )
        dlg.show_all()
        resp = dlg.run()

        if resp:
            self.actions = helper.collect_data()
            run_dir = self.actions['run_from']
            if self.actions['run_netlister'][0]:
                if not self.exec_ext_command(self.actions['run_netlister'][1][0], run_dir):
                    dlg.destroy()
                    return
            if self.actions['run_simulator'][0]:
                if not self.exec_ext_command(self.actions['run_simulator'][1][0], run_dir):
                    dlg.destroy()
                    return
            if self.actions['update']:
                self.ctxt.update()
        dlg.destroy()

    def show_sigwin_activated(self, action, param):
        self.w.show_all()

    def show_figure_activated(self, action, param):
        for w in self.get_windows():
            if w.get_title() == param.get_string():
                w.present()
                self.exec_str('%%oselect %s-1' % param.get_string().split()[1])
                return

    def insert_signal_activated(self, action, param):
        (sigs, figname, gnum) = param.unpack()
        # WARNING : This assumes that the figure number
        # is at end of window title containing the figure
        if figname:
            fignum = int(figname.split()[-1])
            if gnum:
                self.exec_str('%%oselect %d-%d' % (fignum, gnum))
                self.exec_str('%%oinsert %s' % sigs)
            else:
                self.exec_str('%%oselect %d-1' % (fignum))
                self.exec_str('%%oadd %s' % sigs)
        else:
            self.exec_str('%%ocreate %s' % sigs)

    def exec_str(self, line):
        if ' ' in line:
            (first, last) = line.split(' ', 1)
        else:
            first = line
            last = ''
        if first.startswith('%') or self.shell.find_magic(first.split()[0]) is not None:
            name = first.lstrip('%')
            self.shell.run_line_magic(name, last.strip())
        else:
            self.shell.ex(line)

    def exec_ext_command(self, cmd, run_dir):
        old_dir = os.getcwd()
        os.chdir(run_dir)
        try:
            status, output = subprocess.getstatusoutput(cmd)
            if status:
                msg = _("Executing command '%s' failed.") % cmd
                report_error(self.w, msg)
            return status == 0
        finally:
            os.chdir(old_dir)

    def figure_drag_data_received(self, window, drag_context, x, y, selection,
                                  target_type, time):
        print("ioscopyapp: drag data received")
        if target_type == IOscopy_GTK_Figure.TARGET_TYPE_SIGNAL:
            # Retrieve signal list
            signals = {}
            for name in selection.get_text().split():
                signals[name] = self.ctxt.signals[name]

            figure = self.windows_to_figures[window]
            # Retrieve figure and graph numbers
            # HERE : FIXME get canvas height !!!
            canvas = figure.canvas
            my_y = canvas.get_allocation().height - y
            event = LocationEvent('axes_enter_event', canvas, x, my_y)
            if event.inaxes is not None:
                param = GLib.Variant.new_tuple(GLib.Variant.new_string(','.join(selection.get_text().split())),
                                                GLib.Variant.new_string(window.get_title()),
                                                GLib.Variant.new_uint64(figure.graphs.index(event.inaxes) + 1))
                self.activate_action('insert_signal', param)
        print("ioscopyapp: drag data received finished")
    #
    # Callbacks for ioscopy script
    #
    def create(self, sigs):
        """ Instanciate the window widget with the figure inside, set the
        relevant events and add it to the 'Windows' menu.
        Finally, select the first graph of this figure.

        The figure has been instanciated by the application
        and is assumed to be the last one in Context's figure list
        """
            
        fignum = len(self.ctxt.figures) + 1
        figname = _('Figure %d') % fignum
        fig = IOscopy_GTK_Figure(sigs, None, figname, self.uidir)
        self.ctxt.create(fig)

        fig.window.connect_after('drag-data-received', self.figure_drag_data_received)
        fig.canvas.mpl_connect('axes_enter_event', self.axes_enter)
        fig.canvas.mpl_connect('axes_leave_event', self.axes_leave)
        fig.canvas.mpl_connect('figure_enter_event', self.figure_enter)
        fig.canvas.mpl_connect('figure_leave_event', self.figure_leave)

        self.exec_str('%%oselect %d-1' % fignum)

        # Add window to the application menu
        self.add_window(fig.window)
        sect = self.builder.get_object('figwin_section')
        sect.append_item(Gio.MenuItem.new(figname, 'app.show_figure::%s' % figname))
        self.windows_to_figures[fig.window] = fig
        return fig

    def destroy(self, num):
        if not num.isdigit() or int(num) > len(self.ctxt.figures):
            return
        else:
            fignum = int(num)

        for w in self.get_windows():
            if _('Figure %d') % fignum == w.get_title():
                # Remove the window from the appmenu
                sect = self.builder.get_object('figwin_section')
                for i in range(sect.get_n_items()):
                    if sect.get_item_attribute_value(i, 'label', GLib.VariantType.new('s')).get_string() == w.get_title():
                        sect.remove(i)
                        break
                # and finally destroy it
                del self.windows_to_figures[w]
                self.remove_window(w)
                w.destroy()

    def add_file(self, filename):
        if filename.strip() in self.ctxt.readers:
            it = self.store.append(None, (filename.strip(), None, False))
            for name, sig in self.ctxt.readers[filename.strip()]\
                    .signals.items():
                self.store.append(it, (name, sig, sig.freeze))

    def update_readers(self):
        # Parse self._store to find deleted or new signals.
        # Shall be called subsequently to an update of reasers.
        iter = self.store.get_iter_first()
        while iter:
            rname = self.store.get_value(iter, 0)
            # Check for deleted signals
            citer = self.store.iter_children(iter)
            while citer:
                s = self.store.get_value(citer, 1)
                if s.name not in list(self.ctxt.readers[rname].signals.keys()):
                    self.store.remove(citer)
                    if not self.store.iter_is_valid(citer):
                        citer = None
                else:
                    citer = self.store.iter_next(citer)
            # Add new signals
            for sn, s in self.ctxt.readers[rname].signals.items():
                citer = self.store.iter_children(iter)
                while citer:
                    if self.store.get_value(citer, 1).name == sn:
                        break
                    citer = self.store.iter_next(citer)
                if not citer:
                    self.store.append(iter, (sn, s, s.freeze))
            iter = self.store.iter_next(iter)

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
            match_row = self._search(self.store, self._match_func,\
                                         (0, signal.strip()))
            if match_row is not None:
                match_row[2] = match_row[1].freeze
                parent = self.store.iter_parent(match_row.iter)
                iter = self.store.iter_children(parent)
                freeze = match_row[2]
                while iter:
                    if not self.store.get_value(iter, 2) == freeze:
                        break
                    iter = self.store.iter_next(iter)
                if iter == None:
                    # All row at the same freeze value,
                    # set freeze for the reader
                    self.store.set_value(parent, 2, freeze)
                else:
                    # Set reader freeze to false
                    self.store.set_value(parent, 2, False)

    def axes_enter(self, event):
        self.figure_enter(event)
        self.current_graph = event.inaxes

        axes_num = event.canvas.figure.axes.index(event.inaxes) + 1
        fig_num = self.ctxt.figures.index(self.current_figure) + 1
        self.exec_str('%%oselect %d-%d' % (fig_num, axes_num))

    def axes_leave(self, event):
        # Unused for better user interaction
#        self._current_graph = None
        pass

    def figure_enter(self, event):
        self.current_figure = event.canvas.figure
        if hasattr(event, 'inaxes') and event.inaxes is not None:
            axes_num = event.canvas.figure.axes.index(event.inaxes) + 1
        else:
            axes_num = 1
        fig_num = self.ctxt.figures.index(self.current_figure) + 1
        self.exec_str('%%oselect %d-%d' % (fig_num, axes_num))

    def figure_leave(self, event):
#        self._current_figure = None
        pass

    #
    # Configuration-file related functions
    #
    def init_config(self):
        # initialize configuration stuff
        path = BaseDirectory.save_config_path('oscopy')
        self.config_file = os.path.join(path, 'gui')
        self.hist_file = os.path.join(path, 'history')
        section = IOscopyApp.SECTION
        self.config = configparser.RawConfigParser()
        self.config.add_section(section)
        # defaults
        self.config.set(section, IOscopyApp.OPT_NETLISTER_COMMANDS, '')
        self.config.set(section, IOscopyApp.OPT_SIMULATOR_COMMANDS, '')
        self.config.set(section, IOscopyApp.OPT_RUN_DIRECTORY, '.')

    def sanitize_list(self, lst):
        return [x for x in [x.strip() for x in lst] if len(x) > 0]

    def actions_from_config(self, config):
        section =IOscopyApp.SECTION
        netlister_commands = config.get(section, IOscopyApp.OPT_NETLISTER_COMMANDS)
        netlister_commands = self.sanitize_list(netlister_commands.split(';'))
        simulator_commands = config.get(section, IOscopyApp.OPT_SIMULATOR_COMMANDS)
        simulator_commands = self.sanitize_list(simulator_commands.split(';'))
        actions = {
            'run_netlister': (True, netlister_commands),
            'run_simulator': (True, simulator_commands),
            'update': True,
            'run_from': config.get(section, IOscopyApp.OPT_RUN_DIRECTORY)}
        return actions

    def actions_to_config(self, actions, config):
        section = IOscopyApp.SECTION
        netlister_commands = ';'.join(actions['run_netlister'][1])
        simulator_commands = ';'.join(actions['run_simulator'][1])
        config.set(section, IOscopyApp.OPT_NETLISTER_COMMANDS, netlister_commands)
        config.set(section, IOscopyApp.OPT_SIMULATOR_COMMANDS, simulator_commands)
        config.set(section, IOscopyApp.OPT_RUN_DIRECTORY, actions['run_from'])

    def read_config(self):
        self.config.read(self.config_file)
        self.actions = self.actions_from_config(self.config)

    def write_config(self):
        self.actions_to_config(self.actions, self.config)
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def sigusr1_handler(self, signum, frame):
        self.activate_action('update_files', None)

    def sigusr2_handler(self, signum, frame):
        self.activate_action('run_netnsim', None)
