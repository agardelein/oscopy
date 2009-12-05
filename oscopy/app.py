from __future__ import with_statement
import gobject
import gtk

import sys
import re
import readline
import os.path
import time
from context import Context
from cmd import Cmd
from readers.reader import ReadError
from graphs import factors_to_names, abbrevs_to_factors

from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar

class StdoutProxy(object):
    def __getattr__(self, name):
        return getattr(sys.stdout, name)

class OscopyApp(Cmd):
    """ Analyse command arguments and call function from Cmd
    See Cmd for more help
    """
    def __init__(self, context=None):
        Cmd.__init__(self, stdout=StdoutProxy())
        if context is None or not isinstance(context, Context):
            self._ctxt = Context()
        else:
            self._ctxt = context

        # Prompt and intro
        self.prompt = "oscopy> "
        self.intro = "This is oscopy, a program to view electrical simulation results\n\
Copyright (C) 2009 Arnaud Gardelein.\n\
This is free software, you are invited to redistribute it \n\
under certain conditions.\n\
There is ABSOLUTELY NO WARRANTY; not even for MERCHANTIBILITY or\n\
FITNESS FOR A PARTICULAR PURPOSE."

        # History file
        self.hist_file = ".oscopy_hist"

        # Current graph and current figure
        self._current_figure = None
        self._current_graph = None
        self._figcount = 0

    def help_create(self):
        print "create [SIG [, SIG [, SIG]...]]"
        print "   Create a new figure, set_ it as current, add the signals"
    def do_create(self, args):
        self._ctxt.create(self.get_signames(args))
        self._current_figure = self._ctxt.figures[len(self._ctxt.figures) - 1]
        if self._current_figure.graphs:
            self._current_graph =\
                self._current_figure.graphs[len(\
                    self._current_figure.graphs) - 1]
        else:
            self._current_graph = None

    def help_destroy(self):
        print "destroy FIG#"
        print "   Destroy a figure"
    def do_destroy(self, args):
        self._ctxt.destroy(eval(args))
        # Go back to the first graph of the first figure or None
        if len(self._ctxt.figures):
            self._current_figure = self._ctxt.figures[0]
            if self._current_figure.graphs:
                self._current_graph = self._current_figure.graphs[0]
            else:
                self._current_graph = None
        else:
            self._current_figure = None
            self._current_graph = None

    def help_select(self):
        print "select FIG#-GRAPH#"
        print "   Select the current figure and the current graph"
    def do_select(self, args):
        if not args:
            self.help_select()
            return
        s = args.split('-')
        num = eval(s[0])
        if len(s) > 1:
            gn = eval(s[1])
        else:
            self.help_select()
            return
        self._current_figure = self._ctxt.figures[num - 1]
        if len(self._current_figure.graphs):
            self._current_graph = self._current_figure.graphs[gn - 1]
        else:
            self._current_graph = None

    def help_layout(self):
        print "layout horiz|vert|quad"
        print "   Define the layout of the current figure"
    def do_layout(self, args):
        if self._current_figure is not None:
            self._current_figure.layout = args

    def help_figlist(self):
        print "figlist"
        print "   Print the list of figures"
    def do_figlist(self, args):
        SEPARATOR = " "
        for fn, f in enumerate(self._ctxt.figures):
            print "%s Figure %d: %s" %\
                ([" ", "*"][f == self._current_figure],\
                     fn + 1, f.layout)
            for gn, g in enumerate(f.graphs):
                print "    %s Graph %d : (%s) %s" %\
                    ([" ","*"][g == self._current_graph],\
                         gn + 1, g.type,\
                         SEPARATOR.join(g.signals.keys()))

    def help_plot(self):
        print "plot"
        print "   Draw and show the figures"
    def do_plot(self, args):
        if self._figcount == len(self._ctxt.figures):
            self._main_loop.run()
        else:
            # Create a window for each figure, add navigation toolbar
            self._figcount = 0
            for i, f in enumerate(self._ctxt.figures):
                # fig = plt.figure(i + 1)
                w = gtk.Window()
                self._figcount += 1
                w.set_title('Figure %d' % self._figcount)
                vbox = gtk.VBox()
                w.add(vbox)
                canvas = FigureCanvas(f)
                canvas.connect('destroy', self._window_destroy)
                vbox.pack_start(canvas)
                toolbar = NavigationToolbar(canvas, w)
                vbox.pack_start(toolbar, False, False)
                w.resize(640, 480)
                w.show_all()
            self._main_loop = gobject.MainLoop()
            self._main_loop.run()

    def _window_destroy(self, arg):
        self._figcount = self._figcount - 1
        if not self._figcount:
            self._main_loop.quit()
        return False

    def help_read(self):
        print "load DATAFILE"
        print "   Load signal file"
    def do_read(self, args):
        fn = args
        if fn in self._ctxt.readers.keys():
            print "%s already read, use update to reread it" % fn
            return
        try:
            self._ctxt.read(fn)
        except ReadError, e:
            print "Failed to read %s:" % fn, e
        except NotImplementedError:
            print "File format not supported"

    def help_write(self):
        print "write format [(OPTIONS)] FILE SIG [, SIG [, SIG]...]"
        print "   Write signals to file"
    def do_write(self, args):
        # Extract format, options and signal list
        tmp = re.search(r'(?P<fmt>\w+)\s*(?P<opts>\([^\)]*\))?\s+(?P<fn>[\w\./]+)\s+(?P<sigs>\w+(\s*,\s*\w+)*)', args)

        if tmp is None:
            self.help_write()
            return
        fmt = tmp.group('fmt')
        fn = tmp.group('fn')
        opt = tmp.group('opts')
        sns = self.get_signames(tmp.group('sigs'))
        opts = {}
        if opt is not None:
            for on in opt.strip('()').split(','):
                tmp = on.split(':', 1)
                if len(tmp) == 2:
                    opts[tmp[0]] = tmp[1]
        try:
            self._ctxt.write(fn, fmt, sns, opts)
        except WriteError, e:
            print "Write error:", e
        except NotImplementedError:
            print "File format not supported"

    def help_update(self):
        print "update"
        print "   Reread data files"
    def do_update(self, args):
        if not args:
            self._ctxt.update()
        else:
            if self._ctxt.readers.has_key(args):
                self._ctxt.update(self._ctxt.readers[args])
            else:
                print "%s not found in readers" % args

    def help_add(self):
        print "add SIG [, SIG [, SIG]...]"
        print "   Add a graph to the current figure"
    def do_add(self, args):
        if self._current_figure is not None:
            if len(self._current_figure.graphs) == 4:
                print "Maximum graph number reached"
                return
            self._current_figure.add(self._ctxt.names_to_signals(\
                    self.get_signames(args)))
            self._current_graph =\
                self._current_figure.graphs[len(\
                    self._current_figure.graphs) - 1]
        else:
            line = "create %s" % args
            line = self.precmd(line)
            stop = self.onecmd(line)
            self.postcmd(stop, line)

    def help_delete(self):
        print "delete GRAPH#"
        print "   Delete a graph from the current figure"
    def do_delete(self, args):
        if self._current_figure is not None:
            self._current_figure.delete(int(args))
            if self._current_figure.graphs:
                self._current_graph = self._current_figure.graphs[0]
            else:
                self._current_graph = None

    def help_mode(self):
        print "mode MODE"
        print "   Set the type of the current graph of the current figure"
        print "Available modes :\n\
   lin      Linear graph\n"
