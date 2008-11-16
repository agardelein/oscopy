from Gnucap import *
from Signal import *
from Figure import *


class Cmds:
    a = -1
    figs = []
    curfig = 0
    sigs = []
    files = []
    
    def __init__(self):
        self.a = 0

    # Load a file
    def load(self, args):
        for s in self.files:
            if s == args:
                print "Already here"
                return
        obj = Gnucap() # for now only Gnucap is supported
        self.sigs.extend(obj.loadfile(args))
        print args, ":"
        for ns in self.sigs:
            print ns.name, "/", ns.domain
        self.files.append(args)

    # Plot signals
    def plot(self, args):
        if self.sigs == []:
            print "No signal loaded"
            return
        self.a = self.a + 1
        print "plot " + str(self.a)
        if self.figs == []:
            self.new()

    # List of figures
    def list(self, args):
        print "list"
        for f in self.figs:
            f.list()

    # Create a new figure, set it as current
    def new(self):
        print "newfig"
        self.curfig = Figure()
        self.figs.append(self.curfig)

    def siglist(self, args):
        for s in self.sigs:
            print s
