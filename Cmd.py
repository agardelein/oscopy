""" Scope commands

Class Cmds: Commands callables from oscopy commandline

   Methods:
   __init__()
   Create empty lists of figures, readers and signals

   create(args)
   Create a new figure, and assign signals if provided

   destroy(args)
   Delete a figure

   select(args)
   Select the figure and the graph to become the current ones

   layout(args)
   set the layout of the current figure

   figlist(args)
   Print a list of figures

   plot(args)
   plot all the figure

   add(args)
   Add a graph to the current figure

   delete(args)
   Delete a graph from the current figure

   mode(args)
   Set the mode of the current graph

   scale(arg)
   Set the axis scale of the current graph

   range(args)
   Set the axis range of the current graph

   unit(args)
   Set the unit of current graph from current figure

   read(args)
   Read signals from a file

   update(args)
   Reread all signals from files

   insert(args)
   Add signals to the current graph of the current figure

   remove(args)
   Remove signals from the current graph of the current figure

   freeze(args)
   Set the freeze flag of signals

   unfreeze(args)
   Unset the freeze flag of signals

   siglist(args)
   List all the signals

   help(args)
   Print help message

   math(expr)
   Create a signal from a mathematical expression

   gettoplot(args)
   Return a list of the signal names from the arguments provided by the user
   Should not be called from the command line
"""

import sys
#sys.path.insert(0, 'Readers')
import Readers.DetectReader
import Writers.DetectWriter
import Figure
from pylab import show
from pylab import figure as pyfig
import types
import re

