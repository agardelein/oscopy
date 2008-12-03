from GnucapReader import *
from Signal import *
from Figure import *
#import matplotlib.pyplot as plt
#from pylab import *
from pylab import show
from pylab import figure as pyfig
from types import *

class Cmds:
    def __init__(self):
        # self.curfig valid interval: [0..len(self.figs)-1]
        # There is a shift compared to the number displayed
        # by matplotlib, i.e. figure 1 is self.figs[0]
        self.curfig = -1
        self.readers = {}
        self.figs = []
        self.sigs = {}
        
    # Load a file, do not handle signals with same name
    def load(self, args):
        # File already loaded ?
        if args in self.readers.keys():
            print "File already loaded"
            return
            
        r = GnucapReader() # for now only Gnucap is supported
        sigs = r.loadfile(args)
        # Insert signals into the list
        for v in sigs.keys():
            self.sigs[v] = sigs[v]
        print args, ":"
        for ns, si in self.sigs.iteritems():
            print si
        self.readers[args] = r

    # Update the signals from files
    def update(self, args):
        for v in self.readers.keys():
            sigs, u, d, n = self.readers[v].update()
            for s in u:
                self.sigs[s] = sigs[s]
            for s in n:
                self.sigs[s] = sigs[s]
            for s in d:
                del self.sigs[s]

    # Set the plots
    def setplot(self, args):
        toplot = self.gettoplot(args)
        if toplot == None:
            return
        # Can now prepare the plot
        if self.figs == []:
            self.new(toplot)
        else:
            self.figs[self.curfig].setf(toplot)

    # Set the current figure mode
    def setmode(self, args):
        self.figs[self.curfig].setmode(args)

    # Plot the signals
    def plot(self, args):
        if self.figs == []:
            return
        for i, f in enumerate(self.figs):
            pyfig(i + 1)
            f.plot()
        show()

    # Add a graph to the current figure
    def add(self, args):
        if len(self.figs) < 1:
            self.setplot(args)
        else:
            toplot = self.gettoplot(args)
            if toplot == None:
                return
            print "Adding into figure"
            self.figs[self.curfig].add(toplot)

    # Delete a graph from the current figure
    def delfromfig(self, args):
        self.figs[self.curfig].delete(args)
        return

    # Analyse the signals to plot and prepare the list
    def gettoplot(self, args):
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

    # List of figures
    def figlist(self, args):
        print "figlist"
        for f in self.figs:
            f.list()

    # Create a new figure, set it as current
    def new(self, toplot):
        print "newfig"
        print len(toplot), "pp"
        if type(toplot) == StringType:
            if not toplot == "":
                toplot = self.gettoplot(toplot)
            else:
                toplot = None
        elif not type(toplot) == ListType:
            return
        f = Figure(toplot)
        self.figs.append(f)
        self.curfig = self.figs.index(f)

    # List signals
    def siglist(self, args):
        for n, s in self.sigs.iteritems():
            print s

    # Delete a figure
    def delete(self, args):
        num = eval(args)
        if num > len(self.figs) or num < 1:
            return
        del self.figs[num - 1]
        # Handle self.curfig. By default, next figure becomes the current
        if len(self.figs) == 0:
            self.curfig = -1
        elif self.curfig > len(self.figs):
            self.curfig = len(self.figs) - 1
        print "Curfig : ", self.curfig

    # Select the current figure
    def select(self, args):
        num = eval(args)
        if num > len(self.figs) or num < 1:
            return
        self.curfig = num - 1
