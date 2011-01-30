from __future__ import with_statement
import IPython
from IPython.demo import IPythonDemo
import time
import os
import gtk
import re
import dbus
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
from graphs import factors_to_names, abbrevs_to_factors

from context import Context
from readers.reader import ReadError
from ui import App as OscopyGUI
from oscopy import Signal

_globals = None

_ctxt = Context()
ip = IPython.ipapi.get()

_current_figure = None
_current_graph = None
_figcount = 0
_autorefresh = True
bus_name = None

try:
    session_bus = dbus.SessionBus()
    bus_name = dbus.service.BusName('org.freedesktop.Oscopy', bus=session_bus)
except dbus.DBusException, e:
    print 'DBus not available:', e

_gui = OscopyGUI(bus_name, ctxt=_ctxt)

def do_create(self, args):
    """create [SIG [, SIG [, SIG]...]]
    Create a new figure, set_ it as current, add the signals"""
    global _current_figure
    global _current_graph
    _ctxt.create(get_signames(args))
    _current_figure = _ctxt.figures[len(_ctxt.figures) - 1]
    if _current_figure.graphs:
        _current_graph =\
            _current_figure.graphs[len(\
                _current_figure.graphs) - 1]
    else:
        _current_graph = None
    _gui.create()

def do_destroy(self, args):
    """destroy FIG#
    Destroy a figure"""
    global _current_figure
    global _current_graph
    if not args.isdigit():
        raise TypeError(_("do_destroy: Bad argument"))
    else:
        fignum = eval(args)
    _ctxt.destroy(fignum)
    _gui.destroy(args)
    # Go back to the first graph of the first figure or None
    _current_figure = None
    _current_graph = None

def do_select(self, args):
    """select FIG#-GRAPH#
    Select the current figure and the current graph"""
    global _current_figure
    global _current_graph
    if not args:
        raise TypeError(_("do_select: no args"))
    s = args.split('-')
    if not s[0].isdigit() or len(s) < 2 or not s[1].isdigit():
        raise IndexError(_("do_select: bad figure or graph number"))
    num = eval(s[0])
    gn = eval(s[1])
    _current_figure = _ctxt.figures[num - 1]
    if len(_current_figure.graphs) and\
            (gn - 1) < len(_current_figure.graphs) and\
            (gn - 1) >= 0:
        _current_graph = _current_figure.graphs[gn - 1]
    else:
        _current_graph = None

def do_layout(self, args):
    """layout horiz|vert|quad
    Define the layout of the current figure"""
    global _current_figure
    if _current_figure is not None:
        _current_figure.layout = args
    do_refresh(self, '')

def do_figlist(self, args):
    """figlist
    Print the list of figures"""
    global _current_figure
    global _current_graph
    SEPARATOR = " "
    for fn, f in enumerate(_ctxt.figures):
        if f is not None:
            print _("%s Figure %d: %s") %\
                ([" ", "*"][f == _current_figure],\
                     fn + 1, f.layout)
            for gn, g in enumerate(f.graphs):
                print _("    %s Graph %d : (%s) %s") %\
                    ([" ","*"][g == _current_graph],\
                         gn + 1, g.type,\
                         SEPARATOR.join(g.signals.keys()))

def do_read(self, arg):
    """read DATAFILE
    Read signal file"""
    global _globals

    fn = arg
    if fn in _ctxt.readers.keys():
        print _("%s already read, use update to reread it") % fn
        return
    try:
        sigs = _ctxt.read(fn)
        _gui.add_file(fn)
        _globals.update(sigs)
    except ReadError, e:
        print _("Failed to read %s:") % fn, e
    except NotImplementedError:
        print _("File format not supported")

def do_write(self, args):
    """write format [(OPTIONS)] FILE SIG [, SIG [, SIG]...]
    Save signals to file"""
    # Extract format, options and signal list
    tmp = re.search(r'(?P<fmt>\w+)\s*(?P<opts>\([^\)]*\))?\s+(?P<fn>[\w\./]+)\s+(?P<sigs>\w+(\s*,\s*\w+)*)', args)
    
    if tmp is None:
        raise TypeError(_("do_write: Bad arguments"))
    fmt = tmp.group('fmt')
    fn = tmp.group('fn')
    opt = tmp.group('opts')
    sns = get_signames(tmp.group('sigs'))
    opts = {}
    if opt is not None:
        for on in opt.strip('()').split(','):
            tmp = on.split(':', 1)
            if len(tmp) == 2:
                opts[tmp[0]] = tmp[1]
    try:
        _ctxt.write(fn, fmt, sns, opts)
    except WriteError, e:
        print _("Write error:"), e
    except NotImplementedError:
        print _("File format not supported")

