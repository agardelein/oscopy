""" Figure handler

A figure consist of a list of up to 4 graphs, with a layout.
Signal list are passed directly to each graph.
Layout can be either all graphs stacked verticaly, horizontaly or in quad

The variable curgraph represent the active graph on which operations are done.
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

   getsigs()
      Return a list of the signals in all graphs

   setunit()
      Set the current graph units

   setscale()
      Set the current graph axis scale

   setrange()
      Set the current graph axis range
"""

import pylab
import types
from Graphs import Graph
from Graphs.LinGraphs import LinGraph
from Graphs.FFTGraph import FFTGraph, IFFTGraph

class Figure:

    def __init__(self, sigs = {}):
        """ Create a Figure.
        If a signal list is provided, add a graph with the signal list
        By default, create an empty list of graph and set the layout to horiz
        """
        self.graphs = []
        self.layout = "horiz"
        self.curgraph = None
        if sigs == {}:
            return
        elif type(sigs) == types.DictType:
            self.add(sigs)
        else:
            return

    def add(self, sigs = {}):
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
        if self.curgraph == self.graphs[gn - 1]:
            if len(self.graphs) == 1:
                # Only one element in the list
                self.curgraph = None
            elif gn == len(self.graphs):
                # Last element, go to the previous
                self.curgraph = self.graphs[gn - 2]
            else:
                self.curgraph = self.graphs[gn]
        del self.graphs[gn - 1]
        
    def update(self, u, d):
        """ Update the graphs
        """
        if type(u) != types.DictType:
            return
        if type(d) != types.DictType:
            return

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
        self.curgraph = self.graphs[gn - 1]

    def list(self):
        """ List the graphs from the figure
        """
        for gn, g in enumerate(self.graphs):
            if g == self.curgraph:
                print "   *",
            else:
                print "    ",
            print "Graph", gn + 1, ":", g

    def setmode(self, gmode):
        """ Set the mode of the current graph
        """
        if self.curgraph == None:
            return
        if type(gmode) == types.StringType:
            if gmode == "lin":
                g = LinGraph(self.curgraph)
                self.curgraph = g
            elif gmode == "fft":
                g = FFTGraph(self.curgraph)
                self.curgraph = g                
            elif gmode == "ifft":
                g = IFFTGraph(self.curgraph)
                self.curgraph = g                
                
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
            pylab.subplot(nx, ny, gn+1)
            g.plot()

    def insert(self, sigs):
        """ Add a signal into the current graph
        """
        if not self.curgraph == None:
            self.curgraph.insert(sigs)

    def remove(self, sigs, where = "current"):
        """ Delete a signal from the current graph
        """
        if where == "current":
            if not self.curgraph == None:
                self.curgraph.remove(sigs)
        elif where == "all":
            for g in self.graphs:
                g.remove(sigs)

    def getsigs(self):
        """ Return the list of signals in all graphs
        """
        for g in self.graphs:
            for sn in g.getsigs():
                yield sn

    def setunit(self, xu, yu = ""):
        """ Set the current graph units
        """
        if not self.curgraph == None:
            self.curgraph.setunit(xu, yu)

    def setscale(self, a):
        """ Set the current graph axis scale
        """
        if not self.curgraph == None:
            self.curgraph.setscale(a)

    def setrange(self, a1 = "reset", a2 = None, a3 = None, a4 = None):
        """ Set the axis range of the current graph
        """
        if not self.curgraph == None:
            self.curgraph.setrange(a1, a2, a3, a4)

