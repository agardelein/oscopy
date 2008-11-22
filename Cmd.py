from GnucapReader import *
from Signal import *
from Figure import *
import matplotlib.pyplot as plt


class Cmds:
    figs = []
    curfig = 0
    sigs = {}
    files = []
    
    def __init__(self):
        self.a = 0

    # Load a file
    def load(self, args):
        # File already loaded ?
        if args in self.files:
            print "File already loaded"
            return
            
        obj = GnucapReader() # for now only Gnucap is supported
        self.sigs = obj.loadfile(args)
        print args, ":"
        for ns, si in self.sigs.iteritems():
            print si
        self.files.append(args)

    # Plot signals
    def plot(self, args):
        print "plot"
        toplot = []
        # Are there signals to plot ?
        if self.sigs == []:
            print "No signal loaded"
            return

        # Prepare the signal list
        for s in args.split(","):
            s = s.strip()
            if s in self.sigs:
                toplot.append(s)
            else:
                print s + ": Not here"

        # No signals found
        if len(toplot) < 1:
            print "No signals found"
            return

        # Can now prepare the plot
        if self.figs == []:
            self.new(toplot)

    # List of figures
    def list(self, args):
        print "list"
        for f in self.figs:
            f.list()

    # Create a new figure, set it as current
    def new(self, toplot):
        print "newfig"
        self.curfig = Figure(toplot)
        self.figs.append(self.curfig)

    # List signals
    def siglist(self, args):
        for n, s in self.sigs.iteritems():
            print s