def do_update(self, args):
    """ update
    Reread data files"""
    if not args:
        _ctxt.update()
    else:
        if _ctxt.readers.has_key(args):
            _ctxt.update(_ctxt.readers[args])
        else:
            print _("%s not found in readers") % args
    do_refresh(self, '')

def do_add(self, args):
    """add SIG [, SIG [, SIG]...]
    Add a graph to the current figure.
    If no figure is selected, then create a new one"""
    global _current_figure
    global _current_graph

    if _current_figure is not None:
        if len(_current_figure.graphs) == 4:
            print _("Maximum graph number reached")
            return
        _current_figure.add(_ctxt.names_to_signals(\
                get_signames(args)))
        _current_graph =\
            _current_figure.graphs[len(\
                _current_figure.graphs) - 1]
    else:
        do_create(self, args)
    do_refresh(self, '')

def do_delete(self, args):
    """delete GRAPH#
    Delete a graph from the current figure"""
    global _current_figure
    global _current_graph

    if _current_figure is not None:
        _current_figure.delete(int(args))
        if _current_figure.graphs:
            _current_graph = _current_figure.graphs[0]
        else:
            _current_graph = None
    do_refresh(self, '')

def do_mode(self, args):
    """mode MODE
    Set the type of the current graph of the current figure.
    Available modes :
    lin      Linear graph"""
    global _current_figure
    global _current_graph
    if _current_graph is None:
        return
    mode = args
    idx = _current_figure.graphs.index(_current_graph)
    _current_figure.mode = mode
    _current_graph = _current_figure.graphs[idx]
    do_refresh(self, '')

def do_scale(self, args):
    """scale [lin|logx|logy|loglog]
    Set the axis scale"""
    global _current_graph
    if _current_graph is None:
        return
    _current_graph.scale = args
    do_refresh(self, '')

def do_range(self, args):
    """range [x|y min max]|[xmin xmax ymin ymax]|[reset]
    Set the axis range of the current graph of the current figure
    """
    global _current_graph
    if _current_graph is None:
        return

    range = args.split()
    if len(range) == 1:
        if range[0] == "reset":
            _current_graph.range = range[0]
    elif len(range) == 3:
        if range[0] == 'x' or range[0] == 'y':
            _current_graph.range = range[0],\
                [float(range[1]), float(range[2])]
    elif len(range) == 4:
        _current_graph.range = [float(range[0]), float(range[1]),\
                                    float(range[2]), float(range[3])]
    do_refresh(self, '')

def do_unit(self, args):
    """unit [XUNIT,] YUNIT
    Set the unit to be displayed on graph axis"""
    global _current_graph
    units = args.split(",", 1)
    if len(units) < 1 or _current_graph is None\
            or not _current_graph.signals:
        return
    elif len(units) == 1:
        _current_graph.unit = units[0].strip(),
    elif len(units) == 2:
        _current_graph.unit = units[0].strip(), units[1].strip()
    else:
        return
    do_refresh(self, '')

def do_insert(self, args):
    """ insert SIG [, SIG [, SIG]...]
    Insert a list of signals into the current graph"""
    global _current_graph
    if _current_graph is None:
        return
    _current_graph.insert(_ctxt.names_to_signals(get_signames(args)))
    do_refresh(self, '')

def do_remove(self, args):
    """ remove SIG [, SIG [, SIG]...]
    Delete a list of signals into from current graph"""
    global _current_graph
    if _current_graph is None:
        return
    _current_graph.remove(_ctxt.names_to_signals(get_signames(args)))
    do_refresh(self, '')

def do_freeze(self, args):
    """freeze SIG [, SIG [, SIG]...]
    Do not consider signal for subsequent updates"""
    _ctxt.freeze(get_signames(args))
    _gui.freeze(args)

def do_unfreeze(self, args):
    """freeze SIG [, SIG [, SIG]...]
    Consider signal for subsequent updates"""
    _ctxt.unfreeze(get_signames(args))
    _gui.freeze(args)

def do_siglist(self, args):
    """siglist
    List loaded signals"""
    SEPARATOR = "\t"
    HEADER=[_("Name"), _("Unit"), _("Ref"), _("Reader"),_("Last updated (sec)")]
    print SEPARATOR.join(HEADER)
    t = time.time()
    for reader_name, reader in _ctxt.readers.iteritems():
        for signal_name, signal in reader.signals.iteritems():
            print SEPARATOR.join((signal_name, \
                                      signal.unit,\
                                      signal.ref.name,\
                                      reader_name,\
                                      str(int(t - reader.info['last_update']))))

