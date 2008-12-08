""" Scope commands

Class Cmds: Commands callables from scope commandline

   Methods:
   __init__()
   Create empty lists of figures, readers and signals

   load(args)
   Read signals from a file

   update(args)
   Reread all signals from files

   setplot(args)
   Assign signals to the current graph of the current figure,
   create a new figure if none exist

   layout(args)
   set the layout of the current figure

   plot(args)
   plot all the figure

   add(args)
   Add a graph to the current figure

   delfromfig(args)
   Delete a graph from the current figure

   gettoplot(args)
   Return a list of the signal names from the arguments provided by the user
   Should not be called from the command line

   figlist(args)
   Print a list of figures

   new(args)
   Create a new figure, and assign signals if provided

   siglist(args)
   List all the signals

   delete(args)
   Delete a figure

   select(args)
   Select the figure to become the current one
"""

from GnucapReader import *
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
        
    def load(self, args):
        """ Read signals from file.
        Duplicate signal names overwrite the previous one.
        For new only gnucap files are supported.
        Do not load the same file twice.
        """
        # File already loaded ?
        if args in self.readers.keys():
            print "File already loaded"
            return
            
        r = GnucapReader() # for now only Gnucap is supported
        sigs = r.loadfile(args)
        # Insert signals into the dict
        for v in sigs.keys():
            self.sigs[v] = sigs[v]
        print args, ":"
        for ns, si in self.sigs.iteritems():
            print si
        self.readers[args] = r

    def update(self, args):
        """ Reread signal from files.
        TODO : Update signals in figures !
        For each file, reread it, and for updated, new and deleted signal,
        update the signal dict accordingly.
        """
        for v in self.readers.keys():
            sigs, u, d, n = self.readers[v].update()
            for s in u:
                self.sigs[s] = sigs[s]
            for s in n:
                self.sigs[s] = sigs[s]
            for s in d:
                del self.sigs[s]

    def setplot(self, args):
        """ Set the signals of the current graph of the current figure.
        If no figure exist, create a new one.
        """
        toplot = self.gettoplot(args)
        if toplot == None:
            return
        # Can now prepare the plot
        if self.figs == []:
            self.new(toplot)
        else:
            self.figs[self.curfig].setf(toplot)

    def layout(self, args):
        """ Define the layout of the current figure
        """
        self.figs[self.curfig].setlayout(args)

    def plot(self, args):
        """ Plot the figures, and enter in the matplotlib main loop
        """
        if self.figs == []:
            return
        for i, f in enumerate(self.figs):
            pyfig(i + 1)
            f.plot()
        show()

    def add(self, args):
        """ Add a graph to the current figure
        The signal list is a coma separated list of signal names
        If no figure exist, create a new one.
        """
        if len(self.figs) < 1:
            self.setplot(args)
        else:
            toplot = self.gettoplot(args)
            if toplot == None:
                return
            print "Adding into figure"
            self.figs[self.curfig].add(toplot)

    def delfromfig(self, args):
        """ Delete a graph from the current figure
        """
        self.figs[self.curfig].delete(args)
        return

    def gettoplot(self, args):
        """ Return the signal list extracted from the commandline
        The list must be a coma separated list of signal names.
        If no signals are loaded of no signal are found, return None
        """
        toplot = []
        # Are there signals ?
        if self.sigs == []:
            print "No signal loaded"
            return None

        # Prepare the signal list
        for s in args.split(","):
            s = s.strip()
            if s in self.sigs.keys():
                toplot.append(self.sigs[s])
            else:
                print s + ": Not here"

        # No signals found
        if len(toplot) < 1:
            print "No signals found"
            return None
        return toplot

    def figlist(self, args):
        """ Print the list of figures
        """
        for i, f in enumerate(self.figs):
            print "Figure", i + 1, ":", f.layout
            f.list()

    def new(self, toplot):
        """ Create a new figure and set it as current
        Can be either called from commandline or a function.
        When called from commandline, call gettoplot to retrieve
        the signal list
        When called from a function, if the argument is not a list
        then return.
        After those tests, the figure is created with the signal list.
        """
        if type(toplot) == StringType:
            # Called from commandline,
            # Get the signal list from args
            if not toplot == "":
                toplot = self.gettoplot(toplot)
            else:
                # No signal list provided
                toplot = None
        elif not type(toplot) == ListType:
            return
        # toplot is now a list
        f = Figure(toplot)
        self.figs.append(f)
        self.curfig = self.figs.index(f)

    def siglist(self, args):
        """ List loaded signals
        """
        for n, s in self.sigs.iteritems():
            print s

    def delete(self, args):
        """ Delete a figure
        User must provide the figure number.
        If the number is out of range, then return
        Act as a "pop" with self.curfig
        """
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
        num = eval(args)
        if num > len(self.figs) or num < 1:
            return
        self.curfig = num - 1
