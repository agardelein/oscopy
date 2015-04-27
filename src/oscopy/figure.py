""" Figure handler

A figure consist of a list of up to 4 graphs, with a layout.
Signal list are passed directly to each graph.
Layout can be either all graphs stacked verticaly, horizontaly or in quad

Properties
   signals  read/write   Dict of Signals
   graphs   read/write   List of Graphs
   layout   read/write   String representing the layout
   
Signals
   None

Abbreviations
   curgraph: alias to the current graph
   gn:       graph number
   g:        graph
   sn:       signal name

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

   [get|set]_mode(mode)
      Set the mode of the current graph

   [get|set]_layout(layout)
      Set the layout, either horiz, vert or quad

   draw()
      Overload of matplotlib.pyplot.figure.draw()

   signals()
      Return a list of the signals in all graphs

   _key()
      Handle keystrokes during plot
"""

from matplotlib.figure import Figure as MplFig, Axes
from .graphs import Graph, LinGraph, PolarGraph

MAX_GRAPHS_PER_FIGURE = 4

class Figure(MplFig):
    """ Manage figure and its layout
    """
    def __init__(self, sigs={}, fig=None):
        """ Instanciate a Figure.
        If a signal list is provided, add a graph with the signal list
        By default, create an empty list of graph and set the layout to horiz

        Parameters
        ----------
        sigs: dict of Signals
        If provided, the function instanciate the Figure with one Graph and
        insert the Signals

        fig: Not used

        Returns
        -------
        The figure instanciated and initialized
        """
        MplFig.__init__(self)

        self._layout = "horiz"
        self._MODES_NAMES_TO_OBJ = {"lin":LinGraph, "polar":PolarGraph}
        self._kid = None
        # FIXME: Slow way... Surely there exist something faster
        self._OBJ_TO_MODES_NAMES = {}
        for k, v in self._MODES_NAMES_TO_OBJ.items():
            self._OBJ_TO_MODES_NAMES[v] = k

        if not sigs:
            return
        elif isinstance(sigs, dict):
            self.add(sigs)
        else:
            print(sigs)
            assert 0, _("Bad type")

    def add(self, sigs={}):
        """ Add a graph into the figure and set it as current graph.
        Up to four graphs can be plotted on the same figure.
        Additionnal attemps are ignored.
        By default, do nothing.

        Parameter
        ---------
        sigs: dict of Signals
        The list of Signals to add

        Returns
        -------
        Nothing
        """
        if len(self.axes) > (MAX_GRAPHS_PER_FIGURE - 1):
            assert 0, _("Maximum graph number reached")

        # _graph_position use the current length of self.axes to compute
        # the graph coordinates. So we add a fake element into the list
        # and we remove it once the size is computed
        key = 'Nothing'
        a = Axes(self, (0, 0, 1, 1))
        self._axstack.add(key, a)
        gr = LinGraph(self, self._graph_position(len(self.axes) - 1),\
                          sigs, label=str(len(self.axes)))
        self._axstack.remove(a)
        # Allocate a free number up to MAX_GRAPH_PER_FIGURE
        num = 0
        while num < MAX_GRAPHS_PER_FIGURE:
            if self._axstack.get(num) is None:
                break
            num = num + 1
        ax = self._axstack.add(num, gr)

        # Force layout refresh
        self.set_layout(self._layout)

    def delete(self, num=1):
        """ Delete a graph from the figure
        By default, delete the first graph.

        Parameter
        ---------
        num: integer
        The position of the graph to delete

        Returns
        -------
        Nothing
        """
        if not isinstance(num, int):
            assert 0, _("Bad graph number")
        if len(self.axes) < 1 or num < 1 or num > len(self.axes):
            assert 0, _("Bad graph number")
        self._axstack.remove(self._axstack[num - 1][1][1])
        # Force layout refresh
        self.set_layout(self._layout)
        
    def update(self, u, d):
        """ Update the graphs
        FIXME: This function is deprecated by the use of GObject event system
        
        For each Graph in the Figure, replace updated signals in u, and remove
        deleted signals in d

        Parameters
        ----------
        u: Dict of Signals
        List of updated Signals to replace in the graphs
        
        d: Dict of Signals
        List of deleted Signals to remove from the graphs

        Returns
        -------
        Nothing
        """
        if not isinstance(u, dict):
            assert 0, _("Bad type")
        if not isinstance(d, dict):
            assert 0, _("Bad type")
        for g in self.axes:
            ug = {}
            dg = {}
            for sn in g.signals():
                if sn in u:
                    ug[sn] = u[sn]
                elif sn in d:
                    dg[sn] = d[sn]
            g.insert(ug)
            g.remove(dg)

