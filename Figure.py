from Graph import *
import matplotlib.pyplot as plt
from pylab import *

class Figure:

    def __init__(self, sigs = None):
        self.graphs = []
        self.mode = "horiz"
        self.curgraph = -1
        if sigs == None:
            return
        gr = Graph(sigs)
        self.graphs.append(gr)

    # Add a graph into the figure, select the right mode
    def add(self, sigs = None):
        if len(self.graphs) > 3:
            return
        gr = Graph(sigs)
        self.graphs.append(gr)
        self.setgraph(len(self.graphs))

    # Set the signals of the current graph
    def setf(self, sigs = None):
        self.graphs[self.curgraph].setg(sigs)

    # Delete a graph from the figure, default is the first one
    def delete(self, num = 0):
        if len(self.graphs) < 1 or eval(num) > len(self.graphs) - 1:
            return
        del self.graphs[eval(num)]
        ## TODO: Handle self.curgraph

    def update(self):
        a = 0

    # List the graphs
    def list(self):
        for g in self.graphs:
            print g

    # Plot the signals
    def plot(self):
        # Set the number of lines and rows
        if len(self.graphs) < 1:
            return
        if self.mode == "horiz":
            nx = len(self.graphs)
            ny = 1
        elif self.mode == "vert":
            nx = 1
            ny = len(self.graphs)
        elif self.mode == "quad":
            if len(self.graphs) == 1:
                nx = 1
                ny = 1
            elif len(self.graphs) == 2:
                # For two graphs in quad config, go to horiz
                nx = 2
                ny = 1
            else:
                nx = 2
                ny = 2
        else:
            nx = 2
            ny = 2

        # Plot the whole figure
        for i, g in enumerate(self.graphs):
            print i
            subplot(nx, ny, i+1)
            hold(True)
            for n, s in g.sigs.iteritems():
                x = s.ref.pts
                y = s.pts
                plot(x, y)
            hold(False)
            xlabel(g.xaxis)
        return

    # Define graphical mode :
    # horiz : graphs are horizontaly aligned
    # vert  : graphs are verticaly aligned
    # quad  : graphs are 2 x 2 at maximum
    def setmode(self, mode = "quad"):
        if mode == "horiz" or mode == "vert" or mode == "quad":
            self.mode = mode
            return
        else:
            return

    # Select the current graph, depending on current mode
    def setgraph(self, graph = 0):
        if graph < 0 or graph > len(self.graphs):
            return
        self.curgraph = graph

    # Set the signals into the current graph
    def setsigs(self, sigs = None):
        self.graphs[curgraph].add(sigs)