#   fft      Fast Fourier Transform (FFT) of signals\n\
#   ifft     Inverse FFT of signals"
    def do_mode(self, args):
        if self._current_graph is None:
            return
        idx = self._current_figure.graphs.index(self._current_graph)
        self._current_figure.mode = self._current_graph, mode
        self._current_graph = self._current_figure.graphs[idx]

    def help_scale(self):
        print "scale [lin|logx|logy|loglog]"
        print "   Set the axis scale"
    def do_scale(self, args):
        if self._current_graph is None:
            return
        self._current_graph.scale = args

    def help_range(self):
        print "range [x|y min max]|[xmin xmax ymin ymax]|[reset]"
        print "   Set the axis range of the current graph of the current figure"
    def do_range(self, args):
        if self._current_graph is None:
            return

        range = args.split()
        if len(range) == 1:
            if range[0] == "reset":
                self._current_graph.range = range[0]
        elif len(range) == 3:
            if range[0] == 'x' or range[0] == 'y':
                self._current_graph.range = range[0],\
                    [float(range[1]), float(range[2])]
        elif len(range) == 4:
            self._current_graph.range = [float(range[0]), float(range[1]),\
                                             float(range[2]), float(range[3])]

    def help_unit(self):
        print "unit [XUNIT,] YUNIT"
        print "   Set the unit to be displayed on graph axis"
    def do_unit(self, args):
        units = args.split(",", 1)
        if len(units) < 1 or self._current_graph is None:
            return
        elif len(units) == 1:
            self._current_graph.unit = units[0].strip(),
        elif len(units) == 2:
            self._current_graph.unit = units[0].strip(), units[1].strip()
        else:
            return

    def help_insert(self):
        print "insert SIG [, SIG [, SIG]...]"
        print "   Insert a list of signals into the current graph"
    def do_insert(self, args):
        if self._current_graph is None:
            return
        self._current_graph.insert(self._ctxt.names_to_signals(
                self.get_signames(args)))

    def help_remove(self):
        print "remove SIG [, SIG [, SIG]...]"
        print "   Delete a list of signals into from current graph"
    def do_remove(self, args):
        if self._current_graph is None:
            return
        self._current_graph.remove(self._ctxt.names_to_signals(
                self.get_signames(args)))

    def help_freeze(self):
        print "freeze SIG [, SIG [, SIG]...]"
        print "   Do not consider signal for subsequent updates"
    def do_freeze(self, args):
        self._ctxt.freeze(self.get_signames(args))

    def help_unfreeze(self):
        print "unfreeze SIG [, SIG [, SIG]...]"
        print "   Consider signal for subsequent updates"
    def do_unfreeze(self, args):
        self._ctxt.unfreeze(self.get_signames(args))

    def help_siglist(self):
        print "siglist"
        print "   List loaded signals"
    def do_siglist(self, args):
        SEPARATOR = "\t"
        HEADER=["Name", "Unit", "Ref", "Reader","Last updated (sec)"]
        print SEPARATOR.join(HEADER)
        t = time.time()
        for reader_name, reader in self._ctxt.readers.iteritems():
            for signal_name, signal in reader.signals.iteritems():
                print SEPARATOR.join((signal_name, \
                                          signal.unit,\
                                          signal.ref.name,\
                                          reader_name,\
                                          str(int(t - reader.info['last_update']))))

    def help_math(self):
        print "destsig=mathexpr"
        print "   Define a new signal destsig using mathematical expression"
    def do_math(self, inp):
        try:
            self._ctxt.math(inp)
        except ReadError, e:
            print "Error creating signal from math expression", e

    def get_signames(self, args):
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

    def help_echo(self):
        print "echo [TEXT]"
        print "   Print text"
    def do_echo(self, args):
        print args
        
    def help_pause(self):
        print "pause"
        print "   Wait for the user to press enter"
    def do_pause(self, args):
        inp = raw_input("Press enter")

    def emptyline(self):
        return

    def precmd(self, line):
        if line.startswith('#'):
            # Comment
            return ''
        elif line.find('=') > 0:
            return "math " + line
        else:
            return line

    def preloop(self):
        # Readline configuration
        if not os.path.exists(self.hist_file):
            f = open(self.hist_file, "w")
            f.write("figlist")
            f.close()
        readline.read_history_file(self.hist_file)

    def postloop(self):
        readline.write_history_file(self.hist_file)

    def do_EOF(self, line):
        return self.do_quit(line)

    def do_exit(self, line):
        return self.do_quit(line)

    def do_quit(self, line):
        return True

    def help_exec(self):
        print "exec FILENAME"
        print "   execute commands from file"
    def do_exec(self, file):
        try:
            with open(file) as f:
                lines = iter(f)
                for line in lines:
                    line = self.precmd(line)
                    stop = self.onecmd(line)
                    self.postcmd(stop, line)
        except IOError, e:
            print "Script error:", e
            f.close()

    def help_factors(self):
        print "factors X, Y"
        print "   set the scaling factor of the graph (in power of ten)"
        print "   use 'auto' for automatic scaling factor"
        print "   e.g. factor -3, 6 set the scale factor at 1e-3 and 10e6"
    def do_factors(self, args):
        if self._current_graph is None:
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
        self._current_graph.set_scale_factors(factors[0], factors[1])
