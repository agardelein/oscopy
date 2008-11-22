from GnucapReader import *
from Signal import *
from Figure import *

class Cmds:
    figs = []
    curfig = 0
    sigs = {}
    readers = {}
    
    def __init__(self):
        self.a = 0

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

    def update(self, args):
        for v in self.readers.keys():
            sigs, u, d, n = self.readers[v].update()
            for s in u:
                self.sigs[s] = sigs[s]
            for s in n:
                self.sigs[s] = sigs[s]
            for s in d:
                del self.sigs[s]

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
            if s in self.sigs.keys():
                toplot.append(self.sigs[s])
            else:
                print s + ": Not here"

        # No signals found
        if len(toplot) < 1:
            print "No signals found"
            return

        # Can now prepare the plot
        if self.figs == []:
            self.new(toplot)
        self.curfig.plot(toplot)

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
