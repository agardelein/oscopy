""" Figure handler

A figure consist of a list of up to 4 graphs, with a layout.
Signal list are passed directly to each graph.
Layout can be either all graphs stacked verticaly, horizontaly or in quad

The variable curgraph represent the active graph on which operations setf and setsigs can be done.
Valitidy interval : 0..3, -1 when the figure is empty.

class:

Figure -- Handle a list of graphs

   methods:
   __init__(sigs)
      Create a figure and eventually initialize a graphics with a signal list

   add(sigs)
      Add a grapth into the figure

   setf(sigs)
      Set the signals of the current graph

   delete(num)
      Delete a graph

   list()
      List the graph of the current figure

   plot()
      Plot the figure

   setlayout(layout)
      Set the layout, either horiz, vert or quad

   select(graphnum)
      Select the graph to be the default

   setsigs(sigs)
      Add signals into the current graph
"""

from Graph import *
import matplotlib.pyplot as plt
from pylab import *

class Figure:

    def __init__(self, sigs = None):
        """ Create a Figure.
        If a signal list is provided, add a graph with the signal list
        By default, create an empty list of graph and set the layout to horiz
        """
        self.graphs = []
        self.layout = "horiz"
        self.curgraph = -1
        if sigs == None:
            return
        gr = Graph(sigs)
        self.graphs.append(gr)

    def add(self, sigs = None):
        """ Add a graph into the figure and set it as current graph.
        Up to four graphs can be plotted on the same figure.
        Additionnal attemps are ignored.
        By default, do nothing.
        """
        if len(self.graphs) > 3:
            return
        gr = Graph(sigs)
        self.graphs.append(gr)
        self.select(len(self.graphs))

    def setf(self, sigs = None):
        """ Set the signals of the current graph
        By default, do nothing
        """
        self.graphs[self.curgraph].setg(sigs)

    def delete(self, num = 0):
        """ Delete a graph from the figure
        By default, delete the first graph.
        Act as a "pop" with curgraph variable.
        """
        if len(self.graphs) < 1 or eval(num) > len(self.graphs) - 1:
            return
        del self.graphs[eval(num)]
        
        # Handle self.curgraph
        # By default, next figure becomes the current
        if len(self.graphs) == 0:
            self.curgraph = -1
        elif self.curgraph > len(self.graphs):
            self.curgraph = len(self.graphs) - 1

    def update(self):
        a = 0

    def list(self):
        """ List the graphs from the figure
        """
        for g in self.graphs:
            print g

    # Plot the signals
    def plot(self):
        """ Plot the figure
        First compute the number of subplot and the layout
        And then really call the plot function of each graph
        """
        # Set the number of lines and rows
        if len(self.graphs) < 1:
            return
        if self.layout == "horiz":
            nx = len(self.graphs)
            ny = 1
        elif self.layout == "vert":
            nx = 1
            ny = len(self.graphs)
        elif self.layout == "quad":
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
            subplot(nx, ny, i+1)
            g.plot()
        return

    def setlayout(self, layout = "quad"):
        """ Set the layout of the figure, default is quad
        horiz : graphs are horizontaly aligned
        vert  : graphs are verticaly aligned
        quad  : graphs are 2 x 2 at maximum
        """
        if layout == "horiz" or layout == "vert" or layout == "quad":
            self.layout = layout
            return
        else:
            return

    def select(self, graph = 0):
        """ Select the current graph
        """
        if graph < 0 or graph > len(self.graphs):
            return
        self.curgraph = graph

    def setsigs(self, sigs = None):
        """ Add signals into the current graph
        """
        self.graphs[curgraph].add(sigs)
