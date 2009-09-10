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

    def __init__(self, sigs={}, fig=None):
        """ Create a Figure.
        If a signal list is provided, add a graph with the signal list
        By default, create an empty list of graph and set_ the layout to horiz
        """
        self._graphs = []
        self._axes = []
        self._layout = "horiz"
        self._current = None
        self._MODES_NAMES_TO_OBJ = {"lin":LinGraph}
        self._kid = None
        # Slow way... Surely there exist something faster
        self._OBJ_TO_MODES_NAMES = {}
        for k, v in self._MODES_NAMES_TO_OBJ.iteritems():
            self._OBJ_TO_MODES_NAMES[v] = k

        if fig == None:
            self._fig = plt.figure()
        else:
            self._fig = fig

        if not sigs:
            return
        elif isinstance(sigs, dict):
            self.add(sigs)
        else:
            assert 0, "Bad type"

    def add(self, sigs={}):
        """ Add a graph into the figure and set it as current graph.
        Up to four graphs can be plotted on the same figure.
        Additionnal attemps are ignored.
        By default, do nothing.
        """
        if len(self._graphs) > 3:
            assert 0, "Bad graph number"

        self._graphs.append(None)

        ax = self._fig.add_axes(self._graph_position(len(self._graphs) - 1),\
                                    label=str(len(self._graphs)))
        gr = LinGraph(ax, sigs)

        self._graphs[self._graphs.index(None)] = gr
        self._axes.append(ax)
        self.set_current(self._graphs.index(gr) + 1)
        # Force layout refresh
        self.set_layout(self._layout)

    def delete(self, num=1):
        """ Delete a graph from the figure
        By default, delete the first graph.
        Act as a "pop" with curgraph variable.
        """
        if not isinstance(num, int):
            assert 0, "Bad graph number"
        if len(self._graphs) < 1 or num < 1 or num > len(self._graphs):
            assert 0, "Bad graph number"
        if self._current == self._graphs[num - 1]:
            if len(self._graphs) == 1:
                # Only one element in the list
                self._current = None
            elif num == len(self._graphs):
                # Last element, go to the previous
                self._current = self._graphs[num - 2]
            else:
                self._current = self._graphs[num]
        del self._graphs[num - 1]
        del self._axes[num - 1]
        
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
            for sn in g.signals():
                if sn in u:
                    ug[sn] = u[sn]
                elif sn in d:
                    dg[sn] = d[sn]
            g.insert(ug)
            g.remove(dg)
            # ipython: to update data in a line2D:
            # l.set_data() and then plot() from matplotlib to update the plot

    def get_current(self):
        """ Return the number of the current graph """
        return self._graphs.index(self._current) + 1

    def set_current(self, gn=0):
        """ Select the current graph
        """
        if gn < 1 or gn > len(self._graphs):
            assert 0, "Bad graph number"
        self._current = self._graphs[gn - 1]

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
        # To change the layout: use ax.set_position

        if layout == "horiz" or layout == "vert" or layout == "quad":
            self._layout = layout
        else:
            assert 0, "Bad layout"

        for gn, g in enumerate(self._graphs):
            g.position = self._graph_position(gn)

    def plot(self):
        """ Plot the figure in Matplotlib Figure instance fig
        First compute the number of subplot and the layout
        And then really call the plot function of each graph
        """
        # Set the number of lines and rows
        if not self._graphs:
            assert 0, "No graphs defined"

        # Plot the whole figure
        for gn, g in enumerate(self._graphs):
            g.plot()
#            self._axes = ax
        if not self._kid:
            self._kid = self._fig.canvas.mpl_connect('key_press_event', self._key)

    def draw(self):
        """ Draw the figure
        To be called by when the figure should be updated
        """
        self._fig.canvas.draw()


    def insert(self, sigs):
        """ Add a signal into the current graph
        """
        if self._current is not None:
            return self._current.insert(sigs)
        else:
            assert 0, "No graph defined"

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

    def _graph_position(self, num):
        """ Compute the position of the graph upon its number
        """
        # 1 graph: x:0->1 y:0->1   dx=1 dy=1
        # 3 graphs horiz: x:0->.333 y:0->1 dx=.333 dy=1
        # 3 graphs quads: x:0->.5 y:0->.5  dx=.5 dy=.5

        if self._layout == "horiz":
            dx = 1
            dy = 1.0 / len(self._graphs)
            num_to_xy = [[0, y] for y in xrange(len(self._graphs))]
        elif self._layout == "vert":
            dx = 1.0 / len(self._graphs)
            dy = 1
            num_to_xy = [[x, 0] for x in xrange(len(self._graphs))]
        elif self._layout == "quad":
            dx = 0.5
            dy = 0.5
            num_to_xy = [[x, y] for y in xrange(2) for x in xrange(2)]
        else:
            assert 0, "Bad layout"

        pos_x = num_to_xy[num][0]
        pos_y = num_to_xy[len(self._graphs) - num - 1][1]
        x1 = pos_x * dx + 0.15 * dx
        y1 = pos_y * dy + 0.15 * dy
        return [x1, y1, dx * 0.75, dy * 0.75]

    @property
    def signals(self):
        """ Return the list of signals in all graphs
        """
        for g in self._graphs:
            for sn in g.get_signals():
                yield sn

    @property
    def grafs(self):
        """ Return the graph list """
        return self._graphs

    layout = property(get_layout, set_layout)
    mode = property(get_mode, set_mode)
    current = property(get_current, set_current)
