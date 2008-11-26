from GnucapReader import *
from Signal import *
from Figure import *

class Cmds:
    def __init__(self):
        self.curfig = 0
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
        self.figs[self.curfig].plot()

    # Add a graph to the current figure
    def addtofig(self, args):
        if len(self.figs) < 1:
            self.setplot(args)
        else:
            toplot = self.gettoplot(args)
            if toplot == None:
                return
            print "Adding into figure"
            self.figs[self.curfig].add(toplot)

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
        f = Figure(toplot)
        self.figs.append(f)
        self.curfig = 0

    # List signals
    def siglist(self, args):
        for n, s in self.sigs.iteritems():
            print s
