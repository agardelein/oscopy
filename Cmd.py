""" Scope commands

Class Cmds: Commands callables from scope commandline

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

   load(args)
   Read signals from a file

   update(args)
   Reread all signals from files

   insert(args)
   Add signals to the current graph of the current figure

   remove(args)
   Remove signals from the current graph of the current figure

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

from GnucapReader import *
from MathReader import *
from Signal import *
from Figure import *
from pylab import show
from pylab import figure as pyfig
from types import *

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

        if type(toplot) == StringType:
            # Called from commandline,
            # Get the signal list from args
            if not toplot == "":
                toplot = self.gettoplot(toplot)
            else:
                # No signal list provided
                toplot = None
        elif not type(toplot) == DictType:
            return
        # toplot is now a list
        f = Figure(toplot)
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

        s = args.split(',')

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

    def load(self, args):
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
            
        r = GnucapReader() # for now only Gnucap is supported
        sigs = r.loadfile(args)
        # Insert signals into the dict
        for sn in sigs.keys():
            self.sigs[sn] = sigs[sn]
        print args, ":"
        for s in self.sigs.itervalues():
            print s
        self.readers[args] = r

    def update(self, args):
        """ Reread signal from files.
        For each file, reread it, and for updated, new and deleted signal,
        update the signal dict accordingly.
        Avoid sending the whole signal dict to each figure by asking each one
        its signal list and tailoring the updated and deleted signals dicts
        """
        if args == "help":
            print "Usage : update"
            print "   Reread data files"
            return

        # Reread the files
        for rn in self.readers.keys():
            sigs, u, d, n = self.readers[rn].update()
            self.sigs.update(u)
            self.sigs.update(n)
            for k in d.keys():
                if k in self.sigs:
                    del self.sigs[k]
            # Update in figures
            for f in self.figs:
                fu = {}
                fd = {}
                # Iterate through the graphs to get the signames
                for sn in f.getsigs():
                    if sn in u.keys():
                        fu[sn] = u[sn]
                    elif sn in d.keys():
                        fd[sn] = d[sn]
                # Update the figure
                f.update(fu, fd)

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
            if toplot == None:
                return
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
   lin      x and y linear\n\
   logx     x log, y linear\n\
   logy     x linear, y log\n\
   loglog   x and y log"
            return

        self.figs[self.curfig].setmode(args)

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
Commands related to signals:\n\
   load        read signals from file\n\
   update      reread signals from file(s)\n\
   insert      add a signal to the current graph of the current figure\n\
   remove      delete a signal from the current graph of the current figure\n\
   siglist     list the signals\n\
Misc commands:\n\
   quit, exit  exit the program\n\
   help        display this help message\n\
\n\
Help for individual command can be obtained with 'help COMMAND'\n\
"
        else:
            eval("self." + args + "(\"help\")")

    def math(self, inp):
        """ Create a signal from mathematical expression
        """
        sigs = {}

        # Build the list of signals to be used
        for sn, s in self.sigs.iteritems():
            if inp.find(sn) > 0:
                sigs[sn] = s
        if sigs == {}:
            # No sigs, nothing to do
            return

        # Split left hand and right hand
        tmp = inp.split("=", 1)
        lh = tmp[0]
        rh = tmp[1]

        # Create the expression
        r = MathReader(sigs)
        ss = r.loadfile(inp)
        for sn, s in ss.iteritems():
            self.sigs[sn] = s
        if len(ss) > 0:
            self.readers[inp] = r
        return

    def gettoplot(self, args):
        """ Return the signal list extracted from the commandline
        The list must be a coma separated list of signal names.
        If no signals are loaded of no signal are found, return None
        """
        toplot = {}
        # Are there signals ?
        if self.sigs == []:
            print "No signal loaded"
            return None

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
            return None
        return toplot