#    def get_mode(self):
#        """ Return the mode of the current graph"""
#        FIXME: DISABLED AS ONLY ONE MODE CURRENTLY AVAILABLE
#        return self._OBJ_TO_MODES_NAMES(self._current)

    def set_mode(self, gr, new_mode):
        """ Set the mode of the current graph
        Replace the graph provided by a new one of other mode, i.e. copy the
        Signals from it.
        The graph is replaced in the Figure internal list of graphs

        Parameters
        ----------
        args: tuple of (graph, gmode)
           graph: graph
           The graph to change
           gmode: string
           The new mode

        Returns
        -------
        Nothing
        """
        # Currently this cannot be tested (only one mode available)
        old_graph = gr
        gmode = new_mode
        if not self.axes:
            assert 0, _("No graph defined")
        pos = self._graph_position(len(self.axes) - 1)
        a = (self._MODES_NAMES_TO_OBJ[gmode])(self, pos, old_graph)
        idx = self._axstack.as_list().index(old_graph)
        self._axstack.remove(old_graph)
        self._axstack.add(idx, a)

    def get_layout(self):
        """ Return the figure layout

        Parameter
        ---------
        Nothing

        Returns
        -------
        string
        The name of the current layout
        """
        return self._layout

    def set_layout(self, layout="quad"):
        """ Set the layout of the figure, default is 'quad'
        'horiz' : graphs are horizontaly aligned
        'vert'  : graphs are verticaly aligned
        'quad'  : graphs are 2 x 2 at maximum
        Other values are ignored

        Parameters
        ----------
        layout: string
        One of ['horiz'|'vert'|'quad']. Default is 'quad'

        Returns
        -------
        Nothing
        """
        # To change the layout: use ax.set_position

        if layout == "horiz" or layout == "vert" or layout == "quad":
            self._layout = layout
        else:
            assert 0, _("Bad layout")

        for gn, g in enumerate(self.axes):
            g.set_position(self._graph_position(gn))

    def draw(self, canvas):
        """ Draw the Figure
        Wrapper to parent class function. Set also the key_press_event callback

        Parameter
        ---------
        canvas: Canvas
        Canvas to use to draw the figure

        Returns
        -------
        tmp: Value returned by parent class function call
        """
        tmp = MplFig.draw(self, canvas)
        if not self._kid:
            self._kid = self.canvas.mpl_connect('key_press_event', self._key)

        return tmp

    def _key(self, event):
        """ Handle key press event
        1, 2: toggle vertical cursors #0 and #1
        3, 4: toggle horizontal cursors #0 and #1

        Parameter
        ---------
        event: Matplotlib Event
        The event that triggered the call-back

        Returns
        -------
        Nothing
        """
        if event.inaxes is None:
            return
        # Find graph
        g = None
        for g in self.axes:
            if g == event.inaxes:
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
        """ Compute the position of the graph upon its number and the layout

        Parameter
        ---------
        num: integer
        The position of the graph in the list

        Returns
        -------
        array of 4 floats
        The coordinates of the graph
        """
        # 1 graph: x:0->1 y:0->1   dx=1 dy=1
        # 3 graphs horiz: x:0->.333 y:0->1 dx=.333 dy=1
        # 3 graphs quads: x:0->.5 y:0->.5  dx=.5 dy=.5

        if self._layout == "horiz":
            dx = 1
            dy = 1.0 / len(self.axes)
            num_to_xy = [[0, y] for y in range(len(self.axes))]
        elif self._layout == "vert":
            dx = 1.0 / len(self.axes)
            dy = 1
            num_to_xy = [[x, 0] for x in range(len(self.axes))]
        elif self._layout == "quad":
            dx = 0.5
            dy = 0.5
            num_to_xy = [[x, y] for y in range(2) for x in range(2)]
        else:
            assert 0, _("Bad layout")

        pos_x = num_to_xy[num][0]
        pos_y = num_to_xy[len(self.axes) - num - 1][1]
        x1 = pos_x * dx + 0.15 * dx
        y1 = pos_y * dy + 0.15 * dy
        return [x1, y1, dx * 0.75, dy * 0.75]

    @property
    def signals(self):
        """ Return the list of signals in all graphs
        Generator function.

        Parameter
        ---------
        Nothing

        Returns
        -------
        A list of the signals contained in all graphs
        """
        for g in self.axes:
            for sn in g.get_signals():
                yield sn

    @property
    def graphs(self):
        """ Return the graph list
        
        Parameter
        ---------
        Nothing

        Returns
        -------
        The list of graphs
        """
        return self.axes

    layout = property(get_layout, set_layout)
#    mode = property(get_mode, set_mode)
