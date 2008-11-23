from Graph import *
import matplotlib.pyplot as plt
from pylab import *

class Figure:

    def __init__(self, sigs = None):
        self.graphs = []
        self.mode = 0
        self.curgraph = 0
        if sigs == None:
            return
        gr = Graph(sigs)
        self.graphs.append(gr)

    # Add a graph into the figure, select the right mode
    def add(self, sigs = None):
        if self.mode == 3:
            if len(self.graphs) < 4:
                gr = Graph(sigs)
                self.graphs.append(gr)
                self.setgraph(4)
                return
            else:
                return
        if self.mode == 0:
            self.setmode(1)
            print "Here"
            gr = Graph(sigs)
            print "There"
            self.graphs.append(gr)
            self.setgraph(1)
            return
        if self.mode == 1 or self.mode == 2:
            self.setmode(3)
            gr = Graph(sigs)
            self.graphs.append(gr)
            self.setgraph(3)

    # Set the signals of the current graph
    def setf(self, sigs = None):
        self.graphs[self.curgraph].setg(sigs)
                        
    def delete(self):
        a = 0

    def update(self):
        a = 0

    # List the graphs
    def list(self):
        for g in self.graphs:
            print g

    # Plot the signals
    def plot(self):
        if len(self.graphs) < 1:
            return
        nx = (self.mode >= 2) + 1
        ny = (self.mode == 1 or self.mode == 3) + 1
        for i, g in enumerate(self.graphs):
            subplot(nx, ny, i+1)
            hold(True)
            for n, s in g.sigs.iteritems():
                x = s.ref.pts
                y = s.pts
                plot(x, y)
            hold(False)
            xlabel(g.xaxis)
        show()
        return

    # Define graphical mode :
    # 0 : one subplot
    # 1 : two subplots, top/bottom
    # 2 : two subplots, left/right
    # 3 : four subplots
    def setmode(self, mode = 0):
        if mode >= 0 and mode <= 3:
            self.mode = mode
            return
        else:
            return

    # Select the current graph, depending on current mode
    def setgraph(self, graph = 0):
        if graph < 0:
            return
        if self.mode == 0:
            self.curgraph = 0
            return
        if self.mode == 1 or self.mode == 2:
            if graph > 1:
                return
            else:
                self.curgraph = graph
                return
        if self.mode == 3:
            if graph > 3:
                return
            else:
                self.curgraph = graph
                return

    # Set the signals into the current graph
    def setsigs(self, sigs = None):
        self.graphs[curgraph].add(sigs)
