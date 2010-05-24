import IPython
from context import Context
from app import OscopyApp

_ctxt = Context()
_app = OscopyApp(_ctxt)
ip = IPython.ipapi.get()

_current_figure = None
_current_graph = None
_figcount = 0

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

def do_plot(self, args):
    _app.do_plot(args)

def do_read(self, arg):
    """read DATAFILE
       Read signal file"""

    fn = arg
    if fn in _ctxt.readers.keys():
        print _("%s already read, use update to reread it") % fn
        return
    try:
        _ctxt.read(fn)
    except ReadError, e:
        print _("Failed to read %s:") % fn, e
    except NotImplementedError:
        print _("File format not supported")

def do_write(self, arg):
    _app.do_write(arg)

def do_update(self, args):
    _app.do_update(args)

def do_add(self, args):
    _app.do_add(args)

def do_delete(self, args):
    _app.do_delete(args)

def do_mode(self, args):
    _app.do_mode(args)

def do_scale(self, args):
    _app.do_scale(args)

def do_range(self, args):
    _app.do_range(args)

def do_unit(self, args):
    _app.do_unit(args)

def do_insert(self, args):
    _app.do_insert(args)

def do_remove(self, args):
    _app.do_remove(args)

def do_freeze(self, args):
    _app.do_freeze(args)

def do_unfreeze(self, args):
    _app.do_unfreeze(args)

def do_siglist(self, args):
    _app.do_siglist(args)

def do_math(self, args):
    _app.do_math(args)

def do_exec(self, args):
    _app.do_exec(args)

def do_factors(self, args):
    _app.do_factors(args)

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
    ip.expose_magic('create', do_create)
    ip.expose_magic('destroy', do_destroy)
    ip.expose_magic('select', do_select)
    ip.expose_magic('layout', do_layout)
    ip.expose_magic('figlist', do_figlist)
    ip.expose_magic('plot', do_plot)
    ip.expose_magic('read', do_read)
    ip.expose_magic('write', do_write)
    ip.expose_magic('update', do_update)
    ip.expose_magic('add', do_add)
    ip.expose_magic('delete', do_delete)
    ip.expose_magic('mode', do_mode)
    ip.expose_magic('scale', do_scale)
    ip.expose_magic('range', do_range)
    ip.expose_magic('unit', do_unit)
    ip.expose_magic('insert', do_insert)
    ip.expose_magic('remove', do_remove)
    ip.expose_magic('freeze', do_freeze)
    ip.expose_magic('unfreeze', do_unfreeze)
    ip.expose_magic('siglist', do_siglist)
    ip.expose_magic('math', do_math)
    ip.expose_magic('exec', do_exec)
    ip.expose_magic('factors', do_factors)