def do_math(self, args):
    # Note: this function will be useless now, signals will be computed directly
    """math destsig=mathexpr
    Define a new signal destsig using mathematical expression"""
    global _globals
    try:
        sigs = _ctxt.math(args)
    except ReadError, e:
        print _("Error creating signal from math expression:"), e
    _gui.add_file(args)
    _globals.update(sigs)

def do_exec(self, file):
    """exec FILENAME
    execute commands from file"""
    try:
        if not file.startswith('/'):
            file = "/".join((os.getcwd(), file))
        mydemo = IPythonDemo(file)
        mydemo()
    except IOError, e:
        print _("Script error:"), e
        if hasattr(self, "f") and hasattr(f, "close")\
                and callable(f.close):
            f.close()
        print os.getcwd()

def do_factors(self, args):
    """factors X, Y
    set the scaling factor of the graph (in power of ten)
    use 'auto' for automatic scaling factor
    e.g. factor -3, 6 set the scale factor at 1e-3 and 10e6"""
    global _current_graph
    if _current_graph is None:
        return
    factors = [None, None]
    for i, f in enumerate(args.split(',')):
        if i > 1:
            break
        factor = f.strip()
        if factor.isdigit() or (len(factor) > 1 and factor[0] == '-' and\
                                    factor[1:].isdigit()):
            factors[i] = int(factor)
        else:
            if factor == 'auto':
                factors[i] = None
            else:
                factors[i] = abbrevs_to_factors[factor]
    _current_graph.set_scale_factors(factors[0], factors[1])
    do_refresh(self, '')

def do_refresh(self, args):
    """refresh FIG#|on|off|current|all'
    on|off       toggle auto refresh of current figure
    current|all  refresh either current figure or all
    FIG#         figure to refresh
    without arguments refresh current figure"""
    global _current_figure
    global _current_graph
    global _autorefresh

    if args == 'on':
        _autorefresh = True
    elif args == 'off':
        _autorefresh = False
    elif args == 'current' or args == '':
        if _current_figure is not None and\
                _current_figure.canvas is not None:
            _current_figure.canvas.draw()
    elif args == 'all':
        for fig in _ctxt.figures:
            if fig.canvas is not None:
                fig.canvas.draw()
    elif args.isdigit():
        fignum = int(args) - 1
        if fignum >= 0 and fignum < len(_ctxt.figures):
            if _ctxt.figures[fignum].canvas is not None:
                print _('refreshing')
                _ctxt.figures[fignum].canvas.draw()

def do_gui(self, args):
    """gui
    Invoke the oscopy gui
    """
    global _gui
    global _ctxt
    _gui.show_all()

def do_import(self, args):
    """import
    Import a signal into the oscopy context.
    This is done through the signal_reader class
    """
    global _globals
    for name in args.split(','):
        try:
            sig = _globals.get(name)
            sigs = _ctxt.import_signal(sig, name)
            for s in sigs.itervalues():
                _globals[s.name] = s
            _gui.add_file("%s=%s" % (name, sig.name))
        except ReadError, e:
            print _("Error: Signal not recognized (%s)") % e
            return
#    _globals.update(sigs)
    

def get_signames(args):
    """ Return the signal names list extracted from the commandline
    The list must be a coma separated list of signal names.
    If no signals are loaded of no signal are found, return []
    """
    sns = []
    if args == "":
        sns = []
    else:
        for sn in args.split(","):
            sns.append(sn.strip())
    return sns

def init():
    oscopy_magics = {'o_create': do_create,
                     'o_destroy': do_destroy,
                     'o_select': do_select,
                     'o_layout': do_layout,
                     'o_figlist': do_figlist,
                     'o_read': do_read,
                     'o_write': do_write,
                     'o_update': do_update,
                     'o_add': do_add,
                     'o_delete': do_delete,
                     'o_mode': do_mode,
                     'o_scale': do_scale,
                     'o_range': do_range,
                     'o_unit': do_unit,
                     'o_insert': do_insert,
                     'o_remove': do_remove,
                     'o_freeze': do_freeze,
                     'o_unfreeze': do_unfreeze,
                     'o_siglist': do_siglist,
                     'o_math': do_math,
                     'o_exec': do_exec,
                     'o_factors': do_factors,
                     'o_refresh': do_refresh,
                     'o_gui': do_gui,
                     'o_import': do_import}
    
    for name, func in oscopy_magics.iteritems():
            ip.expose_magic(name, func)
