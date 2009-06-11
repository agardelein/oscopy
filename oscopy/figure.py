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

   get_signals()
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
        self._MODES_NAMES_TO_OBJ = {"lin":LinGraph}
        # Slow way... Surely there exist something faster
        self._OBJ_TO_MODES_NAMES = {}
        for k, v in self._MODES_NAMES_TO_OBJ.iteritems():
            self._OBJ_TO_MODES_NAMES[v] = k

        if not sigs:
            return
        elif isinstance(sigs, dict):
            self.add(sigs)
        else:
            assert 0, "Bad type"

    def add(self, sigs={}):
        """ Add a graph into the figure and set_ it as current graph.
        Up to four graphs can be plotted on the same figure.
        Additionnal attemps are ignored.
        By default, do nothing.
        """
        if len(self._graphs) > 3:
            assert 0, "Bad graph number"
        gr = LinGraph(sigs)
        self._graphs.append(gr)
        self.select(self._graphs.index(gr) + 1)

    def delete(self, num=1):
        """ Delete a graph from the figure
        By default, delete the first graph.
        Act as a "pop" with curgraph variable.
        """
        if not isinstance(num, int):
            assert 0, "Bad graph number"
        gn = eval(num)   # Graph number
        if len(self._graphs) < 1 or gn < 1 or gn > len(self._graphs):
            assert 0, "Bad graph number"
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
            assert 0, "Bad type"
        if not isinstance(d, dict):
            assert 0, "Bad type"

        for g in self._graphs:
            ug = {}
            dg = {}
            for sn in g.get_signals():
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
            assert 0, "Bad graph number"
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

    def get_mode(self):
        """ Return the mode of the current graph"""
        return self._OBJ_TO_MODES_NAMES(self._current)

    def set_mode(self, gmode):
        """ Set the mode of the current graph
        """
        # Currently this cannot be tested (only one mode available)
        if self._current is None:
            assert 0, "No graph defined"
        g = (self._MODES_NAMES_TO_OBJ(gmode))(self._current)
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
            assert 0, "Bad layout"

    def plot(self, fig):
        """ Plot the figure in Matplotlib Figure instance fig
        First compute the number of subplot and the layout
        And then really call the plot function of each graph
        """
        # Set the number of lines and rows
        if not self._graphs:
            assert 0, "No graphs defined"
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
        else:
            assert 0, "Bad location"

    def get_unit(self):
        """ Return the current graph unit"""
        if self._current is not None:
            return self._current.unit
        else:
            assert 0, "No graph defined"
        

    def set_unit(self, unit):
        """ Set the current graph units
        """
        if self._current is not None:
            self._current.unit = unit
        else:
            assert 0, "No graph defined"

    def get_scale(self):
        """Return the current graph axis scale """
        if self._current is not None:
            return self._current.scale
        else:
            assert 0, "No graph defined"
        

    def set_scale(self, scale):
        """ Set the current graph axis scale
        """
        if self._current is not None:
            self._current.scale = scale
        else:
            assert 0, "No graph defined"

    def get_range(self):
        """ Return the axis range of the current graph"""
        if self._current is not None:
            return self._current.range
        else:
            assert 0, "No graph defined"

    def set_range(self, arg):
        """ Set the axis range of the current graph
        """
        if self._current is not None:
            self._current.range = arg
        else:
            assert 0, "No graph defined"

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

    @property
    def signals(self):
        """ Return the list of signals in all graphs
        """
        for g in self._graphs:
            for sn in g.get_signals():
                yield sn

    layout = property(get_layout, set_layout)
    range = property(get_range, set_range)
    scale = property(get_scale, set_scale)
    unit = property(get_unit, set_unit)
    mode = property(get_mode, set_mode)
