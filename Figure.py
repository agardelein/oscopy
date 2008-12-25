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

   delete(num)
      Delete a graph

   update(toupdate, todelete)
      Update the signals of the figure

   select(graphnum)
      Select the graph to be the default

   list()
      List the graph of the current figure

   setmode(mode)
      Set the mode of the current graph

   setlayout(layout)
      Set the layout, either horiz, vert or quad

   plot()
      Plot the figure

#   setsigs(sigs)
#      Add signals into the current graph
   
   getsigs()
      Return a list of the signals in all graphs

   setf(sigs)
      Set the signals of the current graph

   fft()
      Do fft of signals of current graph before plotting

   iff()
      Do ifft of signal of current graph before plotting

   nofft()
      Do neither fft nor ifft
"""

from LinGraph import *
from LogGraphs import *
import matplotlib.pyplot as plt
from pylab import *
from types import *

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
        gr = LinGraph(sigs)
        self.graphs.append(gr)

    def add(self, sigs = None):
        """ Add a graph into the figure and set it as current graph.
        Up to four graphs can be plotted on the same figure.
        Additionnal attemps are ignored.
        By default, do nothing.
        """
        if len(self.graphs) > 3:
            return
        gr = LinGraph(sigs)
        self.graphs.append(gr)
        self.select(len(self.graphs) - 1)

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

    def update(self, u, d):
        # TODO : update
        """ Update the graphs
        """
        for g in self.graphs:
            # Get the signal list from the graph
            sg = g.getsigs()
            # Generate the list of updated signals
            ug = {}
            for k, s in u.iteritems():
                if k in sg:
                    ug[k] = u[k]
            # Generate the list of deleted signals
            dg = []
            for k in d:
                if k in sg:
                    dg.append(k)
            # Update the graph
            g.update(ug, dg)

    def select(self, graph = 0):
        """ Select the current graph
        """
        if graph < 0 or graph > len(self.graphs):
            return
        self.curgraph = graph

    def list(self):
        """ List the graphs from the figure
        """
        for i, g in enumerate(self.graphs):
            print "  Graph :", i, g

    def setmode(self, gmode):
        """ Set the mode of the current graph
        """
        if type(gmode) == StringType:
            if gmode == "lin":
                g = LinGraph(self.graphs[self.curgraph])
                self.graphs[self.curgraph] = g
            elif gmode == "logx":
                g = LogxGraph(self.graphs[self.curgraph])
                self.graphs[self.curgraph] = g
            elif gmode == "logy":
                g = LogyGraph(self.graphs[self.curgraph])
                self.graphs[self.curgraph] = g
            elif gmode == "loglog":
                g = LoglogGraph(self.graphs[self.curgraph])
                self.graphs[self.curgraph] = g
                
    def setlayout(self, layout = "quad"):
        """ Set the layout of the figure, default is quad
        horiz : graphs are horizontaly aligned
        vert  : graphs are verticaly aligned
        quad  : graphs are 2 x 2 at maximum
        Other values are ignored
        """
        if layout == "horiz" or layout == "vert" or layout == "quad":
            self.layout = layout
            return
        else:
            return

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

    def insert(self, sigs):
        """ Add a signal into the current graph
        """
        if self.curgraph < 0 or self.curgraph > len(self.graphs):
            return
        self.graphs[self.curgraph].insert(sigs)

    def remove(self, sigs):
        """ Delete a signal from the current graph
        """
        if self.curgraph < 0 or self.curgraph > len(self.graphs):
            return
        self.graphs[self.curgraph].remove(sigs)

#    def setsigs(self, sigs = None):
#        """ Add signals into the current graph
#        """
#        self.graphs[curgraph].insert(sigs)

    def getsigs(self):
        """ Return the list of signals in all graphs
        """
        sigs = []
        for i, g in enumerate(self.graphs):
            sigs.extend(g.getsigs())
        return sigs

    def setf(self, sigs = None):
        """ Set the signals of the current graph
        By default, do nothing
        """
        if self.curgraph < 0 or self.curgraph > len(self.graphs):
            return
        self.graphs[self.curgraph].setg(sigs)

    def fft(self):
        """ Set fft mode to the current graph
        """
        if self.curgraph < 0 or self.curgraph > len(self.graphs):
            return
        self.graphs[self.curgraph].fft()

    def ifft(self):
        """ Set ifft mode to the current graph
        """
        if self.curgraph < 0 or self.curgraph > len(self.graphs):
            return
        self.graphs[self.curgraph].ifft()

    def nofft(self):
        """ Set no fft mode to the current graph
        """
        if self.curgraph < 0 or self.curgraph > len(self.graphs):
            return
        self.graphs[self.curgraph].nofft()
