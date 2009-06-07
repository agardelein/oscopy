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

   _key()
      Handle keystrokes during plot
"""

import matplotlib.pyplot as plt
from graphs import Graph, LinGraph

class Figure(object):

    def __init__(self, sigs={}):
        """ Create a Figure.
        If a signal list is provided, add a graph with the signal list
        By default, create an empty list of graph and set_ the layout to horiz
        """
        self._graphs = []
        self._layout = "horiz"
        self._current = None
        if not sigs:
            return
        elif isinstance(sigs, dict):
            self.add(sigs)
        else:
            return

    def add(self, sigs={}):
        """ Add a graph into the figure and set_ it as current graph.
        Up to four graphs can be plotted on the same figure.
        Additionnal attemps are ignored.
        By default, do nothing.
        """
        if len(self._graphs) > 3:
            return
        gr = LinGraph(sigs)
        self._graphs.append(gr)
        self.select(self._graphs.index(gr) + 1)

    def delete(self, num=1):
        """ Delete a graph from the figure
        By default, delete the first graph.
        Act as a "pop" with curgraph variable.
        """
        if not isinstance(num, int):
            return
        gn = eval(num)   # Graph number
        if len(self._graphs) < 1 or gn < 1 or gn > len(self._graphs):
            return
        if self._current == self._graphs[gn - 1]:
            if len(self._graphs) == 1:
                # Only one element in the list
                self._current = None
            elif gn == len(self._graphs):
                # Last element, go to the previous
                self._current = self._graphs[gn - 2]
            else:
                self._current = self._graphs[gn]
        del self._graphs[gn - 1]
        
    def update(self, u, d):
        """ Update the graphs
        """
        if not isinstance(u, dict):
            return
        if not isinstance(d, dict):
            return

        for g in self._graphs:
            ug = {}
            dg = {}
            for sn in g.get_sigs():
                if sn in u:
                    ug[sn] = u[sn]
                elif sn in d:
                    dg[sn] = d[sn]
            g.insert(ug)
            g.remove(dg)

    def select(self, gn=0):
        """ Select the current graph
        """
        if gn < 1 or gn > len(self._graphs):
            return
        self._current = self._graphs[gn - 1]

    def list(self):
        """ List the graphs from the figure
        """
        for gn, g in enumerate(self._graphs):
            if g == self._current:
                print "   *",
            else:
                print "    ",
            print "Graph", gn + 1, ":", g

    def set_mode(self, gmode):
        """ Set the mode of the current graph
        """
        if self._current is None:
            return
        if isinstance(gmode, str):
            if gmode == "lin":
                g = LinGraph(self._current)
#            elif gmode == "fft":
#                g = FFTGraph(self._current)
#            elif gmode == "ifft":
#                g = IFFTGraph(self._current)
            else:
                return
            self._graphs[self._graphs.index(self._current)] = g
            self._current = g

    def get_layout(self):
        """ Return the figure layout"""
        return self._layout

    def set_layout(self, layout="quad"):
        """ Set the layout of the figure, default is quad
        horiz : graphs are horizontaly aligned
        vert  : graphs are verticaly aligned
        quad  : graphs are 2 x 2 at maximum
        Other values are ignored
        """
        if layout == "horiz" or layout == "vert" or layout == "quad":
            self._layout = layout
            return
        else:
            return

    def plot(self, fig):
        """ Plot the figure in Matplotlib Figure instance fig
        First compute the number of subplot and the layout
        And then really call the plot function of each graph
        """
        # Set the number of lines and rows
        if not self._graphs:
            return
        if self._layout == "horiz":
            nx = len(self._graphs)
            ny = 1
        elif self._layout == "vert":
            nx = 1
            ny = len(self._graphs)
        elif self._layout == "quad":
            if len(self._graphs) == 1:
                nx = 1
                ny = 1
            elif len(self._graphs) == 2:
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
        for gn, g in enumerate(self._graphs):
            ax = fig.add_subplot(nx, ny, gn+1)
            g.plot(ax)
        self.kid = fig.canvas.mpl_connect('key_press_event', self._key)

    def insert(self, sigs):
        """ Add a signal into the current graph
        """
        if self._current is not None:
            self._current.insert(sigs)

    def remove(self, sigs, where="current"):
        """ Delete a signal from the current graph
        """
        if where == "current":
            if self._current is not None:
                self._current.remove(sigs)
        elif where == "all":
            for g in self._graphs:
                g.remove(sigs)

    def get_sigs(self):
        """ Return the list of signals in all graphs
        """
        for g in self._graphs:
            for sn in g.get_sigs():
                yield sn

    def set_unit(self, xu, yu=""):
        """ Set the current graph units
        """
        if self._current is not None:
            self._current.unit = xu, yu

    def set_scale(self, scale):
        """ Set the current graph axis scale
        """
        if self._current is not None:
            self._current.scale = scale

    def set_range(self, arg):
        """ Set the axis range of the current graph
        """
        if self._current is not None:
            self._current.range = arg

    def _key(self, event):
        """ Handle key press event
        1, 2: toggle vertical cursors #0 and #1
        3, 4: toggle horizontal cursors #0 and #1
        """
        if event.inaxes is None:
            return
        # Find graph
        g = None
        for g in self._graphs:
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

    layout = property(get_layout, set_layout)

