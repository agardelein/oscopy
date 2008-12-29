""" Figure handler

A figure consist of a list of up to 4 graphs, with a layout.
Signal list are passed directly to each graph.
Layout can be either all graphs stacked verticaly, horizontaly or in quad

The variable curgraph represent the active graph on which operations setf and setsigs can be done.
Valitidy interval : 1..4, 0 when the figure is empty.

gn : graph number
g : graph
sn : signal name

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
#   
   getsigs()
      Return a list of the signals in all graphs

#   setf(sigs)
#      Set the signals of the current graph
#
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
        self.curgraph = 0
        if sigs == None:
            return
        else:
            self.add(sigs)

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
        self.select(self.graphs.index(gr) + 1)

    def delete(self, num = 1):
        """ Delete a graph from the figure
        By default, delete the first graph.
        Act as a "pop" with curgraph variable.
        """
        gn = eval(num)   # Graph number
        if len(self.graphs) < 1 or gn < 1 or gn > len(self.graphs):
            return
        del self.graphs[gn - 1]
        
        # Handle self.curgraph
        # By default, next figure becomes the current
        if len(self.graphs) == 0:
            self.curgraph = 0
        elif self.curgraph > len(self.graphs):
            self.curgraph = len(self.graphs)

    def update(self, u, d):
        """ Update the graphs
        """
        for g in self.graphs:
            ug = {}
            dg = {}
            for sn in g.getsigs():
                if sn in u:
                    ug[sn] = u[sn]
                elif sn in d:
                    dg[sn] = d[sn]
            g.insert(ug)
            g.remove(dg)

    def select(self, gn = 0):
        """ Select the current graph
        """
        if gn < 1 or gn > len(self.graphs):
            return
        self.curgraph = gn - 1

    def list(self):
        """ List the graphs from the figure
        """
        for gn, g in enumerate(self.graphs):
            print "  Graph :", gn, g

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
        for gn, g in enumerate(self.graphs):
            subplot(nx, ny, gn+1)
            g.plot()
        return

    def insert(self, sigs):
        """ Add a signal into the current graph
        """
        print self.curgraph
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
        for g in self.graphs:
            for sn in g.getsigs():
                yield sn

#    def setf(self, sigs = None):
#        """ Set the signals of the current graph
#        By default, do nothing
#        """
#        if self.curgraph < 0 or self.curgraph > len(self.graphs):
#            return
#        self.graphs[self.curgraph].setg(sigs)
#
    def fft(self):
        """ Set fft mode to the current graph
        """
        if self.curgraph < 1 or self.curgraph > len(self.graphs):
            return
        self.graphs[self.curgraph].fft()

    def ifft(self):
        """ Set ifft mode to the current graph
        """
        if self.curgraph < 1 or self.curgraph > len(self.graphs):
            return
        self.graphs[self.curgraph].ifft()

    def nofft(self):
        """ Set no fft mode to the current graph
        """
        if self.curgraph < 1 or self.curgraph > len(self.graphs):
            return
        self.graphs[self.curgraph].nofft()
