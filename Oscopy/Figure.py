""" Figure handler

A figure consist of a list of up to 4 graphs, with a layout.
Signal list are passed directly to each graph.
Layout can be either all graphs stacked verticaly, horizontaly or in quad

curgraph: alias to the current graph
gn: graph number
g: graph
sn: signal name

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

   set_mode(mode)
      Set the mode of the current graph

   set_layout(layout)
      Set the layout, either horiz, vert or quad

   plot()
      Plot the figure

   get_sigs()
      Return a list of the signals in all graphs

   set_unit()
      Set the current graph units

   set_scale()
      Set the current graph axis scale

   set_range()
      Set the current graph axis range

   key()
      Handle keystrokes during plot
"""

import types
import matplotlib.pyplot as plt
from Graphs import Graph
from Graphs.LinGraphs import LinGraph
from Graphs.FFTGraph import FFTGraph, IFFTGraph

class Figure:

    def __init__(self, sigs = {}):
        """ Create a Figure.
        If a signal list is provided, add a graph with the signal list
        By default, create an empty list of graph and set_ the layout to horiz
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
        """ Add a graph into the figure and set_ it as current graph.
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
        if not type(num) == types.IntType:
            return
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
            for sn in g.get_sigs():
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

    def set_mode(self, gmode):
        """ Set the mode of the current graph
        """
        if self.curgraph is None:
            return
        if type(gmode) == types.StringType:
            if gmode == "lin":
                g = LinGraph(self.curgraph)
#            elif gmode == "fft":
#                g = FFTGraph(self.curgraph)
#            elif gmode == "ifft":
#                g = IFFTGraph(self.curgraph)
            else:
                return
            self.graphs[self.graphs.index(self.curgraph)] = g
            self.curgraph = g

    def set_layout(self, layout = "quad"):
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

    def plot(self, fig):
        """ Plot the figure in Matplotlib Figure instance fig
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
            ax = fig.add_subplot(nx, ny, gn+1)
            g.plot(ax)
        self.kid = fig.canvas.mpl_connect('key_press_event', self.key)

    def insert(self, sigs):
        """ Add a signal into the current graph
        """
        if self.curgraph is not None:
            self.curgraph.insert(sigs)

    def remove(self, sigs, where = "current"):
        """ Delete a signal from the current graph
        """
        if where == "current":
            if self.curgraph is not None:
                self.curgraph.remove(sigs)
        elif where == "all":
            for g in self.graphs:
                g.remove(sigs)

    def get_sigs(self):
        """ Return the list of signals in all graphs
        """
        for g in self.graphs:
            for sn in g.get_sigs():
                yield sn

    def set_unit(self, xu, yu = ""):
        """ Set the current graph units
        """
        if self.curgraph is not None:
            self.curgraph.set_unit(xu, yu)

    def set_scale(self, a):
        """ Set the current graph axis scale
        """
        if self.curgraph is not None:
            self.curgraph.set_scale(a)

    def set_range(self, a1 = "reset_", a2 = None, a3 = None, a4 = None):
        """ Set the axis range of the current graph
        """
        if self.curgraph is not None:
            self.curgraph.set_range(a1, a2, a3, a4)

    def key(self, event):
        """ Handle key press event
        1, 2: toggle vertical cursors #0 and #1
        3, 4: toggle horizontal cursors #0 and #1
        """
        if event.inaxes is None:
            return
        # Find graph
        g = None
        for g in self.graphs:
            if g.ax == event.inaxes:
                break
            else:
                g = None
        if g is None:
            return
        # Set cursor for graph
        if event.key == "1":
            g.toggle_cursors("vert", 0, event.xdata)
        elif event.key == "2":
            g.toggle_cursors("vert", 1, event.xdata)
        elif event.key == "3":
            g.toggle_cursors("horiz", 0, event.ydata)
        elif event.key == "4":
            g.toggle_cursors("horiz", 1, event.ydata)
        else:
            return
        event.canvas.draw()