class Cmds:
    """ Class cmd -- Handle command line

    This object maintain a list of figure, a dict of reader and of signals.
    The current figure curfig has a valid interval [0..len(self.figs)-1]
    which is different from the one presented to the user by matplotlib,
    i.e. diplayed is Figure 2 and in this class it is self.figs[1]

    The keys for the signal dict are the signal name, as presented to the user
    The keys for the reader dict are the file name.
    """

    def __init__(self):
        """ Create the instance variables
        """
        # self.curfig valid interval: [0..len(self.figs)-1]
        # There is a shift compared to the number displayed
        # by matplotlib, i.e. figure 1 is self.figs[0]
        self.curfig = -1
        self.readers = {}
        self.figs = []
        self.sigs = {}
        self.upn = -1
        
    def create(self, toplot):
        """ Create a new figure and set it as current
        Can be either called from commandline or a function.
        When called from commandline, call gettoplot to retrieve
        the signal list
        When called from a function, if the argument is not a list
        then return.
        After those tests, the figure is created with the signal list.
        """
        if toplot == "help":
            print "Usage : create [SIG [, SIG [, SIG]...]]"
            print "   Create a new figure, set it as current, add the signals"
            return

        if type(toplot) == types.StringType:
            # Called from commandline,
            # Get the signal list from args
            if not toplot == "":
                toplot = self.gettoplot(toplot)
            else:
                # No signal list provided
                toplot = {}
        elif not type(toplot) == types.DictType:
            return
        # toplot is now a list
        f = Figure.Figure(toplot)
        self.figs.append(f)
        self.curfig = self.figs.index(f)

    def destroy(self, args):
        """ Delete a figure
        User must provide the figure number.
        If the number is out of range, then return
        Act as a "pop" with self.curfig
        """
        if args == "help":
            print "Usage : delete FIG#"
            print "   Delete a figure"
            return
        
        num = eval(args)
        if num > len(self.figs) or num < 1:
            return
        del self.figs[num - 1]
        # Handle self.curfig.
        # By default, next figure becomes the current
        if len(self.figs) == 0:
            self.curfig = -1
        elif self.curfig > len(self.figs):
            self.curfig = len(self.figs) - 1
        print "Curfig : ", self.curfig

    def select(self, args):
        """ Select the current figure
        """
        if args == "help":
            print "Usage: select FIG#[, GRAPH#]"
            print "   Select the current figure and the current graph"
            return

        s = args.split('-')

        num = eval(s[0])
        if num > len(self.figs) or num < 1:
            return
        self.curfig = num - 1
        if len(s) > 1:
            self.figs[self.curfig].select(eval(s[1]))

    def layout(self, args):
        """ Define the layout of the current figure
        """
        if args == "help":
            print "Usage : layout horiz|vert|quad"
            print "   Define the layout of the current figure"
            return

        self.figs[self.curfig].setlayout(args)

    def figlist(self, args):
        """ Print the list of figures
        """
        if args == "help":
            print "Usage : figlist"
            print "   Print the list of figures"
            return

        for i, f in enumerate(self.figs):
            if i == self.curfig:
                print "*",
            else:
                print " ",
            print "Figure", i + 1, ":", f.layout
            f.list()

    def plot(self, args):
        """ Plot the figures, and enter in the matplotlib main loop
        """
        if args == "help":
            print "Usage : plot"
            print "   Draw and show the figures"
            return

        if self.figs == []:
            return
        for i, f in enumerate(self.figs):
            pyfig(i + 1)
            f.plot()
        show()

    def read(self, args):
        """ Read signals from file.
        Duplicate signal names overwrite the previous one.
        For new only gnucap files are supported.
        Do not load the same file twice.
        """
        if args == "help":
            print "Usage : load DATAFILE"
            print "   Load signal file"
            return

        # File already loaded ?
        if args in self.readers.keys():
            print "File already loaded"
            return
        try:
            r = Readers.DetectReader.DetectReader(args)
        except Readers.Reader.ReadError, e:
            print "Read error:", e
            return

        if r == None:
            print "File format unknown"
            return
        sigs = r.read(args)

        # Insert signals into the dict
        for sn in sigs.keys():
            self.sigs[sn] = sigs[sn]
        print args, ":"
        for s in sigs.itervalues():
            print s
        self.readers[args] = r

    def write(self, args):
        """ Write signals to file
        """
        if args == "help":
            print "Usage: write format [(OPTIONS)] FILE SIG [, SIG [, SIG]...]"
            print "   Write signals to file"
            return
        # Extract format, options and signal list
        tmp = re.search(r'(?P<fmt>\w+)\s*(?P<opts>\([^\)]*\))?\s+(?P<fn>[\w\.]+)\s+(?P<sigs>\w+(\s*,\s*\w+)*)', args)

        if tmp == None:
            print "What format ? Where ? Which signals ?"
            return
        fmt = tmp.group('fmt')
        fn = tmp.group('fn')
        opt = tmp.group('opts')
        sigs = self.gettoplot(tmp.group('sigs'))
        opts = {}
        if opt != None:
            for on in opt.strip('()').split(','):
                tmp = on.split(':', 1)
                if len(tmp) == 2:
                    opts[tmp[0]] = tmp[1]
        # Create the object
        try:
            w = Writers.DetectWriter.DetectWriter(fmt, fn, True)
        except Writers.Writer.WriteError, e:
            print "Write error:", e
            return
        if w != None:
            try:
                w.write(fn, sigs, opts)
            except Writers.Writer.WriteError, e:
                print "Write error:", e

    def update(self, args):
        """ Reread signal from files.
        For each file, reread it, and for updated, new and deleted signal,
        update the signal dict accordingly.
        """
        if args == "help":
            print "Usage : update"
            print "   Reread data files"
            return
        self.upn = self.upn + 1
        d = []
        n = {}
        # Update the signal, the new signals list and sigs to be deleted
        for sn, s in self.sigs.iteritems():
            print sn
            n.update(s.update(self.upn, False))
            if s.getpts() == None:
                d.append(sn)
        # Insert new signals
        self.sigs.update(n)
        # Delete signals
        for sn in d:
            for f in self.figs:
                f.remove({sn:self.sigs[sn]}, "all")
            del self.sigs[sn]

    def add(self, args):
        """ Add a graph to the current figure
        The signal list is a coma separated list of signal names
        If no figure exist, create a new one.
        """
        if args == "help":
            print "Usage : add SIG [, SIG [, SIG]...]"
            print "   Add a graph to the current figure"
            return

        if len(self.figs) < 1:
            self.create(args)
        else:
            toplot = self.gettoplot(args)
            self.figs[self.curfig].add(toplot)

    def delete(self, args):
        """ Delete a graph from the current figure
        """
        if args == "help":
            print "Usage : delete GRAPH#"
            print "   Delete a graph from the current figure"
            return

        self.figs[self.curfig].delete(args)
        return

    def mode(self, args):
        """ Set the mode of the current graph of the current figure
        """
        if args == "help":
            print "Usage: mode MODE"
            print "   Set the type of the current graph of the current figure"
            print "Available modes :\n\
   lin      Linear graph\n\
   fft      Fast Fourier Transform (FFT) of signals\n\
   ifft     Inverse FFT of signals"
            return

        self.figs[self.curfig].setmode(args)

    def scale(self, args):
        """ Set the axis scale of the current graph of the current figure
        """
        if args == "help":
            print "Usage: scale [lin|logx|logy|loglog]"
            print "   Set the axis scale"
            return
        self.figs[self.curfig].setscale(args)

    def range(self, args):
        """ Set the axis range of the current graph of the current figure
        """
        if args == "help":
            print "Usage: range [x|y min max]|[xmin xmax ymin ymax]|[reset]"
            print "   Set the axis range of the current graph of the current figure"
            return
        tmp = args.split()
        if len(tmp) == 1:
            if tmp[0] == "reset":
                self.figs[self.curfig].setrange(tmp[0])
        elif len(tmp) == 3:
            if tmp[0] == 'x' or tmp[0] == 'y':
                self.figs[self.curfig].setrange(tmp[0], float(tmp[1]), float(tmp[2]))
        elif len(tmp) == 4:
            self.figs[self.curfig].setrange(float(tmp[0]), float(tmp[1]), float(tmp[2]), float(tmp[3]))

    def unit(self, args):
        """ Set the units of current graph of current figure
        """
        if args == "help":
            print "Usage: unit [XUNIT,] YUNIT"
            print "   Set the unit to be displayed on graph axis"
            return

        if self.curfig < 0 and self.curfig > len(self.figs):
            return
        us = args.split(",", 1)
        if len(us) < 1:
            return
        elif len(us) == 1:
            self.figs[self.curfig].setunit(us[0].strip())
        elif len(us) == 2:
            self.figs[self.curfig].setunit(us[0].strip(), us[1].strip())
        else:
            return
            
    def insert(self, args):
        """ Insert a list of signals into the current graph 
        of the current figure
        """
        if args == "help":
            print "Usage: insert SIG [, SIG [, SIG]...]"
            print "   Insert a list of signals into the current graph"
            return

        if self.figs == []:
            return

        sigs = self.gettoplot(args)
        self.figs[self.curfig].insert(sigs)
        return

    def remove(self, args):
        """ Remove a list of signals from the current graph
        of the current figure
        """
        if args == "help":
            print "Usage: remove SIG [, SIG [, SIG]...]"
            print "   Delete a list of signals into from current graph"
            return
        if self.figs == []:
            return

        sigs = self.gettoplot(args)
        self.figs[self.curfig].remove(sigs)
        return

    def freeze(self, args):
        """ Set the freeze flag of signals
        """
        if args == "help":
            print "Usage: freeze SIG [, SIG [, SIG]...]"
            print "   Do not consider signal for subsequent updates"
        sigs = self.gettoplot(args)
        for s in sigs.itervalues():
            s.freeze(True)

    def unfreeze(self, args):
        """ Unset the freeze flag of signals
        """
        if args == "help":
            print "Usage: unfreeze SIG [, SIG [, SIG]...]"
            print "   Consider signal for subsequent updates"
        sigs = self.gettoplot(args)
        for s in sigs.itervalues():
            s.freeze(False)

    def siglist(self, args):
        """ List loaded signals
        """
        if args == "help":
            print "Usage : siglist"
            print "   List loaded signals"
            return

        for s in self.sigs.itervalues():
            print s

    def help(self, args):
        """ Display general help message or individual command help
        """
        if args == "":
            print "\
Commands related to figures:\n\
   create      create a new figure\n\
   destroy     delete a figure\n\
   select      define the current figure and the current graph\n\
   layout      set the layout (either horiz, vert or quad)\n\
   figlist     list the existing figures\n\
   plot        draw and show the figures\n\
Commands related to graphs:\n\
   add         add a graph to the current figure\n\
   delete      delete a graph from the current figure\n\
   mode        set the mode of the current graph of the current figure\n\
   unit        set the units of the current graph of the current figure\n\
   scale       set the scale of the current graph of the current figure\n\
   range       set the axis range of the current graph of the current figure\n\
Commands related to signals:\n\
   read        read signals from file\n\
   write       write signals to file\n\
   update      reread signals from file(s)\n\
   insert      add a signal to the current graph of the current figure\n\
   remove      delete a signal from the current graph of the current figure\n\
   (un)freeze  toggle signal update\n\
   siglist     list the signals\n\
Misc commands:\n\
   quit, exit  exit the program\n\
   help        display this help message\n\
\n\
Help for individual command can be obtained with 'help COMMAND'\
"
        else:
            eval("self." + args + "(\"help\")")

    def math(self, inp):
        """ Create a signal from mathematical expression
        """
        sigs = {}

        # Create the expression
        r = Readers.DetectReader.DetectReader(inp)
        ss = r.read(inp)
        if len(ss) == 0:
            if hasattr(r, "missing") and callable(r.missing):
                sns = r.missing()
                if hasattr(r, "setorigsigs") and callable(r.setorigsigs):
                    for sn in sns:
                        if self.sigs.has_key(sn):
                            sigs[sn] = self.sigs[sn]
                        else:
                            print "What is", sn
                    r.setorigsigs(sigs)
                    ss = r.read(inp)
                    if len(ss) == 0:
                        print "Signal not generated"
        for sn, s in ss.iteritems():
            self.sigs[sn] = s
        return

    def gettoplot(self, args):
        """ Return the signal list extracted from the commandline
        The list must be a coma separated list of signal names.
        If no signals are loaded of no signal are found, return None
        """
        if args == "":
            return {}

        toplot = {}
        # Are there signals ?
        if self.sigs == []:
            print "No signal loaded"
            return {}

        # Prepare the signal list
        for sn in args.split(","):
            sn = sn.strip()
            if sn in self.sigs.keys():
                toplot[sn] = self.sigs[sn]
            else:
                print sn + ": Not here"

        # No signals found
        if len(toplot) < 1:
            print "No signals found"
            return {}
        return toplot
